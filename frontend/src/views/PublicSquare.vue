<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { api } from '../api'

const list = ref([])
const loading = ref(false)
const noteText = ref({})   // 每条问答的备注输入框内容

async function load() {
  loading.value = true
  try {
    list.value = await api.publicQa()
  } catch (e) {
    ElMessage.error(e.message)
  } finally {
    loading.value = false
  }
}

async function addNote(r) {
  const content = (noteText.value[r.id] || '').trim()
  if (!content) {
    ElMessage.warning('请输入备注内容')
    return
  }
  try {
    const res = await api.qaAddNote(r.id, content)
    ElMessage.success(`备注已添加（当前 ${res.total} 条）`)
    noteText.value[r.id] = ''
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
        <div class="card-title"><span class="head-dot"></span>问答广场</div>
        <span class="tip">全校同学设为「公开」的问答都会展示在这里，可对问答追加备注（最多 10 条），点击提问者名字可进入其个人主页</span>
      </div>
    </template>

    <div v-if="loading" class="empty">加载中…</div>
    <div v-else-if="!list.length" class="empty">暂时没有公开问答，去提问并把问答设为「公开」就能分享给大家</div>

    <div v-for="r in list" :key="r.id" class="qa-item">
      <div class="meta">
        <router-link :to="`/u/${r.user_id}`" class="owner-link">🧑‍🎓 {{ r.username }}</router-link>
        <el-tag size="small" type="success" effect="light" round>公开</el-tag>
        <span class="time">{{ r.created_at }}</span>
      </div>
      <div class="q"><span class="q-mark">Q</span>{{ r.question }}</div>
      <div class="a"><span class="a-mark">A</span>{{ r.answer }}</div>
      <div v-if="r.note" class="note">📝 {{ r.note }}</div>
      <div v-if="r.teacher_note" class="teacher-note">👩‍🏫 教师评语：{{ r.teacher_note }}</div>

      <div v-if="r.notes && r.notes.length" class="notes-box">
        <div class="notes-title">📌 追加备注（{{ r.notes.length }} 条）</div>
        <div v-for="(n, i) in r.notes" :key="i" class="note-row">
          <span class="note-author">{{ n.username }}</span>
          <span class="note-content">{{ n.content }}</span>
          <span class="note-time">{{ n.created_at }}</span>
        </div>
      </div>

      <div class="add-note">
        <el-input
          v-model="noteText[r.id]"
          size="small"
          placeholder="追加一条备注（学习笔记/补充说明）"
          maxlength="200"
          show-word-limit
          clearable
          @keyup.enter="addNote(r)"
        />
        <el-button size="small" type="primary" plain @click="addNote(r)">添加备注</el-button>
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
.owner-link { font-weight: 600; color: #0ea5e9; font-size: 13px; text-decoration: none; }
.owner-link:hover { text-decoration: underline; }
.time { font-size: 12px; color: #94a3b8; }
.q { display: flex; align-items: flex-start; font-weight: 700; color: #0f172a; margin-bottom: 8px; font-size: 15px; }
.q-mark, .a-mark { flex-shrink: 0; width: 22px; height: 22px; border-radius: 7px; margin-right: 10px; display: inline-flex; align-items: center; justify-content: center; font-size: 12px; font-weight: 700; color: #fff; }
.q-mark { background: linear-gradient(135deg, #0ea5e9, #38bdf8); }
.a-mark { background: linear-gradient(135deg, #10b981, #34d399); }
.a { color: #475569; line-height: 1.75; white-space: pre-wrap; word-break: break-word; font-size: 14px; padding-left: 32px; }
.note { font-size: 13px; color: #b45309; margin-top: 10px; background: #fef3c7; padding: 7px 12px; border-radius: 10px; border: 1px solid #fde68a; }
.teacher-note { font-size: 13px; color: #047857; margin-top: 10px; background: #d1fae5; padding: 7px 12px; border-radius: 10px; border: 1px solid #a7f3d0; }
.notes-box { margin-top: 10px; background: #f0f9ff; border: 1px solid #bae6fd; border-radius: 10px; padding: 10px 14px; }
.notes-title { font-size: 12px; font-weight: 700; color: #0369a1; margin-bottom: 8px; }
.note-row { display: flex; align-items: baseline; gap: 10px; padding: 5px 0; border-top: 1px dashed #bae6fd; font-size: 13px; }
.note-row:first-of-type { border-top: none; }
.note-author { font-weight: 600; color: #0ea5e9; flex-shrink: 0; }
.note-content { color: #334155; flex: 1; }
.note-time { font-size: 11px; color: #94a3b8; flex-shrink: 0; }
.add-note { display: flex; gap: 8px; margin-top: 12px; }
.add-note .el-input { flex: 1; }
.empty { text-align: center; color: #94a3b8; padding: 60px 0; font-size: 14px; }
</style>
