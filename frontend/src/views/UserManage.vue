<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { api } from '../api'

const list = ref([])
const username = ref('')
const password = ref('')
const loading = ref(false)
const creating = ref(false)

const roleMap = { student: '学生', teacher: '老师', admin: '高级管理员' }

async function load() {
  loading.value = true
  try {
    list.value = await api.adminUsers()
  } catch (e) {
    ElMessage.error(e.message)
  } finally {
    loading.value = false
  }
}

async function createTeacher() {
  if (!username.value.trim() || !password.value) return ElMessage.warning('请输入用户名和密码')
  creating.value = true
  try {
    await api.adminCreateTeacher(username.value.trim(), password.value)
    ElMessage.success('老师账号已创建')
    username.value = ''
    password.value = ''
    load()
  } catch (e) {
    ElMessage.error(e.message)
  } finally {
    creating.value = false
  }
}

async function delUser(row) {
  try {
    await ElMessageBox.confirm(
      `确定删除账号「${row.username}」吗？该用户的文档与问答记录将一并删除，不可恢复。`,
      '删除确认',
      { type: 'warning', confirmButtonText: '删除', cancelButtonText: '取消' }
    )
  } catch (e) {
    return
  }
  try {
    await api.adminDeleteUser(row.id)
    ElMessage.success('用户已删除')
    load()
  } catch (e) {
    ElMessage.error(e.message)
  }
}

onMounted(load)
</script>

<template>
  <el-row :gutter="20">
    <el-col :xs="24" :md="8">
      <el-card shadow="never" class="wrap soft-card">
        <template #header>
          <div class="card-title"><span class="head-dot"></span>新增老师账号</div>
        </template>
        <el-form @submit.prevent="createTeacher">
          <el-input v-model="username" placeholder="老师用户名" class="mb" />
          <el-input v-model="password" type="password" placeholder="初始密码（至少4位）" show-password class="mb" />
          <el-button type="primary" class="full" :loading="creating" @click="createTeacher">创建账号</el-button>
        </el-form>
      </el-card>
    </el-col>

    <el-col :xs="24" :md="16">
      <el-card shadow="never" class="wrap soft-card">
        <template #header>
          <div class="card-title"><span class="head-dot head-dot-2"></span>用户列表</div>
        </template>
        <el-table :data="list" v-loading="loading" class="user-table" :header-cell-style="{ background: '#f0f9ff', color: '#0369a1', fontWeight: 700 }">
          <el-table-column prop="username" label="用户名" />
          <el-table-column label="角色" width="120">
            <template #default="{ row }">
              <el-tag :type="row.role === 'admin' ? 'danger' : row.role === 'teacher' ? 'warning' : 'primary'" size="small" effect="light">
                {{ roleMap[row.role] }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="状态" width="100">
            <template #default="{ row }">
              <el-tag :type="row.status === 1 ? 'success' : 'info'" size="small" effect="light">{{ row.status === 1 ? '启用' : '禁用' }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="created_at" label="创建时间" min-width="140" />
          <el-table-column label="操作" width="110">
            <template #default="{ row }">
              <el-button
                v-if="row.role !== 'admin'"
                size="small"
                type="danger"
                plain
                @click="delUser(row)"
              >
                删除
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-card>
    </el-col>
  </el-row>
</template>

<style scoped>
.card-title { display: flex; align-items: center; font-weight: 700; }
.head-dot { width: 10px; height: 10px; border-radius: 50%; background: linear-gradient(135deg, #0ea5e9, #10b981); margin-right: 10px; box-shadow: 0 0 0 3px rgba(14,165,233,.15); }
.head-dot-2 { background: linear-gradient(135deg, #10b981, #0ea5e9); box-shadow: 0 0 0 3px rgba(16,185,129,.15); }
.mb { margin-bottom: 14px; }
.full { width: 100%; }
.user-table { border-radius: 12px; overflow: hidden; }
.user-table :deep(.el-table__inner-wrapper) { border-radius: 12px; }
</style>