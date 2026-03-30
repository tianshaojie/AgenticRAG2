<template>
  <div class="flex flex-col gap-6 p-6 max-w-2xl">
    <div>
      <h1 class="text-2xl font-bold tracking-tight">Settings</h1>
      <p class="text-sm text-muted-foreground">System health and API configuration.</p>
    </div>

    <!-- Health card -->
    <section class="rounded-lg border bg-card divide-y">
      <div class="px-5 py-4 flex items-center justify-between">
        <h2 class="text-sm font-semibold">System Status</h2>
        <button
          @click="fetchStatus"
          :disabled="loading"
          class="text-xs text-muted-foreground hover:text-foreground transition-colors disabled:opacity-40"
        >
          <RefreshCw :class="['h-3.5 w-3.5', loading ? 'animate-spin' : '']" />
        </button>
      </div>

      <div v-if="error" class="px-5 py-3">
        <ErrorState title="Cannot reach backend" :message="error" :on-retry="fetchStatus" />
      </div>

      <template v-else>
        <div class="px-5 py-3 flex items-center justify-between text-sm">
          <span class="text-muted-foreground">API</span>
          <span :class="health?.status === 'ok' ? 'text-green-600' : 'text-red-500'" class="font-medium">
            {{ loading ? 'checking…' : (health?.status ?? 'unreachable') }}
          </span>
        </div>
        <div class="px-5 py-3 flex items-center justify-between text-sm">
          <span class="text-muted-foreground">Version</span>
          <span class="font-mono text-xs">{{ health?.version ?? '—' }}</span>
        </div>
        <div class="px-5 py-3 flex items-center justify-between text-sm">
          <span class="text-muted-foreground">Environment</span>
          <span class="font-mono text-xs">{{ health?.environment ?? '—' }}</span>
        </div>
        <div class="px-5 py-3 flex items-center justify-between text-sm">
          <span class="text-muted-foreground">Database</span>
          <span :class="ready?.checks?.database ? 'text-green-600' : 'text-red-500'" class="font-medium">
            {{ loading ? '…' : (ready?.checks?.database ? 'connected' : 'unavailable') }}
          </span>
        </div>
        <div class="px-5 py-3 flex items-center justify-between text-sm">
          <span class="text-muted-foreground">pgvector</span>
          <span :class="ready?.checks?.pgvector ? 'text-green-600' : 'text-red-500'" class="font-medium">
            {{ loading ? '…' : (ready?.checks?.pgvector ? 'enabled' : 'unavailable') }}
          </span>
        </div>
      </template>
    </section>

    <!-- API config -->
    <section class="rounded-lg border bg-card divide-y">
      <div class="px-5 py-4">
        <h2 class="text-sm font-semibold">API Configuration</h2>
      </div>
      <div class="px-5 py-3 flex items-center justify-between text-sm">
        <span class="text-muted-foreground">Base URL</span>
        <span class="font-mono text-xs text-muted-foreground">{{ baseUrl }}</span>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { RefreshCw } from 'lucide-vue-next'
import { useHealth } from '@/composables/useHealth'
import ErrorState from '@/components/ErrorState.vue'

const { health, ready, loading, error, fetchStatus } = useHealth(true)
const baseUrl = computed(() => import.meta.env.VITE_API_BASE_URL ?? '/api/v1')
</script>
