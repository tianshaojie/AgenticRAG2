"""Unit tests for EchoStubAnswerGenerator — abstain and generate paths."""

from __future__ import annotations

import uuid
from unittest.mock import MagicMock

import pytest

from app.core.config import Settings
from app.domain.document import DocumentChunk
from app.retrieval.protocols import RetrievalResult
from app.services.answer_generator import (
    EchoStubAnswerGenerator,
    OpenAIAnswerGenerator,
    build_answer_generator,
)


def _settings(**kw) -> Settings:
    base = dict(
        database_url="postgresql+asyncpg://x:x@localhost/x",
        answer_provider="echo_stub",
        min_evidence_chunks=1,
    )
    base.update(kw)
    return Settings(**base)  # type: ignore[arg-type]


def _make_result(content: str = "relevant content", score: float = 0.85) -> RetrievalResult:
    chunk = MagicMock(spec=DocumentChunk)
    chunk.id = uuid.uuid4()
    chunk.chunk_index = 0
    chunk.content = content
    return RetrievalResult(chunk=chunk, score=score, rank=0)


@pytest.mark.asyncio
async def test_echo_stub_abstains_when_no_evidence():
    gen = EchoStubAnswerGenerator(_settings(min_evidence_chunks=1))
    answer, abstained = await gen.generate("What is X?", [])
    assert abstained is True
    assert "cannot" in answer.lower() or "insufficient" in answer.lower()


@pytest.mark.asyncio
async def test_echo_stub_abstains_below_min_evidence():
    gen = EchoStubAnswerGenerator(_settings(min_evidence_chunks=3))
    results = [_make_result("chunk content")]  # only 1, need 3
    answer, abstained = await gen.generate("question", results)
    assert abstained is True


@pytest.mark.asyncio
async def test_echo_stub_generates_when_sufficient_evidence():
    gen = EchoStubAnswerGenerator(_settings(min_evidence_chunks=1))
    results = [_make_result("important context here")]
    answer, abstained = await gen.generate("What is context?", results)
    assert abstained is False
    assert "important context here" in answer


@pytest.mark.asyncio
async def test_echo_stub_answer_contains_all_chunks():
    gen = EchoStubAnswerGenerator(_settings(min_evidence_chunks=1))
    results = [
        _make_result("chunk A content"),
        _make_result("chunk B content"),
        _make_result("chunk C content"),
    ]
    answer, abstained = await gen.generate("multi-chunk question", results)
    assert abstained is False
    assert "chunk A content" in answer
    assert "chunk B content" in answer
    assert "chunk C content" in answer


@pytest.mark.asyncio
async def test_echo_stub_returns_string_and_bool():
    gen = EchoStubAnswerGenerator(_settings())
    answer, abstained = await gen.generate("q", [_make_result()])
    assert isinstance(answer, str)
    assert isinstance(abstained, bool)


@pytest.mark.asyncio
async def test_openai_generator_raises_not_implemented():
    gen = OpenAIAnswerGenerator(_settings())
    with pytest.raises(NotImplementedError):
        await gen.generate("question", [_make_result()])


def test_build_answer_generator_returns_echo_stub_by_default():
    s = _settings(answer_provider="echo_stub")
    gen = build_answer_generator(s)
    assert isinstance(gen, EchoStubAnswerGenerator)
