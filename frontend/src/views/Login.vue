<script setup>
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { api } from '../api'
import { useUserStore } from '../stores/user'

const router = useRouter()
const route = useRoute()
const user = useUserStore()

const username = ref('')
const password = ref('')
const loading = ref(false)

function homeOf(role) {
  if (role === 'admin') return '/admin'
  if (role === 'teacher') return '/teacher'
  return '/student'
}

async function login() {
  if (!username.value.trim() || !password.value) return ElMessage.warning('请输入用户名和密码')
  loading.value = true
  try {
    const data = await api.login(username.value.trim(), password.value)
    user.setAuth(data)
    ElMessage.success('登录成功')
    router.push(route.query.redirect || homeOf(data.role))
  } catch (e) {
    ElMessage.error(e.message)
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="auth-wrap">
    <el-card class="auth-card" shadow="never">
      <div class="auth-head">
        <div class="logo">✦</div>
        <h2>校园资料AI检索助手</h2>
        <p>登录后使用 AI 问答</p>
      </div>
      <el-form @submit.prevent="login">
        <el-input v-model="username" placeholder="用户名" size="large" class="mb" @keyup.enter="login" />
        <el-input v-model="password" type="password" placeholder="密码" size="large" show-password class="mb" @keyup.enter="login" />
        <el-button type="primary" size="large" class="submit" :loading="loading" @click="login">登录</el-button>
      </el-form>
      <div class="auth-foot">
        还没有账号？<router-link to="/register">学生注册</router-link>
      </div>
    </el-card>
  </div>
</template>

<style scoped>
.auth-wrap { min-height: 100vh; display: flex; align-items: center; justify-content: center; background: linear-gradient(135deg, #eef2ff, #f5f3ff); }
.auth-card { width: 380px; border-radius: 18px; border: 1px solid #e7ebf3; padding: 8px 12px 20px; }
.auth-head { text-align: center; margin-bottom: 18px; }
.auth-head .logo { width: 52px; height: 52px; margin: 0 auto 12px; border-radius: 14px; background: linear-gradient(135deg, #6366f1, #8b5cf6); color: #fff; font-size: 24px; display: flex; align-items: center; justify-content: center; }
.auth-head h2 { margin: 0; font-size: 20px; color: #1e293b; }
.auth-head p { margin: 6px 0 0; color: #94a3b8; font-size: 13px; }
.mb { margin-bottom: 14px; }
.submit { width: 100%; }
.auth-foot { margin-top: 16px; text-align: center; font-size: 13px; color: #64748b; }
.auth-foot a { color: #6366f1; text-decoration: none; font-weight: 600; }
</style>