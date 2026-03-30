"""ORM models: chat_sessions and chat_messages."""

import uuid

from sqlalchemy import Boolean, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class ChatSession(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """A conversation session between a user and the RAG agent."""

    __tablename__ = "chat_sessions"

    title: Mapped[str | None] = mapped_column(String(512), nullable=True)
    # opaque user identifier — authentication is out of scope for Step 1
    user_id: Mapped[str | None] = mapped_column(String(256), nullable=True, index=True)
    # session-level metadata (language, model override, etc.)
    meta: Mapped[dict] = mapped_column(JSONB, nullable=False, server_default="{}")
    is_archived: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    messages: Mapped[list["ChatMessage"]] = relationship(
        "ChatMessage", back_populates="session", cascade="all, delete-orphan",
        order_by="ChatMessage.turn_index",
    )


class ChatMessage(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """A single turn in a ChatSession."""

    __tablename__ = "chat_messages"

    session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("chat_sessions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    # role: user | assistant | system
    role: Mapped[str] = mapped_column(String(32), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    # sequential position within the session
    turn_index: Mapped[int] = mapped_column(Integer, nullable=False)
    # did the agent abstain on this turn?
    abstained: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    # citations attached to this message (assembled by CitationAssembler)
    citations: Mapped[list] = mapped_column(JSONB, nullable=False, server_default="[]")
    # link to the agent trace that produced this message (nullable for user turns)
    agent_trace_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("agent_traces.id", ondelete="SET NULL"),
        nullable=True,
    )
    meta: Mapped[dict] = mapped_column(JSONB, nullable=False, server_default="{}")

    session: Mapped["ChatSession"] = relationship("ChatSession", back_populates="messages")
