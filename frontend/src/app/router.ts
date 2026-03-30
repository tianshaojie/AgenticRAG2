import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      redirect: '/chat',
    },
    {
      path: '/documents',
      name: 'documents',
      component: () => import('@/pages/DocumentsPage.vue'),
      meta: { title: 'Documents' },
    },
    {
      path: '/chat',
      name: 'chat',
      component: () => import('@/pages/ChatPage.vue'),
      meta: { title: 'Chat' },
    },
    {
      path: '/traces/:traceId',
      name: 'trace-detail',
      component: () => import('@/pages/TraceDetailPage.vue'),
      meta: { title: 'Trace Detail' },
    },
    {
      path: '/evals',
      name: 'evals',
      component: () => import('@/pages/EvalDashboardPage.vue'),
      meta: { title: 'Evaluations' },
    },
    {
      path: '/settings',
      name: 'settings',
      component: () => import('@/pages/SettingsPage.vue'),
      meta: { title: 'Settings' },
    },
  ],
})

router.beforeEach((to) => {
  document.title = to.meta.title ? `${to.meta.title} — AgenticRAG` : 'AgenticRAG'
})

export default router
