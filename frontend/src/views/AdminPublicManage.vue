<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { api } from '../api'

const list = ref([])
const loading = ref(false)

async function load() {
  loading.value = true
  try {
    list.value = await api.adminPublicQa()
  } catch (e) {
    ElMessage.error(e.message)
  } finally {
    loading.value = false
  }
}

async function del(row) {
  try {
    await ElMessageBox.confirm('确定删除这条公开问答吗？此操作不可恢复。', '删除确认', { type: 'warning' })
  } catch (e) {
    return
  }
  try {
    await api.adminDeletePublicQa(row.id)
    ElMessage.success('删除成功')
    load()
  } catch (e) {
    ElMessage.error(e.message)
  }
}

onMounted(load)
</script>

<template>
  <el-card shadow="never" class="wrap">
    <template #header>
      <div class="head">
        <div class="card-title"><span class="head-dot"></span>公开内容总管理</div>
        <span class="tip">查看并删除全部用户的公开问答与公开备注</span>
      </div>
    </template>

    <div v-if="loading" class="empty">加载中…</div>
    <div v-else-if="!list.length" class="empty">暂无公开问答</div>

    <div v-for="r in list" :key="r.id" class="qa-item">
      <div class="meta">
        <span class="owner">{{ r.username }}</span>
        <span class="time">{{ r.created_at }}</span>
      </div>
      <div class="q"><span class="q-mark">Q</span>{{ r.question }}</div>
      <div class="a"><span class="a-mark">A</span>{{ r.answer }}</div>
      <div v-if="r.note" class="note">📝 {{ r.note }}</div>
      <div v-if="r.notes && r.notes.length" class="notes-box">
        <div class="notes-title">📌 追加备注（{{ r.notes.length }} 条）</div>
        <div v-for="(n, i) in r.notes" :key="i" class="note-row">
          <span class="note-author">{{ n.username }}</span>
          <span class="note-content">{{ n.content }}</span>
          <span class="note-time">{{ n.created_at }}</span>
        </div>
      </div>
      <div class="ops">
        <el-button size="small" type="danger" @click="del(r)">删除</el-button>
      </div>
    </div>
  </el-card>
</template>

<style scoped>
.card-title { display: flex; align-items: center; font-weight: 700; }
.head-dot { width: 10px; height: 10px; border-radius: 50%; background: linear-gradient(135deg, #0ea5e9, #10b981); margin-right: 10px; box-shadow: 0 0 0 3px rgba(14,165,233,.15); }
.head { display: flex; align-items: center; gap: 12px; flex-wrap: wrap; }
.tip { font-size: 12px; color: #94a3b8; font-weight: normal; }
.qa-item { padding: 18px 20px; border: 1px solid #e6f0f8; border-radius: 14px; margin-bottom: 14px; background: #fff; box-shadow: 0 2px 10px rgba(15,118,110,.05); transition: box-shadow .2s ease, transform .2s ease; }
.qa-item:hover { box-shadow: 0 8px 24px rgba(14,165,233,.12); transform: translateY(-1px); }
.meta { display: flex; align-items: center; gap: 10px; margin-bottom: 8px; }
.owner { font-weight: 600; color: #0ea5e9; font-size: 13px; }
.time { font-size: 12px; color: #94a3b8; }
.q { display: flex; align-items: flex-start; font-weight: 700; color: #0f172a; margin-bottom: 8px; font-size: 15px; }
.q-mark, .a-mark { flex-shrink: 0; width: 22px; height: 22px; border-radius: 7px; margin-right: 10px; display: inline-flex; align-items: center; justify-content: center; font-size: 12px; font-weight: 700; color: #fff; }
.q-mark { background: linear-gradient(135deg, #0ea5e9, #38bdf8); }
.a-mark { background: linear-gradient(135deg, #10b981, #34d399); }
.a { color: #475569; line-height: 1.75; white-space: pre-wrap; word-break: break-word; font-size: 14px; padding-left: 32px; }
.note { font-size: 13px; color: #b45309; margin-top: 10px; background: #fef3c7; padding: 7px 12px; border-radius: 10px; border: 1px solid #fde68a; }
.notes-box { margin-top: 10px; background: #f0f9ff; border: 1px solid #bae6fd; border-radius: 10px; padding: 10px 14px; }
.notes-title { font-size: 12px; font-weight: 700; color: #0369a1; margin-bottom: 8px; }
.note-row { display: flex; align-items: baseline; gap: 10px; padding: 5px 0; border-top: 1px dashed #bae6fd; font-size: 13px; }
.note-row:first-of-type { border-top: none; }
.note-author { font-weight: 600; color: #0ea5e9; flex-shrink: 0; }
.note-content { color: #334155; flex: 1; }
.note-time { font-size: 11px; color: #94a3b8; flex-shrink: 0; }
.ops { margin-top: 12px; text-align: right; }
</style>