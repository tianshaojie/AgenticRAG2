"""Protocol interfaces for document ingestion and chunking."""

from typing import Protocol, runtime_checkable

from app.domain.document import Document, DocumentChunk


@runtime_checkable
class DocumentIngestor(Protocol):
    """Parse a raw document and persist it as a Document entity.

    Responsibilities:
    - Validate file type and size
    - Compute content hash for deduplication
    - Store raw bytes / path
    - Create Document record with status='pending'
    - Trigger chunking (may delegate to Chunker)

    NOT responsible for embedding or indexing.
    """

    async def ingest(
        self,
        filename: str,
        content_type: str,
        raw_bytes: bytes,
        meta: dict | None = None,
    ) -> Document:
        ...


@runtime_checkable
class Chunker(Protocol):
    """Split a Document's text content into DocumentChunks.

    Chunking strategy is implementation-specific (fixed-size, sentence,
    recursive, etc.). All implementations must:
    - Preserve chunk_index ordering
    - Populate token_count when possible
    - Not embed — embedding is the Embedder's responsibility
    """

    async def chunk(self, document: Document, text: str) -> list[DocumentChunk]:
        ...
