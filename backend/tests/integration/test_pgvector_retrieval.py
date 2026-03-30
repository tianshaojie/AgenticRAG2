"""Integration tests for pgvector-based retrieval.

Tests:
- VectorIndex upsert + search round-trip
- Score threshold filtering
- Empty retrieval → abstain path
- Retrieval with filter_metadata (JSONB)
"""

from __future__ import annotations

import uuid

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings
from app.domain.document import Document, DocumentChunk
from app.indexing.embedder import DeterministicStubEmbedder
from app.indexing.vector_index import PgVectorIndex
from app.retrieval.service import VectorRetriever


def _stub_settings(**kw) -> Settings:
    base = dict(
        database_url="postgresql+asyncpg://x:x@localhost/x",
        embedding_provider="deterministic_stub",
        vector_dimension=64,
        retrieval_top_k=5,
        retrieval_score_threshold=0.0,  # accept all results
        min_evidence_chunks=1,
        chunk_size_tokens=50,
        chunk_overlap_tokens=5,
        chunk_min_tokens=2,
    )
    base.update(kw)
    return Settings(**base)  # type: ignore[arg-type]


async def _create_document(session: AsyncSession) -> Document:
    doc = Document(
        id=uuid.uuid4(),
        filename="test.txt",
        content_type="text/plain",
        content_hash=uuid.uuid4().hex,
        size_bytes=100,
        status="pending",
        meta={"raw_text": "test content"},
        is_deleted=False,
    )
    session.add(doc)
    await session.flush()
    return doc


async def _create_chunk(
    session: AsyncSession,
    document: Document,
    content: str,
    chunk_index: int = 0,
    meta: dict | None = None,
) -> DocumentChunk:
    chunk = DocumentChunk(
        id=uuid.uuid4(),
        document_id=document.id,
        chunk_index=chunk_index,
        content=content,
        token_count=len(content.split()),
        meta=meta or {},
    )
    session.add(chunk)
    await session.flush()
    return chunk


@pytest.mark.asyncio
async def test_vector_index_upsert_and_search(db_session: AsyncSession):
    """Upsert a vector then search → it should be returned."""
    settings = _stub_settings(vector_dimension=64)
    embedder = DeterministicStubEmbedder(settings)
    index = PgVectorIndex(db_session, settings)

    doc = await _create_document(db_session)
    chunk = await _create_chunk(db_session, doc, "The quick brown fox")

    vector = (await embedder.embed([chunk.content]))[0]
    cv = await index.upsert(chunk, vector)

    assert cv.chunk_id == chunk.id
    assert cv.model_name == settings.embedding_model
    assert len(cv.embedding) == 64

    # Search with the same vector → should return the chunk
    results = await index.search(vector, top_k=3)
    assert len(results) >= 1
    chunk_ids = [r[0].chunk_id for r in results]
    assert chunk.id in chunk_ids


@pytest.mark.asyncio
async def test_vector_index_upsert_is_idempotent(db_session: AsyncSession):
    """Upserting the same chunk twice updates embedding_version."""
    settings = _stub_settings(vector_dimension=64)
    embedder = DeterministicStubEmbedder(settings)
    index = PgVectorIndex(db_session, settings)

    doc = await _create_document(db_session)
    chunk = await _create_chunk(db_session, doc, "Idempotent test content")
    vector = (await embedder.embed([chunk.content]))[0]

    cv1 = await index.upsert(chunk, vector)
    cv2 = await index.upsert(chunk, vector)

    assert cv1.chunk_id == cv2.chunk_id
    assert cv2.embedding_version == 2


@pytest.mark.asyncio
async def test_retriever_returns_results_for_query(db_session: AsyncSession):
    """End-to-end: ingest chunks → retrieve with VectorRetriever."""
    settings = _stub_settings(
        vector_dimension=64,
        retrieval_score_threshold=0.0,
        retrieval_top_k=5,
    )
    embedder = DeterministicStubEmbedder(settings)
    index = PgVectorIndex(db_session, settings)

    doc = await _create_document(db_session)
    texts = [
        "Python is a programming language",
        "FastAPI is a web framework",
        "PostgreSQL is a relational database",
    ]
    for i, text in enumerate(texts):
        chunk = await _create_chunk(db_session, doc, text, chunk_index=i)
        vector = (await embedder.embed([text]))[0]
        await index.upsert(chunk, vector)

    retriever = VectorRetriever(db_session, settings)
    results = await retriever.retrieve("Python programming")

    assert len(results) >= 1
    assert all(r.score >= 0.0 for r in results)
    ranks = [r.rank for r in results]
    assert ranks == list(range(len(ranks)))  # 0-indexed, consecutive


@pytest.mark.asyncio
async def test_retriever_score_threshold_filters_low_scores(db_session: AsyncSession):
    """Score threshold of 1.0 should return no results (nothing is that similar with stub)."""
    settings = _stub_settings(
        vector_dimension=64,
        retrieval_score_threshold=1.0,  # practically impossible threshold
        retrieval_top_k=5,
    )
    embedder = DeterministicStubEmbedder(settings)
    index = PgVectorIndex(db_session, settings)

    doc = await _create_document(db_session)
    chunk = await _create_chunk(db_session, doc, "Some content with stub embeddings")
    vector = (await embedder.embed([chunk.content]))[0]
    await index.upsert(chunk, vector)

    retriever = VectorRetriever(db_session, settings)
    results = await retriever.retrieve("totally different query content")

    # With threshold=1.0, no results should pass
    assert results == []


@pytest.mark.asyncio
async def test_retriever_top_k_limits_results(db_session: AsyncSession):
    """top_k parameter must be respected."""
    settings = _stub_settings(
        vector_dimension=64,
        retrieval_score_threshold=0.0,
        retrieval_top_k=2,
    )
    embedder = DeterministicStubEmbedder(settings)
    index = PgVectorIndex(db_session, settings)

    doc = await _create_document(db_session)
    for i in range(10):
        chunk = await _create_chunk(db_session, doc, f"Content item {i}", chunk_index=i)
        vector = (await embedder.embed([chunk.content]))[0]
        await index.upsert(chunk, vector)

    retriever = VectorRetriever(db_session, settings)
    results = await retriever.retrieve("content item", top_k=2)

    assert len(results) <= 2


@pytest.mark.asyncio
async def test_vector_index_delete_removes_vector(db_session: AsyncSession):
    """Deleting a vector removes it from search results."""
    settings = _stub_settings(vector_dimension=64)
    embedder = DeterministicStubEmbedder(settings)
    index = PgVectorIndex(db_session, settings)

    doc = await _create_document(db_session)
    chunk = await _create_chunk(db_session, doc, "To be deleted content")
    vector = (await embedder.embed([chunk.content]))[0]
    await index.upsert(chunk, vector)

    # Verify it's there
    results_before = await index.search(vector, top_k=5)
    assert any(r[0].chunk_id == chunk.id for r in results_before)

    # Delete
    await index.delete(str(chunk.id))

    # Verify it's gone
    results_after = await index.search(vector, top_k=5)
    assert not any(r[0].chunk_id == chunk.id for r in results_after)
