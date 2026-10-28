<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { api } from '../api'

const list = ref([])
const loading = ref(false)

async function load() {
  loading.value = true
  try {
    list.value = await api.teacherPublicQa()
  } catch (e) {
    ElMessage.error(e.message)
  } finally {
    loading.value = false
  }
}

async function del(row) {
  try {
    await ElMessageBox.confirm(
      '确定删除这条公开问答吗？仅能删除与你上传文档相关的问答。',
      '删除确认',
      { type: 'warning' }
    )
  } catch (e) {
    return
  }
  try {
    await api.deletePublicQa(row.id)
    ElMessage.success('删除成功')
    load()
  } catch (e) {
    ElMessage.error(e.message)
  }
}

async function noteQa(row) {
  try {
    const { value } = await ElMessageBox.prompt(
      '给学生这条问答写评语（学生可见），留空可清除评语：',
      row.teacher_note ? '修改评语' : '写评语',
      { inputValue: row.teacher_note || '', inputPlaceholder: '例如：回答得很完整，继续保持！', confirmButtonText: '保存', cancelButtonText: '取消' }
    )
    await api.teacherQaNote(row.id, value || '')
    ElMessage.success('评语已保存')
    load()
  } catch (e) {
    if (e && e.message) ElMessage.error(e.message)
  }
}

onMounted(load)
</script>

<template>
  <el-card shadow="never" class="wrap">
    <template #header>
      <div class="head">
        <div class="card-title"><span class="head-dot"></span>公开内容管理</div>
        <span class="tip">仅展示学生标记为「公开」的问答与备注；只能删除与你上传文档相关的公开问答</span>
      </div>
    </template>

    <div v-if="loading" class="empty">加载中…</div>
    <div v-else-if="!list.length" class="empty">暂无学生公开问答</div>

    <div v-for="r in list" :key="r.id" class="qa-item">
      <div class="meta">
        <span class="owner">{{ r.username }}</span>
        <span class="time">{{ r.created_at }}</span>
      </div>
      <div class="q"><span class="q-mark">Q</span>{{ r.question }}</div>
      <div class="a"><span class="a-mark">A</span>{{ r.answer }}</div>
      <div v-if="r.note" class="note">📝 {{ r.note }}</div>
      <div v-if="r.teacher_note" class="teacher-note">👩‍🏫 教师评语：{{ r.teacher_note }}</div>
      <div class="ops">
        <el-button size="small" type="primary" plain @click="noteQa(r)">
          {{ r.teacher_note ? '改评语' : '写评语' }}
        </el-button>
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
.teacher-note { font-size: 13px; color: #047857; margin-top: 10px; background: #d1fae5; padding: 7px 12px; border-radius: 10px; border: 1px solid #a7f3d0; }
.ops { margin-top: 12px; text-align: right; }
.ops .el-button + .el-button { margin-left: 8px; }
</style>