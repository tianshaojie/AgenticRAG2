<template>
  <div class="rounded-lg border bg-card overflow-hidden">
    <table class="w-full text-sm">
      <thead class="border-b bg-muted/50">
        <tr>
          <th class="text-left px-4 py-3 font-medium text-muted-foreground">Name</th>
          <th class="text-left px-4 py-3 font-medium text-muted-foreground w-28">Status</th>
          <th class="text-left px-4 py-3 font-medium text-muted-foreground w-24 hidden sm:table-cell">Size</th>
          <th class="text-left px-4 py-3 font-medium text-muted-foreground w-36 hidden md:table-cell">Uploaded</th>
          <th class="px-4 py-3 w-32" />
        </tr>
      </thead>
      <tbody class="divide-y">
        <tr
          v-for="doc in items"
          :key="doc.id"
          class="hover:bg-muted/30 transition-colors"
        >
          <!-- Name -->
          <td class="px-4 py-3">
            <div class="flex items-center gap-2">
              <FileText class="h-4 w-4 text-muted-foreground shrink-0" />
              <div class="min-w-0">
                <p class="font-medium truncate max-w-[200px]">{{ doc.title || doc.filename }}</p>
                <p v-if="doc.title" class="text-xs text-muted-foreground truncate max-w-[200px]">{{ doc.filename }}</p>
              </div>
            </div>
          </td>

          <!-- Status badge -->
          <td class="px-4 py-3">
            <span :class="statusClass(doc.status)" class="inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-xs font-medium">
              <Loader2 v-if="doc.status === 'processing' || indexingIds.has(doc.id)" class="h-3 w-3 animate-spin" />
              <CheckCircle2 v-else-if="doc.status === 'indexed'" class="h-3 w-3" />
              <AlertCircle v-else-if="doc.status === 'failed'" class="h-3 w-3" />
              <Clock v-else class="h-3 w-3" />
              {{ indexingIds.has(doc.id) ? 'indexing…' : doc.status }}
            </span>
          </td>

          <!-- Size -->
          <td class="px-4 py-3 text-muted-foreground hidden sm:table-cell">
            {{ formatSize(doc.size_bytes) }}
          </td>

          <!-- Date -->
          <td class="px-4 py-3 text-muted-foreground hidden md:table-cell">
            {{ formatDate(doc.created_at) }}
          </td>

          <!-- Actions -->
          <td class="px-4 py-3">
            <div class="flex items-center justify-end gap-2">
              <button
                v-if="doc.status !== 'indexed'"
                @click="$emit('index', doc.id)"
                :disabled="indexingIds.has(doc.id) || doc.status === 'processing'"
                class="text-xs text-primary hover:underline disabled:opacity-40 disabled:cursor-not-allowed"
              >
                Index
              </button>
              <button
                v-else
                @click="$emit('index', doc.id)"
                :disabled="indexingIds.has(doc.id)"
                class="text-xs text-muted-foreground hover:text-foreground hover:underline disabled:opacity-40"
              >
                Re-index
              </button>
              <button
                @click="$emit('remove', doc.id)"
                class="text-xs text-destructive hover:underline"
              >
                Delete
              </button>
            </div>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup lang="ts">
import { FileText, Loader2, CheckCircle2, AlertCircle, Clock } from 'lucide-vue-next'
import type { DocumentResponse, DocumentStatus } from '@/types/api'

defineProps<{
  items: DocumentResponse[]
  indexingIds: Set<string>
}>()

defineEmits<{
  index: [id: string]
  remove: [id: string]
}>()

function statusClass(status: DocumentStatus) {
  const map: Record<DocumentStatus, string> = {
    pending: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400',
    processing: 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400',
    indexed: 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400',
    failed: 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400',
  }
  return map[status] ?? 'bg-muted text-muted-foreground'
}

function formatSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}

function formatDate(iso: string): string {
  return new Date(iso).toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' })
}
</script>
