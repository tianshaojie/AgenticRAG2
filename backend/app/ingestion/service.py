"""DocumentIngestor default implementation for txt/markdown files."""

from __future__ import annotations

import hashlib
import uuid
from typing import TYPE_CHECKING

import structlog
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.config import Settings
from app.domain.document import Document
from app.ingestion.protocols import DocumentIngestor

if TYPE_CHECKING:
    pass

logger = structlog.get_logger(__name__)

SUPPORTED_CONTENT_TYPES = {
    "text/plain",
    "text/markdown",
    "text/x-markdown",
    # allow browsers that send no content-type or octet-stream for .txt/.md
    "application/octet-stream",
}


class TextDocumentIngestor:
    """Ingest plain-text / markdown documents into the documents table.

    Responsibilities:
    - Validate content-type and file size against Settings
    - Compute SHA-256 for deduplication (returns existing doc if hash matches)
    - Persist Document with status='pending'
    - Does NOT chunk or embed (that is the indexing pipeline's job)
    """

    def __init__(self, session: AsyncSession, settings: Settings) -> None:
        self._session = session
        self._settings = settings

    async def ingest(
        self,
        filename: str,
        content_type: str,
        raw_bytes: bytes,
        meta: dict | None = None,
    ) -> Document:
        log = logger.bind(filename=filename, content_type=content_type)

        # --- validate size ---
        if len(raw_bytes) > self._settings.max_upload_size_bytes:
            raise ValueError(
                f"File size {len(raw_bytes)} exceeds limit "
                f"{self._settings.max_upload_size_bytes} bytes."
            )

        # --- validate content-type (permissive: also allow application/octet-stream) ---
        normalised_ct = content_type.split(";")[0].strip().lower()
        if normalised_ct not in SUPPORTED_CONTENT_TYPES:
            raise ValueError(
                f"Unsupported content type '{content_type}'. "
                f"Supported: {sorted(SUPPORTED_CONTENT_TYPES)}"
            )

        # --- deduplication via SHA-256 ---
        content_hash = hashlib.sha256(raw_bytes).hexdigest()
        existing = await self._session.scalar(
            select(Document).where(
                Document.content_hash == content_hash,
                Document.is_deleted.is_(False),
            )
        )
        if existing is not None:
            log.info("document.deduplicated", document_id=str(existing.id))
            return existing

        # --- decode text ---
        try:
            text = raw_bytes.decode("utf-8")
        except UnicodeDecodeError:
            text = raw_bytes.decode("latin-1")

        document = Document(
            id=uuid.uuid4(),
            filename=filename,
            content_type=normalised_ct,
            content_hash=content_hash,
            size_bytes=len(raw_bytes),
            title=meta.get("title") if meta else None,
            status="pending",
            meta={
                "char_count": len(text),
                "line_count": text.count("\n") + 1,
                **(meta or {}),
            },
        )
        self._session.add(document)
        await self._session.flush()  # get the id without committing

        log.info(
            "document.ingested",
            document_id=str(document.id),
            size_bytes=len(raw_bytes),
            content_hash=content_hash,
        )
        return document


# Verify protocol conformance at import time
assert isinstance(TextDocumentIngestor.__new__(TextDocumentIngestor), DocumentIngestor)
