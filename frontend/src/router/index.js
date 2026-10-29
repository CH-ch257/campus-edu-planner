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
      { path: 'square', name: 'student-square', component: () => import('../views/PublicSquare.vue'), meta: { title: '问答广场' } },
      { path: 'history', name: 'student-history', component: () => import('../views/History.vue'), meta: { title: '问答历史' } },
      { path: 'profile', name: 'student-profile', component: () => import('../views/Profile.vue'), meta: { title: '个人主页' } },
      { path: 'settings', name: 'student-settings', component: () => import('../views/Settings.vue'), meta: { title: '个人设置' } }
    ]
  },
  {
    path: '/teacher',
    component: () => import('../views/RoleLayout.vue'),
    meta: { requiresAuth: true, roles: ['teacher'] },
    children: [
      { path: '', name: 'teacher-home', component: () => import('../views/AiChat.vue'), meta: { title: 'AI 问答' } },
      { path: 'manage', name: 'teacher-manage', component: () => import('../views/TeacherManage.vue'), meta: { title: '公开内容管理' } }
    ]
  },
  {
    path: '/admin',
    component: () => import('../views/RoleLayout.vue'),
    meta: { requiresAuth: true, roles: ['admin'] },
    children: [
      { path: '', name: 'admin-home', component: () => import('../views/AdminHome.vue'), meta: { title: '后台首页' } },
      { path: 'users', name: 'admin-users', component: () => import('../views/UserManage.vue'), meta: { title: '用户管理' } },
      { path: 'public', name: 'admin-public', component: () => import('../views/AdminPublicManage.vue'), meta: { title: '公开内容管理' } }
    ]
  },
  // 公开路由（无需登录）：分享落地页、他人公开主页
  { path: '/share/:token', name: 'share', component: () => import('../views/ShareView.vue'), meta: { title: '分享' } },
  { path: '/u/:userId', name: 'public-profile', component: () => import('../views/PublicProfile.vue'), meta: { title: '个人主页' } },
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
  if (role === 'student') return '/student'
  return '/login'
}

// 全局前置守卫：登录校验 + 角色越权拦截
router.beforeEach((to) => {
  const user = useUserStore()
  // 登录态必须 token 与合法角色同时存在才算已登录，否则视为未登录（防止残留脏数据导致无限重定向）
  const logged = user.isLoggedIn && ['student', 'teacher', 'admin'].includes(user.role)
  if (to.meta.requiresAuth) {
    if (!logged) return { path: '/login', query: { redirect: to.fullPath } }
    if (to.meta.roles && !to.meta.roles.includes(user.role)) return homeOf(user.role)
  }
  // 已登录用户访问登录/注册页，跳转到自己角色首页
  if ((to.path === '/login' || to.path === '/register') && logged) {
    return homeOf(user.role)
  }
  return true
})

router.afterEach((to) => {
  if (to.meta.title) document.title = `${to.meta.title} · 校园资料AI检索助手`
})

export default router