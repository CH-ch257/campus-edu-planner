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
        <b>公开内容总管理</b>
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
      <div class="q">{{ r.question }}</div>
      <div class="a">{{ r.answer }}</div>
      <div v-if="r.note" class="note">备注：{{ r.note }}</div>
      <div class="ops">
        <el-button size="small" type="danger" @click="del(r)">删除</el-button>
      </div>
    </div>
  </el-card>
</template>

<style scoped>
.wrap { border-radius: 16px; border: 1px solid #e7ebf3; }
.head { display: flex; align-items: center; gap: 12px; flex-wrap: wrap; }
.tip { font-size: 12px; color: #94a3b8; font-weight: normal; }
.empty { color: #94a3b8; text-align: center; padding: 40px 0; font-size: 14px; }
.qa-item { padding: 14px; border: 1px solid #eef2f7; border-radius: 12px; margin-bottom: 12px; }
.meta { display: flex; align-items: center; gap: 10px; margin-bottom: 6px; }
.owner { font-weight: 600; color: #4f46e5; font-size: 13px; }
.time { font-size: 12px; color: #94a3b8; }
.q { font-weight: 600; color: #1e293b; margin-bottom: 6px; }
.a { color: #475569; line-height: 1.7; white-space: pre-wrap; word-break: break-word; font-size: 14px; }
.note { font-size: 13px; color: #b45309; margin-top: 8px; background: #fef3c7; padding: 6px 10px; border-radius: 8px; }
.ops { margin-top: 10px; text-align: right; }
</style>