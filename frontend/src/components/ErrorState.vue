<template>
  <div class="rounded-lg border border-destructive/30 bg-destructive/5 p-4 flex items-start gap-3">
    <AlertCircle class="h-4 w-4 text-destructive mt-0.5 shrink-0" />
    <div class="flex-1 min-w-0">
      <p class="text-sm font-medium text-destructive">{{ title }}</p>
      <p v-if="message" class="text-xs text-muted-foreground mt-1">{{ message }}</p>
    </div>
    <button v-if="onRetry" @click="onRetry" class="text-xs text-destructive underline hover:no-underline shrink-0">
      Retry
    </button>
  </div>
</template>

<script setup lang="ts">
import { AlertCircle } from 'lucide-vue-next'

defineProps<{
  title?: string
  message?: string
  onRetry?: () => void
}>()
</script>
