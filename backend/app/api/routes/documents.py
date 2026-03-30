"""Document management API endpoints.

Routes:
    POST   /documents           — Upload and ingest a document
    GET    /documents           — List documents (paginated)
    GET    /documents/{id}      — Get document detail
    DELETE /documents/{id}      — Soft-delete a document
    POST   /documents/{id}/index — Trigger (re-)indexing
"""

import uuid

from fastapi import APIRouter, HTTPException, status

from app.schemas.common import APIResponse, PaginatedResponse
from app.schemas.document import (
    DocumentIndexRequest,
    DocumentIndexResponse,
    DocumentResponse,
)

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post(
    "",
    response_model=APIResponse[DocumentResponse],
    status_code=status.HTTP_202_ACCEPTED,
    summary="Upload and ingest a document",
)
async def upload_document() -> APIResponse[DocumentResponse]:
    """Accept a multipart/form-data upload.

    Step 1: Returns 501 NOT IMPLEMENTED — full implementation in Step 2.
    """
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Document ingestion pipeline not yet implemented (Step 2).",
    )


@router.get(
    "",
    response_model=PaginatedResponse[DocumentResponse],
    summary="List documents",
)
async def list_documents(
    page: int = 1,
    page_size: int = 20,
) -> PaginatedResponse[DocumentResponse]:
    """Return paginated list of documents.

    Step 1: Returns 501 NOT IMPLEMENTED — full implementation in Step 2.
    """
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Document listing not yet implemented (Step 2).",
    )


@router.get(
    "/{document_id}",
    response_model=APIResponse[DocumentResponse],
    summary="Get document detail",
)
async def get_document(document_id: uuid.UUID) -> APIResponse[DocumentResponse]:
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Not yet implemented (Step 2).",
    )


@router.delete(
    "/{document_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Soft-delete a document",
)
async def delete_document(document_id: uuid.UUID) -> None:
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Not yet implemented (Step 2).",
    )


@router.post(
    "/{document_id}/index",
    response_model=APIResponse[DocumentIndexResponse],
    summary="Trigger (re-)indexing of a document",
)
async def index_document(
    document_id: uuid.UUID,
    body: DocumentIndexRequest,
) -> APIResponse[DocumentIndexResponse]:
    """Enqueue embedding + vector indexing for a document.

    Step 1: Returns 501 NOT IMPLEMENTED — full implementation in Step 3.
    """
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Indexing pipeline not yet implemented (Step 3).",
    )
