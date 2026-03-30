<template>
  <div class="flex flex-col gap-2">
    <h3 class="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
      Citations ({{ citations.length }})
    </h3>
    <div
      v-for="(c, i) in citations"
      :key="c.chunk_id"
      class="rounded-md border bg-card p-3 text-xs"
    >
      <div class="flex items-start justify-between gap-2 mb-1">
        <span class="font-medium text-foreground truncate">
          [{{ i + 1 }}] {{ c.document_title || 'Untitled' }}
        </span>
        <span class="shrink-0 rounded-full bg-muted px-1.5 py-0.5 text-muted-foreground font-mono">
          {{ (c.score * 100).toFixed(0) }}%
        </span>
      </div>
      <p class="text-muted-foreground leading-relaxed line-clamp-3">{{ c.content_snippet }}</p>
      <div class="flex items-center gap-2 mt-1.5 text-muted-foreground/70">
        <span v-if="c.page_number">p.{{ c.page_number }}</span>
        <span v-if="c.section_title" class="truncate">{{ c.section_title }}</span>
        <span class="ml-auto">chunk #{{ c.chunk_index }}</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { Citation } from '@/types/api'
defineProps<{ citations: Citation[] }>()
</script>
