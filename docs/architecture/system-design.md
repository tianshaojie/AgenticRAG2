# System Design — Agentic RAG

## Overview

AgenticRAG is a production-grade Retrieval-Augmented Generation system.
Every answer is grounded in retrievable document evidence with full citation traceability.
The system is designed as a finite-state agent loop over a layered retrieval pipeline.

## Architecture Diagram

```
┌──────────────────────────────────────────────────────────┐
│                        Frontend                          │
│  Vue 3 + Vite + TypeScript + shadcn-vue + Tailwind       │
│                                                          │
│  Pages: Chat | Documents | Traces | Evals | Settings     │
└───────────────────┬──────────────────────────────────────┘
                    │  HTTP / REST  (OpenAPI 3.1)
┌───────────────────▼──────────────────────────────────────┐
│                     FastAPI Backend                       │
│                                                          │
│  ┌──────────┐  ┌──────────────┐  ┌──────────────────┐   │
│  │   API    │  │   Schemas    │  │  Observability   │   │
│  │  Router  │  │  (Pydantic)  │  │  (structlog)     │   │
│  └────┬─────┘  └──────────────┘  └──────────────────┘   │
│       │                                                   │
│  ┌────▼──────────────────────────────────────────────┐   │
│  │                  Agent (FSM)                      │   │
│  │  IDLE→RETRIEVING→EVALUATING→GENERATING→DONE       │   │
│  │                           ↘ ABSTAINING            │   │
│  └────┬──────────────────────────────────────────────┘   │
│       │                                                   │
│  ┌────▼──────┐  ┌────────────┐  ┌────────────────────┐  │
│  │ Retrieval │  │  Reranker  │  │ CitationAssembler  │  │
│  │ (pgvector)│  │            │  │                    │  │
│  └────┬──────┘  └────────────┘  └────────────────────┘  │
│       │                                                   │
│  ┌────▼──────────────────────────────────────────────┐   │
│  │              Ingestion / Indexing                 │   │
│  │  DocumentIngestor → Chunker → Embedder            │   │
│  └────┬──────────────────────────────────────────────┘   │
└───────┼──────────────────────────────────────────────────┘
        │
┌───────▼──────────────────────────────────────────────────┐
│                    PostgreSQL 15+                         │
│                                                          │
│  documents          document_chunks     chunk_vectors    │
│  chat_sessions      chat_messages       agent_traces     │
│  agent_trace_steps  eval_runs           eval_cases       │
│  eval_results                                            │
│                                                          │
│  pgvector: HNSW index on chunk_vectors.embedding         │
│  Distance: cosine similarity (<=>)                       │
└──────────────────────────────────────────────────────────┘
```

## Module Responsibilities

| Module | Responsibility |
|--------|---------------|
| `api/` | FastAPI routers — request validation and response formatting only |
| `core/` | Configuration (pydantic-settings), DI factories, lifespan hooks |
| `db/` | Async SQLAlchemy engine, session factory, base ORM class |
| `domain/` | ORM models (Document, Chunk, Vector, Chat, Agent, Eval) |
| `schemas/` | Pydantic request/response schemas (API contract) |
| `ingestion/` | DocumentIngestor, Chunker protocols + implementations |
| `indexing/` | Embedder, VectorIndex protocols + pgvector implementation |
| `retrieval/` | Retriever, Reranker protocols + pgvector ANN implementation |
| `services/` | CitationAssembler, AnswerGenerator — cross-module coordination |
| `agent/` | AgentPolicy finite-state machine |
| `evals/` | EvaluationRunner, metrics computation |
| `observability/` | structlog configuration, request tracing middleware |

## Data Flow

### Ingestion (Step 2)
```
HTTP POST /documents
  → DocumentIngestor.ingest()
    → Chunker.chunk()       # text splitting
    → Embedder.embed()      # vector generation
    → VectorIndex.upsert()  # pgvector write
  → Document.status = "indexed"
```

### Query (Step 4)
```
HTTP POST /chat/query
  → AgentPolicy.run(context)
    [IDLE → RETRIEVING]
      → Retriever.retrieve()
          → Embedder.embed(query)
          → VectorIndex.search(top_k=10)
    [RETRIEVING → EVALUATING_EVIDENCE]
      → Reranker.rerank()
      → score_threshold check
        → if insufficient → ABSTAINING
    [EVALUATING_EVIDENCE → GENERATING]
      → AnswerGenerator.generate(query, chunks)
      → CitationAssembler.assemble(results)
    [GENERATING → DONE]
      → persist AgentTrace + ChatMessage
  → HTTP 200 ChatQueryResponse
```

## pgvector Design Decisions

### Vector Column Placement
- Vectors stored in `chunk_vectors` table (separate from `document_chunks`)
- Rationale: keeps `document_chunks` lean for non-vector queries; allows re-embedding without modifying chunk rows; enables per-vector model versioning

### Distance Metric
- **Cosine similarity** (`<=>` operator) — default
- Rationale: normalized distance handles variable-length text well; OpenAI embeddings are designed for cosine similarity

### Index Strategy
- **HNSW** (m=16, ef_construction=64) for production ANN retrieval
- Sub-linear O(log n) search time; supports concurrent reads
- IVFFlat available as lower-memory alternative for development

### top-k Retrieval SQL Pattern
```sql
SELECT cv.*, dc.*,
       1 - (cv.embedding <=> $1::vector) AS score
FROM chunk_vectors cv
JOIN document_chunks dc ON dc.id = cv.chunk_id
JOIN documents d ON d.id = dc.document_id
WHERE d.is_deleted = false
  AND (dc.meta @> $2 OR $2 = '{}')   -- metadata filter
ORDER BY cv.embedding <=> $1::vector
LIMIT $3;
```

### Metadata Filter Strategy
- JSONB `@>` containment operator on `document_chunks.meta`
- Supports key-value filtering (e.g., `{"language": "en", "source": "manual"}`)
- GIN index on `document_chunks.meta` (added in Step 3 migration)

### Reranking Layering
```
pgvector ANN (top-k * 3 candidates)
  → Reranker (cross-encoder or BM25 hybrid)
    → top-k final results
```
- Retriever fetches 3x candidates to compensate for ANN recall loss
- Reranker is a pluggable protocol — default implementation in Step 3

## Security Assumptions (Step 1)
- No authentication implemented yet — all endpoints are public
- CORS restricted to empty list in production mode
- API keys loaded from environment variables only (never hardcoded)

## Scalability Considerations
- Async SQLAlchemy + asyncpg throughout — no blocking I/O
- Connection pool configurable via environment
- pgvector HNSW supports concurrent reads without locking
- Ingestion and indexing designed for background task offload (Step 2+)
