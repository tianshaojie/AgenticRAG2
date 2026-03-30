/**
 * Document API — wraps /api/v1/documents endpoints.
 * Step 1: Stubs only. Full implementation in Step 2.
 */

import { httpClient, unwrap } from './client'
import type {
  APIResponse,
  DocumentIndexResponse,
  DocumentResponse,
  PaginatedResponse,
} from '@/types/api'

export const documentsApi = {
  list(page = 1, pageSize = 20) {
    return httpClient.get<PaginatedResponse<DocumentResponse>>('/documents', {
      params: { page, page_size: pageSize },
    })
  },

  get(id: string) {
    return unwrap(
      httpClient.get<APIResponse<DocumentResponse>>(`/documents/${id}`),
    )
  },

  upload(file: File, title?: string, meta?: Record<string, unknown>) {
    const form = new FormData()
    form.append('file', file)
    if (title) form.append('title', title)
    if (meta) form.append('meta', JSON.stringify(meta))
    return unwrap(
      httpClient.post<APIResponse<DocumentResponse>>('/documents', form, {
        headers: { 'Content-Type': 'multipart/form-data' },
      }),
    )
  },

  index(id: string, forceReindex = false) {
    return unwrap(
      httpClient.post<APIResponse<DocumentIndexResponse>>(
        `/documents/${id}/index`,
        { force_reindex: forceReindex },
      ),
    )
  },

  delete(id: string) {
    return httpClient.delete(`/documents/${id}`)
  },
}
