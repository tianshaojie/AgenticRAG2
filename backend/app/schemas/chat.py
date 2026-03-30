"""Pydantic schemas for chat API endpoints."""

import uuid
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.common import TimestampedSchema


class Citation(BaseModel):
    chunk_id: uuid.UUID
    document_id: uuid.UUID
    document_title: str | None
    chunk_index: int
    page_number: int | None
    section_title: str | None
    content_snippet: str
    score: float


class ChatQueryRequest(BaseModel):
    session_id: uuid.UUID | None = None
    query: str = Field(..., min_length=1, max_length=4096)
    meta: dict[str, Any] = Field(default_factory=dict)


class ChatQueryResponse(BaseModel):
    session_id: uuid.UUID
    message_id: uuid.UUID
    answer: str
    abstained: bool
    citations: list[Citation]
    agent_trace_id: uuid.UUID | None
    latency_ms: int


class AgentTraceStepResponse(BaseModel):
    step_index: int
    state_from: str
    state_to: str
    action: str
    input_data: dict[str, Any]
    output_data: dict[str, Any]
    latency_ms: int | None
    retrieval_score: float | None


class AgentTraceResponse(TimestampedSchema):
    session_id: uuid.UUID | None
    query: str
    final_state: str
    total_steps: int
    abstained: bool
    latency_ms: int | None
    steps: list[AgentTraceStepResponse]
