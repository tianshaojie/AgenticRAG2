/**
 * TypeScript types mirroring the backend OpenAPI schema.
 * Generated from FastAPI OpenAPI spec — keep in sync with backend/app/schemas/.
 */

// ── Common ────────────────────────────────────────────────────────────

export interface APIResponse<T> {
  success: boolean
  data: T | null
  error: string | null
  request_id: string | null
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  page_size: number
  has_next: boolean
}

// ── Documents ─────────────────────────────────────────────────────────

export type DocumentStatus = 'pending' | 'processing' | 'indexed' | 'failed'

export interface DocumentResponse {
  id: string
  filename: string
  content_type: string
  content_hash: string
  size_bytes: number
  title: string | null
  status: DocumentStatus
  meta: Record<string, unknown>
  is_deleted: boolean
  created_at: string
  updated_at: string
}

export interface DocumentIndexResponse {
  document_id: string
  status: string
  message: string
}

// ── Chat ──────────────────────────────────────────────────────────────

export interface Citation {
  chunk_id: string
  document_id: string
  document_title: string | null
  chunk_index: number
  page_number: number | null
  section_title: string | null
  content_snippet: string
  score: number
}

export interface ChatQueryRequest {
  session_id?: string
  query: string
  meta?: Record<string, unknown>
}

export interface ChatQueryResponse {
  session_id: string
  message_id: string
  answer: string
  abstained: boolean
  citations: Citation[]
  agent_trace_id: string | null
  latency_ms: number
}

// ── Agent Traces ──────────────────────────────────────────────────────

export type AgentState =
  | 'IDLE'
  | 'RETRIEVING'
  | 'EVALUATING_EVIDENCE'
  | 'GENERATING'
  | 'DONE'
  | 'ABSTAINING'
  | 'ERROR'

export interface AgentTraceStep {
  step_index: number
  state_from: AgentState
  state_to: AgentState
  action: string
  input_data: Record<string, unknown>
  output_data: Record<string, unknown>
  latency_ms: number | null
  retrieval_score: number | null
}

export interface AgentTraceResponse {
  id: string
  session_id: string | null
  query: string
  final_state: AgentState
  total_steps: number
  abstained: boolean
  latency_ms: number | null
  steps: AgentTraceStep[]
  created_at: string
  updated_at: string
}

// ── Evals ─────────────────────────────────────────────────────────────

export type EvalRunStatus = 'pending' | 'running' | 'completed' | 'failed'

export interface EvalResultResponse {
  case_id: string
  generated_answer: string | null
  retrieved_chunk_ids: string[]
  faithfulness_score: number | null
  answer_relevance_score: number | null
  retrieval_precision: number | null
  retrieval_recall: number | null
  passed: boolean
  abstained: boolean
  latency_ms: number | null
  error_message: string | null
}

export interface EvalRunResponse {
  id: string
  name: string
  description: string | null
  status: EvalRunStatus
  metrics: Record<string, number | null>
  total_cases: number
  passed_cases: number
  results: EvalResultResponse[]
  created_at: string
  updated_at: string
}
