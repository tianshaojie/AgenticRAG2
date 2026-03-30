"""Chat and agent trace API endpoints.

Routes:
    POST   /chat/query          — Submit a query to the RAG agent
    GET    /chat/sessions       — List chat sessions
    GET    /chat/{session_id}   — Get session detail with messages
    GET    /chat/{session_id}/trace — Get agent trace for latest turn
    GET    /traces/{trace_id}   — Get full agent trace detail
"""

import uuid

from fastapi import APIRouter, HTTPException, status

from app.schemas.chat import AgentTraceResponse, ChatQueryRequest, ChatQueryResponse
from app.schemas.common import APIResponse

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post(
    "/query",
    response_model=APIResponse[ChatQueryResponse],
    summary="Submit a query to the RAG agent",
)
async def query(body: ChatQueryRequest) -> APIResponse[ChatQueryResponse]:
    """Execute a full RAG agent cycle for the given query.

    Step 1: Returns 501 NOT IMPLEMENTED — full implementation in Step 4.
    """
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Agent pipeline not yet implemented (Step 4).",
    )


@router.get(
    "/sessions",
    summary="List chat sessions",
)
async def list_sessions(page: int = 1, page_size: int = 20):
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Not yet implemented (Step 4).",
    )


@router.get(
    "/{session_id}",
    summary="Get session with messages",
)
async def get_session(session_id: uuid.UUID):
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Not yet implemented (Step 4).",
    )


@router.get(
    "/{session_id}/trace",
    response_model=APIResponse[AgentTraceResponse],
    summary="Get agent trace for the latest turn in a session",
)
async def get_session_trace(session_id: uuid.UUID) -> APIResponse[AgentTraceResponse]:
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Not yet implemented (Step 4).",
    )


traces_router = APIRouter(prefix="/traces", tags=["traces"])


@traces_router.get(
    "/{trace_id}",
    response_model=APIResponse[AgentTraceResponse],
    summary="Get full agent trace by ID",
)
async def get_trace(trace_id: uuid.UUID) -> APIResponse[AgentTraceResponse]:
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Not yet implemented (Step 4).",
    )
