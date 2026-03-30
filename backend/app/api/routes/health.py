"""Health and readiness check endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings, get_settings
from app.core.dependencies import get_db
from app.schemas.common import HealthResponse, ReadyResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse, summary="Liveness check")
async def health(
    settings: Settings = Depends(get_settings),
) -> HealthResponse:
    """Returns 200 if the application process is alive."""
    return HealthResponse(
        status="ok",
        version=settings.app_version,
        environment=settings.environment,
    )


@router.get("/ready", response_model=ReadyResponse, summary="Readiness check")
async def ready(
    db: AsyncSession = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> ReadyResponse:
    """Returns 200 when all dependencies (DB, vector extension) are reachable."""
    db_ok = False
    pgvector_ok = False
    try:
        await db.execute(text("SELECT 1"))
        db_ok = True
        # verify pgvector extension is available
        result = await db.execute(
            text("SELECT 1 FROM pg_extension WHERE extname = 'vector'")
        )
        pgvector_ok = result.scalar() == 1
    except Exception:
        pass

    checks = {
        "database": db_ok,
        "pgvector": pgvector_ok,
    }
    return ReadyResponse(ready=all(checks.values()), checks=checks)
