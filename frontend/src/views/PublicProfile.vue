<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { api } from '../api'

const route = useRoute()
const profile = ref(null)
const list = ref([])
const error = ref('')
const loading = ref(true)

onMounted(async () => {
  try {
    profile.value = await api.userProfile(route.params.userId)
    list.value = await api.userPublic(route.params.userId)
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div class="pub-wrap">
    <div class="brand"><span class="logo">✦</span>校园资料AI检索助手</div>
    <el-card shadow="never" class="card">
      <div v-if="loading" class="empty">加载中…</div>
      <div v-else-if="error" class="empty">{{ error }}</div>
      <template v-else>
        <div class="head">
          <b>{{ profile?.username }}</b> 的公开问答
          <span class="count">共 {{ list.length }} 条</span>
        </div>
        <div v-if="!list.length" class="empty">该用户暂无公开问答</div>
        <div v-for="(r, i) in list" :key="i" class="qa-item">
          <div class="q">{{ r.question }}</div>
          <div class="a">{{ r.answer }}</div>
          <div v-if="r.note" class="note">备注：{{ r.note }}</div>
          <div class="time">{{ r.created_at }}</div>
        </div>
      </template>
    </el-card>
  </div>
</template>

<style scoped>
.pub-wrap { min-height: 100vh; display: flex; flex-direction: column; align-items: center; padding: 40px 16px; background: linear-gradient(135deg, #eef2ff, #f5f3ff); }
.brand { display: flex; align-items: center; font-weight: 700; font-size: 16px; color: #1e293b; margin-bottom: 20px; }
.brand .logo { width: 34px; height: 34px; border-radius: 10px; background: linear-gradient(135deg, #6366f1, #8b5cf6); color: #fff; display: flex; align-items: center; justify-content: center; margin-right: 10px; font-size: 17px; }
.card { width: 100%; max-width: 720px; border-radius: 16px; border: 1px solid #e7ebf3; }
.head { font-size: 16px; color: #1e293b; margin-bottom: 14px; }
.count { font-size: 12px; color: #94a3b8; margin-left: 8px; font-weight: normal; }
.qa-item { padding: 14px; border: 1px solid #eef2f7; border-radius: 12px; margin-bottom: 12px; }
.q { font-weight: 600; color: #1e293b; margin-bottom: 6px; }
.a { color: #475569; line-height: 1.8; white-space: pre-wrap; word-break: break-word; font-size: 14px; }
.note { font-size: 13px; color: #b45309; margin-top: 8px; background: #fef3c7; padding: 6px 10px; border-radius: 8px; }
.time { font-size: 12px; color: #94a3b8; margin-top: 8px; }
.empty { color: #94a3b8; text-align: center; padding: 40px 0; }
</style>