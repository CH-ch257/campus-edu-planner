<script setup>
import { useUserStore } from '../stores/user'

const user = useUserStore()
</script>

<template>
  <el-card shadow="never" class="wrap">
    <div class="hero">
      <div class="logo">✦</div>
      <h2>欢迎，{{ user.username }}</h2>
      <p>高级管理员后台。你拥有最高权限：可管理用户、查看并删除全部公开内容。</p>
    </div>
  </el-card>
</template>

<style scoped>
.wrap { border-radius: 16px; border: 1px solid #e7ebf3; }
.hero { text-align: center; padding: 60px 20px; }
.logo { width: 60px; height: 60px; margin: 0 auto 16px; border-radius: 16px; background: linear-gradient(135deg, #6366f1, #8b5cf6); color: #fff; font-size: 30px; display: flex; align-items: center; justify-content: center; }
h2 { margin: 0 0 8px; color: #1e293b; }
p { color: #64748b; font-size: 14px; }
</style>