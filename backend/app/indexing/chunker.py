"""Fixed-token-window Chunker implementation using tiktoken."""

from __future__ import annotations

import uuid

import structlog
import tiktoken
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings
from app.domain.document import Document, DocumentChunk
from app.ingestion.protocols import Chunker

logger = structlog.get_logger(__name__)

# cl100k_base is used by gpt-4 / text-embedding-3-* models
_TIKTOKEN_ENCODING = "cl100k_base"


class FixedTokenChunker:
    """Split document text into fixed-size token windows with overlap.

    Strategy:
    - Tokenise the full text with tiktoken (cl100k_base)
    - Slide a window of `chunk_size_tokens` tokens, advancing by
      (chunk_size_tokens - chunk_overlap_tokens) each step
    - Decode each window back to a UTF-8 string
    - Skip windows with fewer than `chunk_min_tokens` tokens (trailing noise)

    This is a token-level split, NOT sentence-aware. Sentence-aware splitting
    is deferred to Step 3 if retrieval quality requires it.
    """

    def __init__(self, session: AsyncSession, settings: Settings) -> None:
        self._session = session
        self._settings = settings
        self._enc = tiktoken.get_encoding(_TIKTOKEN_ENCODING)

    async def chunk(self, document: Document, text: str) -> list[DocumentChunk]:
        log = logger.bind(document_id=str(document.id))

        tokens = self._enc.encode(text)
        size = self._settings.chunk_size_tokens
        overlap = self._settings.chunk_overlap_tokens
        min_tokens = self._settings.chunk_min_tokens
        stride = max(1, size - overlap)

        chunks: list[DocumentChunk] = []
        chunk_index = 0
        pos = 0

        while pos < len(tokens):
            window = tokens[pos : pos + size]
            if len(window) < min_tokens:
                break

            chunk_text = self._enc.decode(window)
            chunk = DocumentChunk(
                id=uuid.uuid4(),
                document_id=document.id,
                chunk_index=chunk_index,
                content=chunk_text,
                token_count=len(window),
                meta={},
            )
            self._session.add(chunk)
            chunks.append(chunk)
            chunk_index += 1
            pos += stride

        await self._session.flush()

        log.info(
            "document.chunked",
            num_chunks=len(chunks),
            total_tokens=len(tokens),
            chunk_size=size,
            overlap=overlap,
        )
        return chunks


# Verify protocol conformance
assert isinstance(FixedTokenChunker.__new__(FixedTokenChunker), Chunker)
