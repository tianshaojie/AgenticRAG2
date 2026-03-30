"""Unit tests for DeterministicStubEmbedder."""

from __future__ import annotations

import math

import pytest

from app.core.config import Settings
from app.indexing.embedder import DeterministicStubEmbedder, build_embedder


def _settings(**kw) -> Settings:
    base = dict(
        database_url="postgresql+asyncpg://x:x@localhost/x",
        embedding_provider="deterministic_stub",
        vector_dimension=64,
    )
    base.update(kw)
    return Settings(**base)  # type: ignore[arg-type]


@pytest.mark.asyncio
async def test_stub_returns_correct_dimension():
    emb = DeterministicStubEmbedder(_settings(vector_dimension=64))
    vecs = await emb.embed(["hello world"])
    assert len(vecs) == 1
    assert len(vecs[0]) == 64


@pytest.mark.asyncio
async def test_stub_is_deterministic():
    emb = DeterministicStubEmbedder(_settings(vector_dimension=32))
    v1 = (await emb.embed(["same text"]))[0]
    v2 = (await emb.embed(["same text"]))[0]
    assert v1 == v2


@pytest.mark.asyncio
async def test_stub_different_texts_give_different_vectors():
    emb = DeterministicStubEmbedder(_settings(vector_dimension=32))
    v1 = (await emb.embed(["text one"]))[0]
    v2 = (await emb.embed(["text two"]))[0]
    assert v1 != v2


@pytest.mark.asyncio
async def test_stub_vector_is_unit_normalised():
    emb = DeterministicStubEmbedder(_settings(vector_dimension=128))
    vec = (await emb.embed(["normalisation test"]))[0]
    norm = math.sqrt(sum(x * x for x in vec))
    assert abs(norm - 1.0) < 1e-6


@pytest.mark.asyncio
async def test_stub_batch_embedding():
    emb = DeterministicStubEmbedder(_settings(vector_dimension=16))
    texts = ["a", "b", "c", "d"]
    vecs = await emb.embed(texts)
    assert len(vecs) == len(texts)
    assert all(len(v) == 16 for v in vecs)


def test_build_embedder_returns_stub_by_default():
    s = _settings(embedding_provider="deterministic_stub")
    emb = build_embedder(s)
    assert isinstance(emb, DeterministicStubEmbedder)


def test_embedder_model_name_and_dimension():
    emb = DeterministicStubEmbedder(_settings(vector_dimension=256))
    assert emb.model_name == "deterministic_stub"
    assert emb.dimension == 256
