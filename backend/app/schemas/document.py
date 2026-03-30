"""Pydantic schemas for document API endpoints."""

import uuid
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.common import TimestampedSchema


class DocumentCreate(BaseModel):
    """Request body when uploading a new document (multipart handled in router)."""

    title: str | None = Field(None, max_length=1024)
    meta: dict[str, Any] = Field(default_factory=dict)


class DocumentResponse(TimestampedSchema):
    filename: str
    content_type: str
    content_hash: str
    size_bytes: int
    title: str | None
    status: str
    meta: dict[str, Any]
    is_deleted: bool


class DocumentIndexRequest(BaseModel):
    """Trigger (re-)indexing of a document."""

    force_reindex: bool = False


class DocumentIndexResponse(BaseModel):
    document_id: uuid.UUID
    status: str
    message: str


class DocumentChunkResponse(TimestampedSchema):
    document_id: uuid.UUID
    chunk_index: int
    content: str
    token_count: int | None
    page_number: int | None
    section_title: str | None
    meta: dict[str, Any]
