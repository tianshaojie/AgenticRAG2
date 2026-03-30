<template>
  <div class="flex flex-col items-center justify-center py-16 px-4 text-center">
    <div class="rounded-full bg-muted p-4 mb-4">
      <component :is="iconComponent" class="h-8 w-8 text-muted-foreground" />
    </div>
    <h3 class="text-sm font-semibold mb-1">{{ title }}</h3>
    <p class="text-sm text-muted-foreground max-w-xs">{{ description }}</p>
    <slot />
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { FileText, MessageCircle, Inbox } from 'lucide-vue-next'

const props = withDefaults(
  defineProps<{
    title: string
    description?: string
    icon?: 'file' | 'chat' | 'inbox'
  }>(),
  { description: '', icon: 'inbox' },
)

const iconComponent = computed(() => {
  const map = { file: FileText, chat: MessageCircle, inbox: Inbox }
  return map[props.icon]
})
</script>
