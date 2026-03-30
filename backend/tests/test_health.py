"""Smoke tests for health and readiness endpoints."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_returns_ok(client: AsyncClient):
    response = await client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "version" in data
    assert "environment" in data


@pytest.mark.asyncio
async def test_ready_returns_200(client: AsyncClient):
    response = await client.get("/api/v1/ready")
    assert response.status_code == 200
    data = response.json()
    assert "ready" in data
    assert "checks" in data


@pytest.mark.asyncio
async def test_documents_returns_501(client: AsyncClient):
    """Step 1: document endpoints must return 501 until Step 2."""
    response = await client.get("/api/v1/documents")
    assert response.status_code == 501


@pytest.mark.asyncio
async def test_chat_query_returns_501(client: AsyncClient):
    """Step 1: chat endpoint must return 501 until Step 4."""
    response = await client.post(
        "/api/v1/chat/query",
        json={"query": "What is RAG?"},
    )
    assert response.status_code == 501
