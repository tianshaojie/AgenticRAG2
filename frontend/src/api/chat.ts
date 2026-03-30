/**
 * Chat API — wraps /api/v1/chat endpoints.
 * Step 1: Stubs only. Full implementation in Step 4.
 */

import { httpClient, unwrap } from './client'
import type {
  APIResponse,
  AgentTraceResponse,
  ChatQueryRequest,
  ChatQueryResponse,
} from '@/types/api'

export const chatApi = {
  query(request: ChatQueryRequest) {
    return unwrap(
      httpClient.post<APIResponse<ChatQueryResponse>>('/chat/query', request),
    )
  },

  getTrace(traceId: string) {
    return unwrap(
      httpClient.get<APIResponse<AgentTraceResponse>>(`/traces/${traceId}`),
    )
  },

  getSessionTrace(sessionId: string) {
    return unwrap(
      httpClient.get<APIResponse<AgentTraceResponse>>(
        `/chat/${sessionId}/trace`,
      ),
    )
  },
}
