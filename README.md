# AgenticRAG

Production-grade Agentic RAG (Retrieval-Augmented Generation) system with citation-grounded answers.

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.12 + FastAPI + Pydantic v2 |
| Database | PostgreSQL 15+ + pgvector |
| ORM / Migration | SQLAlchemy 2.x + Alembic |
| Frontend | Vue 3 + TypeScript + Vite + shadcn-vue + Tailwind |
| Testing | pytest / vitest |

## Quick Start

```bash
# 1. Install dependencies
make install

# 2. Configure environment
cp backend/.env.example backend/.env
# Edit backend/.env with your PostgreSQL credentials

# 3. Setup database
make db-setup

# 4. Run migrations
make db-migrate

# 5. Start backend (port 8000)
make dev-backend

# 6. Start frontend (port 5173)
make dev-frontend
```

## Development

```bash
make test-backend    # run pytest
make test-frontend   # run vitest
make lint            # ruff linter
make fmt             # ruff formatter
make db-migrate-create MSG="add user table"  # new migration
```

## API Documentation

- OpenAPI UI: http://localhost:8000/api/v1/docs
- ReDoc: http://localhost:8000/api/v1/redoc
- OpenAPI JSON: http://localhost:8000/api/v1/openapi.json

## Project Structure

```
AgenticRAG/
├── AGENTS.md                    # Project context for AI agents
├── Makefile                     # Development commands
├── backend/
│   ├── app/
│   │   ├── api/                 # FastAPI routes
│   │   ├── core/                # Config, DI, lifespan
│   │   ├── db/                  # SQLAlchemy engine + session
│   │   ├── domain/              # ORM models
│   │   ├── schemas/             # Pydantic schemas
│   │   ├── ingestion/           # DocumentIngestor, Chunker
│   │   ├── indexing/            # Embedder, VectorIndex
│   │   ├── retrieval/           # Retriever, Reranker
│   │   ├── services/            # CitationAssembler, AnswerGenerator
│   │   ├── agent/               # AgentPolicy FSM
│   │   ├── evals/               # EvaluationRunner
│   │   └── observability/       # structlog, middleware
│   ├── alembic/                 # DB migrations
│   └── tests/                   # pytest test suite
├── frontend/
│   └── src/
│       ├── pages/               # Chat, Documents, Traces, Evals, Settings
│       ├── features/            # Feature-scoped components (Step 6)
│       ├── api/                 # Axios API clients
│       ├── types/               # TypeScript API types
│       └── lib/                 # Utilities (cn, etc.)
├── docs/
│   ├── architecture/            # System design, DB schema, API contract
│   └── quality/                 # Acceptance criteria
└── evals/                       # Eval cases and scripts
```

## Implementation Stages

| Stage | Status | Description |
|-------|--------|-------------|
| Step 1 | ✅ Done | Architecture, directory, schema, interface skeleton |
| Step 2 | 🔜 Next | Document ingestion, chunking, embedding pipeline |
| Step 3 | ⏳ | pgvector retrieval, Reranker, CitationAssembler |
| Step 4 | ⏳ | Agent FSM, AnswerGenerator, full RAG pipeline |
| Step 5 | ⏳ | Eval framework, metrics, regression tests |
| Step 6 | ⏳ | Frontend full implementation, E2E tests |
| Step 7 | ⏳ | Production hardening: monitoring, rate limiting, deployment |
