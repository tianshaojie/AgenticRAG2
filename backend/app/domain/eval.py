"""ORM models: eval_runs, eval_cases, eval_results."""

import uuid

from sqlalchemy import Boolean, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class EvalRun(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """A single evaluation run over a set of EvalCases."""

    __tablename__ = "eval_runs"

    name: Mapped[str] = mapped_column(String(256), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    # status: pending | running | completed | failed
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="pending", index=True)
    # aggregate metrics stored as JSON (precision, recall, faithfulness, …)
    metrics: Mapped[dict] = mapped_column(JSONB, nullable=False, server_default="{}")
    total_cases: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    passed_cases: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    meta: Mapped[dict] = mapped_column(JSONB, nullable=False, server_default="{}")

    results: Mapped[list["EvalResult"]] = relationship(
        "EvalResult", back_populates="run", cascade="all, delete-orphan"
    )


class EvalCase(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """A single question-answer pair used for evaluation.

    Cases are independent of runs and can be reused across multiple runs.
    """

    __tablename__ = "eval_cases"

    name: Mapped[str | None] = mapped_column(String(256), nullable=True)
    question: Mapped[str] = mapped_column(Text, nullable=False)
    reference_answer: Mapped[str | None] = mapped_column(Text, nullable=True)
    # expected citation chunk IDs (for retrieval recall evaluation)
    expected_chunk_ids: Mapped[list] = mapped_column(
        JSONB, nullable=False, server_default="[]"
    )
    tags: Mapped[list] = mapped_column(JSONB, nullable=False, server_default="[]")
    meta: Mapped[dict] = mapped_column(JSONB, nullable=False, server_default="{}")

    results: Mapped[list["EvalResult"]] = relationship(
        "EvalResult", back_populates="case"
    )


class EvalResult(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """The outcome of running one EvalCase in one EvalRun."""

    __tablename__ = "eval_results"

    run_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("eval_runs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    case_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("eval_cases.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    # generated answer for this run/case
    generated_answer: Mapped[str | None] = mapped_column(Text, nullable=True)
    # retrieved chunk IDs (for recall computation)
    retrieved_chunk_ids: Mapped[list] = mapped_column(
        JSONB, nullable=False, server_default="[]"
    )
    # per-case scores
    faithfulness_score: Mapped[float | None] = mapped_column(Numeric(5, 4), nullable=True)
    answer_relevance_score: Mapped[float | None] = mapped_column(Numeric(5, 4), nullable=True)
    retrieval_precision: Mapped[float | None] = mapped_column(Numeric(5, 4), nullable=True)
    retrieval_recall: Mapped[float | None] = mapped_column(Numeric(5, 4), nullable=True)
    passed: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    abstained: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    latency_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    meta: Mapped[dict] = mapped_column(JSONB, nullable=False, server_default="{}")

    run: Mapped["EvalRun"] = relationship("EvalRun", back_populates="results")
    case: Mapped["EvalCase"] = relationship("EvalCase", back_populates="results")
