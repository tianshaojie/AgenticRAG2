"""pgvector VectorIndex implementation.

Current retrieval strategy: SEQUENTIAL SCAN (no ANN index active by default).

Rationale:
- Step 2 uses sequential scan (<=> ORDER BY ... LIMIT k) intentionally.
- This is correct and gives exact results for small-to-medium datasets.
- The HNSW index is already defined in the Alembic migration (0001_initial_schema.py)
  and will be activated automatically once PostgreSQL has enough data.
- For datasets < 100k rows, sequential scan is often faster than ANN overhead.
- Switching to ANN retrieval (HNSW) requires no code change — it is controlled
  by the index existing on the table. PostgreSQL will use it automatically once
  the planner decides it is beneficial (or via `SET enable_seqscan = off`).

To explicitly force HNSW in production:
  SET hnsw.ef_search = 64;
  SET enable_seqscan = off;
  (add these as session-level settings in retrieval queries — Step 3)
"""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

import structlog
from pgvector.sqlalchemy import Vector
from sqlalchemy import delete, select, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.config import Settings
from app.domain.document import DocumentChunk
from app.domain.vector import ChunkVector
from app.indexing.protocols import VectorIndex

if TYPE_CHECKING:
    pass

logger = structlog.get_logger(__name__)


class PgVectorIndex:
    """Store and search embedding vectors using pgvector.

    Index strategy:
    - Write: INSERT ... ON CONFLICT (chunk_id) DO UPDATE (upsert)
    - Read: ORDER BY embedding <=> $query_vector LIMIT $top_k
    - Filter: dc.meta @> $filter (JSONB containment, if filter_metadata provided)
    - Current mode: sequential scan (exact cosine distance)
    - HNSW index present on table; PostgreSQL will use it automatically at scale
    """

    def __init__(self, session: AsyncSession, settings: Settings) -> None:
        self._session = session
        self._settings = settings

    async def upsert(self, chunk: DocumentChunk, vector: list[float]) -> ChunkVector:
        """Insert or update the ChunkVector for a chunk (idempotent)."""
        # Check for existing vector
        existing = await self._session.scalar(
            select(ChunkVector).where(ChunkVector.chunk_id == chunk.id)
        )
        if existing is not None:
            existing.embedding = vector
            existing.model_name = self._settings.embedding_model
            existing.embedding_version = existing.embedding_version + 1
            await self._session.flush()
            logger.debug(
                "vector_index.upsert.updated",
                chunk_id=str(chunk.id),
                model=self._settings.embedding_model,
            )
            return existing

        chunk_vector = ChunkVector(
            id=uuid.uuid4(),
            chunk_id=chunk.id,
            embedding=vector,
            model_name=self._settings.embedding_model,
            embedding_version=1,
        )
        self._session.add(chunk_vector)
        await self._session.flush()
        logger.debug(
            "vector_index.upsert.inserted",
            chunk_id=str(chunk.id),
            model=self._settings.embedding_model,
        )
        return chunk_vector

    async def delete(self, chunk_id: str) -> None:
        """Remove the vector entry for a chunk."""
        await self._session.execute(
            delete(ChunkVector).where(
                ChunkVector.chunk_id == uuid.UUID(chunk_id)
            )
        )
        await self._session.flush()

    async def search(
        self,
        query_vector: list[float],
        top_k: int,
        filter_metadata: dict | None = None,
    ) -> list[tuple[ChunkVector, float]]:
        """Return top-k (ChunkVector, cosine_similarity) pairs.

        Implementation notes:
        - Uses pgvector <=> (cosine distance) operator.
        - cosine_similarity = 1 - cosine_distance.
        - Joins chunk_vectors → document_chunks for metadata filtering.
        - Eager-loads chunk.document via selectinload for citation assembly.
        - filter_metadata: JSONB @> containment on document_chunks.meta.
        - Current mode: sequential scan (exact cosine distance).
          HNSW index present; PostgreSQL will use it automatically at scale.
        """
        import json as _json

        # Serialize vector as a PostgreSQL vector literal: '[x,y,z]'
        vec_str = "[" + ",".join(str(float(x)) for x in query_vector) + "]"

        # Build distance expression as a text column label
        distance_col = text(
            f"(chunk_vectors.embedding <=> '{vec_str}'::vector) AS _distance"
        )
        score_col = text(
            f"(1.0 - (chunk_vectors.embedding <=> '{vec_str}'::vector)) AS _score"
        )
        order_expr = text(f"chunk_vectors.embedding <=> '{vec_str}'::vector")

        stmt = (
            select(ChunkVector, score_col)
            .join(DocumentChunk, DocumentChunk.id == ChunkVector.chunk_id)
            .options(
                selectinload(ChunkVector.chunk).selectinload(DocumentChunk.document)
            )
            .order_by(order_expr)
            .limit(top_k)
        )

        if filter_metadata:
            stmt = stmt.where(
                text("document_chunks.meta @> CAST(:filter AS jsonb)")
            ).params(filter=_json.dumps(filter_metadata))

        rows = (await self._session.execute(stmt)).all()
        results: list[tuple[ChunkVector, float]] = [
            (row[0], float(row[1])) for row in rows
        ]

        logger.debug(
            "vector_index.search",
            top_k=top_k,
            returned=len(results),
            filter=filter_metadata,
        )
        return results


# Protocol conformance
assert isinstance(PgVectorIndex.__new__(PgVectorIndex), VectorIndex)
