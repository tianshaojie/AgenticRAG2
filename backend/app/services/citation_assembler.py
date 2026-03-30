"""CitationAssembler default implementation."""

from __future__ import annotations

import structlog

from app.retrieval.protocols import RetrievalResult
from app.schemas.chat import Citation
from app.services.protocols import CitationAssembler

logger = structlog.get_logger(__name__)


class DefaultCitationAssembler:
    """Map RetrievalResult list → Citation list.

    Rules:
    - One Citation per RetrievalResult (no deduplication in Step 2;
      deduplication by page/source is deferred to Step 3).
    - Content snippet is the first 200 chars of the chunk text.
    - Sorted by descending score (already sorted by Retriever, preserved).
    - document.id and document.title are eagerly loaded via selectinload
      in PgVectorIndex.search(); no extra queries are issued here.
    """

    async def assemble(self, results: list[RetrievalResult]) -> list[Citation]:
        citations: list[Citation] = []
        for result in results:
            chunk = result.chunk
            doc = chunk.document  # eager-loaded
            citations.append(
                Citation(
                    chunk_id=chunk.id,
                    document_id=doc.id if doc else chunk.document_id,
                    document_title=doc.title if doc else None,
                    chunk_index=chunk.chunk_index,
                    page_number=chunk.page_number,
                    section_title=chunk.section_title,
                    content_snippet=chunk.content[:200],
                    score=round(result.score, 4),
                )
            )
        logger.debug(
            "citation_assembler.assembled",
            num_citations=len(citations),
        )
        return citations


# Protocol conformance
assert isinstance(DefaultCitationAssembler.__new__(DefaultCitationAssembler), CitationAssembler)
