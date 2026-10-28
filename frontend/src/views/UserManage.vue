<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
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

async function toggleStatus(row) {
  const next = row.status === 1 ? 0 : 1
  try {
    await api.adminSetStatus(row.id, next)
    ElMessage.success(next === 1 ? '已启用' : '已禁用')
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
      <el-card shadow="never" class="wrap">
        <template #header><b>新增老师账号</b></template>
        <el-form @submit.prevent="createTeacher">
          <el-input v-model="username" placeholder="老师用户名" class="mb" />
          <el-input v-model="password" type="password" placeholder="初始密码（至少4位）" show-password class="mb" />
          <el-button type="primary" class="full" :loading="creating" @click="createTeacher">创建账号</el-button>
        </el-form>
      </el-card>
    </el-col>

    <el-col :xs="24" :md="16">
      <el-card shadow="never" class="wrap">
        <template #header><b>用户列表</b></template>
        <el-table :data="list" v-loading="loading" border stripe>
          <el-table-column prop="username" label="用户名" />
          <el-table-column label="角色" width="120">
            <template #default="{ row }">
              <el-tag :type="row.role === 'admin' ? 'danger' : row.role === 'teacher' ? 'warning' : 'primary'" size="small">
                {{ roleMap[row.role] }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="状态" width="100">
            <template #default="{ row }">
              <el-tag :type="row.status === 1 ? 'success' : 'info'" size="small">{{ row.status === 1 ? '启用' : '禁用' }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="created_at" label="创建时间" min-width="140" />
          <el-table-column label="操作" width="110">
            <template #default="{ row }">
              <el-button
                v-if="row.role === 'teacher'"
                size="small"
                :type="row.status === 1 ? 'danger' : 'success'"
                @click="toggleStatus(row)"
              >
                {{ row.status === 1 ? '禁用' : '启用' }}
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-card>
    </el-col>
  </el-row>
</template>

<style scoped>
.wrap { border-radius: 16px; border: 1px solid #e7ebf3; }
.mb { margin-bottom: 14px; }
.full { width: 100%; }
</style>