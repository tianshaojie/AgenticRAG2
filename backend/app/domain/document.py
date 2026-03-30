"""ORM models: documents and document_chunks."""

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, Boolean, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.domain.vector import ChunkVector


class Document(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Represents an ingested source document."""

    __tablename__ = "documents"

    filename: Mapped[str] = mapped_column(String(512), nullable=False)
    content_type: Mapped[str] = mapped_column(String(128), nullable=False)
    # sha256 of raw content for deduplication
    content_hash: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    size_bytes: Mapped[int] = mapped_column(BigInteger, nullable=False)
    storage_path: Mapped[str | None] = mapped_column(Text, nullable=True)
    title: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    # indexing status: pending | processing | indexed | failed
    status: Mapped[str] = mapped_column(
        String(32), nullable=False, default="pending", index=True
    )
    # arbitrary key-value metadata (author, source_url, language, …)
    meta: Mapped[dict] = mapped_column(JSONB, nullable=False, server_default="{}")
    is_deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    chunks: Mapped[list["DocumentChunk"]] = relationship(
        "DocumentChunk", back_populates="document", cascade="all, delete-orphan"
    )


class DocumentChunk(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """A single text chunk derived from a Document."""

    __tablename__ = "document_chunks"

    document_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    # 0-based sequential position in the document
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    # token count (filled during ingestion)
    token_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    # page/section info for citation assembly
    page_number: Mapped[int | None] = mapped_column(Integer, nullable=True)
    section_title: Mapped[str | None] = mapped_column(String(512), nullable=True)
    # arbitrary extra metadata per chunk
    meta: Mapped[dict] = mapped_column(JSONB, nullable=False, server_default="{}")

    document: Mapped["Document"] = relationship("Document", back_populates="chunks")
    vector: Mapped["ChunkVector | None"] = relationship(
        "ChunkVector", back_populates="chunk", uselist=False
    )
