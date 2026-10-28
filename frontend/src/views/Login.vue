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
    <div class="blob blob-1"></div>
    <div class="blob blob-2"></div>
    <div class="blob blob-3"></div>
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
.auth-wrap {
  min-height: 100vh; display: flex; align-items: center; justify-content: center;
  position: relative; overflow: hidden;
  background: linear-gradient(150deg, #e0f2fe 0%, #ecfeff 45%, #f0fdf4 100%);
}
/* 背景装饰光斑 */
.blob { position: absolute; border-radius: 50%; filter: blur(70px); opacity: .5; pointer-events: none; }
.blob-1 { width: 420px; height: 420px; background: #7dd3fc; top: -120px; left: -80px; }
.blob-2 { width: 380px; height: 380px; background: #6ee7b7; bottom: -100px; right: -60px; }
.blob-3 { width: 240px; height: 240px; background: #a5f3fc; top: 40%; right: 12%; }
.auth-card {
  width: 400px; border-radius: 22px; padding: 12px 16px 24px;
  border: 1px solid rgba(255,255,255,.85) !important;
  background: rgba(255,255,255,.9) !important;
  box-shadow: 0 24px 60px rgba(14, 165, 233, .16), 0 6px 20px rgba(15, 118, 110, .08);
  backdrop-filter: blur(12px);
  position: relative; z-index: 1;
}
.auth-head { text-align: center; margin-bottom: 22px; }
.auth-head .logo {
  width: 56px; height: 56px; margin: 0 auto 14px; border-radius: 16px;
  background: linear-gradient(135deg, #0ea5e9, #10b981);
  color: #fff; font-size: 26px; display: flex; align-items: center; justify-content: center;
  box-shadow: 0 10px 24px rgba(14, 165, 233, .35);
}
.auth-head h2 { margin: 0; font-size: 21px; color: #0f172a; letter-spacing: .5px; }
.auth-head p { margin: 7px 0 0; color: #94a3b8; font-size: 13px; }
.mb { margin-bottom: 16px; }
.submit { width: 100%; height: 44px !important; font-size: 15px; }
.auth-foot { margin-top: 18px; text-align: center; font-size: 13px; color: #64748b; }
.auth-foot a { color: #0ea5e9; text-decoration: none; font-weight: 600; }
.auth-foot a:hover { text-decoration: underline; }
</style>
