"""Document management API endpoints.

Routes:
    POST   /documents              — Upload and ingest a document (txt/md)
    GET    /documents              — List documents (paginated)
    GET    /documents/{id}         — Get document detail
    DELETE /documents/{id}         — Soft-delete a document
    POST   /documents/{id}/index   — Trigger (re-)indexing
"""

from __future__ import annotations

import uuid
from math import ceil
from typing import Annotated

import structlog
from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status
from fastapi.params import Depends
from fastapi.responses import Response
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings, get_settings
from app.core.dependencies import get_db
from app.domain.document import Document
from app.indexing.pipeline import IndexingPipeline
from app.ingestion.service import TextDocumentIngestor
from app.schemas.common import APIResponse, PaginatedResponse
from app.schemas.document import (
    DocumentIndexRequest,
    DocumentIndexResponse,
    DocumentResponse,
)

logger = structlog.get_logger(__name__)
router = APIRouter(prefix="/documents", tags=["documents"])


def _to_response(doc: Document) -> DocumentResponse:
    # Strip raw_text from meta before returning (can be large)
    safe_meta = {k: v for k, v in doc.meta.items() if k != "raw_text"}
    return DocumentResponse(
        id=doc.id,
        created_at=doc.created_at,
        updated_at=doc.updated_at,
        filename=doc.filename,
        content_type=doc.content_type,
        content_hash=doc.content_hash,
        size_bytes=doc.size_bytes,
        title=doc.title,
        status=doc.status,
        meta=safe_meta,
        is_deleted=doc.is_deleted,
    )


@router.post(
    "",
    response_model=APIResponse[DocumentResponse],
    status_code=status.HTTP_202_ACCEPTED,
    summary="Upload and ingest a document (txt / markdown)",
)
async def upload_document(
    file: Annotated[UploadFile, File(description="txt or markdown file")],
    title: Annotated[str | None, Form()] = None,
    db: AsyncSession = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> APIResponse[DocumentResponse]:
    """Accept multipart/form-data upload. Returns the created Document.

    The raw text is stored in document.meta['raw_text'] for the indexing
    pipeline. Call POST /documents/{id}/index to trigger embedding.
    """
    raw = await file.read()
    content_type = file.content_type or "text/plain"

    # Pre-decode to validate encoding before storing
    try:
        raw.decode("utf-8")
    except UnicodeDecodeError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="File must be UTF-8 or latin-1 encoded text.",
        )

    # Store raw_text in meta for indexing pipeline (Step 2 storage strategy)
    meta: dict = {"raw_text": raw.decode("utf-8", errors="replace")}
    if title:
        meta["title"] = title

    ingestor = TextDocumentIngestor(session=db, settings=settings)
    try:
        doc = await ingestor.ingest(
            filename=file.filename or "upload.txt",
            content_type=content_type,
            raw_bytes=raw,
            meta=meta,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        )

    logger.info("api.documents.upload", document_id=str(doc.id))
    return APIResponse(success=True, data=_to_response(doc))


@router.get(
    "",
    response_model=PaginatedResponse[DocumentResponse],
    summary="List documents (paginated)",
)
async def list_documents(
    page: int = 1,
    page_size: int = 20,
    db: AsyncSession = Depends(get_db),
) -> PaginatedResponse[DocumentResponse]:
    if page < 1:
        page = 1
    if page_size < 1 or page_size > 100:
        page_size = 20

    total_scalar = await db.scalar(
        select(func.count(Document.id)).where(Document.is_deleted.is_(False))
    )
    total = total_scalar or 0

    docs = (
        await db.scalars(
            select(Document)
            .where(Document.is_deleted.is_(False))
            .order_by(Document.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
    ).all()

    return PaginatedResponse(
        items=[_to_response(d) for d in docs],
        total=total,
        page=page,
        page_size=page_size,
        has_next=(page * page_size) < total,
    )


@router.get(
    "/{document_id}",
    response_model=APIResponse[DocumentResponse],
    summary="Get document detail",
)
async def get_document(
    document_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> APIResponse[DocumentResponse]:
    doc = await db.scalar(
        select(Document).where(
            Document.id == document_id,
            Document.is_deleted.is_(False),
        )
    )
    if doc is None:
        raise HTTPException(status_code=404, detail="Document not found.")
    return APIResponse(success=True, data=_to_response(doc))


@router.delete(
    "/{document_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
    summary="Soft-delete a document",
)
async def delete_document(
    document_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> Response:
    doc = await db.scalar(
        select(Document).where(
            Document.id == document_id,
            Document.is_deleted.is_(False),
        )
    )
    if doc is None:
        raise HTTPException(status_code=404, detail="Document not found.")
    doc.is_deleted = True
    await db.flush()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post(
    "/{document_id}/index",
    response_model=APIResponse[DocumentIndexResponse],
    summary="Trigger (re-)indexing of a document",
)
async def index_document(
    document_id: uuid.UUID,
    body: DocumentIndexRequest,
    db: AsyncSession = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> APIResponse[DocumentIndexResponse]:
    """Trigger chunking + embedding + pgvector indexing for a document."""
    doc = await db.scalar(
        select(Document).where(
            Document.id == document_id,
            Document.is_deleted.is_(False),
        )
    )
    if doc is None:
        raise HTTPException(status_code=404, detail="Document not found.")

    pipeline = IndexingPipeline(session=db, settings=settings)
    try:
        doc = await pipeline.run(doc, force_reindex=body.force_reindex)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        )

    return APIResponse(
        success=True,
        data=DocumentIndexResponse(
            document_id=doc.id,
            status=doc.status,
            message=f"Document indexed successfully ({doc.status}).",
        ),
    )
