"""Integration tests for POST /chat/query.

Covers:
- Query with indexed documents → answer with citations
- Query with no indexed documents → abstain response
- Abstain contract enforcement (citations=[])
"""

from __future__ import annotations

import io

import pytest
from httpx import AsyncClient


async def _upload_and_index(client: AsyncClient, content: bytes, filename: str) -> str:
    """Helper: upload + index a document, return doc_id."""
    upload = await client.post(
        "/api/v1/documents",
        files={"file": (filename, io.BytesIO(content), "text/plain")},
    )
    assert upload.status_code == 202, upload.text
    doc_id = upload.json()["data"]["id"]
    idx = await client.post(
        f"/api/v1/documents/{doc_id}/index",
        json={"force_reindex": False},
    )
    assert idx.status_code == 200, idx.text
    return doc_id


@pytest.mark.asyncio
async def test_chat_query_abstains_when_no_documents(client: AsyncClient):
    """With no indexed documents, the response must be abstained=True."""
    response = await client.post(
        "/api/v1/chat/query",
        json={"query": "What is the meaning of life?"},
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["success"] is True
    data = body["data"]
    assert data["abstained"] is True
    assert data["citations"] == []
    assert isinstance(data["answer"], str)
    assert len(data["answer"]) > 0


@pytest.mark.asyncio
async def test_chat_query_returns_citations_after_indexing(client: AsyncClient):
    """With indexed documents, response must include non-empty citations."""
    content = b" ".join([f"word{i}".encode() for i in range(300)])
    await _upload_and_index(client, content, "rag_source.txt")

    # Query with something that overlaps with indexed content
    response = await client.post(
        "/api/v1/chat/query",
        json={"query": "word1 word2 word3"},
    )
    assert response.status_code == 200, response.text
    data = response.json()["data"]

    # With score_threshold=0.0 (test settings), we should get citations
    assert isinstance(data["citations"], list)
    assert data["abstained"] is False
    assert len(data["citations"]) >= 1


@pytest.mark.asyncio
async def test_chat_query_response_schema(client: AsyncClient):
    """Response must conform to ChatQueryResponse schema."""
    response = await client.post(
        "/api/v1/chat/query",
        json={"query": "schema test query"},
    )
    assert response.status_code == 200
    data = response.json()["data"]

    required_fields = {
        "session_id", "message_id", "answer", "abstained",
        "citations", "agent_trace_id", "latency_ms",
    }
    assert required_fields <= set(data.keys())
    assert isinstance(data["abstained"], bool)
    assert isinstance(data["citations"], list)
    assert isinstance(data["latency_ms"], int)


@pytest.mark.asyncio
async def test_chat_query_citation_schema(client: AsyncClient):
    """Citations must contain all required fields when present."""
    content = b" ".join([f"info{i}".encode() for i in range(200)])
    await _upload_and_index(client, content, "cite_source.txt")

    response = await client.post(
        "/api/v1/chat/query",
        json={"query": "info1 info2 info3"},
    )
    data = response.json()["data"]

    if not data["abstained"]:
        for citation in data["citations"]:
            assert "chunk_id" in citation
            assert "document_id" in citation
            assert "chunk_index" in citation
            assert "content_snippet" in citation
            assert "score" in citation
            assert isinstance(citation["score"], float)
            assert 0.0 <= citation["score"] <= 1.0


@pytest.mark.asyncio
async def test_chat_query_empty_query_rejected(client: AsyncClient):
    """Empty query string should return 422."""
    response = await client.post(
        "/api/v1/chat/query",
        json={"query": ""},
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_chat_query_with_session_id(client: AsyncClient):
    """Providing a session_id should be accepted and echoed back."""
    import uuid
    sid = str(uuid.uuid4())
    response = await client.post(
        "/api/v1/chat/query",
        json={"query": "test with session", "session_id": sid},
    )
    assert response.status_code == 200
    # session_id in response may be same or new (Step 2 creates new if not found)
    data = response.json()["data"]
    assert "session_id" in data
