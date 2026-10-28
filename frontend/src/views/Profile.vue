<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { api } from '../api'
import { useUserStore } from '../stores/user'

const user = useUserStore()
const list = ref([])
const loading = ref(false)

async function load() {
  loading.value = true
  try {
    list.value = await api.userPublic(user.userId)
  } catch (e) {
    ElMessage.error(e.message)
  } finally {
    loading.value = false
  }
}

async function copyProfile() {
  const url = `${window.location.origin}/u/${user.userId}`
  try {
    await navigator.clipboard.writeText(url)
    ElMessage.success('主页链接已复制')
  } catch {
    ElMessage.info(url)
  }
}

onMounted(load)
</script>

<template>
  <el-card shadow="never" class="wrap">
    <template #header>
      <div class="head">
        <div>
          <b>{{ user.username }}</b> 的个人主页
          <div class="tip">你标记为「公开」的问答将展示在这里，任何人访问你的主页都能看到</div>
        </div>
        <el-button type="primary" @click="copyProfile">复制主页链接</el-button>
      </div>
    </template>

    <div v-if="loading" class="empty">加载中…</div>
    <div v-else-if="!list.length" class="empty">暂无公开问答</div>

    <div v-for="(r, i) in list" :key="i" class="qa-item">
      <div class="q">{{ r.question }}</div>
      <div class="a">{{ r.answer }}</div>
      <div v-if="r.note" class="note">备注：{{ r.note }}</div>
      <div class="time">{{ r.created_at }}</div>
    </div>
  </el-card>
</template>

<style scoped>
.wrap { border-radius: 16px; border: 1px solid #e7ebf3; }
.head { display: flex; justify-content: space-between; align-items: center; gap: 16px; flex-wrap: wrap; }
.tip { font-size: 12px; color: #94a3b8; font-weight: normal; margin-top: 4px; }
.empty { color: #94a3b8; text-align: center; padding: 40px 0; font-size: 14px; }
.qa-item { padding: 14px; border: 1px solid #eef2f7; border-radius: 12px; margin-bottom: 12px; }
.q { font-weight: 600; color: #1e293b; margin-bottom: 6px; }
.a { color: #475569; line-height: 1.7; white-space: pre-wrap; word-break: break-word; font-size: 14px; }
.note { font-size: 13px; color: #b45309; margin-top: 8px; background: #fef3c7; padding: 6px 10px; border-radius: 8px; }
.time { font-size: 12px; color: #94a3b8; margin-top: 8px; }
</style>