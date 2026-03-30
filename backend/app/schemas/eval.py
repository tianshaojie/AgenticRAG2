"""Pydantic schemas for eval API endpoints."""

import uuid
from typing import Any

from pydantic import BaseModel, Field

from app.schemas.common import TimestampedSchema


class EvalCaseInput(BaseModel):
    name: str | None = None
    question: str = Field(..., min_length=1)
    reference_answer: str | None = None
    expected_chunk_ids: list[uuid.UUID] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    meta: dict[str, Any] = Field(default_factory=dict)


class EvalRunRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=256)
    description: str | None = None
    case_ids: list[uuid.UUID] | None = None
    # if None, run all available cases
    meta: dict[str, Any] = Field(default_factory=dict)


class EvalResultResponse(BaseModel):
    case_id: uuid.UUID
    generated_answer: str | None
    retrieved_chunk_ids: list[uuid.UUID]
    faithfulness_score: float | None
    answer_relevance_score: float | None
    retrieval_precision: float | None
    retrieval_recall: float | None
    passed: bool
    abstained: bool
    latency_ms: int | None
    error_message: str | None


class EvalRunResponse(TimestampedSchema):
    name: str
    description: str | None
    status: str
    metrics: dict[str, Any]
    total_cases: int
    passed_cases: int
    results: list[EvalResultResponse] = Field(default_factory=list)
