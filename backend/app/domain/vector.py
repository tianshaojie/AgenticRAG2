"""ORM model: chunk_vectors — pgvector embedding storage."""

import uuid
from typing import TYPE_CHECKING

from pgvector.sqlalchemy import Vector
from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.config import get_settings
from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.domain.document import DocumentChunk

_settings = get_settings()


class ChunkVector(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Stores the embedding vector for a DocumentChunk.

    Design decisions:
    - Separated from document_chunks to allow the main table to remain lean and
      indexable without carrying large vector blobs.
    - Distance metric: cosine similarity (<=> operator in pgvector).
    - Index type: HNSW (m=16, ef_construction=64) for sub-linear ANN retrieval.
    - Dimension is configured via Settings.vector_dimension (default 1536).
    - model_name records which embedding model produced the vector, enabling
      future re-indexing without a full data migration.
    """

    __tablename__ = "chunk_vectors"

    chunk_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("document_chunks.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    # Embedding vector — dimension set at runtime via settings
    # DDL for the actual column + HNSW index is in the Alembic migration
    embedding: Mapped[list[float]] = mapped_column(
        Vector(_settings.vector_dimension), nullable=False
    )
    model_name: Mapped[str] = mapped_column(String(128), nullable=False)
    model_version: Mapped[str | None] = mapped_column(String(64), nullable=True)
    # embedding generation ordinality (useful for detecting stale vectors)
    embedding_version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    chunk: Mapped["DocumentChunk"] = relationship(
        "DocumentChunk", back_populates="vector"
    )
