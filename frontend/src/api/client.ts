/**
 * Axios HTTP client with base URL, request ID injection, and error handling.
 */

import axios, { type AxiosInstance, type AxiosResponse } from 'axios'
import type { APIResponse } from '@/types/api'

const BASE_URL = import.meta.env.VITE_API_BASE_URL ?? '/api/v1'

export const httpClient: AxiosInstance = axios.create({
  baseURL: BASE_URL,
  timeout: 30_000,
  headers: {
    'Content-Type': 'application/json',
  },
})

httpClient.interceptors.response.use(
  (response: AxiosResponse) => response,
  (error) => {
    const message =
      error.response?.data?.detail ??
      error.response?.data?.error ??
      error.message ??
      'Unknown error'
    return Promise.reject(new Error(message))
  },
)

export async function unwrap<T>(
  promise: Promise<AxiosResponse<APIResponse<T>>>,
): Promise<T> {
  const response = await promise
  const body = response.data
  if (!body.success || body.data === null || body.data === undefined) {
    throw new Error(body.error ?? 'API returned no data')
  }
  return body.data
}
