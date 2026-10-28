<script setup>
import { useUserStore } from './stores/user'
import { ElMessage, ElMessageBox } from 'element-plus'

const user = useUserStore()

async function toggleAdmin() {
  if (user.isAdmin) {
    user.setAdmin(false)
    ElMessage.success('已退出管理员模式')
    return
  }
  try {
    const { value } = await ElMessageBox.prompt('请输入管理员密钥', '管理员登录', {
      inputType: 'password',
      confirmButtonText: '登录',
      cancelButtonText: '取消'
    })
    if (value === 'admin123456') {
      user.setAdmin(true)
      ElMessage.success('管理员登录成功')
    } else {
      ElMessage.error('密钥错误')
    }
  } catch (e) {
    /* 用户取消 */
  }
}
</script>

<template>
  <div class="app-shell">
    <header class="topbar">
      <div class="brand"><span class="logo">✦</span>校园资料AI检索助手</div>
      <div class="actions">
        <el-tag v-if="user.username" class="me" round effect="light">{{ user.username }}</el-tag>
        <el-button :type="user.isAdmin ? 'warning' : 'default'" round @click="toggleAdmin">
          {{ user.isAdmin ? '管理员模式（已开启）' : '管理员登录' }}
        </el-button>
      </div>
    </header>
    <main class="main">
      <router-view />
    </main>
  </div>
</template>

<style>
:root {
  --primary: #6366f1;
  --primary-2: #8b5cf6;
  --bg: #f3f5fb;
  --grad: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
}
* { box-sizing: border-box; }
body { margin: 0; background: var(--bg); font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Microsoft YaHei", sans-serif; }
.app-shell { min-height: 100vh; display: flex; flex-direction: column; }
.topbar {
  height: 64px; position: sticky; top: 0; z-index: 100;
  display: flex; align-items: center; justify-content: space-between;
  padding: 0 24px; background: rgba(255,255,255,.85);
  backdrop-filter: saturate(180%) blur(12px);
  border-bottom: 1px solid #e7ebf3;
}
.brand { display: flex; align-items: center; font-weight: 700; font-size: 18px; color: #1e293b; }
.brand .logo {
  width: 34px; height: 34px; border-radius: 10px; background: var(--grad);
  color: #fff; display: inline-flex; align-items: center; justify-content: center;
  margin-right: 10px; font-size: 17px;
}
.actions { display: flex; align-items: center; }
.actions .me { margin-right: 10px; }
.main { flex: 1; width: 100%; max-width: 1280px; margin: 0 auto; padding: 24px; }
</style>