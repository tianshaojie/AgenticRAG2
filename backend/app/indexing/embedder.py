"""Embedder implementations.

DeterministicStubEmbedder — hash-based local stub, no external calls.
  - Produces stable vectors for the same text (deterministic).
  - Dimension matches Settings.vector_dimension.
  - Suitable for dev / CI without API keys.
  - NOT semantically meaningful; retrieval quality will be random.

OpenAIEmbedder — real OpenAI Embeddings API (Step 2+, requires llm_api_key).
  - Respects embedding_timeout_seconds.
  - Retries up to embedding_max_retries times with exponential backoff.
  - Logs model, latency, batch size via structlog.
"""

from __future__ import annotations

import hashlib
import math
import time
from typing import Any

import structlog
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from app.core.config import Settings
from app.indexing.protocols import Embedder

logger = structlog.get_logger(__name__)


class DeterministicStubEmbedder:
    """Hash-based stub embedder — no external dependencies.

    Each text is hashed with SHA-256; the raw bytes are spread into a
    float32 vector of the configured dimension by interpreting each pair
    of bytes as a signed integer and normalising to unit length.

    Properties:
    - Deterministic: same text → same vector across runs.
    - Unit-normalised: cosine similarity is well-defined.
    - NOT semantically meaningful.
    """

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._dim = settings.vector_dimension

    @property
    def model_name(self) -> str:
        return "deterministic_stub"

    @property
    def dimension(self) -> int:
        return self._dim

    async def embed(self, texts: list[str]) -> list[list[float]]:
        start = time.monotonic()
        vectors = [self._hash_vector(t) for t in texts]
        elapsed_ms = int((time.monotonic() - start) * 1000)
        logger.debug(
            "embedder.stub.embed",
            model=self.model_name,
            batch_size=len(texts),
            latency_ms=elapsed_ms,
        )
        return vectors

    def _hash_vector(self, text: str) -> list[float]:
        dim = self._dim
        # Produce enough bytes by repeatedly hashing with a counter
        raw: list[int] = []
        counter = 0
        while len(raw) < dim * 2:
            digest = hashlib.sha256(f"{counter}:{text}".encode()).digest()
            raw.extend(digest)
            counter += 1

        # Convert byte pairs to floats in [-1, 1]
        floats: list[float] = []
        for i in range(dim):
            val = raw[i * 2] - raw[i * 2 + 1]  # signed, range [-255, 255]
            floats.append(float(val))

        # L2-normalise to unit sphere (safe for cosine similarity)
        norm = math.sqrt(sum(x * x for x in floats)) or 1.0
        return [x / norm for x in floats]


class OpenAIEmbedder:
    """OpenAI Embeddings API client with timeout and retry.

    Requires: pip install openai>=1.0.0 (not in default requirements —
    add when enabling this provider).
    """

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._dim = settings.vector_dimension

        try:
            import openai  # type: ignore[import]
            self._client = openai.AsyncOpenAI(
                api_key=settings.llm_api_key,
                timeout=float(settings.embedding_timeout_seconds),
            )
        except ImportError as exc:
            raise RuntimeError(
                "openai package is required for OpenAIEmbedder. "
                "Add 'openai>=1.0.0' to requirements.txt."
            ) from exc

    @property
    def model_name(self) -> str:
        return self._settings.embedding_model

    @property
    def dimension(self) -> int:
        return self._dim

    @retry(
        retry=retry_if_exception_type(Exception),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=8),
        reraise=True,
    )
    async def embed(self, texts: list[str]) -> list[list[float]]:
        start = time.monotonic()
        response = await self._client.embeddings.create(
            input=texts,
            model=self._settings.embedding_model,
        )
        elapsed_ms = int((time.monotonic() - start) * 1000)
        vectors = [item.embedding for item in response.data]
        logger.info(
            "embedder.openai.embed",
            model=self.model_name,
            batch_size=len(texts),
            latency_ms=elapsed_ms,
        )
        return vectors


def build_embedder(settings: Settings) -> Any:
    """Factory: return correct Embedder implementation based on settings."""
    if settings.embedding_provider == "openai":
        return OpenAIEmbedder(settings)
    return DeterministicStubEmbedder(settings)


# Protocol conformance checks
assert isinstance(DeterministicStubEmbedder.__new__(DeterministicStubEmbedder), Embedder)
assert isinstance(OpenAIEmbedder.__new__(OpenAIEmbedder), Embedder)
