<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useUserStore } from '../stores/user'

const user = useUserStore()
const router = useRouter()

const roleLabel = { student: '学生', teacher: '老师', admin: '高级管理员' }

const menus = computed(() => {
  if (user.role === 'student') return [
    { path: '/student', label: 'AI 问答' },
    { path: '/student/history', label: '问答历史' },
    { path: '/student/profile', label: '个人主页' },
    { path: '/student/settings', label: '个人设置' }
  ]
  if (user.role === 'teacher') return [
    { path: '/teacher', label: 'AI 问答' }
  ]
  return [
    { path: '/admin', label: '后台首页' }
  ]
})

function logout() {
  user.logout()
  ElMessage.success('已退出登录')
  router.push('/login')
}
</script>

<template>
  <div class="app-shell">
    <header class="topbar">
      <div class="brand"><span class="logo">✦</span>校园资料AI检索助手</div>
      <nav class="nav">
        <router-link v-for="m in menus" :key="m.path" :to="m.path" class="nav-link">{{ m.label }}</router-link>
      </nav>
      <div class="actions">
        <el-tag round effect="light" class="role-tag" :type="user.role === 'admin' ? 'danger' : user.role === 'teacher' ? 'warning' : 'primary'">{{ roleLabel[user.role] }}</el-tag>
        <el-tag class="me" round type="info" effect="plain">{{ user.username }}</el-tag>
        <el-button round @click="logout">退出登录</el-button>
      </div>
    </header>
    <main class="main">
      <router-view />
    </main>
  </div>
</template>

<style scoped>
.app-shell { min-height: 100vh; display: flex; flex-direction: column; background: var(--bg, #f3f5fb); }
.topbar {
  height: 64px; position: sticky; top: 0; z-index: 100;
  display: flex; align-items: center; justify-content: space-between;
  padding: 0 24px; background: rgba(255,255,255,.85);
  backdrop-filter: saturate(180%) blur(12px);
  border-bottom: 1px solid #e7ebf3;
}
.brand { display: flex; align-items: center; font-weight: 700; font-size: 18px; color: #1e293b; }
.brand .logo { width: 34px; height: 34px; border-radius: 10px; background: linear-gradient(135deg, #6366f1, #8b5cf6); color: #fff; display: inline-flex; align-items: center; justify-content: center; margin-right: 10px; font-size: 17px; }
.nav { display: flex; gap: 4px; flex: 1; margin: 0 24px; }
.nav-link { padding: 6px 14px; border-radius: 8px; color: #475569; text-decoration: none; font-size: 14px; white-space: nowrap; }
.nav-link.router-link-active { background: #eef2ff; color: #4f46e5; font-weight: 600; }
.actions { display: flex; align-items: center; gap: 8px; }
.me { margin-right: 2px; }
.main { flex: 1; width: 100%; max-width: 1280px; margin: 0 auto; padding: 24px; }
</style>