<template>
  <div class="flex flex-col gap-6 p-6">
    <div>
      <h1 class="text-2xl font-bold tracking-tight">Agent Trace</h1>
      <p class="text-sm text-muted-foreground">
        Inspect step-by-step agent reasoning and state transitions.
      </p>
    </div>

    <!-- TODO(Step 4): AgentTraceViewer component -->
    <div class="rounded-lg border bg-card p-8 text-center text-muted-foreground">
      <p class="text-sm">Agent trace viewer available in Step 4.</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRoute } from 'vue-router'

const route = useRoute()
// TODO(Step 4): fetch trace by route.params.traceId via chatApi.getTrace()
const _traceId = route.params.traceId
</script>
