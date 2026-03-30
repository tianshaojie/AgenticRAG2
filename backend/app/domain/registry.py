"""Import all domain models so Alembic autogenerate can discover them."""

from app.domain.document import Document, DocumentChunk  # noqa: F401
from app.domain.vector import ChunkVector  # noqa: F401
from app.domain.chat import ChatSession, ChatMessage  # noqa: F401
from app.domain.agent import AgentTrace, AgentTraceStep  # noqa: F401
from app.domain.eval import EvalRun, EvalCase, EvalResult  # noqa: F401
