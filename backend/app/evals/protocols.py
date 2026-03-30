"""Protocol interfaces for the evaluation framework."""

from dataclasses import dataclass, field
from typing import Protocol, runtime_checkable

from app.domain.eval import EvalCase, EvalRun


@dataclass
class EvalMetrics:
    """Aggregate metrics for an EvalRun."""

    faithfulness: float | None = None
    answer_relevance: float | None = None
    retrieval_precision: float | None = None
    retrieval_recall: float | None = None
    abstain_rate: float | None = None
    pass_rate: float | None = None
    avg_latency_ms: float | None = None
    extra: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "faithfulness": self.faithfulness,
            "answer_relevance": self.answer_relevance,
            "retrieval_precision": self.retrieval_precision,
            "retrieval_recall": self.retrieval_recall,
            "abstain_rate": self.abstain_rate,
            "pass_rate": self.pass_rate,
            "avg_latency_ms": self.avg_latency_ms,
            **self.extra,
        }


@runtime_checkable
class EvaluationRunner(Protocol):
    """Run evaluation cases and compute aggregate metrics.

    Constraints:
    - Must persist EvalRun and EvalResult records to the database
    - Must handle individual case failures gracefully (mark as failed, continue)
    - Must compute EvalMetrics after all cases complete
    - Must update EvalRun.status to 'completed' or 'failed' when done
    - Must log per-case results via structlog
    """

    async def run(
        self,
        eval_run: EvalRun,
        cases: list[EvalCase],
    ) -> EvalMetrics:
        ...
