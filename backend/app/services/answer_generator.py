"""AnswerGenerator implementations.

EchoStubAnswerGenerator — dev/test stub:
  - Concatenates retrieved chunk content as the "answer".
  - Returns abstained=True if no chunks provided.
  - No LLM calls; safe for CI.

OpenAIAnswerGenerator — real LLM (Step 4 full implementation):
  - Minimal skeleton kept here to ensure the protocol is satisfied.
  - Raises NotImplementedError until Step 4.
"""

from __future__ import annotations

import time

import structlog

from app.core.config import Settings
from app.retrieval.protocols import RetrievalResult
from app.services.protocols import AnswerGenerator

logger = structlog.get_logger(__name__)

_ABSTAIN_RESPONSE = (
    "I cannot find sufficient evidence in the available documents "
    "to answer this question."
)


class EchoStubAnswerGenerator:
    """Stub generator: echoes retrieved context as the answer.

    Abstain logic:
    - If len(context_chunks) < settings.min_evidence_chunks → abstain.
    - If context_chunks is empty → abstain.

    This generator is deterministic and suitable for testing the full
    RAG pipeline end-to-end without an LLM API key.
    """

    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    async def generate(
        self,
        query: str,
        context_chunks: list[RetrievalResult],
    ) -> tuple[str, bool]:
        start = time.monotonic()

        if len(context_chunks) < self._settings.min_evidence_chunks:
            elapsed_ms = int((time.monotonic() - start) * 1000)
            logger.info(
                "answer_generator.abstain",
                query_preview=query[:80],
                evidence_count=len(context_chunks),
                min_required=self._settings.min_evidence_chunks,
                latency_ms=elapsed_ms,
            )
            return _ABSTAIN_RESPONSE, True

        # Assemble answer from retrieved chunks
        parts: list[str] = []
        for r in context_chunks:
            parts.append(
                f"[chunk {r.chunk.chunk_index}, score={r.score:.3f}]\n"
                f"{r.chunk.content}"
            )
        answer = (
            f"Based on the retrieved documents:\n\n"
            + "\n\n---\n\n".join(parts)
        )

        elapsed_ms = int((time.monotonic() - start) * 1000)
        logger.info(
            "answer_generator.generated",
            query_preview=query[:80],
            evidence_count=len(context_chunks),
            answer_len=len(answer),
            latency_ms=elapsed_ms,
        )
        return answer, False


class OpenAIAnswerGenerator:
    """OpenAI Chat Completions answer generator — full implementation in Step 4.

    In Step 2 this class satisfies the protocol but raises NotImplementedError
    when called, ensuring the interface contract is verifiable now.
    """

    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    async def generate(
        self,
        query: str,
        context_chunks: list[RetrievalResult],
    ) -> tuple[str, bool]:
        raise NotImplementedError(
            "OpenAIAnswerGenerator is not yet implemented. "
            "Set ANSWER_PROVIDER=echo_stub or wait for Step 4."
        )


def build_answer_generator(settings: Settings) -> AnswerGenerator:
    """Factory: return correct AnswerGenerator based on settings."""
    if settings.answer_provider == "openai":
        return OpenAIAnswerGenerator(settings)
    return EchoStubAnswerGenerator(settings)


# Protocol conformance
assert isinstance(EchoStubAnswerGenerator.__new__(EchoStubAnswerGenerator), AnswerGenerator)
assert isinstance(OpenAIAnswerGenerator.__new__(OpenAIAnswerGenerator), AnswerGenerator)
