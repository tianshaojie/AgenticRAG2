<template>
  <div class="flex flex-col gap-6 p-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold tracking-tight">Documents</h1>
        <p class="text-sm text-muted-foreground">
          Upload, manage and index documents for retrieval.
        </p>
      </div>
      <!-- TODO(Step 2): Upload button -->
      <button
        class="inline-flex items-center gap-2 rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground opacity-50 cursor-not-allowed"
        disabled
      >
        Upload Document
      </button>
    </div>

    <!-- TODO(Step 2): Document list table -->
    <div class="rounded-lg border bg-card p-8 text-center text-muted-foreground">
      <p class="text-sm">Document management available in Step 2.</p>
    </div>
  </div>
</template>

<script setup lang="ts">
// TODO(Step 2): wire up documentsApi and useDocumentsStore
</script>
