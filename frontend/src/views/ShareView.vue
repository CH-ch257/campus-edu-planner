<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { api } from '../api'

const route = useRoute()
const data = ref(null)
const error = ref('')
const loading = ref(true)

onMounted(async () => {
  try {
    data.value = await api.qaShareView(route.params.token)
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div class="share-wrap">
    <div class="brand"><span class="logo">✦</span>校园资料AI检索助手 · 分享</div>
    <el-card shadow="never" class="card">
      <div v-if="loading" class="empty">加载中…</div>
      <div v-else-if="error" class="empty">{{ error }}</div>
      <template v-else>
        <div class="owner">来自用户：{{ data.owner }}</div>
        <div class="q">{{ data.question }}</div>
        <div class="a">{{ data.answer }}</div>
        <div v-if="data.note" class="note">备注：{{ data.note }}</div>
        <div v-if="data.sources && data.sources.length" class="src">
          参考：{{ data.sources.map(s => s.doc_name).join('、') }}
        </div>
      </template>
    </el-card>
  </div>
</template>

<style scoped>
.share-wrap { min-height: 100vh; display: flex; flex-direction: column; align-items: center; padding: 40px 16px; background: linear-gradient(135deg, #eef2ff, #f5f3ff); }
.brand { display: flex; align-items: center; font-weight: 700; font-size: 16px; color: #1e293b; margin-bottom: 20px; }
.brand .logo { width: 34px; height: 34px; border-radius: 10px; background: linear-gradient(135deg, #6366f1, #8b5cf6); color: #fff; display: flex; align-items: center; justify-content: center; margin-right: 10px; font-size: 17px; }
.card { width: 100%; max-width: 720px; border-radius: 16px; border: 1px solid #e7ebf3; }
.owner { font-size: 12px; color: #94a3b8; margin-bottom: 10px; }
.q { font-weight: 600; font-size: 17px; color: #1e293b; margin-bottom: 10px; }
.a { color: #475569; line-height: 1.8; white-space: pre-wrap; word-break: break-word; }
.note { font-size: 13px; color: #b45309; margin-top: 12px; background: #fef3c7; padding: 8px 12px; border-radius: 8px; }
.src { font-size: 12px; color: #64748b; margin-top: 12px; padding: 6px 10px; background: #eef2ff; border-radius: 8px; }
.empty { color: #94a3b8; text-align: center; padding: 40px 0; }
</style>