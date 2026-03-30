"""Health and readiness check endpoints."""

from fastapi import APIRouter

from app.core.config import get_settings
from app.schemas.common import HealthResponse, ReadyResponse

router = APIRouter(tags=["health"])
settings = get_settings()


@router.get("/health", response_model=HealthResponse, summary="Liveness check")
async def health() -> HealthResponse:
    """Returns 200 if the application process is alive."""
    return HealthResponse(
        status="ok",
        version=settings.app_version,
        environment=settings.environment,
    )


@router.get("/ready", response_model=ReadyResponse, summary="Readiness check")
async def ready() -> ReadyResponse:
    """Returns 200 when all dependencies (DB, etc.) are reachable."""
    # TODO(Step 2): add real DB ping
    checks = {
        "database": True,  # placeholder
    }
    all_ready = all(checks.values())
    return ReadyResponse(ready=all_ready, checks=checks)
