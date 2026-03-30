/**
 * Step 1 smoke test: verify TypeScript types compile and are self-consistent.
 * No runtime logic — just type-level assertions.
 */

import { describe, expect, it } from 'vitest'
import type { AgentState, ChatQueryResponse, DocumentResponse } from '@/types/api'

describe('API types', () => {
  it('DocumentResponse has required fields', () => {
    const doc: DocumentResponse = {
      id: 'uuid',
      filename: 'test.pdf',
      content_type: 'application/pdf',
      content_hash: 'abc123',
      size_bytes: 1024,
      title: null,
      status: 'pending',
      meta: {},
      is_deleted: false,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    }
    expect(doc.status).toBe('pending')
  })

  it('AgentState enum values are correct strings', () => {
    const states: AgentState[] = [
      'IDLE', 'RETRIEVING', 'EVALUATING_EVIDENCE',
      'GENERATING', 'DONE', 'ABSTAINING', 'ERROR',
    ]
    expect(states).toHaveLength(7)
  })

  it('ChatQueryResponse has abstained flag', () => {
    const response: ChatQueryResponse = {
      session_id: 'uuid',
      message_id: 'uuid',
      answer: 'I cannot answer without evidence.',
      abstained: true,
      citations: [],
      agent_trace_id: null,
      latency_ms: 100,
    }
    expect(response.abstained).toBe(true)
  })
})
