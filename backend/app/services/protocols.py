"""Protocol interfaces for cross-module services."""

from typing import Protocol, runtime_checkable

from app.retrieval.protocols import RetrievalResult
from app.schemas.chat import Citation


@runtime_checkable
class CitationAssembler(Protocol):
    """Assemble citation objects from retrieval results.

    Responsibilities:
    - Map RetrievalResult → Citation (enriching with document metadata)
    - Deduplicate citations pointing to the same source page
    - Sort by descending score
    - NOT responsible for filtering — caller decides which results to pass in

    Assumption: All chunks' parent documents are already loaded (eager load
    or explicit query). If not loaded, the assembler will issue a lazy query.
    """

    async def assemble(
        self, results: list[RetrievalResult]
    ) -> list[Citation]:
        ...


@runtime_checkable
class AnswerGenerator(Protocol):
    """Generate a grounded answer from a query and retrieval context.

    Constraints:
    - Must only use information present in context_chunks
    - Must return abstained=True when context is insufficient
    - Must respect LLM timeout (Settings.llm_timeout_seconds)
    - Must log token usage and latency via structlog
    - Prompt engineering is an implementation detail — this interface is stable

    NOT responsible for retrieval — caller must provide context_chunks.
    """

    async def generate(
        self,
        query: str,
        context_chunks: list[RetrievalResult],
    ) -> tuple[str, bool]:
        """Return (answer_text, abstained).

        abstained=True means the generator found insufficient evidence.
        """
        ...
