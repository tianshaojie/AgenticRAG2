"""Integration tests for /documents endpoints.

Requires a running PostgreSQL 15+ with pgvector.
Set TEST_DATABASE_URL to point to the test DB.
"""

from __future__ import annotations

import io

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_upload_txt_document(client: AsyncClient):
    """POST /documents with a plain text file → 202, document returned."""
    content = b"Hello, this is a test document.\nIt has multiple lines.\n"
    response = await client.post(
        "/api/v1/documents",
        files={"file": ("test.txt", io.BytesIO(content), "text/plain")},
    )
    assert response.status_code == 202, response.text
    body = response.json()
    assert body["success"] is True
    data = body["data"]
    assert data["filename"] == "test.txt"
    assert data["status"] == "pending"
    assert data["content_type"] == "text/plain"
    assert "raw_text" not in data["meta"]  # must be stripped


@pytest.mark.asyncio
async def test_upload_markdown_document(client: AsyncClient):
    """POST /documents with markdown → accepted."""
    content = b"# Title\n\nThis is **markdown** content.\n"
    response = await client.post(
        "/api/v1/documents",
        files={"file": ("readme.md", io.BytesIO(content), "text/markdown")},
        data={"title": "My Markdown Doc"},
    )
    assert response.status_code == 202
    data = response.json()["data"]
    assert data["title"] == "My Markdown Doc"
    assert data["filename"] == "readme.md"


@pytest.mark.asyncio
async def test_upload_deduplication(client: AsyncClient):
    """Uploading the same content twice returns the existing document."""
    content = b"Duplicate content for deduplication test."
    files = {"file": ("dup.txt", io.BytesIO(content), "text/plain")}

    r1 = await client.post("/api/v1/documents", files=files)
    r2 = await client.post(
        "/api/v1/documents",
        files={"file": ("dup.txt", io.BytesIO(content), "text/plain")},
    )
    assert r1.status_code == 202
    assert r2.status_code == 202
    assert r1.json()["data"]["id"] == r2.json()["data"]["id"]


@pytest.mark.asyncio
async def test_upload_unsupported_type_rejected(client: AsyncClient):
    """Uploading a non-text file returns 422."""
    response = await client.post(
        "/api/v1/documents",
        files={"file": ("doc.pdf", io.BytesIO(b"%PDF-"), "application/pdf")},
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_list_documents_returns_paginated(client: AsyncClient):
    """GET /documents returns paginated list."""
    # Upload a doc first
    await client.post(
        "/api/v1/documents",
        files={"file": ("list_test.txt", io.BytesIO(b"content for list test"), "text/plain")},
    )
    response = await client.get("/api/v1/documents?page=1&page_size=20")
    assert response.status_code == 200
    body = response.json()
    assert "items" in body
    assert "total" in body
    assert body["total"] >= 1
    assert isinstance(body["items"], list)


@pytest.mark.asyncio
async def test_get_document_by_id(client: AsyncClient):
    """GET /documents/{id} returns correct document."""
    upload = await client.post(
        "/api/v1/documents",
        files={"file": ("byid.txt", io.BytesIO(b"get by id content"), "text/plain")},
    )
    doc_id = upload.json()["data"]["id"]

    response = await client.get(f"/api/v1/documents/{doc_id}")
    assert response.status_code == 200
    assert response.json()["data"]["id"] == doc_id


@pytest.mark.asyncio
async def test_get_nonexistent_document_returns_404(client: AsyncClient):
    import uuid
    response = await client.get(f"/api/v1/documents/{uuid.uuid4()}")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_document(client: AsyncClient):
    """DELETE /documents/{id} soft-deletes the document."""
    upload = await client.post(
        "/api/v1/documents",
        files={"file": ("delete_me.txt", io.BytesIO(b"delete test content"), "text/plain")},
    )
    doc_id = upload.json()["data"]["id"]

    del_response = await client.delete(f"/api/v1/documents/{doc_id}")
    assert del_response.status_code == 204

    # Document should now be gone from listing
    get_response = await client.get(f"/api/v1/documents/{doc_id}")
    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_index_document_transitions_status(client: AsyncClient):
    """POST /documents/{id}/index → status becomes 'indexed'."""
    content = b"Document to be indexed. Contains useful retrieval content here."
    upload = await client.post(
        "/api/v1/documents",
        files={"file": ("index_me.txt", io.BytesIO(content), "text/plain")},
    )
    assert upload.status_code == 202
    doc_id = upload.json()["data"]["id"]

    index_response = await client.post(
        f"/api/v1/documents/{doc_id}/index",
        json={"force_reindex": False},
    )
    assert index_response.status_code == 200
    data = index_response.json()["data"]
    assert data["status"] == "indexed"
    assert data["document_id"] == doc_id


@pytest.mark.asyncio
async def test_index_creates_chunks_in_db(client: AsyncClient, db_session):
    """After indexing, document_chunks should exist in the DB."""
    from sqlalchemy import select
    from app.domain.document import Document, DocumentChunk

    content = b" ".join([f"word{i}".encode() for i in range(200)])
    upload = await client.post(
        "/api/v1/documents",
        files={"file": ("chunked.txt", io.BytesIO(content), "text/plain")},
    )
    doc_id = upload.json()["data"]["id"]
    await client.post(f"/api/v1/documents/{doc_id}/index", json={"force_reindex": False})

    import uuid
    chunks = (await db_session.scalars(
        select(DocumentChunk).where(DocumentChunk.document_id == uuid.UUID(doc_id))
    )).all()
    assert len(chunks) > 0
    assert all(c.token_count is not None for c in chunks)


@pytest.mark.asyncio
async def test_force_reindex_recreates_chunks(client: AsyncClient, db_session):
    """force_reindex=True deletes old chunks and creates new ones."""
    from sqlalchemy import select
    from app.domain.document import DocumentChunk
    import uuid

    content = b" ".join([f"tok{i}".encode() for i in range(100)])
    upload = await client.post(
        "/api/v1/documents",
        files={"file": ("reindex.txt", io.BytesIO(content), "text/plain")},
    )
    doc_id = upload.json()["data"]["id"]

    # First index
    await client.post(f"/api/v1/documents/{doc_id}/index", json={"force_reindex": False})
    chunks_after_first = (await db_session.scalars(
        select(DocumentChunk).where(DocumentChunk.document_id == uuid.UUID(doc_id))
    )).all()

    # Force re-index
    r = await client.post(f"/api/v1/documents/{doc_id}/index", json={"force_reindex": True})
    assert r.status_code == 200
    chunks_after_second = (await db_session.scalars(
        select(DocumentChunk).where(DocumentChunk.document_id == uuid.UUID(doc_id))
    )).all()

    # Chunks should exist and have new IDs (old ones were deleted and re-created)
    assert len(chunks_after_second) > 0
    first_ids = {c.id for c in chunks_after_first}
    second_ids = {c.id for c in chunks_after_second}
    assert first_ids.isdisjoint(second_ids)
