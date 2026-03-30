import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { defineComponent, h } from 'vue'

// ── Stub lucide icons globally ────────────────────────────────────────
vi.mock('lucide-vue-next', () => ({
  AlertCircle: defineComponent({ render: () => h('span', 'alert-circle') }),
  AlertTriangle: defineComponent({ render: () => h('span', 'alert-triangle') }),
  BookOpen: defineComponent({ render: () => h('span', 'book-open') }),
  CheckCircle2: defineComponent({ render: () => h('span', 'check-circle') }),
  ChevronLeft: defineComponent({ render: () => h('span', 'chevron-left') }),
  ChevronRight: defineComponent({ render: () => h('span', 'chevron-right') }),
  Clock: defineComponent({ render: () => h('span', 'clock') }),
  FileText: defineComponent({ render: () => h('span', 'file-text') }),
  Inbox: defineComponent({ render: () => h('span', 'inbox') }),
  Loader2: defineComponent({ render: () => h('span', 'loader') }),
  MessageCircle: defineComponent({ render: () => h('span', 'message-circle') }),
  Plus: defineComponent({ render: () => h('span', 'plus') }),
  RefreshCw: defineComponent({ render: () => h('span', 'refresh') }),
  SendHorizontal: defineComponent({ render: () => h('span', 'send') }),
  Settings: defineComponent({ render: () => h('span', 'settings') }),
  Upload: defineComponent({ render: () => h('span', 'upload') }),
  X: defineComponent({ render: () => h('span', 'x') }),
}))

// ── LoadingState ──────────────────────────────────────────────────────
import LoadingState from '@/components/LoadingState.vue'

describe('LoadingState', () => {
  it('renders default message', () => {
    const wrapper = mount(LoadingState)
    expect(wrapper.text()).toContain('Loading…')
  })

  it('renders custom message', () => {
    const wrapper = mount(LoadingState, { props: { message: 'Please wait' } })
    expect(wrapper.text()).toContain('Please wait')
  })
})

// ── EmptyState ─────────────────────────────────────────────────────────
import EmptyState from '@/components/EmptyState.vue'

describe('EmptyState', () => {
  it('renders title and description', () => {
    const wrapper = mount(EmptyState, {
      props: { title: 'No items', description: 'Add some items first' },
    })
    expect(wrapper.text()).toContain('No items')
    expect(wrapper.text()).toContain('Add some items first')
  })

  it('renders slot content', () => {
    const wrapper = mount(EmptyState, {
      props: { title: 'Empty' },
      slots: { default: '<button>Add</button>' },
    })
    expect(wrapper.find('button').exists()).toBe(true)
  })
})

// ── ErrorState ─────────────────────────────────────────────────────────
import ErrorState from '@/components/ErrorState.vue'

describe('ErrorState', () => {
  it('renders title and message', () => {
    const wrapper = mount(ErrorState, {
      props: { title: 'Error occurred', message: 'Try again later' },
    })
    expect(wrapper.text()).toContain('Error occurred')
    expect(wrapper.text()).toContain('Try again later')
  })

  it('shows retry button when onRetry is provided', async () => {
    const onRetry = vi.fn()
    const wrapper = mount(ErrorState, {
      props: { title: 'Error', onRetry },
    })
    const btn = wrapper.find('button')
    expect(btn.exists()).toBe(true)
    await btn.trigger('click')
    expect(onRetry).toHaveBeenCalledOnce()
  })

  it('hides retry button when no onRetry', () => {
    const wrapper = mount(ErrorState, { props: { title: 'Error' } })
    expect(wrapper.find('button').exists()).toBe(false)
  })
})

// ── CitationList ───────────────────────────────────────────────────────
import CitationList from '@/components/CitationList.vue'
import type { Citation } from '@/types/api'

describe('CitationList', () => {
  const citations: Citation[] = [
    {
      chunk_id: 'c1',
      document_id: 'd1',
      document_title: 'Doc A',
      chunk_index: 0,
      page_number: 1,
      section_title: 'Introduction',
      content_snippet: 'This is a relevant snippet.',
      score: 0.92,
    },
    {
      chunk_id: 'c2',
      document_id: 'd1',
      document_title: 'Doc A',
      chunk_index: 1,
      page_number: null,
      section_title: null,
      content_snippet: 'Another snippet.',
      score: 0.75,
    },
  ]

  it('renders correct citation count', () => {
    const wrapper = mount(CitationList, { props: { citations } })
    expect(wrapper.text()).toContain('Citations (2)')
  })

  it('renders document titles', () => {
    const wrapper = mount(CitationList, { props: { citations } })
    expect(wrapper.text()).toContain('Doc A')
  })

  it('renders snippet text', () => {
    const wrapper = mount(CitationList, { props: { citations } })
    expect(wrapper.text()).toContain('This is a relevant snippet.')
  })

  it('renders score as percentage', () => {
    const wrapper = mount(CitationList, { props: { citations } })
    expect(wrapper.text()).toContain('92%')
  })
})

// ── AnswerCard ─────────────────────────────────────────────────────────
import AnswerCard from '@/components/AnswerCard.vue'
import type { ChatQueryResponse } from '@/types/api'

describe('AnswerCard', () => {
  const normalResponse: ChatQueryResponse = {
    session_id: 's1',
    message_id: 'm1',
    answer: 'The answer is 42.',
    abstained: false,
    citations: [],
    agent_trace_id: null,
    latency_ms: 120,
  }

  const abstainedResponse: ChatQueryResponse = {
    ...normalResponse,
    abstained: true,
    answer: 'I cannot answer this based on the available documents.',
  }

  it('renders answer text', () => {
    const wrapper = mount(AnswerCard, { props: { response: normalResponse } })
    expect(wrapper.text()).toContain('The answer is 42.')
  })

  it('shows abstain banner when abstained=true', () => {
    const wrapper = mount(AnswerCard, { props: { response: abstainedResponse } })
    expect(wrapper.text()).toContain('Insufficient evidence')
  })

  it('does NOT show abstain banner when abstained=false', () => {
    const wrapper = mount(AnswerCard, { props: { response: normalResponse } })
    expect(wrapper.text()).not.toContain('Insufficient evidence')
  })

  it('shows latency', () => {
    const wrapper = mount(AnswerCard, { props: { response: normalResponse } })
    expect(wrapper.text()).toContain('120ms')
  })

  it('applies yellow styling when abstained', () => {
    const wrapper = mount(AnswerCard, { props: { response: abstainedResponse } })
    expect(wrapper.find('div').classes().some((c) => c.includes('yellow'))).toBe(true)
  })
})
