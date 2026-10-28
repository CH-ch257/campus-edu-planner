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
        <div class="q"><span class="q-mark">Q</span>{{ data.question }}</div>
        <div class="a"><span class="a-mark">A</span>{{ data.answer }}</div>
        <div v-if="data.note" class="note">📝 {{ data.note }}</div>
        <div v-if="data.teacher_note" class="teacher-note">👩‍🏫 教师评语：{{ data.teacher_note }}</div>
        <div v-if="data.sources && data.sources.length" class="src">
          📎 参考：{{ data.sources.map(s => s.doc_name).join('、') }}
        </div>
      </template>
    </el-card>
  </div>
</template>

<style scoped>
.share-wrap { min-height: 100vh; display: flex; flex-direction: column; align-items: center; padding: 40px 16px; background: linear-gradient(135deg, #e0f2fe, #ecfeff); }
.brand { display: flex; align-items: center; font-weight: 700; font-size: 16px; color: #1e293b; margin-bottom: 20px; }
.brand .logo { width: 34px; height: 34px; border-radius: 10px; background: linear-gradient(135deg, #0ea5e9, #10b981); color: #fff; display: flex; align-items: center; justify-content: center; margin-right: 10px; font-size: 17px; }
.card { width: 100%; max-width: 720px; border-radius: 18px; border: 1px solid #e2ecf5; box-shadow: 0 10px 30px rgba(14,165,233,.08); }
.owner { font-size: 12px; color: #94a3b8; margin-bottom: 10px; }
.q { font-weight: 600; font-size: 17px; color: #1e293b; margin-bottom: 10px; }
.a { color: #475569; line-height: 1.8; white-space: pre-wrap; word-break: break-word; }
.note { font-size: 13px; color: #b45309; margin-top: 12px; background: #fef3c7; padding: 8px 12px; border-radius: 8px; }
.src { font-size: 12px; color: #64748b; margin-top: 12px; padding: 6px 10px; background: #e0f2fe; border-radius: 8px; }
.empty { color: #94a3b8; text-align: center; padding: 40px 0; }

.card-title { display: flex; align-items: center; font-weight: 700; }
.head-dot { width: 10px; height: 10px; border-radius: 50%; background: linear-gradient(135deg, #0ea5e9, #10b981); margin-right: 10px; box-shadow: 0 0 0 3px rgba(14,165,233,.15); }
.qa-item { padding: 18px 20px; border: 1px solid #e6f0f8; border-radius: 14px; margin-bottom: 14px; background: #fff; box-shadow: 0 2px 10px rgba(15,118,110,.05); transition: box-shadow .2s ease, transform .2s ease; }
.qa-item:hover { box-shadow: 0 8px 24px rgba(14,165,233,.12); transform: translateY(-1px); }
.q { display: flex; align-items: flex-start; font-weight: 700; color: #0f172a; margin-bottom: 8px; font-size: 15px; }
.q-mark, .a-mark { flex-shrink: 0; width: 22px; height: 22px; border-radius: 7px; margin-right: 10px; display: inline-flex; align-items: center; justify-content: center; font-size: 12px; font-weight: 700; color: #fff; }
.q-mark { background: linear-gradient(135deg, #0ea5e9, #38bdf8); }
.a-mark { background: linear-gradient(135deg, #10b981, #34d399); }
.a { color: #475569; line-height: 1.75; white-space: pre-wrap; word-break: break-word; font-size: 14px; padding-left: 32px; }
.note { font-size: 13px; color: #b45309; margin-top: 10px; background: #fef3c7; padding: 7px 12px; border-radius: 10px; border: 1px solid #fde68a; }
.teacher-note { font-size: 13px; color: #047857; margin-top: 10px; background: #d1fae5; padding: 7px 12px; border-radius: 10px; border: 1px solid #a7f3d0; }</style>