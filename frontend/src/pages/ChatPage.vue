<template>
  <div class="flex h-[calc(100vh-56px)]">
    <!-- Chat panel -->
    <div class="flex flex-1 flex-col min-w-0">
      <!-- Messages area -->
      <div ref="messagesEl" class="flex-1 overflow-y-auto p-6 space-y-4">
        <!-- Empty state -->
        <EmptyState
          v-if="messages.length === 0"
          title="Start a conversation"
          description="Upload and index a document first, then ask questions about it."
          icon="chat"
        />

        <template v-for="msg in messages" :key="msg.id">
          <!-- User bubble -->
          <div v-if="msg.role === 'user'" class="flex justify-end">
            <div class="max-w-[70%] rounded-2xl rounded-tr-sm bg-primary px-4 py-2.5 text-sm text-primary-foreground">
              {{ msg.query }}
            </div>
          </div>

          <!-- Assistant bubble -->
          <div v-else class="flex justify-start">
            <div class="max-w-[80%] space-y-2">
              <!-- Loading -->
              <div v-if="msg.loading" class="flex items-center gap-2 text-muted-foreground text-sm py-2">
                <div class="h-4 w-4 animate-spin rounded-full border-2 border-muted border-t-primary" />
                Thinking…
              </div>

              <!-- Error -->
              <ErrorState
                v-else-if="msg.error"
                title="Query failed"
                :message="msg.error"
              />

              <!-- Answer -->
              <AnswerCard v-else-if="msg.response" :response="msg.response" />
            </div>
          </div>
        </template>
      </div>

      <!-- Input bar -->
      <div class="border-t p-4 shrink-0">
        <ChatInput
          :disabled="loading"
          @submit="send"
        />
        <p v-if="messages.length > 0" class="text-xs text-muted-foreground mt-2 text-center">
          <button @click="clearHistory" class="hover:underline">Clear conversation</button>
        </p>
      </div>
    </div>

    <!-- Citation panel -->
    <aside class="w-80 border-l bg-muted/20 flex flex-col hidden xl:flex">
      <div class="px-4 pt-4 pb-2 border-b shrink-0">
        <h2 class="text-sm font-semibold">Citations</h2>
      </div>
      <div class="flex-1 overflow-y-auto p-4">
        <CitationList
          v-if="latestCitations.length > 0"
          :citations="latestCitations"
        />
        <p v-else class="text-xs text-muted-foreground">No citations yet.</p>
      </div>
    </aside>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, watch, nextTick } from 'vue'
import { useChat } from '@/composables/useChat'
import ChatInput from '@/components/ChatInput.vue'
import AnswerCard from '@/components/AnswerCard.vue'
import CitationList from '@/components/CitationList.vue'
import EmptyState from '@/components/EmptyState.vue'
import ErrorState from '@/components/ErrorState.vue'
import type { Citation } from '@/types/api'

const { messages, loading, send, clearHistory } = useChat()
const messagesEl = ref<HTMLElement>()

// Scroll to bottom on new messages
watch(
  () => messages.value.length,
  () => nextTick(() => {
    if (messagesEl.value) {
      messagesEl.value.scrollTop = messagesEl.value.scrollHeight
    }
  }),
)

// Show citations from last assistant response
const latestCitations = computed<Citation[]>(() => {
  for (let i = messages.value.length - 1; i >= 0; i--) {
    const msg = messages.value[i]
    if (msg.role === 'assistant' && msg.response?.citations?.length) {
      return msg.response.citations
    }
  }
  return []
})
</script>
