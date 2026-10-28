import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '../stores/user'

const routes = [
  { path: '/login', name: 'login', component: () => import('../views/Login.vue'), meta: { title: '登录' } },
  { path: '/register', name: 'register', component: () => import('../views/Register.vue'), meta: { title: '注册' } },
  {
    path: '/student',
    component: () => import('../views/RoleLayout.vue'),
    meta: { requiresAuth: true, roles: ['student'] },
    children: [
      { path: '', name: 'student-home', component: () => import('../views/AiChat.vue'), meta: { title: 'AI 问答' } },
      { path: 'history', name: 'student-history', component: () => import('../views/Placeholder.vue'), meta: { title: '问答历史' } },
      { path: 'profile', name: 'student-profile', component: () => import('../views/Placeholder.vue'), meta: { title: '个人主页' } },
      { path: 'settings', name: 'student-settings', component: () => import('../views/Placeholder.vue'), meta: { title: '个人设置' } }
    ]
  },
  {
    path: '/teacher',
    component: () => import('../views/RoleLayout.vue'),
    meta: { requiresAuth: true, roles: ['teacher'] },
    children: [
      { path: '', name: 'teacher-home', component: () => import('../views/AiChat.vue'), meta: { title: 'AI 问答' } }
    ]
  },
  {
    path: '/admin',
    component: () => import('../views/RoleLayout.vue'),
    meta: { requiresAuth: true, roles: ['admin'] },
    children: [
      { path: '', name: 'admin-home', component: () => import('../views/Placeholder.vue'), meta: { title: '后台首页' } }
    ]
  },
  { path: '/', redirect: '/login' },
  { path: '/:pathMatch(.*)*', redirect: '/login' }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

function homeOf(role) {
  if (role === 'admin') return '/admin'
  if (role === 'teacher') return '/teacher'
  return '/student'
}

// 全局前置守卫：登录校验 + 角色越权拦截
router.beforeEach((to) => {
  const user = useUserStore()
  if (to.meta.requiresAuth) {
    if (!user.isLoggedIn) return { path: '/login', query: { redirect: to.fullPath } }
    if (to.meta.roles && !to.meta.roles.includes(user.role)) return homeOf(user.role)
  }
  // 已登录用户访问登录/注册页，跳转到自己角色首页
  if ((to.path === '/login' || to.path === '/register') && user.isLoggedIn) {
    return homeOf(user.role)
  }
  return true
})

router.afterEach((to) => {
  if (to.meta.title) document.title = `${to.meta.title} · 校园资料AI检索助手`
})

export default router