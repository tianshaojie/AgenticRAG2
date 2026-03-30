"""Evaluation API endpoints.

Routes:
    POST   /evals/run           — Trigger an evaluation run
    GET    /evals/{run_id}      — Get evaluation run result
    POST   /evals/cases         — Create an eval case
    GET    /evals/cases         — List eval cases
"""

import uuid

from fastapi import APIRouter, HTTPException, status

from app.schemas.common import APIResponse, PaginatedResponse
from app.schemas.eval import EvalCaseInput, EvalRunRequest, EvalRunResponse

router = APIRouter(prefix="/evals", tags=["evals"])


@router.post(
    "/run",
    response_model=APIResponse[EvalRunResponse],
    status_code=status.HTTP_202_ACCEPTED,
    summary="Trigger an evaluation run",
)
async def run_eval(body: EvalRunRequest) -> APIResponse[EvalRunResponse]:
    """Enqueue an evaluation run over a set of eval cases.

    Step 1: Returns 501 NOT IMPLEMENTED — full implementation in Step 5.
    """
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Eval runner not yet implemented (Step 5).",
    )


@router.get(
    "/{run_id}",
    response_model=APIResponse[EvalRunResponse],
    summary="Get evaluation run by ID",
)
async def get_eval_run(run_id: uuid.UUID) -> APIResponse[EvalRunResponse]:
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Not yet implemented (Step 5).",
    )


@router.post(
    "/cases",
    status_code=status.HTTP_201_CREATED,
    summary="Create an eval case",
)
async def create_eval_case(body: EvalCaseInput):
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Not yet implemented (Step 5).",
    )


@router.get(
    "/cases",
    response_model=PaginatedResponse,
    summary="List eval cases",
)
async def list_eval_cases(page: int = 1, page_size: int = 20):
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Not yet implemented (Step 5).",
    )
