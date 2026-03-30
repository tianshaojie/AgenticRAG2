import { ref, computed } from 'vue'
import { documentsApi } from '@/api/documents'
import type { DocumentResponse, PaginatedResponse } from '@/types/api'

export function useDocuments() {
  const items = ref<DocumentResponse[]>([])
  const total = ref(0)
  const page = ref(1)
  const pageSize = ref(20)
  const loading = ref(false)
  const error = ref<string | null>(null)
  const indexingIds = ref<Set<string>>(new Set())

  const hasNext = computed(() => page.value * pageSize.value < total.value)

  async function fetchList() {
    loading.value = true
    error.value = null
    try {
      const data: PaginatedResponse<DocumentResponse> = await documentsApi.list(
        page.value,
        pageSize.value,
      )
      items.value = data.items
      total.value = data.total
    } catch (e: unknown) {
      error.value = e instanceof Error ? e.message : 'Failed to load documents'
    } finally {
      loading.value = false
    }
  }

  async function upload(file: File, title?: string): Promise<DocumentResponse | null> {
    error.value = null
    try {
      const doc = await documentsApi.upload(file, title)
      await fetchList()
      return doc
    } catch (e: unknown) {
      error.value = e instanceof Error ? e.message : 'Upload failed'
      return null
    }
  }

  async function triggerIndex(id: string): Promise<void> {
    indexingIds.value.add(id)
    error.value = null
    try {
      await documentsApi.index(id, false)
      // refresh to get updated status
      await fetchList()
    } catch (e: unknown) {
      error.value = e instanceof Error ? e.message : 'Indexing failed'
    } finally {
      indexingIds.value.delete(id)
    }
  }

  async function remove(id: string): Promise<void> {
    error.value = null
    try {
      await documentsApi.remove(id)
      await fetchList()
    } catch (e: unknown) {
      error.value = e instanceof Error ? e.message : 'Delete failed'
    }
  }

  function nextPage() {
    if (hasNext.value) {
      page.value++
      fetchList()
    }
  }

  function prevPage() {
    if (page.value > 1) {
      page.value--
      fetchList()
    }
  }

  return {
    items,
    total,
    page,
    pageSize,
    loading,
    error,
    indexingIds,
    hasNext,
    fetchList,
    upload,
    triggerIndex,
    remove,
    nextPage,
    prevPage,
  }
}
