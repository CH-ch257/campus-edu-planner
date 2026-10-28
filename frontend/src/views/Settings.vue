<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { api } from '../api'
import { useUserStore } from '../stores/user'

const user = useUserStore()
const router = useRouter()

const oldPassword = ref('')
const newPassword = ref('')
const confirm = ref('')
const loading = ref(false)

async function submit() {
  if (!oldPassword.value || !newPassword.value) return ElMessage.warning('请填写完整')
  if (newPassword.value.length < 4) return ElMessage.warning('新密码至少4位')
  if (newPassword.value !== confirm.value) return ElMessage.warning('两次输入的新密码不一致')
  loading.value = true
  try {
    await api.changePassword(oldPassword.value, newPassword.value)
    ElMessage.success('密码修改成功，请重新登录')
    user.logout()
    router.push('/login')
  } catch (e) {
    ElMessage.error(e.message)
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <el-card shadow="never" class="wrap">
    <template #header><b>个人设置 · 修改密码</b></template>
    <el-form label-width="90px" class="form" @submit.prevent="submit">
      <el-form-item label="原密码">
        <el-input v-model="oldPassword" type="password" show-password placeholder="请输入原密码" />
      </el-form-item>
      <el-form-item label="新密码">
        <el-input v-model="newPassword" type="password" show-password placeholder="至少4位" />
      </el-form-item>
      <el-form-item label="确认密码">
        <el-input v-model="confirm" type="password" show-password placeholder="再次输入新密码" @keyup.enter="submit" />
      </el-form-item>
      <el-form-item>
        <el-button type="primary" :loading="loading" @click="submit">确认修改</el-button>
      </el-form-item>
    </el-form>
  </el-card>
</template>

<style scoped>
.wrap { border-radius: 16px; border: 1px solid #e7ebf3; }
.form { max-width: 440px; margin-top: 8px; }
</style>