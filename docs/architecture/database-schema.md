# Database Schema — Agentic RAG

## Tables Overview

```
documents               — source documents
document_chunks         — text chunks from documents
chunk_vectors           — pgvector embeddings (HNSW indexed)
chat_sessions           — conversation sessions
chat_messages           — individual turns (user/assistant)
agent_traces            — top-level agent execution record
agent_trace_steps       — per-step FSM transition record
eval_runs               — evaluation run metadata
eval_cases              — question/answer eval cases
eval_results            — per-case results for a run
```

## Table Definitions

### documents
| Column | Type | Notes |
|--------|------|-------|
| id | UUID PK | gen_random_uuid() |
| filename | VARCHAR(512) | original filename |
| content_type | VARCHAR(128) | MIME type |
| content_hash | VARCHAR(64) | SHA-256, indexed for deduplication |
| size_bytes | BIGINT | raw file size |
| storage_path | TEXT | nullable — local path or object store key |
| title | VARCHAR(1024) | optional human-readable title |
| status | VARCHAR(32) | pending / processing / indexed / failed |
| meta | JSONB | flexible key-value metadata |
| is_deleted | BOOLEAN | soft-delete flag |
| created_at | TIMESTAMPTZ | auto |
| updated_at | TIMESTAMPTZ | trigger-maintained |

### document_chunks
| Column | Type | Notes |
|--------|------|-------|
| id | UUID PK | |
| document_id | UUID FK → documents.id | CASCADE delete |
| chunk_index | INTEGER | 0-based sequential position |
| content | TEXT | chunk text |
| token_count | INTEGER | nullable, filled during ingestion |
| page_number | INTEGER | nullable, for PDF citation |
| section_title | VARCHAR(512) | nullable |
| meta | JSONB | extra metadata (GIN index in Step 3) |

### chunk_vectors *(pgvector)*
| Column | Type | Notes |
|--------|------|-------|
| id | UUID PK | |
| chunk_id | UUID FK → document_chunks.id | UNIQUE, CASCADE |
| embedding | VECTOR(1536) | HNSW cosine index |
| model_name | VARCHAR(128) | e.g. text-embedding-3-small |
| model_version | VARCHAR(64) | nullable |
| embedding_version | INTEGER | incremented on re-embed |

**HNSW Index:**
```sql
CREATE INDEX ix_chunk_vectors_embedding_hnsw
ON chunk_vectors
USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);
```

### chat_sessions
| Column | Type | Notes |
|--------|------|-------|
| id | UUID PK | |
| title | VARCHAR(512) | nullable |
| user_id | VARCHAR(256) | nullable, indexed |
| meta | JSONB | |
| is_archived | BOOLEAN | |

### chat_messages
| Column | Type | Notes |
|--------|------|-------|
| id | UUID PK | |
| session_id | UUID FK → chat_sessions.id | CASCADE |
| role | VARCHAR(32) | user / assistant / system |
| content | TEXT | |
| turn_index | INTEGER | ordering within session |
| abstained | BOOLEAN | true if agent abstained |
| citations | JSONB | assembled Citation objects |
| agent_trace_id | UUID FK → agent_traces.id | nullable, SET NULL |

### agent_traces
| Column | Type | Notes |
|--------|------|-------|
| id | UUID PK | |
| session_id | UUID FK → chat_sessions.id | SET NULL |
| query | TEXT | original user query |
| final_state | VARCHAR(32) | DONE / ABSTAINING / ERROR |
| total_steps | INTEGER | |
| abstained | BOOLEAN | |
| latency_ms | INTEGER | nullable |
| request_id | VARCHAR(128) | indexed, for distributed tracing |
| trace_id | VARCHAR(128) | from X-Trace-ID header |
| meta | JSONB | |

### agent_trace_steps
| Column | Type | Notes |
|--------|------|-------|
| id | UUID PK | |
| trace_id | UUID FK → agent_traces.id | CASCADE |
| step_index | INTEGER | 0-based |
| state_from | VARCHAR(64) | FSM state before |
| state_to | VARCHAR(64) | FSM state after |
| action | VARCHAR(64) | retrieve / rerank / generate / abstain |
| input_data | JSONB | structured step input |
| output_data | JSONB | structured step output |
| latency_ms | INTEGER | |
| retrieval_score | NUMERIC(6,4) | for RETRIEVING steps |

### eval_runs / eval_cases / eval_results
See `backend/app/domain/eval.py` for full column definitions.

## Indexes Summary

| Table | Index | Type | Purpose |
|-------|-------|------|---------|
| documents | content_hash | BTREE | deduplication lookup |
| documents | status | BTREE | filter by indexing status |
| document_chunks | document_id | BTREE | chunk lookup by doc |
| document_chunks | (document_id, chunk_index) | BTREE | ordered chunk fetch |
| chunk_vectors | chunk_id | BTREE | unique FK lookup |
| chunk_vectors | embedding (HNSW) | HNSW | ANN cosine search |
| chat_sessions | user_id | BTREE | session lookup |
| chat_messages | session_id | BTREE | message history |
| agent_traces | session_id | BTREE | trace by session |
| agent_traces | request_id | BTREE | distributed trace lookup |
| agent_trace_steps | trace_id | BTREE | steps by trace |
| eval_results | run_id, case_id | BTREE | result lookup |

## Migration Strategy

- All schema changes via Alembic autogenerate + manual review
- Initial migration: `0001_initial_schema.py`
- Downgrade path implemented for all migrations
- Vector index created with raw SQL in migration (pgvector DDL not supported by autogenerate)
- `updated_at` column maintained via PostgreSQL trigger (not SQLAlchemy `onupdate`)
