"""Chat API endpoints.

Routes:
    POST   /chat/query          — Submit a query to the RAG pipeline (Step 2: single-pass)
    GET    /chat/sessions       — List chat sessions (Step 4)
    GET    /chat/{session_id}   — Get session detail (Step 4)
    GET    /chat/{session_id}/trace — Agent trace for session (Step 4)
    GET    /traces/{trace_id}   — Full agent trace detail (Step 4)
"""

from __future__ import annotations

import uuid

import structlog
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings, get_settings
from app.core.dependencies import get_db
from app.schemas.chat import AgentTraceResponse, ChatQueryRequest, ChatQueryResponse
from app.schemas.common import APIResponse
from app.services.rag_service import RAGService

logger = structlog.get_logger(__name__)
router = APIRouter(prefix="/chat", tags=["chat"])
traces_router = APIRouter(prefix="/traces", tags=["traces"])


@router.post(
    "/query",
    response_model=APIResponse[ChatQueryResponse],
    summary="Submit a query to the RAG pipeline",
)
async def query(
    body: ChatQueryRequest,
    db: AsyncSession = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> APIResponse[ChatQueryResponse]:
    """Single-pass RAG: retrieve → cite → generate.

    Step 2: Uses EchoStubAnswerGenerator (no LLM call).
    Full AgentPolicy loop is implemented in Step 4.

    Abstain contract: if insufficient evidence, returns abstained=True
    and citations=[].
    """
    svc = RAGService(session=db, settings=settings)
    result = await svc.query(
        query=body.query,
        session_id=body.session_id,
    )
    return APIResponse(success=True, data=result)


@router.get("/sessions", summary="List chat sessions (Step 4)")
async def list_sessions(page: int = 1, page_size: int = 20):
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Session management not yet implemented (Step 4).",
    )


@router.get("/{session_id}", summary="Get session with messages (Step 4)")
async def get_session(session_id: uuid.UUID):
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Not yet implemented (Step 4).",
    )


@router.get(
    "/{session_id}/trace",
    response_model=APIResponse[AgentTraceResponse],
    summary="Agent trace for session (Step 4)",
)
async def get_session_trace(session_id: uuid.UUID) -> APIResponse[AgentTraceResponse]:
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Not yet implemented (Step 4).",
    )


@traces_router.get(
    "/{trace_id}",
    response_model=APIResponse[AgentTraceResponse],
    summary="Full agent trace detail (Step 4)",
)
async def get_trace(trace_id: uuid.UUID) -> APIResponse[AgentTraceResponse]:
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Not yet implemented (Step 4).",
    )
