<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { api } from '../api'

const list = ref([])
const keyword = ref('')
const loading = ref(false)

const permMap = {
  private: { label: '私有', type: 'info' },
  link: { label: '仅链接可见', type: 'warning' },
  public: { label: '公开', type: 'success' }
}

async function load() {
  loading.value = true
  try {
    list.value = await api.qaHistory(keyword.value.trim() || undefined)
  } catch (e) {
    ElMessage.error(e.message)
  } finally {
    loading.value = false
  }
}

function search() {
  load()
}

async function editNote(row) {
  try {
    const { value } = await ElMessageBox.prompt('填写备注', '修改备注', {
      inputValue: row.note || '',
      inputType: 'textarea',
      confirmButtonText: '保存',
      cancelButtonText: '取消'
    })
    await api.qaNote(row.id, value || '')
    ElMessage.success('备注已保存')
    load()
  } catch (e) {
    if (e && e.message) ElMessage.error(e.message)
  }
}

async function changePermission(row, val) {
  try {
    await api.qaPermission(row.id, val)
    ElMessage.success('权限已更新')
    load()
  } catch (e) {
    ElMessage.error(e.message)
  }
}

async function share(row) {
  if (row.permission === 'private') {
    return ElMessage.warning('私有问答不能分享，请先改为「仅链接可见」或「公开」')
  }
  try {
    const data = await api.qaShare(row.id)
    const url = `${window.location.origin}/share/${data.share_token}`
    try {
      await navigator.clipboard.writeText(url)
      ElMessage.success('分享链接已复制')
    } catch {
      ElMessage.info('复制失败，请手动复制下方链接')
    }
    await ElMessageBox.alert(url, '分享链接', { confirmButtonText: '知道了' })
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
        <b>我的问答历史</b>
        <div class="search">
          <el-input v-model="keyword" placeholder="搜索问题或回答..." clearable @keyup.enter="search" @clear="search" />
          <el-button type="primary" @click="search">搜索</el-button>
        </div>
      </div>
    </template>

    <div v-if="loading" class="empty">加载中…</div>
    <div v-else-if="!list.length" class="empty">暂无问答记录，去「AI 问答」提问吧</div>

    <div v-for="r in list" :key="r.id" class="qa-item">
      <div class="q">{{ r.question }}</div>
      <div class="a">{{ r.answer }}</div>
      <div v-if="r.sources && r.sources.length" class="src">
        参考：{{ r.sources.map(s => s.doc_name).join('、') }}
      </div>
      <div v-if="r.note" class="note">备注：{{ r.note }}</div>
      <div class="meta">
        <span class="time">{{ r.created_at }}</span>
        <el-tag size="small" :type="permMap[r.permission]?.type || 'info'">{{ permMap[r.permission]?.label }}</el-tag>
        <div class="ops">
          <el-select :model-value="r.permission" size="small" style="width: 130px" @change="(v) => changePermission(r, v)">
            <el-option label="私有" value="private" />
            <el-option label="仅链接可见" value="link" />
            <el-option label="公开" value="public" />
          </el-select>
          <el-button size="small" @click="editNote(r)">写备注</el-button>
          <el-button size="small" type="primary" @click="share(r)">分享链接</el-button>
        </div>
      </div>
    </div>
  </el-card>
</template>

<style scoped>
.wrap { border-radius: 16px; border: 1px solid #e7ebf3; }
.head { display: flex; justify-content: space-between; align-items: center; gap: 16px; flex-wrap: wrap; }
.search { display: flex; gap: 8px; width: 320px; }
.empty { color: #94a3b8; text-align: center; padding: 40px 0; font-size: 14px; }
.qa-item { padding: 14px; border: 1px solid #eef2f7; border-radius: 12px; margin-bottom: 12px; }
.q { font-weight: 600; color: #1e293b; margin-bottom: 6px; }
.a { color: #475569; line-height: 1.7; white-space: pre-wrap; word-break: break-word; font-size: 14px; }
.src { font-size: 12px; color: #64748b; margin-top: 8px; padding: 5px 10px; background: #eef2ff; border-radius: 8px; }
.note { font-size: 13px; color: #b45309; margin-top: 8px; background: #fef3c7; padding: 6px 10px; border-radius: 8px; }
.meta { display: flex; align-items: center; gap: 10px; margin-top: 10px; flex-wrap: wrap; }
.time { font-size: 12px; color: #94a3b8; }
.ops { margin-left: auto; display: flex; align-items: center; gap: 6px; flex-wrap: wrap; }
</style>