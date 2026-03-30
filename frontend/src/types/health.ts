export interface HealthResponse {
  status: string
  version: string
  environment: string
}

export interface ReadyResponse {
  ready: boolean
  checks: Record<string, boolean>
}
