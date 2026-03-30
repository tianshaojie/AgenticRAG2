"""Protocol interfaces for embedding and vector indexing."""

from typing import Protocol, runtime_checkable

from app.domain.document import DocumentChunk
from app.domain.vector import ChunkVector


@runtime_checkable
class Embedder(Protocol):
    """Convert text into a dense embedding vector.

    Constraints:
    - Must respect timeout (configured via Settings.embedding_timeout_seconds)
    - Must retry on transient errors (max 3 attempts with exponential backoff)
    - Must log model name and latency via structlog
    - Must NOT store vectors — storage is VectorIndex's responsibility
    """

    async def embed(self, texts: list[str]) -> list[list[float]]:
        ...

    @property
    def model_name(self) -> str:
        ...

    @property
    def dimension(self) -> int:
        ...


@runtime_checkable
class VectorIndex(Protocol):
    """Write and retrieve embedding vectors.

    Default implementation: pgvector with HNSW index.
    Distance metric: cosine similarity (<=> operator).

    This protocol intentionally separates vector storage concerns from
    retrieval ranking concerns (Retriever handles the latter).
    """

    async def upsert(self, chunk: DocumentChunk, vector: list[float]) -> ChunkVector:
        """Insert or update the vector for a chunk."""
        ...

    async def delete(self, chunk_id: str) -> None:
        """Remove the vector entry for a chunk."""
        ...

    async def search(
        self,
        query_vector: list[float],
        top_k: int,
        filter_metadata: dict | None = None,
    ) -> list[tuple[ChunkVector, float]]:
        """Return top-k (ChunkVector, similarity_score) pairs.

        filter_metadata: optional key-value filter applied to chunk.meta
        (implemented via JSONB containment @> in PostgreSQL).
        """
        ...
