import { ref, onMounted } from 'vue'
import { healthApi } from '@/api/health'
import type { HealthResponse, ReadyResponse } from '@/types/health'

export function useHealth(autoFetch = true) {
  const health = ref<HealthResponse | null>(null)
  const ready = ref<ReadyResponse | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  async function fetchStatus() {
    loading.value = true
    error.value = null
    try {
      const [h, r] = await Promise.all([healthApi.health(), healthApi.ready()])
      health.value = h.data
      ready.value = r.data
    } catch (e: unknown) {
      error.value = e instanceof Error ? e.message : 'Health check failed'
    } finally {
      loading.value = false
    }
  }

  if (autoFetch) onMounted(fetchStatus)

  return { health, ready, loading, error, fetchStatus }
}
