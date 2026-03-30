"""Protocol interfaces for retrieval and reranking."""

from typing import Protocol, runtime_checkable

from app.domain.document import DocumentChunk


class RetrievalResult:
    """Value object returned by Retriever and Reranker."""

    def __init__(
        self,
        chunk: DocumentChunk,
        score: float,
        rank: int,
    ) -> None:
        self.chunk = chunk
        self.score = score
        self.rank = rank

    def __repr__(self) -> str:
        return (
            f"RetrievalResult(chunk_id={self.chunk.id!r}, "
            f"score={self.score:.4f}, rank={self.rank})"
        )


@runtime_checkable
class Retriever(Protocol):
    """Retrieve top-k relevant chunks for a query.

    Layering:
    1. Retriever calls VectorIndex.search() for ANN candidates
    2. (Optionally) passes results to Reranker for cross-encoder scoring
    3. Returns final ranked list to AgentPolicy

    Retriever is responsible for:
    - Embedding the query via Embedder
    - Calling VectorIndex.search()
    - Applying score threshold filtering
    - NOT responsible for reranking (see Reranker)
    """

    async def retrieve(
        self,
        query: str,
        top_k: int | None = None,
        filter_metadata: dict | None = None,
    ) -> list[RetrievalResult]:
        ...


@runtime_checkable
class Reranker(Protocol):
    """Re-score and re-rank retrieval results.

    Typically uses a cross-encoder model or BM25 hybrid scoring.
    Receives the ANN results from Retriever and returns a re-ranked list.

    IMPORTANT: Reranker must NOT reduce the list below min_keep items
    unless the score threshold demands it. This prevents over-filtering.
    """

    async def rerank(
        self,
        query: str,
        results: list[RetrievalResult],
        top_k: int | None = None,
    ) -> list[RetrievalResult]:
        ...
