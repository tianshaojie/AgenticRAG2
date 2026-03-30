<template>
  <div class="flex flex-col gap-6 p-6">
    <div>
      <h1 class="text-2xl font-bold tracking-tight">Settings</h1>
      <p class="text-sm text-muted-foreground">
        System health, configuration and API status.
      </p>
    </div>

    <!-- Health status -->
    <section class="rounded-lg border bg-card p-6">
      <h2 class="text-sm font-semibold mb-4">System Health</h2>
      <div class="flex flex-col gap-2 text-sm">
        <div class="flex items-center justify-between">
          <span class="text-muted-foreground">Backend API</span>
          <span
            :class="health ? 'text-green-600' : 'text-red-500'"
          >
            {{ health ? health.status : 'checking…' }}
          </span>
        </div>
        <div class="flex items-center justify-between">
          <span class="text-muted-foreground">Version</span>
          <span>{{ health?.version ?? '—' }}</span>
        </div>
        <div class="flex items-center justify-between">
          <span class="text-muted-foreground">Environment</span>
          <span>{{ health?.environment ?? '—' }}</span>
        </div>
        <div class="flex items-center justify-between">
          <span class="text-muted-foreground">Database</span>
          <span :class="ready?.checks?.database ? 'text-green-600' : 'text-red-500'">
            {{ ready?.checks?.database ? 'connected' : 'unavailable' }}
          </span>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { httpClient } from '@/api/client'
import type { HealthResponse, ReadyResponse } from '@/types/health'

const health = ref<HealthResponse | null>(null)
const ready = ref<ReadyResponse | null>(null)

onMounted(async () => {
  try {
    const [h, r] = await Promise.all([
      httpClient.get<HealthResponse>('/health'),
      httpClient.get<ReadyResponse>('/ready'),
    ])
    health.value = h.data
    ready.value = r.data
  } catch {
    // ignore — UI shows "unavailable"
  }
})
</script>
