"""Indexing pipeline: orchestrates Chunker → Embedder → VectorIndex.

This service is called by the POST /documents/{id}/index endpoint.
It is intentionally simple: one document at a time, synchronous within
the request. Background task offload is deferred to Step 7.
"""

from __future__ import annotations

import time

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings
from app.domain.document import Document, DocumentChunk
from app.indexing.chunker import FixedTokenChunker
from app.indexing.embedder import build_embedder
from app.indexing.vector_index import PgVectorIndex

logger = structlog.get_logger(__name__)


class IndexingPipeline:
    """Orchestrate the full ingestion → chunking → embedding → vector-store path.

    Steps:
    1. Load Document from DB (must exist, status must be 'pending' or 'failed')
    2. Chunk the document text using FixedTokenChunker
    3. Embed all chunk texts in a single batch call (Embedder)
    4. Upsert each (chunk, vector) pair into pgvector (VectorIndex)
    5. Update Document.status = 'indexed'

    Force re-index:
    - Deletes existing DocumentChunks (and cascade-deletes ChunkVectors)
    - Re-runs the full pipeline
    """

    def __init__(self, session: AsyncSession, settings: Settings) -> None:
        self._session = session
        self._settings = settings
        self._chunker = FixedTokenChunker(session, settings)
        self._embedder = build_embedder(settings)
        self._vector_index = PgVectorIndex(session, settings)

    async def run(self, document: Document, force_reindex: bool = False) -> Document:
        log = logger.bind(document_id=str(document.id))
        start_ms = int(time.monotonic() * 1000)

        if document.is_deleted:
            raise ValueError(f"Document {document.id} is deleted.")

        if document.status == "indexed" and not force_reindex:
            log.info("indexing_pipeline.skip", reason="already_indexed")
            return document

        # Mark as processing
        document.status = "processing"
        await self._session.flush()

        try:
            # 1. Delete existing chunks if re-indexing
            if force_reindex:
                from sqlalchemy import delete as sa_delete
                await self._session.execute(
                    sa_delete(DocumentChunk).where(
                        DocumentChunk.document_id == document.id
                    )
                )
                await self._session.flush()
                log.info("indexing_pipeline.cleared_chunks")

            # 2. Decode text
            text = await self._load_text(document)

            # 3. Chunk
            chunks = await self._chunker.chunk(document, text)
            if not chunks:
                document.status = "failed"
                await self._session.flush()
                log.warning("indexing_pipeline.no_chunks")
                return document

            # 4. Embed (batch)
            texts = [c.content for c in chunks]
            vectors = await self._embedder.embed(texts)

            # 5. Upsert vectors
            for chunk, vector in zip(chunks, vectors):
                await self._vector_index.upsert(chunk, vector)

            # 6. Mark indexed
            document.status = "indexed"
            await self._session.flush()

            elapsed_ms = int(time.monotonic() * 1000) - start_ms
            log.info(
                "indexing_pipeline.done",
                num_chunks=len(chunks),
                latency_ms=elapsed_ms,
                embedder=self._embedder.model_name,
            )

        except Exception as exc:
            document.status = "failed"
            await self._session.flush()
            log.error("indexing_pipeline.error", error=str(exc))
            raise

        return document

    async def _load_text(self, document: Document) -> str:
        """Extract the raw text stored in document.meta['raw_text'].

        For txt/markdown uploads, the API stores the decoded text in
        document.meta['raw_text'] at upload time. This avoids needing
        a file-system storage layer in Step 2.
        """
        raw_text = document.meta.get("raw_text")
        if not raw_text:
            raise ValueError(
                f"Document {document.id} has no 'raw_text' in meta. "
                "Re-upload the document."
            )
        return raw_text
