<template>
  <form @submit.prevent="handleSubmit" class="flex gap-2 items-end">
    <div class="flex-1 relative">
      <textarea
        ref="textareaRef"
        v-model="inputText"
        :placeholder="placeholder"
        :disabled="disabled"
        rows="1"
        class="w-full resize-none rounded-md border bg-background px-3 py-2 text-sm placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring disabled:opacity-50 disabled:cursor-not-allowed overflow-hidden"
        style="min-height: 40px; max-height: 160px"
        @keydown.enter.exact.prevent="handleSubmit"
        @keydown.enter.shift.exact="insertNewline"
        @input="autoResize"
      />
    </div>
    <button
      type="submit"
      :disabled="disabled || !inputText.trim()"
      class="shrink-0 inline-flex items-center justify-center rounded-md h-10 w-10 bg-primary text-primary-foreground hover:bg-primary/90 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
    >
      <Loader2 v-if="disabled" class="h-4 w-4 animate-spin" />
      <SendHorizontal v-else class="h-4 w-4" />
    </button>
  </form>
</template>

<script setup lang="ts">
import { ref, nextTick } from 'vue'
import { SendHorizontal, Loader2 } from 'lucide-vue-next'

withDefaults(
  defineProps<{
    disabled?: boolean
    placeholder?: string
  }>(),
  { placeholder: 'Ask a question… (Enter to send, Shift+Enter for newline)' },
)

const emit = defineEmits<{ submit: [query: string] }>()

const inputText = ref('')
const textareaRef = ref<HTMLTextAreaElement>()

function handleSubmit() {
  const q = inputText.value.trim()
  if (!q) return
  emit('submit', q)
  inputText.value = ''
  nextTick(() => autoResize())
}

function insertNewline() {
  // allow default behavior — shift+enter adds newline
}

function autoResize() {
  const el = textareaRef.value
  if (!el) return
  el.style.height = 'auto'
  el.style.height = Math.min(el.scrollHeight, 160) + 'px'
}
</script>
