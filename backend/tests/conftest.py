"""Pytest fixtures shared across all backend tests.

Database strategy:
- One engine for the whole test session (session-scoped).
- pgvector extension and schema created via create_all + raw SQL on first run.
- Each test gets an isolated session that is rolled back after the test
  (savepoint-based isolation so DDL effects persist but DML is reverted).
- The ASGI client override injects the test db_session via DI override.

Requires:
  TEST_DATABASE_URL env var (or the default below) pointing to an existing
  PostgreSQL 15+ database with pgvector installed.
  Run: make db-setup before running tests.
"""

from __future__ import annotations

import asyncio
import os
from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import event, text
from sqlalchemy.ext.asyncio import (
    AsyncConnection,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import Settings
from app.db.base import Base
from app.main import app

TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql+asyncpg://postgres:postgres@localhost:5432/agentic_rag_test",
)

# ── Event loop ─────────────────────────────────────────────────────────────


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


# ── Engine (session-scoped) ────────────────────────────────────────────────


@pytest_asyncio.fixture(scope="session")
async def test_engine():
    engine = create_async_engine(TEST_DATABASE_URL, echo=False, future=True)

    async with engine.begin() as conn:
        # Enable pgvector before create_all
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS pgcrypto"))
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


# ── Per-test session with savepoint rollback ───────────────────────────────


@pytest_asyncio.fixture
async def db_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """Transactional test session: rolls back after each test via savepoint."""
    connection: AsyncConnection = await test_engine.connect()
    await connection.begin()  # outer transaction

    session = AsyncSession(bind=connection, expire_on_commit=False)
    await connection.begin_nested()  # savepoint

    @event.listens_for(session.sync_session, "after_transaction_end")
    def restart_savepoint(session_, transaction):
        if transaction.nested and not transaction._parent.nested:
            connection.sync_connection.begin_nested()

    try:
        yield session
    finally:
        await session.close()
        await connection.rollback()  # rolls back the outer transaction
        await connection.close()


# ── Settings override for tests ────────────────────────────────────────────


@pytest.fixture
def test_settings() -> Settings:
    return Settings(
        database_url=TEST_DATABASE_URL,  # type: ignore[arg-type]
        embedding_provider="deterministic_stub",
        answer_provider="echo_stub",
        retrieval_score_threshold=0.0,  # accept all scores in unit tests
        min_evidence_chunks=1,
        log_format="console",
    )


# ── ASGI test client with DI override ─────────────────────────────────────


@pytest_asyncio.fixture
async def client(db_session: AsyncSession, test_settings: Settings) -> AsyncGenerator[AsyncClient, None]:
    """HTTP test client with DB session and settings injected."""
    from app.core.dependencies import get_db
    from app.core.config import get_settings

    app.dependency_overrides[get_db] = lambda: _yield_session(db_session)
    app.dependency_overrides[get_settings] = lambda: test_settings

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as c:
        yield c

    app.dependency_overrides.clear()


async def _yield_session(session: AsyncSession):
    """Helper to make db_session usable as a FastAPI dependency override."""
    yield session
