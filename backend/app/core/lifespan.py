"""FastAPI application lifespan: startup and shutdown hooks."""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

import structlog
from fastapi import FastAPI

from app.db.session import init_db, close_db
from app.observability.logging import configure_logging

logger = structlog.get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    configure_logging()
    logger.info("application.startup", version=app.version)

    await init_db()
    logger.info("database.connected")

    yield

    await close_db()
    logger.info("application.shutdown")
