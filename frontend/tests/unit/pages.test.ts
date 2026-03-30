import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { defineComponent, h } from 'vue'
import { createRouter, createMemoryHistory } from 'vue-router'

// ── Mock lucide icons ──────────────────────────────────────────────────
vi.mock('lucide-vue-next', () => {
  const stub = (name: string) => defineComponent({ name, render: () => h('span', name) })
  return {
    AlertCircle: stub('AlertCircle'),
    AlertTriangle: stub('AlertTriangle'),
    BookOpen: stub('BookOpen'),
    CheckCircle2: stub('CheckCircle2'),
    ChevronLeft: stub('ChevronLeft'),
    ChevronRight: stub('ChevronRight'),
    Clock: stub('Clock'),
    FileText: stub('FileText'),
    Inbox: stub('Inbox'),
    Loader2: stub('Loader2'),
    MessageCircle: stub('MessageCircle'),
    Plus: stub('Plus'),
    RefreshCw: stub('RefreshCw'),
    SendHorizontal: stub('SendHorizontal'),
    Settings: stub('Settings'),
    Upload: stub('Upload'),
    X: stub('X'),
  }
})

// ── Mock API modules ───────────────────────────────────────────────────
vi.mock('@/api/documents', () => ({
  documentsApi: {
    list: vi.fn(),
    upload: vi.fn(),
    index: vi.fn(),
    remove: vi.fn(),
    get: vi.fn(),
  },
}))

vi.mock('@/api/chat', () => ({
  chatApi: {
    query: vi.fn(),
  },
}))

vi.mock('@/api/health', () => ({
  healthApi: {
    health: vi.fn(),
    ready: vi.fn(),
  },
}))

import { documentsApi } from '@/api/documents'
import { chatApi } from '@/api/chat'
import { healthApi } from '@/api/health'
import type { DocumentResponse, ChatQueryResponse } from '@/types/api'

// ── DocumentsPage ──────────────────────────────────────────────────────
import DocumentsPage from '@/pages/DocumentsPage.vue'

const mockDoc: DocumentResponse = {
  id: 'doc-1',
  filename: 'test.txt',
  content_type: 'text/plain',
  content_hash: 'abc123',
  size_bytes: 1024,
  title: 'Test Document',
  status: 'indexed',
  meta: {},
  is_deleted: false,
  created_at: '2024-01-01T00:00:00Z',
  updated_at: '2024-01-01T00:00:00Z',
}

const emptyList = { items: [], total: 0, page: 1, page_size: 20, has_next: false }
const singleList = { items: [mockDoc], total: 1, page: 1, page_size: 20, has_next: false }

describe('DocumentsPage', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('shows empty state when no documents', async () => {
    vi.mocked(documentsApi.list).mockResolvedValue(emptyList)
    const wrapper = mount(DocumentsPage)
    await flushPromises()
    expect(wrapper.text()).toContain('No documents yet')
  })

  it('shows document table when documents exist', async () => {
    vi.mocked(documentsApi.list).mockResolvedValue(singleList)
    const wrapper = mount(DocumentsPage)
    await flushPromises()
    expect(wrapper.text()).toContain('Test Document')
  })

  it('shows upload form when Upload button clicked', async () => {
    vi.mocked(documentsApi.list).mockResolvedValue(emptyList)
    const wrapper = mount(DocumentsPage)
    await flushPromises()

    await wrapper.find('button').trigger('click')
    expect(wrapper.text()).toContain('Upload Document')
  })

  it('shows error state on API failure', async () => {
    vi.mocked(documentsApi.list).mockRejectedValue(new Error('Network error'))
    const wrapper = mount(DocumentsPage)
    await flushPromises()
    expect(wrapper.text()).toContain('Something went wrong')
  })
})

// ── ChatPage ───────────────────────────────────────────────────────────
import ChatPage from '@/pages/ChatPage.vue'

const normalResponse: ChatQueryResponse = {
  session_id: 's1',
  message_id: 'm1',
  answer: 'The capital of France is Paris.',
  abstained: false,
  citations: [
    {
      chunk_id: 'c1',
      document_id: 'd1',
      document_title: 'Geography',
      chunk_index: 0,
      page_number: 1,
      section_title: null,
      content_snippet: 'France is a country in Western Europe.',
      score: 0.91,
    },
  ],
  agent_trace_id: null,
  latency_ms: 150,
}

const abstainResponse: ChatQueryResponse = {
  ...normalResponse,
  abstained: true,
  answer: 'I cannot answer based on available documents.',
  citations: [],
}

describe('ChatPage', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('shows empty state initially', () => {
    const wrapper = mount(ChatPage)
    expect(wrapper.text()).toContain('Start a conversation')
  })

  it('renders user message after submit', async () => {
    vi.mocked(chatApi.query).mockResolvedValue(normalResponse)
    const wrapper = mount(ChatPage)

    const textarea = wrapper.find('textarea')
    await textarea.setValue('What is Paris?')
    await wrapper.find('form').trigger('submit')
    await flushPromises()

    expect(wrapper.text()).toContain('What is Paris?')
  })

  it('renders assistant answer after query', async () => {
    vi.mocked(chatApi.query).mockResolvedValue(normalResponse)
    const wrapper = mount(ChatPage)

    const textarea = wrapper.find('textarea')
    await textarea.setValue('What is Paris?')
    await wrapper.find('form').trigger('submit')
    await flushPromises()

    expect(wrapper.text()).toContain('The capital of France is Paris.')
  })

  it('renders abstain banner when answer is abstained', async () => {
    vi.mocked(chatApi.query).mockResolvedValue(abstainResponse)
    const wrapper = mount(ChatPage)

    const textarea = wrapper.find('textarea')
    await textarea.setValue('Random question')
    await wrapper.find('form').trigger('submit')
    await flushPromises()

    expect(wrapper.text()).toContain('Insufficient evidence')
  })

  it('shows error message on query failure', async () => {
    vi.mocked(chatApi.query).mockRejectedValue(new Error('Backend unavailable'))
    const wrapper = mount(ChatPage)

    const textarea = wrapper.find('textarea')
    await textarea.setValue('Test question')
    await wrapper.find('form').trigger('submit')
    await flushPromises()

    expect(wrapper.text()).toContain('Query failed')
  })
})
