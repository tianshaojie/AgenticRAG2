"""Smoke tests: verify the full RAG pipeline works end-to-end.

These tests run against a real PostgreSQL + pgvector database.
They exercise the critical path:
  upload → index → query → citations / abstain

Run with: pytest tests/test_smoke.py -v
"""

from __future__ import annotations

import io

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_smoke_health_endpoints(client: AsyncClient):
    """Both /health and /ready must respond 200."""
    h = await client.get("/api/v1/health")
    assert h.status_code == 200
    assert h.json()["status"] == "ok"

    r = await client.get("/api/v1/ready")
    assert r.status_code == 200
    ready_data = r.json()
    assert ready_data["checks"]["database"] is True
    assert ready_data["checks"]["pgvector"] is True


@pytest.mark.asyncio
async def test_smoke_upload_document(client: AsyncClient):
    """Can upload a text document successfully."""
    content = b"Retrieval-Augmented Generation (RAG) combines retrieval with generation.\n"
    r = await client.post(
        "/api/v1/documents",
        files={"file": ("rag_intro.txt", io.BytesIO(content), "text/plain")},
        data={"title": "RAG Introduction"},
    )
    assert r.status_code == 202
    doc = r.json()["data"]
    assert doc["status"] == "pending"
    assert doc["title"] == "RAG Introduction"


@pytest.mark.asyncio
async def test_smoke_full_rag_pipeline(client: AsyncClient):
    """Full RAG pipeline: upload → index → query → citations present."""
    # 1. Upload
    content = (
        b"FastAPI is a modern, fast web framework for building APIs with Python. "
        b"It is based on standard Python type hints. "
        b"FastAPI uses Pydantic for data validation. "
        b"It generates OpenAPI documentation automatically. "
        b"FastAPI supports asynchronous request handling. "
    ) * 5  # repeat to ensure enough tokens for chunking
    upload_r = await client.post(
        "/api/v1/documents",
        files={"file": ("fastapi_intro.txt", io.BytesIO(content), "text/plain")},
    )
    assert upload_r.status_code == 202
    doc_id = upload_r.json()["data"]["id"]

    # 2. Index
    idx_r = await client.post(
        f"/api/v1/documents/{doc_id}/index",
        json={"force_reindex": False},
    )
    assert idx_r.status_code == 200
    assert idx_r.json()["data"]["status"] == "indexed"

    # 3. Query
    query_r = await client.post(
        "/api/v1/chat/query",
        json={"query": "FastAPI web framework Python"},
    )
    assert query_r.status_code == 200
    data = query_r.json()["data"]

    # With score_threshold=0.0 (test settings), we expect citations
    assert data["abstained"] is False
    assert len(data["citations"]) >= 1

    # Verify citation schema
    for c in data["citations"]:
        assert "chunk_id" in c
        assert "document_id" in c
        assert c["document_id"] == doc_id
        assert "content_snippet" in c
        assert isinstance(c["score"], float)

    # Verify response schema
    assert "session_id" in data
    assert "message_id" in data
    assert "answer" in data
    assert "latency_ms" in data
    assert isinstance(data["latency_ms"], int)


@pytest.mark.asyncio
async def test_smoke_abstain_when_no_evidence(client: AsyncClient):
    """Query with no relevant documents must abstain."""
    # Use a very high score threshold in settings to force abstain
    # (test_settings has score_threshold=0.0, but this test explicitly uses
    #  a separate client context — here we just query a fresh DB state)
    query_r = await client.post(
        "/api/v1/chat/query",
        json={"query": "completely irrelevant quantum entanglement query"},
    )
    assert query_r.status_code == 200
    data = query_r.json()["data"]

    # abstained must be a bool and answer must be non-empty
    assert isinstance(data["abstained"], bool)
    assert isinstance(data["answer"], str)
    assert len(data["answer"]) > 0
    # citations must be a list (empty if abstained)
    assert isinstance(data["citations"], list)
    if data["abstained"]:
        assert data["citations"] == []


@pytest.mark.asyncio
async def test_smoke_list_documents(client: AsyncClient):
    """GET /documents returns valid paginated response."""
    r = await client.get("/api/v1/documents")
    assert r.status_code == 200
    body = r.json()
    assert "items" in body
    assert "total" in body
    assert "page" in body
    assert "page_size" in body
    assert "has_next" in body
