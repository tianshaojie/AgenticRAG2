"""Unit tests for DefaultCitationAssembler."""

from __future__ import annotations

import uuid
from unittest.mock import MagicMock

import pytest

from app.domain.document import Document, DocumentChunk
from app.retrieval.protocols import RetrievalResult
from app.services.citation_assembler import DefaultCitationAssembler


def _make_chunk(
    chunk_index: int = 0,
    content: str = "Test content for citation.",
    page_number: int | None = None,
    section_title: str | None = None,
) -> DocumentChunk:
    doc = MagicMock(spec=Document)
    doc.id = uuid.uuid4()
    doc.title = "Test Document"

    chunk = MagicMock(spec=DocumentChunk)
    chunk.id = uuid.uuid4()
    chunk.document_id = doc.id
    chunk.document = doc
    chunk.chunk_index = chunk_index
    chunk.content = content
    chunk.page_number = page_number
    chunk.section_title = section_title
    return chunk


def _make_result(chunk: DocumentChunk, score: float, rank: int = 0) -> RetrievalResult:
    return RetrievalResult(chunk=chunk, score=score, rank=rank)


@pytest.mark.asyncio
async def test_assemble_returns_citation_for_each_result():
    assembler = DefaultCitationAssembler()
    chunks = [_make_chunk(i, f"content {i}") for i in range(3)]
    results = [_make_result(c, score=0.9 - i * 0.1, rank=i) for i, c in enumerate(chunks)]

    citations = await assembler.assemble(results)

    assert len(citations) == 3


@pytest.mark.asyncio
async def test_assemble_empty_results_returns_empty():
    assembler = DefaultCitationAssembler()
    citations = await assembler.assemble([])
    assert citations == []


@pytest.mark.asyncio
async def test_assemble_citation_fields_are_correct():
    assembler = DefaultCitationAssembler()
    chunk = _make_chunk(
        chunk_index=5,
        content="A" * 300,  # longer than 200 chars
        page_number=3,
        section_title="Introduction",
    )
    result = _make_result(chunk, score=0.87)

    citations = await assembler.assemble([result])
    c = citations[0]

    assert c.chunk_id == chunk.id
    assert c.document_id == chunk.document.id
    assert c.document_title == "Test Document"
    assert c.chunk_index == 5
    assert c.page_number == 3
    assert c.section_title == "Introduction"
    assert len(c.content_snippet) == 200  # truncated
    assert c.score == 0.87


@pytest.mark.asyncio
async def test_assemble_score_rounded_to_4_decimal_places():
    assembler = DefaultCitationAssembler()
    chunk = _make_chunk()
    result = _make_result(chunk, score=0.123456789)

    citations = await assembler.assemble([result])
    assert citations[0].score == round(0.123456789, 4)


@pytest.mark.asyncio
async def test_assemble_preserves_order():
    """Citations must be returned in the same order as input results."""
    assembler = DefaultCitationAssembler()
    scores = [0.9, 0.8, 0.7, 0.6]
    results = [_make_result(_make_chunk(i), score=s, rank=i) for i, s in enumerate(scores)]

    citations = await assembler.assemble(results)

    for i, (c, expected_score) in enumerate(zip(citations, scores)):
        assert c.score == expected_score
