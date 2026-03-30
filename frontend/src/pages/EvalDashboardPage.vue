<template>
  <div class="flex flex-col gap-6 p-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold tracking-tight">Evaluations</h1>
        <p class="text-sm text-muted-foreground">
          Run and monitor RAG quality evaluations.
        </p>
      </div>
      <!-- TODO(Step 5): Run Eval button -->
      <button
        disabled
        class="inline-flex items-center gap-2 rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground opacity-50 cursor-not-allowed"
      >
        Run Evaluation
      </button>
    </div>

    <!-- TODO(Step 5): Metrics summary cards -->
    <div class="grid grid-cols-2 gap-4 sm:grid-cols-4">
      <div
        v-for="metric in ['Faithfulness', 'Answer Relevance', 'Retrieval Recall', 'Pass Rate']"
        :key="metric"
        class="rounded-lg border bg-card p-4"
      >
        <p class="text-xs text-muted-foreground">{{ metric }}</p>
        <p class="mt-1 text-2xl font-bold text-muted-foreground/40">—</p>
      </div>
    </div>

    <!-- TODO(Step 5): EvalRun list table -->
    <div class="rounded-lg border bg-card p-8 text-center text-muted-foreground">
      <p class="text-sm">Eval dashboard available in Step 5.</p>
    </div>
  </div>
</template>

<script setup lang="ts">
// TODO(Step 5): wire up evalsApi and useEvalsStore
</script>
