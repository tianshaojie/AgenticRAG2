import { describe, it, expect, vi, beforeEach } from 'vitest'
import axios from 'axios'

vi.mock('axios', () => {
  const instance = {
    get: vi.fn(),
    post: vi.fn(),
    delete: vi.fn(),
    interceptors: {
      response: { use: vi.fn() },
    },
    defaults: { headers: { common: {} } },
  }
  return {
    default: {
      create: vi.fn(() => instance),
      ...instance,
    },
  }
})

import { httpClient, unwrap } from '@/api/client'
import type { APIResponse } from '@/types/api'

describe('unwrap', () => {
  it('returns data when success=true', async () => {
    const payload: APIResponse<string> = {
      success: true,
      data: 'hello',
      error: null,
      request_id: null,
    }
    const result = await unwrap(
      Promise.resolve({ data: payload } as any),
    )
    expect(result).toBe('hello')
  })

  it('throws when success=false', async () => {
    const payload: APIResponse<string> = {
      success: false,
      data: null,
      error: 'Not found',
      request_id: null,
    }
    await expect(
      unwrap(Promise.resolve({ data: payload } as any)),
    ).rejects.toThrow('Not found')
  })

  it('throws when data is null even if success=true', async () => {
    const payload: APIResponse<null> = {
      success: true,
      data: null,
      error: null,
      request_id: null,
    }
    await expect(
      unwrap(Promise.resolve({ data: payload } as any)),
    ).rejects.toThrow()
  })
})
