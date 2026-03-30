<template>
  <div class="flex h-full">
    <!-- Chat panel -->
    <div class="flex flex-1 flex-col">
      <!-- Messages area -->
      <div class="flex-1 overflow-y-auto p-6 space-y-4">
        <!-- TODO(Step 4): render ChatMessage components -->
        <div class="rounded-lg border bg-card p-8 text-center text-muted-foreground">
          <p class="text-sm">Chat agent available in Step 4.</p>
        </div>
      </div>

      <!-- Input bar -->
      <div class="border-t p-4">
        <div class="flex gap-2">
          <input
            type="text"
            placeholder="Ask a question… (Step 4)"
            disabled
            class="flex-1 rounded-md border bg-background px-3 py-2 text-sm opacity-50 cursor-not-allowed"
          />
          <button
            disabled
            class="rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground opacity-50 cursor-not-allowed"
          >
            Send
          </button>
        </div>
      </div>
    </div>

    <!-- Evidence / Citation panel (Step 3+) -->
    <aside class="w-80 border-l bg-muted/30 p-4 hidden xl:block">
      <h2 class="text-sm font-semibold mb-3">Citations</h2>
      <!-- TODO(Step 3): CitationPanel component -->
      <p class="text-xs text-muted-foreground">No citations yet.</p>
    </aside>
  </div>
</template>

<script setup lang="ts">
// TODO(Step 4): wire up chatApi and useChatStore
</script>
