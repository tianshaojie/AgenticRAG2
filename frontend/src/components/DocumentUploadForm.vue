<template>
  <div class="rounded-lg border bg-card p-4">
    <h3 class="text-sm font-semibold mb-3">Upload Document</h3>
    <form @submit.prevent="handleSubmit" class="flex flex-col gap-3">
      <!-- File drop zone -->
      <label
        :class="[
          'flex flex-col items-center justify-center rounded-md border-2 border-dashed px-4 py-6 cursor-pointer transition-colors',
          isDragging ? 'border-primary bg-primary/5' : 'border-border hover:border-primary/50',
        ]"
        @dragover.prevent="isDragging = true"
        @dragleave="isDragging = false"
        @drop.prevent="onDrop"
      >
        <Upload class="h-6 w-6 text-muted-foreground mb-2" />
        <span class="text-sm text-muted-foreground text-center">
          <span class="font-medium text-foreground">Click to upload</span> or drag & drop
        </span>
        <span class="text-xs text-muted-foreground mt-1">.txt or .md files</span>
        <input
          ref="fileInput"
          type="file"
          accept=".txt,.md,text/plain,text/markdown"
          class="sr-only"
          @change="onFileChange"
        />
      </label>

      <!-- Selected file -->
      <div v-if="selectedFile" class="flex items-center gap-2 rounded-md bg-muted px-3 py-2 text-sm">
        <FileText class="h-4 w-4 text-muted-foreground shrink-0" />
        <span class="flex-1 truncate">{{ selectedFile.name }}</span>
        <span class="text-xs text-muted-foreground">{{ formatSize(selectedFile.size) }}</span>
        <button type="button" @click="clearFile" class="text-muted-foreground hover:text-foreground">
          <X class="h-4 w-4" />
        </button>
      </div>

      <!-- Optional title -->
      <input
        v-model="title"
        type="text"
        placeholder="Document title (optional)"
        class="w-full rounded-md border bg-background px-3 py-2 text-sm placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring"
      />

      <!-- Submit -->
      <button
        type="submit"
        :disabled="!selectedFile || uploading"
        :class="[
          'inline-flex items-center justify-center gap-2 rounded-md px-4 py-2 text-sm font-medium transition-colors',
          !selectedFile || uploading
            ? 'bg-muted text-muted-foreground cursor-not-allowed'
            : 'bg-primary text-primary-foreground hover:bg-primary/90',
        ]"
      >
        <Loader2 v-if="uploading" class="h-4 w-4 animate-spin" />
        {{ uploading ? 'Uploading…' : 'Upload' }}
      </button>
    </form>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { Upload, FileText, X, Loader2 } from 'lucide-vue-next'

const emit = defineEmits<{
  uploaded: [file: File, title?: string]
}>()

const props = defineProps<{ uploading?: boolean }>()

const fileInput = ref<HTMLInputElement>()
const selectedFile = ref<File | null>(null)
const title = ref('')
const isDragging = ref(false)

function onFileChange(e: Event) {
  const input = e.target as HTMLInputElement
  if (input.files?.[0]) selectedFile.value = input.files[0]
}

function onDrop(e: DragEvent) {
  isDragging.value = false
  const file = e.dataTransfer?.files[0]
  if (file) selectedFile.value = file
}

function clearFile() {
  selectedFile.value = null
  title.value = ''
  if (fileInput.value) fileInput.value.value = ''
}

function handleSubmit() {
  if (!selectedFile.value || props.uploading) return
  emit('uploaded', selectedFile.value, title.value || undefined)
  clearFile()
}

function formatSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}
</script>
