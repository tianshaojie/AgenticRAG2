"""ORM models: agent_traces and agent_trace_steps."""

import uuid

from sqlalchemy import Boolean, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class AgentTrace(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Top-level record of a single agent reasoning cycle.

    One ChatMessage (assistant turn) corresponds to one AgentTrace.
    The trace captures the full finite-state execution path.

    States: IDLE → RETRIEVING → EVALUATING_EVIDENCE → GENERATING → DONE
                                                     ↘ ABSTAINING
    """

    __tablename__ = "agent_traces"

    session_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("chat_sessions.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    query: Mapped[str] = mapped_column(Text, nullable=False)
    # final state: DONE | ABSTAINING | ERROR
    final_state: Mapped[str] = mapped_column(String(32), nullable=False, default="IDLE")
    total_steps: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    abstained: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    # total latency in milliseconds
    latency_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    # request-scoped identifiers for distributed tracing
    request_id: Mapped[str | None] = mapped_column(String(128), nullable=True, index=True)
    trace_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    meta: Mapped[dict] = mapped_column(JSONB, nullable=False, server_default="{}")

    steps: Mapped[list["AgentTraceStep"]] = relationship(
        "AgentTraceStep",
        back_populates="trace",
        cascade="all, delete-orphan",
        order_by="AgentTraceStep.step_index",
    )


class AgentTraceStep(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """One step in an AgentTrace finite-state execution.

    Each step records the state transition, input context, and output.
    """

    __tablename__ = "agent_trace_steps"

    trace_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("agent_traces.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    step_index: Mapped[int] = mapped_column(Integer, nullable=False)
    # state before and after this step
    state_from: Mapped[str] = mapped_column(String(64), nullable=False)
    state_to: Mapped[str] = mapped_column(String(64), nullable=False)
    # action taken (e.g. retrieve, rerank, generate, abstain)
    action: Mapped[str] = mapped_column(String(64), nullable=False)
    # structured input/output for this step (chunks, scores, prompt snippets)
    input_data: Mapped[dict] = mapped_column(JSONB, nullable=False, server_default="{}")
    output_data: Mapped[dict] = mapped_column(JSONB, nullable=False, server_default="{}")
    latency_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    # retrieval score (if this step is a RETRIEVING step)
    retrieval_score: Mapped[float | None] = mapped_column(Numeric(6, 4), nullable=True)

    trace: Mapped["AgentTrace"] = relationship("AgentTrace", back_populates="steps")
