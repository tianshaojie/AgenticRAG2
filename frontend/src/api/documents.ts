import { httpClient, unwrap } from './client'
import type {
  APIResponse,
  DocumentIndexResponse,
  DocumentResponse,
  PaginatedResponse,
} from '@/types/api'

export const documentsApi = {
  async list(page = 1, pageSize = 20): Promise<PaginatedResponse<DocumentResponse>> {
    const response = await httpClient.get<PaginatedResponse<DocumentResponse>>('/documents', {
      params: { page, page_size: pageSize },
    })
    return response.data
  },

  get(id: string) {
    return unwrap(httpClient.get<APIResponse<DocumentResponse>>(`/documents/${id}`))
  },

  upload(file: File, title?: string) {
    const form = new FormData()
    form.append('file', file)
    if (title) form.append('title', title)
    return unwrap(
      httpClient.post<APIResponse<DocumentResponse>>('/documents', form, {
        headers: { 'Content-Type': 'multipart/form-data' },
      }),
    )
  },

  index(id: string, forceReindex = false) {
    return unwrap(
      httpClient.post<APIResponse<DocumentIndexResponse>>(`/documents/${id}/index`, {
        force_reindex: forceReindex,
      }),
    )
  },

  remove(id: string) {
    return httpClient.delete(`/documents/${id}`)
  },
}
