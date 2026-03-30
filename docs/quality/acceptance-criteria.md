# Acceptance Criteria — Agentic RAG

## Step 1: Architecture, Directory, Schema, Interface Skeleton

### ✅ Directory Structure
- [ ] `backend/app/{api,core,db,schemas,domain,ingestion,indexing,retrieval,services,agent,evals,observability}/` created
- [ ] `frontend/src/{app,pages,components,features,api,lib,types}/` created
- [ ] `docs/architecture/`, `docs/quality/`, `evals/`, `scripts/` created
- [ ] `backend/alembic/versions/` created

### ✅ Core Interfaces (typing.Protocol)
- [ ] `DocumentIngestor`, `Chunker` in `ingestion/protocols.py`
- [ ] `Embedder`, `VectorIndex` in `indexing/protocols.py`
- [ ] `Retriever`, `Reranker` in `retrieval/protocols.py`
- [ ] `CitationAssembler`, `AnswerGenerator` in `services/protocols.py`
- [ ] `AgentPolicy`, `AgentState`, `AgentContext` in `agent/protocols.py`
- [ ] `EvaluationRunner`, `EvalMetrics` in `evals/protocols.py`

### ✅ Database Schema
- [ ] All 10 domain tables defined as SQLAlchemy ORM models
- [ ] pgvector `VECTOR(1536)` column on `chunk_vectors.embedding`
- [ ] HNSW index defined in Alembic migration
- [ ] `updated_at` trigger defined in migration
- [ ] All FK relationships with correct `ondelete` behaviour
- [ ] JSONB `meta` columns on all domain models

### ✅ Alembic Migration
- [ ] `0001_initial_schema.py` creates all tables
- [ ] `downgrade()` drops all tables in reverse dependency order
- [ ] pgvector extension enabled in migration

### ✅ API Routes (501 stubs)
- [ ] `POST /api/v1/documents` → 501
- [ ] `GET /api/v1/documents` → 501
- [ ] `POST /api/v1/documents/{id}/index` → 501
- [ ] `POST /api/v1/chat/query` → 501
- [ ] `GET /api/v1/chat/{id}/trace` → 501
- [ ] `GET /api/v1/health` → 200
- [ ] `GET /api/v1/ready` → 200
- [ ] `POST /api/v1/evals/run` → 501
- [ ] `GET /api/v1/evals/{id}` → 501

### ✅ Tests Pass
- [ ] `test_health_returns_ok` passes
- [ ] `test_ready_returns_200` passes
- [ ] `test_documents_returns_501` passes
- [ ] `test_chat_query_returns_501` passes
- [ ] `test_agent_state_values` passes
- [ ] `test_agent_context_defaults` passes

---

## Step 2: Ingestion, Chunking, Embedding Pipeline

### Acceptance Criteria
- [ ] `POST /documents` accepts PDF and plain text files
- [ ] `DocumentIngestor` deduplicates by content_hash
- [ ] `Chunker` produces correct chunk_index ordering
- [ ] `Embedder` calls embedding API with timeout and retry (max 3)
- [ ] `VectorIndex.upsert()` writes to `chunk_vectors` table
- [ ] `Document.status` transitions: `pending → processing → indexed / failed`
- [ ] All steps logged with `request_id` and `document_id`
- [ ] Unit tests for `Chunker` with at least 3 chunk scenarios
- [ ] Integration test: upload PDF → verify chunks in DB

---

## Step 3: Retrieval, Reranker, CitationAssembler

### Acceptance Criteria
- [ ] `VectorIndex.search()` uses HNSW ANN with cosine distance
- [ ] `Retriever.retrieve()` applies `score_threshold` filtering
- [ ] `Reranker.rerank()` does not reduce results below `min_keep`
- [ ] `CitationAssembler.assemble()` deduplicates same-source citations
- [ ] `GET /documents/{id}/index` triggers re-embedding correctly
- [ ] metadata filter (`dc.meta @> $filter`) tested with JSONB fixtures
- [ ] Retrieval latency < 200ms for 10k chunks (benchmark test)

---

## Step 4: Agent FSM, AnswerGenerator, Full RAG Pipeline

### Acceptance Criteria
- [ ] Agent never exceeds `MAX_AGENT_STEPS` (hard limit enforced in test)
- [ ] Agent sets `abstained=True` when no chunks exceed score threshold
- [ ] `AgentTraceStep` records written for every state transition
- [ ] `ChatMessage.citations` populated by `CitationAssembler`
- [ ] `POST /chat/query` returns `ChatQueryResponse` with non-empty `citations`
- [ ] `GET /traces/{id}` returns full `AgentTraceResponse` with steps
- [ ] No LLM call is made when `abstained=True`
- [ ] Integration test: end-to-end query over indexed document

---

## Step 5: Eval Framework

### Acceptance Criteria
- [ ] `EvaluationRunner` persists `EvalRun`, `EvalResult` for each case
- [ ] `faithfulness_score`, `answer_relevance_score`, `retrieval_precision`, `retrieval_recall` computed
- [ ] `EvalRun.status` transitions: `pending → running → completed / failed`
- [ ] Failed individual cases do not abort the run
- [ ] `POST /evals/run` returns 202 with `EvalRunResponse`
- [ ] `GET /evals/{id}` returns completed metrics
- [ ] At least 5 eval cases in `evals/cases/`
- [ ] Regression test: `pass_rate >= 0.8` on the basic test set

---

## Non-Functional Acceptance Criteria (All Steps)

| Criterion | Threshold |
|-----------|-----------|
| All API responses include `X-Request-ID` header | ✓ always |
| structlog JSON output includes `request_id`, `trace_id` | ✓ always |
| No hardcoded API keys in source code | ✓ always |
| No circular imports between modules | ✓ always |
| pytest coverage ≥ 80% for `app/` | ✓ from Step 2 |
| All external calls have timeout configured | ✓ from Step 2 |
| Alembic downgrade tested | ✓ from Step 1 |
