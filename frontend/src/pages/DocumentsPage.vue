<template>
  <div class="flex flex-col gap-6 p-6">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold tracking-tight">Documents</h1>
        <p class="text-sm text-muted-foreground">
          Upload, manage and index documents for retrieval.
        </p>
      </div>
      <button
        @click="showUpload = !showUpload"
        class="inline-flex items-center gap-2 rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90 transition-colors"
      >
        <Plus class="h-4 w-4" />
        Upload
      </button>
    </div>

    <!-- Upload form (toggle) -->
    <DocumentUploadForm
      v-if="showUpload"
      :uploading="uploadInProgress"
      @uploaded="onUploaded"
    />

    <!-- Error -->
    <ErrorState
      v-if="error"
      title="Something went wrong"
      :message="error"
      :on-retry="fetchList"
    />

    <!-- Loading -->
    <LoadingState v-else-if="loading && items.length === 0" message="Loading documents…" />

    <!-- Empty -->
    <EmptyState
      v-else-if="!loading && items.length === 0"
      title="No documents yet"
      description="Upload a .txt or .md file to get started."
      icon="file"
    >
      <button
        @click="showUpload = true"
        class="mt-4 text-sm text-primary underline hover:no-underline"
      >
        Upload your first document
      </button>
    </EmptyState>

    <!-- Table -->
    <template v-else>
      <DocumentTable
        :items="items"
        :indexing-ids="indexingIds"
        @index="triggerIndex"
        @remove="remove"
      />

      <!-- Pagination -->
      <div v-if="total > pageSize" class="flex items-center justify-between text-sm text-muted-foreground">
        <span>{{ total }} documents total</span>
        <div class="flex gap-2">
          <button
            @click="prevPage"
            :disabled="page <= 1"
            class="rounded-md border px-3 py-1.5 text-xs hover:bg-muted disabled:opacity-40 disabled:cursor-not-allowed"
          >
            Previous
          </button>
          <span class="flex items-center px-2">Page {{ page }}</span>
          <button
            @click="nextPage"
            :disabled="!hasNext"
            class="rounded-md border px-3 py-1.5 text-xs hover:bg-muted disabled:opacity-40 disabled:cursor-not-allowed"
          >
            Next
          </button>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Plus } from 'lucide-vue-next'
import { useDocuments } from '@/composables/useDocuments'
import DocumentUploadForm from '@/components/DocumentUploadForm.vue'
import DocumentTable from '@/components/DocumentTable.vue'
import EmptyState from '@/components/EmptyState.vue'
import ErrorState from '@/components/ErrorState.vue'
import LoadingState from '@/components/LoadingState.vue'

const {
  items, total, page, pageSize, loading, error, indexingIds,
  hasNext, fetchList, upload, triggerIndex, remove, nextPage, prevPage,
} = useDocuments()

const showUpload = ref(false)
const uploadInProgress = ref(false)

onMounted(fetchList)

async function onUploaded(file: File, title?: string) {
  uploadInProgress.value = true
  const doc = await upload(file, title)
  uploadInProgress.value = false
  if (doc) {
    showUpload.value = false
    // auto-trigger indexing after upload
    await triggerIndex(doc.id)
  }
}
</script>
