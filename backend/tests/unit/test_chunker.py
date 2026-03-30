"""Unit tests for FixedTokenChunker."""

from __future__ import annotations

import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest
import pytest_asyncio

from app.core.config import Settings
from app.domain.document import Document, DocumentChunk
from app.indexing.chunker import FixedTokenChunker


def _make_settings(**overrides) -> Settings:
    base = dict(
        database_url="postgresql+asyncpg://x:x@localhost/x",
        chunk_size_tokens=10,
        chunk_overlap_tokens=2,
        chunk_min_tokens=3,
        embedding_provider="deterministic_stub",
        answer_provider="echo_stub",
    )
    base.update(overrides)
    return Settings(**base)  # type: ignore[arg-type]


def _make_document():
    from unittest.mock import MagicMock
    doc = MagicMock(spec=Document)
    doc.id = uuid.uuid4()
    doc.filename = "test.txt"
    doc.content_type = "text/plain"
    doc.content_hash = "abc"
    doc.size_bytes = 100
    doc.status = "pending"
    doc.meta = {}
    doc.is_deleted = False
    return doc


def _make_mock_session():
    session = AsyncMock()
    session.add = MagicMock()
    session.flush = AsyncMock()
    return session


@pytest.mark.asyncio
async def test_chunker_produces_chunks_for_normal_text():
    """Standard text → multiple chunks produced."""
    settings = _make_settings(chunk_size_tokens=10, chunk_overlap_tokens=2, chunk_min_tokens=3)
    session = _make_mock_session()
    chunker = FixedTokenChunker(session, settings)
    doc = _make_document()

    text = " ".join([f"word{i}" for i in range(50)])  # ~50 tokens
    chunks = await chunker.chunk(doc, text)

    assert len(chunks) > 1
    assert all(isinstance(c, DocumentChunk) for c in chunks)
    assert all(c.document_id == doc.id for c in chunks)
    # chunk_index must be sequential and start at 0
    indices = [c.chunk_index for c in chunks]
    assert indices == list(range(len(chunks)))


@pytest.mark.asyncio
async def test_chunker_preserves_chunk_index_ordering():
    """chunk_index must be 0-based and strictly monotone."""
    settings = _make_settings(chunk_size_tokens=5, chunk_overlap_tokens=1, chunk_min_tokens=2)
    session = _make_mock_session()
    chunker = FixedTokenChunker(session, settings)
    doc = _make_document()

    text = "alpha beta gamma delta epsilon zeta eta theta iota kappa lambda mu"
    chunks = await chunker.chunk(doc, text)

    for i, c in enumerate(chunks):
        assert c.chunk_index == i


@pytest.mark.asyncio
async def test_chunker_short_text_produces_single_chunk():
    """Very short text → exactly one chunk (if tokens >= min_tokens)."""
    settings = _make_settings(chunk_size_tokens=50, chunk_overlap_tokens=5, chunk_min_tokens=1)
    session = _make_mock_session()
    chunker = FixedTokenChunker(session, settings)
    doc = _make_document()

    text = "Hello world"
    chunks = await chunker.chunk(doc, text)

    assert len(chunks) == 1
    assert chunks[0].chunk_index == 0
    assert "Hello" in chunks[0].content


@pytest.mark.asyncio
async def test_chunker_too_short_text_produces_no_chunks():
    """Text shorter than min_tokens → no chunks produced."""
    settings = _make_settings(chunk_size_tokens=50, chunk_overlap_tokens=5, chunk_min_tokens=100)
    session = _make_mock_session()
    chunker = FixedTokenChunker(session, settings)
    doc = _make_document()

    text = "Hi"
    chunks = await chunker.chunk(doc, text)

    assert chunks == []


@pytest.mark.asyncio
async def test_chunker_token_count_populated():
    """token_count must be set and <= chunk_size_tokens."""
    settings = _make_settings(chunk_size_tokens=8, chunk_overlap_tokens=1, chunk_min_tokens=2)
    session = _make_mock_session()
    chunker = FixedTokenChunker(session, settings)
    doc = _make_document()

    text = " ".join([f"tok{i}" for i in range(30)])
    chunks = await chunker.chunk(doc, text)

    for c in chunks:
        assert c.token_count is not None
        assert c.token_count <= settings.chunk_size_tokens


@pytest.mark.asyncio
async def test_chunker_overlapping_windows_share_tokens():
    """With overlap > 0, adjacent chunks should share some tokens."""
    settings = _make_settings(chunk_size_tokens=10, chunk_overlap_tokens=5, chunk_min_tokens=2)
    session = _make_mock_session()
    chunker = FixedTokenChunker(session, settings)
    doc = _make_document()

    text = " ".join([f"w{i}" for i in range(30)])
    chunks = await chunker.chunk(doc, text)

    assert len(chunks) >= 2
    # Verify overlap: end of chunk[0] text should share words with start of chunk[1]
    words_0 = set(chunks[0].content.split())
    words_1 = set(chunks[1].content.split())
    assert len(words_0 & words_1) > 0
