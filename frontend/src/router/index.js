import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'chat',
    component: () => import('../views/AiChat.vue'),
    meta: { title: 'AI 问答' }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.afterEach((to) => {
  if (to.meta.title) document.title = `${to.meta.title} · 校园资料AI检索助手`
})

export default router