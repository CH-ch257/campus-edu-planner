<script setup>
import { ref, computed, nextTick, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { api, fileUrl } from '../api'
import { useUserStore } from '../stores/user'

const user = useUserStore()

// 问答
const question = ref('')
const messages = ref([{ role: 'ai', content: '你好！我是校园资料助手，可以问我关于上传文档里的内容哦～', sources: [] }])
const chatBox = ref(null)
const asking = ref(false)

// 文档库
const docs = ref([])
const sortMode = ref('time')
const searchKeyword = ref('')
const activeNames = ref([])
const fileInput = ref(null)

// 弹窗
const docDetailVisible = ref(false)
const currentDoc = ref(null)
const verVisible = ref(false)
const versions = ref([])

const catColors = {
  '培养方案': { bg: '#eef2ff', txt: '#4f46e5' },
  '考试通知': { bg: '#fee2e2', txt: '#dc2626' },
  '课件资料': { bg: '#dcfce7', txt: '#16a34a' },
  '行政通知': { bg: '#fef3c7', txt: '#b45309' },
  '社团文件': { bg: '#f1f5f9', txt: '#475569' },
  '作业': { bg: '#f3e8ff', txt: '#7c3aed' },
  '未分类': { bg: '#e0f2fe', txt: '#0369a1' }
}
const catStyle = (c) => catColors[c] || catColors['未分类']

const groupedDocs = computed(() => {
  const groups = {}
  docs.value.forEach(d => {
    const cat = d.category || '未分类'
    ;(groups[cat] = groups[cat] || []).push(d)
  })
  return groups
})

function scrollBottom() {
  nextTick(() => {
    if (chatBox.value) chatBox.value.scrollTop = chatBox.value.scrollHeight
  })
}

async function ask() {
  const q = question.value.trim()
  if (!q || asking.value) return
  messages.value.push({ role: 'user', content: q, sources: [] })
  question.value = ''
  asking.value = true
  scrollBottom()
  try {
    const data = await api.ask(q)
    messages.value.push({ role: 'ai', content: data.answer, sources: data.sources || [] })
  } catch (e) {
    messages.value.push({ role: 'ai', content: e.message, sources: [] })
  } finally {
    asking.value = false
    scrollBottom()
  }
}

async function loadDocs() {
  try {
    let list = await api.listDocuments()
    if (sortMode.value === 'name') list = list.sort((a, b) => a.filename.localeCompare(b.filename, 'zh'))
    docs.value = list
  } catch (e) {
    ElMessage.error(e.message)
  }
}

async function searchDocs() {
  const k = searchKeyword.value.trim()
  if (!k) return loadDocs()
  try {
    let list = await api.searchDocuments(k)
    if (sortMode.value === 'name') list = list.sort((a, b) => a.filename.localeCompare(b.filename, 'zh'))
    docs.value = list
  } catch (e) {
    ElMessage.error(e.message)
  }
}

function toggleSort() {
  sortMode.value = sortMode.value === 'time' ? 'name' : 'time'
  loadDocs()
}

async function viewDoc(id) {
  try {
    const doc = await api.getDocument(id)
    currentDoc.value = doc
    docDetailVisible.value = true
  } catch (e) {
    ElMessage.error(e.message)
  }
}

function openFile() {
  if (currentDoc.value) window.open(fileUrl(currentDoc.value.id), '_blank')
}

async function upload() {
  const f = fileInput.value?.files?.[0]
  if (!f) return ElMessage.warning('请先选择文件')
  try {
    let d = await api.upload(f)
    if (d.need_confirm) {
      await ElMessageBox.confirm(
        `已存在同名文档《${f.name}》（当前版本 v${d.current_version}），确定覆盖并升级为新版本吗？`,
        '覆盖确认',
        { type: 'warning', confirmButtonText: '覆盖升级', cancelButtonText: '取消' }
      )
      d = await api.upload(f, 'yes')
    }
    ElMessage.success(`上传成功：${d.filename}（${d.category} · v${d.version}）`)
    if (fileInput.value) fileInput.value.value = ''
    loadDocs()
  } catch (e) {
    ElMessage.error(e.message)
  }
}

async function delDoc(id) {
  try {
    await ElMessageBox.confirm('确定删除该文档吗？此操作不可恢复。', '删除确认', { type: 'warning' })
  } catch (e) {
    return
  }
  try {
    await api.deleteDocument(id)
    ElMessage.success('删除成功')
    loadDocs()
  } catch (e) {
    ElMessage.error(e.message)
  }
}

async function editCat(id, old) {
  try {
    const { value } = await ElMessageBox.prompt(
      '请输入分类（培养方案/考试通知/课件资料/行政通知/社团文件/作业/未分类）',
      '修改分类',
      { inputValue: old, confirmButtonText: '确定', cancelButtonText: '取消' }
    )
    await api.updateCategory(id, value)
    ElMessage.success('分类已更新')
    loadDocs()
  } catch (e) {
    if (e && e.message) ElMessage.error(e.message)
  }
}

async function showVer(id) {
  try {
    const data = await api.getVersions(id)
    versions.value = data
    verVisible.value = true
  } catch (e) {
    ElMessage.error(e.message)
  }
}

async function rollback(id, ver) {
  try {
    await ElMessageBox.confirm(`确定回滚到 v${ver} 吗？当前最新版将被标记为历史版。`, '回滚确认', { type: 'warning' })
  } catch (e) {
    return
  }
  try {
    await api.rollback(id)
    ElMessage.success('回滚成功')
    verVisible.value = false
    loadDocs()
  } catch (e) {
    ElMessage.error(e.message)
  }
}

onMounted(loadDocs)
</script>

<template>
  <el-row :gutter="20">
    <!-- 问答区 -->
    <el-col :xs="24" :md="16">
      <el-card shadow="never" class="chat-card soft-card">
        <template #header>
          <div class="card-head">
            <span class="head-dot"></span>智能问答
            <span class="head-sub">学生 / 老师 / 管理员均可使用</span>
          </div>
        </template>
        <div ref="chatBox" class="chat-box">
          <div v-for="(m, i) in messages" :key="i" class="msg" :class="m.role">
            <div v-if="m.role === 'ai'" class="avatar">✦</div>
            <div class="msg-body">
              <div class="bubble">{{ m.content }}</div>
              <div v-if="m.sources && m.sources.length" class="source-tag">
                📎 参考：{{ m.sources.map(s => s.doc_name).join('、') }}
              </div>
            </div>
          </div>
          <div v-if="asking" class="msg ai">
            <div class="avatar">✦</div>
            <div class="msg-body"><div class="bubble typing">思考中<span>.</span><span>.</span><span>.</span></div></div>
          </div>
        </div>
        <div class="input-bar">
          <el-input
            v-model="question"
            placeholder="输入你的问题..."
            size="large"
            @keyup.enter="ask"
          />
          <el-button type="primary" size="large" :loading="asking" @click="ask">提问</el-button>
        </div>
      </el-card>
    </el-col>

    <!-- 文档库 -->
    <el-col :xs="24" :md="8">
      <el-card shadow="never" class="doc-card soft-card">
        <template #header>
          <div class="card-head"><span class="head-dot head-dot-2"></span>文档库 · 按分类浏览</div>
        </template>
        <el-input v-model="searchKeyword" placeholder="搜索文件名..." clearable @input="searchDocs" />
        <el-button class="sort-btn" @click="toggleSort">
          排序：{{ sortMode === 'time' ? '按上传时间' : '按文件名' }}
        </el-button>

        <div v-if="!docs.length" class="empty-tip">暂无文档</div>
        <el-collapse v-model="activeNames">
          <el-collapse-item v-for="(list, cat) in groupedDocs" :key="cat" :name="cat">
            <template #title>
              <span class="cat-badge" :style="{ background: catStyle(cat).bg, color: catStyle(cat).txt }">{{ cat }}</span>
              <span class="cat-count">{{ list.length }} 个文档</span>
            </template>
            <div v-for="d in list" :key="d.id" class="doc-item">
              <div class="doc-row">
                <span class="doc-title" @click="viewDoc(d.id)">📄 {{ d.filename }}</span>
                <el-tag size="small" type="info" effect="plain">v{{ d.version }}</el-tag>
              </div>
              <div v-if="user.isTeacher" class="doc-actions">
                <el-button size="small" @click="editCat(d.id, d.category)">改分类</el-button>
                <el-button size="small" @click="showVer(d.id)">历史版本</el-button>
                <el-button size="small" type="danger" plain @click="delDoc(d.id)">删除</el-button>
              </div>
            </div>
          </el-collapse-item>
        </el-collapse>

        <template v-if="user.isTeacher">
          <el-divider>教师上传</el-divider>
          <input ref="fileInput" type="file" accept=".pdf,.doc,.docx,.txt" class="file-input" />
          <el-button type="success" class="upload-btn" @click="upload">上传文档</el-button>
        </template>
      </el-card>
    </el-col>
  </el-row>

  <!-- 文档详情 -->
  <el-dialog v-model="docDetailVisible" :title="currentDoc?.filename || '文档详情'" width="70%" top="5vh">
    <el-button type="primary" plain size="small" @click="openFile">打开原文件</el-button>
    <pre class="doc-content">{{ currentDoc?.content }}</pre>
  </el-dialog>

  <!-- 历史版本 -->
  <el-dialog v-model="verVisible" title="历史版本" width="420px">
    <div v-for="v in versions" :key="v.id" class="ver-row">
      <span>v{{ v.version }}</span>
      <el-tag v-if="v.is_latest" type="success" size="small">当前最新版</el-tag>
      <el-button v-if="!v.is_latest" size="small" type="warning" @click="rollback(v.id, v.version)">回滚到此版本</el-button>
    </div>
    <div v-if="!versions.length" class="empty-tip">没有历史版本</div>
  </el-dialog>
</template>

<style scoped>
.card-head { display: flex; align-items: center; font-weight: 700; color: #0f172a; }
.head-dot { width: 10px; height: 10px; border-radius: 50%; background: linear-gradient(135deg, #0ea5e9, #10b981); margin-right: 10px; box-shadow: 0 0 0 3px rgba(14,165,233,.15); }
.head-dot-2 { background: linear-gradient(135deg, #10b981, #0ea5e9); box-shadow: 0 0 0 3px rgba(16,185,129,.15); }
.head-sub { font-weight: 400; font-size: 12px; color: #94a3b8; margin-left: 10px; }
.chat-box {
  height: 500px; overflow-y: auto;
  background: linear-gradient(180deg, #f8fdfd 0%, #f6fafd 100%);
  border: 1px solid #e2ecf5; border-radius: 14px; padding: 18px;
}
.msg { display: flex; margin-bottom: 16px; max-width: 88%; }
.msg.user { flex-direction: row-reverse; margin-left: auto; }
.msg.ai { align-items: flex-start; }
.avatar {
  width: 32px; height: 32px; border-radius: 50%; flex-shrink: 0;
  background: linear-gradient(135deg, #0ea5e9, #10b981); color: #fff;
  display: flex; align-items: center; justify-content: center; font-size: 14px;
  box-shadow: 0 4px 10px rgba(14,165,233,.3); margin: 4px 10px 0 0;
}
.msg.user .avatar { margin: 4px 0 0 10px; background: linear-gradient(135deg, #64748b, #475569); box-shadow: 0 4px 10px rgba(71,85,105,.3); }
.msg-body { display: flex; flex-direction: column; }
.bubble {
  border-radius: 16px; padding: 11px 16px; line-height: 1.65; font-size: 14px;
  white-space: pre-wrap; word-break: break-word; max-width: 100%;
}
.msg.user .bubble { background: linear-gradient(135deg, #0ea5e9, #14b8a6); color: #fff; border-bottom-right-radius: 4px; box-shadow: 0 4px 12px rgba(14,165,233,.22); }
.msg.ai .bubble { background: #fff; border: 1px solid #e2ecf5; border-bottom-left-radius: 4px; box-shadow: 0 2px 8px rgba(15,118,110,.05); }
.source-tag {
  font-size: 12px; color: #0369a1; margin-top: 7px; padding: 6px 12px;
  background: linear-gradient(135deg, #e0f2fe, #ccfbf1); border-radius: 10px;
  border: 1px solid #bae6fd; align-self: flex-start;
}
.typing span { animation: blink 1.4s infinite; }
.typing span:nth-child(2) { animation-delay: .2s; }
.typing span:nth-child(3) { animation-delay: .4s; }
@keyframes blink { 0%, 80%, 100% { opacity: 0; } 40% { opacity: 1; } }
.input-bar {
  display: flex; gap: 10px; margin-top: 16px; padding: 10px;
  background: rgba(255,255,255,.8); border: 1px solid #e2ecf5; border-radius: 16px;
  box-shadow: 0 4px 14px rgba(15,118,110,.06);
}
.input-bar .el-input { flex: 1; }
.input-bar .el-input__wrapper { background: transparent; }
.sort-btn { width: 100%; margin: 14px 0; }
.cat-badge { font-size: 12px; padding: 4px 10px; border-radius: 8px; font-weight: 600; }
.cat-count { color: #94a3b8; font-size: 12px; margin-left: 8px; }
.doc-item { padding: 12px 6px; border-bottom: 1px solid #f2f7fb; transition: background .15s ease; border-radius: 10px; }
.doc-item:hover { background: #f6fbfe; }
.doc-row { display: flex; align-items: center; justify-content: space-between; gap: 8px; }
.doc-title { cursor: pointer; color: #0ea5e9; font-weight: 600; font-size: 13px; word-break: break-all; transition: color .15s; }
.doc-title:hover { color: #0284c7; text-decoration: underline; }
.doc-actions { display: flex; gap: 6px; margin-top: 8px; }
.file-input { display: block; margin-bottom: 10px; font-size: 13px; color: #64748b; }
.upload-btn { width: 100%; }
.doc-content { white-space: pre-wrap; max-height: 60vh; overflow-y: auto; background: #f8fafc; padding: 16px; border-radius: 10px; font-size: 13px; }
.ver-row { display: flex; align-items: center; gap: 10px; padding: 8px 0; border-bottom: 1px solid #f2f4f9; }
</style>