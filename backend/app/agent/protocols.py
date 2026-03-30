"""Protocol interfaces for the Agent finite-state machine."""

from enum import Enum
from typing import Protocol, runtime_checkable
from dataclasses import dataclass, field

from app.retrieval.protocols import RetrievalResult
from app.schemas.chat import Citation


class AgentState(str, Enum):
    """Finite states for the Agent state machine.

    Transitions:
        IDLE → RETRIEVING → EVALUATING_EVIDENCE → GENERATING → DONE
                                                ↘ ABSTAINING
    Any state → ERROR (on unhandled exception)
    """

    IDLE = "IDLE"
    RETRIEVING = "RETRIEVING"
    EVALUATING_EVIDENCE = "EVALUATING_EVIDENCE"
    GENERATING = "GENERATING"
    DONE = "DONE"
    ABSTAINING = "ABSTAINING"
    ERROR = "ERROR"


@dataclass
class AgentContext:
    """Mutable context passed between agent steps.

    All state transitions read/write this object.
    Immutable after DONE or ABSTAINING.
    """

    query: str
    session_id: str | None = None
    request_id: str | None = None
    current_state: AgentState = AgentState.IDLE
    step_count: int = 0
    retrieval_results: list[RetrievalResult] = field(default_factory=list)
    citations: list[Citation] = field(default_factory=list)
    answer: str = ""
    abstained: bool = False
    trace_steps: list[dict] = field(default_factory=list)
    meta: dict = field(default_factory=dict)


@runtime_checkable
class AgentPolicy(Protocol):
    """Execute the finite-state agent loop for one query.

    Hard constraints (MUST be enforced by all implementations):
    - Maximum steps: Settings.max_agent_steps (default 5)
    - On step limit exceeded: set abstained=True and return
    - All steps must be recorded in AgentContext.trace_steps
    - Must never call LLM without at least one retrieval result

    This protocol is intentionally narrow: callers only see run().
    All internal state transitions are implementation details.
    """

    async def run(self, context: AgentContext) -> AgentContext:
        """Execute the agent loop and return the final context."""
        ...
