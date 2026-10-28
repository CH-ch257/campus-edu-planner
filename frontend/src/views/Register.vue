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
.auth-wrap {
  min-height: 100vh; display: flex; align-items: center; justify-content: center;
  position: relative; overflow: hidden;
  background: linear-gradient(150deg, #e0f2fe 0%, #ecfeff 45%, #f0fdf4 100%);
}
/* 背景装饰光斑 */
.blob { position: absolute; border-radius: 50%; filter: blur(70px); opacity: .5; pointer-events: none; }
.blob-1 { width: 420px; height: 420px; background: #7dd3fc; top: -120px; right: -80px; }
.blob-2 { width: 380px; height: 380px; background: #6ee7b7; bottom: -100px; left: -60px; }
.blob-3 { width: 240px; height: 240px; background: #a5f3fc; top: 40%; left: 10%; }
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