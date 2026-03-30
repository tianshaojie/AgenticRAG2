<template>
  <div
    :class="[
      'rounded-lg border p-4 text-sm',
      response.abstained
        ? 'border-yellow-300 bg-yellow-50 dark:border-yellow-800 dark:bg-yellow-950/30'
        : 'border-border bg-card',
    ]"
  >
    <!-- Abstain banner -->
    <div v-if="response.abstained" class="flex items-center gap-2 mb-3">
      <AlertTriangle class="h-4 w-4 text-yellow-600 dark:text-yellow-400 shrink-0" />
      <span class="text-xs font-semibold text-yellow-700 dark:text-yellow-400 uppercase tracking-wide">
        Insufficient evidence — answer withheld
      </span>
    </div>

    <!-- Answer text -->
    <p class="leading-relaxed whitespace-pre-wrap text-foreground">{{ response.answer }}</p>

    <!-- Meta row -->
    <div class="flex items-center gap-3 mt-3 text-xs text-muted-foreground border-t pt-3">
      <span class="flex items-center gap-1">
        <BookOpen class="h-3 w-3" />
        {{ response.citations.length }} citation{{ response.citations.length !== 1 ? 's' : '' }}
      </span>
      <span class="flex items-center gap-1">
        <Clock class="h-3 w-3" />
        {{ response.latency_ms }}ms
      </span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { AlertTriangle, BookOpen, Clock } from 'lucide-vue-next'
import type { ChatQueryResponse } from '@/types/api'

defineProps<{ response: ChatQueryResponse }>()
</script>
