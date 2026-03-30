import { httpClient } from './client'
import type { HealthResponse, ReadyResponse } from '@/types/health'

export const healthApi = {
  health() {
    return httpClient.get<HealthResponse>('/health')
  },
  ready() {
    return httpClient.get<ReadyResponse>('/ready')
  },
}
