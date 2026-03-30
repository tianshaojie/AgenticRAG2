<template>
  <div class="flex h-screen overflow-hidden bg-background">
    <!-- Sidebar -->
    <aside
      :class="[
        'flex flex-col border-r bg-muted/30 transition-all duration-200',
        sidebarOpen ? 'w-56' : 'w-14',
      ]"
    >
      <!-- Logo -->
      <div class="flex items-center gap-2 px-3 py-4 border-b h-14">
        <div class="flex h-7 w-7 shrink-0 items-center justify-center rounded-md bg-primary text-primary-foreground text-xs font-bold">
          R
        </div>
        <span v-if="sidebarOpen" class="font-semibold text-sm truncate">AgenticRAG</span>
      </div>

      <!-- Nav links -->
      <nav class="flex-1 px-2 py-3 flex flex-col gap-1">
        <RouterLink
          v-for="item in navItems"
          :key="item.to"
          :to="item.to"
          :title="item.label"
          :class="[
            'flex items-center gap-2.5 rounded-md px-2 py-2 text-sm font-medium transition-colors',
            $route.path.startsWith(item.to)
              ? 'bg-primary text-primary-foreground'
              : 'text-muted-foreground hover:bg-accent hover:text-accent-foreground',
          ]"
        >
          <component :is="item.icon" class="h-4 w-4 shrink-0" />
          <span v-if="sidebarOpen" class="truncate">{{ item.label }}</span>
        </RouterLink>
      </nav>

      <!-- Sidebar toggle -->
      <button
        @click="sidebarOpen = !sidebarOpen"
        class="flex items-center justify-center h-10 border-t text-muted-foreground hover:text-foreground transition-colors"
      >
        <ChevronLeft v-if="sidebarOpen" class="h-4 w-4" />
        <ChevronRight v-else class="h-4 w-4" />
      </button>
    </aside>

    <!-- Main content -->
    <main class="flex-1 overflow-hidden flex flex-col">
      <!-- Top bar -->
      <header class="h-14 border-b flex items-center px-4 gap-3 shrink-0">
        <h1 class="text-sm font-semibold">{{ pageTitle }}</h1>
        <div class="ml-auto flex items-center gap-2">
          <!-- Health dot -->
          <div
            :title="healthStatus"
            :class="[
              'h-2 w-2 rounded-full',
              isHealthy ? 'bg-green-500' : 'bg-red-500',
            ]"
          />
        </div>
      </header>

      <!-- Page -->
      <div class="flex-1 overflow-y-auto">
        <slot />
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { RouterLink, useRoute } from 'vue-router'
import { FileText, MessageCircle, Settings, ChevronLeft, ChevronRight } from 'lucide-vue-next'
import { useHealth } from '@/composables/useHealth'

const route = useRoute()
const sidebarOpen = ref(true)
const { health, ready } = useHealth(true)

const navItems = [
  { to: '/chat', label: 'Chat', icon: MessageCircle },
  { to: '/documents', label: 'Documents', icon: FileText },
  { to: '/settings', label: 'Settings', icon: Settings },
]

const pageTitle = computed(() => {
  const found = navItems.find((n) => route.path.startsWith(n.to))
  return found?.label ?? 'AgenticRAG'
})

const isHealthy = computed(
  () => health.value?.status === 'ok' && ready.value?.ready === true,
)

const healthStatus = computed(() => {
  if (!health.value) return 'Connecting…'
  if (!ready.value?.ready) return 'DB unavailable'
  return `${health.value.environment} v${health.value.version}`
})
</script>
