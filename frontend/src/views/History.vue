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
  <el-card shadow="never" class="wrap soft-card">
    <template #header>
      <div class="head">
        <div class="head-title">
          <span class="head-dot"></span>我的问答历史
        </div>
        <div class="search">
          <el-input v-model="keyword" placeholder="搜索问题或回答..." clearable @keyup.enter="search" @clear="search" />
          <el-button type="primary" @click="search">搜索</el-button>
        </div>
      </div>
    </template>

    <div v-if="loading" class="empty-tip">加载中…</div>
    <div v-else-if="!list.length" class="empty-tip">暂无问答记录，去「AI 问答」提问吧</div>

    <div v-for="r in list" :key="r.id" class="qa-item">
      <div class="q"><span class="q-mark">Q</span>{{ r.question }}</div>
      <div class="a"><span class="a-mark">A</span>{{ r.answer }}</div>
      <div v-if="r.sources && r.sources.length" class="src">
        📎 参考：{{ r.sources.map(s => s.doc_name).join('、') }}
      </div>
      <div v-if="r.note" class="note">📝 {{ r.note }}</div>
      <div v-if="r.notes && r.notes.length" class="notes-box">
        <div class="notes-title">📌 追加备注（{{ r.notes.length }} 条）</div>
        <div v-for="(n, i) in r.notes" :key="i" class="note-row">
          <span class="note-author">{{ n.username }}</span>
          <span class="note-content">{{ n.content }}</span>
          <span class="note-time">{{ n.created_at }}</span>
        </div>
      </div>
      <div v-if="r.teacher_note" class="teacher-note">👩‍🏫 教师评语：{{ r.teacher_note }}</div>
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
.head { display: flex; justify-content: space-between; align-items: center; gap: 16px; flex-wrap: wrap; }
.head-title { display: flex; align-items: center; font-weight: 700; }
.head-dot { width: 10px; height: 10px; border-radius: 50%; background: linear-gradient(135deg, #0ea5e9, #10b981); margin-right: 10px; box-shadow: 0 0 0 3px rgba(14,165,233,.15); }
.search { display: flex; gap: 8px; width: 320px; }
.qa-item {
  padding: 18px 20px; border: 1px solid #e6f0f8; border-radius: 14px; margin-bottom: 14px;
  background: #fff; box-shadow: 0 2px 10px rgba(15,118,110,.05);
  transition: box-shadow .2s ease, transform .2s ease;
}
.qa-item:hover { box-shadow: 0 8px 24px rgba(14,165,233,.12); transform: translateY(-1px); }
.q { display: flex; align-items: flex-start; font-weight: 700; color: #0f172a; margin-bottom: 8px; font-size: 15px; }
.q-mark, .a-mark {
  flex-shrink: 0; width: 22px; height: 22px; border-radius: 7px; margin-right: 10px;
  display: inline-flex; align-items: center; justify-content: center;
  font-size: 12px; font-weight: 700; color: #fff;
}
.q-mark { background: linear-gradient(135deg, #0ea5e9, #38bdf8); }
.a-mark { background: linear-gradient(135deg, #10b981, #34d399); }
.a { color: #475569; line-height: 1.75; white-space: pre-wrap; word-break: break-word; font-size: 14px; padding-left: 32px; }
.src { font-size: 12px; color: #0369a1; margin-top: 10px; padding: 7px 12px; background: linear-gradient(135deg, #e0f2fe, #ccfbf1); border-radius: 10px; border: 1px solid #bae6fd; }
.note { font-size: 13px; color: #b45309; margin-top: 10px; background: #fef3c7; padding: 7px 12px; border-radius: 10px; border: 1px solid #fde68a; }
.notes-box { margin-top: 10px; background: #f0f9ff; border: 1px solid #bae6fd; border-radius: 10px; padding: 10px 14px; }
.notes-title { font-size: 12px; font-weight: 700; color: #0369a1; margin-bottom: 8px; }
.note-row { display: flex; align-items: baseline; gap: 10px; padding: 5px 0; border-top: 1px dashed #bae6fd; font-size: 13px; }
.note-row:first-of-type { border-top: none; }
.note-author { font-weight: 600; color: #0ea5e9; flex-shrink: 0; }
.note-content { color: #334155; flex: 1; }
.note-time { font-size: 11px; color: #94a3b8; flex-shrink: 0; }
.meta { display: flex; align-items: center; gap: 10px; margin-top: 12px; flex-wrap: wrap; padding-top: 10px; border-top: 1px dashed #e6f0f8; }
.time { font-size: 12px; color: #94a3b8; }
.ops { margin-left: auto; display: flex; align-items: center; gap: 6px; flex-wrap: wrap; }
.teacher-note { font-size: 13px; color: #047857; margin-top: 10px; background: #d1fae5; padding: 7px 12px; border-radius: 10px; border: 1px solid #a7f3d0; }</style>