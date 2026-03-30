"""RAGService: orchestrates Retriever → CitationAssembler → AnswerGenerator.

This is the main entry point for the POST /chat/query endpoint.
In Step 2 this replaces the full AgentPolicy loop with a single-pass
retrieval + generation pipeline. The AgentPolicy FSM is introduced in Step 4.
"""

from __future__ import annotations

import time
import uuid

import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings
from app.retrieval.service import VectorRetriever
from app.schemas.chat import Citation, ChatQueryResponse
from app.services.answer_generator import build_answer_generator
from app.services.citation_assembler import DefaultCitationAssembler

logger = structlog.get_logger(__name__)


class RAGService:
    """Single-pass RAG pipeline (no agent loop).

    Sequence:
    1. Retrieve top-k chunks (VectorRetriever)
    2. Assemble citations (DefaultCitationAssembler)
    3. Generate answer (EchoStubAnswerGenerator in dev)
    4. Return ChatQueryResponse

    Abstain contract:
    - If retrieved chunks < settings.min_evidence_chunks, generator abstains.
    - Response always contains citations (empty list when abstained).
    """

    def __init__(self, session: AsyncSession, settings: Settings) -> None:
        self._session = session
        self._settings = settings
        self._retriever = VectorRetriever(session, settings)
        self._assembler = DefaultCitationAssembler()
        self._generator = build_answer_generator(settings)

    async def query(
        self,
        query: str,
        session_id: uuid.UUID | None = None,
        request_id: str | None = None,
        meta: dict | None = None,
    ) -> ChatQueryResponse:
        log = logger.bind(
            request_id=request_id,
            session_id=str(session_id) if session_id else None,
            query_preview=query[:80],
        )
        start_ms = int(time.monotonic() * 1000)

        # 1. Retrieve
        results = await self._retriever.retrieve(query=query)

        # 2. Assemble citations
        citations: list[Citation] = await self._assembler.assemble(results)

        # 3. Generate answer
        answer, abstained = await self._generator.generate(
            query=query,
            context_chunks=results,
        )

        latency_ms = int(time.monotonic() * 1000) - start_ms
        message_id = uuid.uuid4()
        effective_session_id = session_id or uuid.uuid4()

        log.info(
            "rag_service.query.done",
            abstained=abstained,
            num_citations=len(citations),
            latency_ms=latency_ms,
        )

        return ChatQueryResponse(
            session_id=effective_session_id,
            message_id=message_id,
            answer=answer,
            abstained=abstained,
            citations=citations,
            agent_trace_id=None,
            latency_ms=latency_ms,
        )
