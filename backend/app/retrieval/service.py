"""Retriever default implementation: pgvector top-k with score threshold."""

from __future__ import annotations

import time

import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings
from app.indexing.embedder import build_embedder
from app.indexing.vector_index import PgVectorIndex
from app.retrieval.protocols import RetrievalResult, Retriever

logger = structlog.get_logger(__name__)


class VectorRetriever:
    """Retrieve top-k chunks using pgvector cosine similarity.

    Pipeline:
    1. Embed the query string via Embedder
    2. Call VectorIndex.search(query_vector, top_k * 2) for candidates
       (2× over-fetch to account for threshold filtering)
    3. Filter by score >= score_threshold
    4. Truncate to top_k and assign ranks

    The Retriever does NOT rerank. Reranking is handled by the Reranker
    protocol (Step 3). In Step 2 the output of this service is used directly.
    """

    def __init__(self, session: AsyncSession, settings: Settings) -> None:
        self._session = session
        self._settings = settings
        self._embedder = build_embedder(settings)
        self._vector_index = PgVectorIndex(session, settings)

    async def retrieve(
        self,
        query: str,
        top_k: int | None = None,
        filter_metadata: dict | None = None,
    ) -> list[RetrievalResult]:
        k = top_k or self._settings.retrieval_top_k
        threshold = self._settings.retrieval_score_threshold
        start = time.monotonic()

        # 1. Embed query
        query_vectors = await self._embedder.embed([query])
        query_vector = query_vectors[0]

        # 2. ANN search (fetch 2× to allow threshold filtering)
        raw = await self._vector_index.search(
            query_vector=query_vector,
            top_k=k * 2,
            filter_metadata=filter_metadata,
        )

        # 3. Filter by threshold
        filtered = [(cv, score) for cv, score in raw if score >= threshold]

        # 4. Truncate and build result objects
        results: list[RetrievalResult] = []
        for rank, (cv, score) in enumerate(filtered[:k]):
            results.append(
                RetrievalResult(
                    chunk=cv.chunk,
                    score=score,
                    rank=rank,
                )
            )

        elapsed_ms = int((time.monotonic() - start) * 1000)
        logger.info(
            "retriever.retrieve",
            query_preview=query[:80],
            top_k=k,
            threshold=threshold,
            candidates=len(raw),
            after_filter=len(filtered),
            returned=len(results),
            latency_ms=elapsed_ms,
        )
        return results


# Protocol conformance
assert isinstance(VectorRetriever.__new__(VectorRetriever), Retriever)
