import { ref } from 'vue'
import { chatApi } from '@/api/chat'
import type { ChatQueryResponse } from '@/types/api'

export interface ChatMessage {
  id: string
  role: 'user' | 'assistant'
  query?: string
  response?: ChatQueryResponse
  loading?: boolean
  error?: string
  timestamp: number
}

export function useChat() {
  const messages = ref<ChatMessage[]>([])
  const loading = ref(false)
  const sessionId = ref<string | undefined>(undefined)

  async function send(query: string): Promise<void> {
    if (!query.trim()) return

    const userMsg: ChatMessage = {
      id: crypto.randomUUID(),
      role: 'user',
      query,
      timestamp: Date.now(),
    }
    const assistantMsg: ChatMessage = {
      id: crypto.randomUUID(),
      role: 'assistant',
      loading: true,
      timestamp: Date.now(),
    }

    messages.value.push(userMsg, assistantMsg)
    loading.value = true

    try {
      const result = await chatApi.query({
        query,
        session_id: sessionId.value,
      })
      sessionId.value = result.session_id
      assistantMsg.response = result
      assistantMsg.loading = false
    } catch (e: unknown) {
      assistantMsg.error = e instanceof Error ? e.message : 'Query failed'
      assistantMsg.loading = false
    } finally {
      loading.value = false
    }
  }

  function clearHistory() {
    messages.value = []
    sessionId.value = undefined
  }

  return { messages, loading, sessionId, send, clearHistory }
}
