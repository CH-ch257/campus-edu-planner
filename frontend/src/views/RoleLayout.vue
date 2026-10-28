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
    { path: '/teacher', label: 'AI 问答' },
    { path: '/teacher/manage', label: '公开内容管理' }
  ]
  return [
    { path: '/admin', label: '后台首页' },
    { path: '/admin/users', label: '用户管理' },
    { path: '/admin/public', label: '公开内容管理' }
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
.app-shell { min-height: 100vh; display: flex; flex-direction: column; }
.topbar {
  height: 66px; position: sticky; top: 0; z-index: 100;
  display: flex; align-items: center; justify-content: space-between;
  padding: 0 26px;
  background: linear-gradient(120deg, #0c4a6e 0%, #0ea5e9 55%, #10b981 130%);
  box-shadow: 0 4px 20px rgba(12, 74, 110, .25);
}
.brand { display: flex; align-items: center; font-weight: 700; font-size: 17px; color: #fff; letter-spacing: .5px; text-shadow: 0 1px 3px rgba(0,0,0,.12); }
.brand .logo {
  width: 34px; height: 34px; border-radius: 10px; margin-right: 10px;
  background: rgba(255,255,255,.18); border: 1px solid rgba(255,255,255,.35);
  color: #fff; display: inline-flex; align-items: center; justify-content: center;
  font-size: 16px; backdrop-filter: blur(4px);
}
.nav { display: flex; gap: 6px; flex: 1; margin: 0 24px; }
.nav-link {
  padding: 7px 16px; border-radius: 10px; color: rgba(255,255,255,.82);
  text-decoration: none; font-size: 14px; white-space: nowrap;
  transition: background .2s ease, color .2s ease;
}
.nav-link:hover { background: rgba(255,255,255,.14); color: #fff; }
.nav-link.router-link-active {
  background: rgba(255,255,255,.22); color: #fff; font-weight: 600;
  box-shadow: inset 0 0 0 1px rgba(255,255,255,.25);
}
.actions { display: flex; align-items: center; gap: 8px; }
.me { margin-right: 2px; }
.main { flex: 1; width: 100%; max-width: 1320px; margin: 0 auto; padding: 26px 24px 40px; }
</style>