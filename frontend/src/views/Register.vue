<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { api } from '../api'

const router = useRouter()
const username = ref('')
const password = ref('')
const confirm = ref('')
const loading = ref(false)

async function register() {
  if (!username.value.trim()) return ElMessage.warning('请输入用户名')
  if (password.value.length < 4) return ElMessage.warning('密码至少4位')
  if (password.value !== confirm.value) return ElMessage.warning('两次输入的密码不一致')
  loading.value = true
  try {
    await api.register(username.value.trim(), password.value)
    ElMessage.success('注册成功，请登录')
    router.push('/login')
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
        <h2>学生注册</h2>
        <p>注册后即可使用 AI 问答</p>
      </div>
      <el-form @submit.prevent="register">
        <el-input v-model="username" placeholder="用户名" size="large" class="mb" />
        <el-input v-model="password" type="password" placeholder="密码（至少4位）" size="large" show-password class="mb" />
        <el-input v-model="confirm" type="password" placeholder="确认密码" size="large" show-password class="mb" @keyup.enter="register" />
        <el-button type="primary" size="large" class="submit" :loading="loading" @click="register">注册</el-button>
      </el-form>
      <div class="auth-foot">
        已有账号？<router-link to="/login">去登录</router-link>
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