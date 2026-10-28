<script setup>
import { useUserStore } from '../stores/user'

const user = useUserStore()
</script>

<template>
  <el-card shadow="never" class="wrap soft-card">
    <div class="hero">
      <div class="logo">✦</div>
      <h2>欢迎，{{ user.username }}</h2>
      <p>高级管理员后台 · 你拥有最高权限：可管理用户、查看并删除全部公开内容</p>
      <div class="badges">
        <div class="badge"><span class="num">3</span><span class="lbl">角色体系</span></div>
        <div class="badge"><span class="num">20+</span><span class="lbl">功能接口</span></div>
        <div class="badge"><span class="num">100%</span><span class="lbl">本地部署</span></div>
      </div>
    </div>
  </el-card>
</template>

<style scoped>
.hero {
  text-align: center; padding: 52px 24px;
  background: linear-gradient(135deg, #0c4a6e 0%, #0ea5e9 60%, #10b981 130%);
  border-radius: 16px; color: #fff; position: relative; overflow: hidden;
}
.hero::before {
  content: ''; position: absolute; width: 300px; height: 300px; border-radius: 50%;
  background: rgba(255,255,255,.08); top: -120px; right: -80px;
}
.hero::after {
  content: ''; position: absolute; width: 220px; height: 220px; border-radius: 50%;
  background: rgba(255,255,255,.06); bottom: -100px; left: -60px;
}
.logo {
  width: 64px; height: 64px; margin: 0 auto 16px; border-radius: 18px;
  background: rgba(255,255,255,.2); border: 1px solid rgba(255,255,255,.4);
  color: #fff; font-size: 30px; display: flex; align-items: center; justify-content: center;
  backdrop-filter: blur(4px); position: relative; z-index: 1;
}
h2 { margin: 0 0 10px; font-size: 24px; position: relative; z-index: 1; }
p { margin: 0; color: rgba(255,255,255,.85); font-size: 14px; position: relative; z-index: 1; }
.badges { display: flex; gap: 16px; justify-content: center; margin-top: 28px; position: relative; z-index: 1; }
.badge {
  background: rgba(255,255,255,.15); border: 1px solid rgba(255,255,255,.25);
  border-radius: 14px; padding: 12px 22px; backdrop-filter: blur(4px);
  display: flex; flex-direction: column; gap: 2px;
}
.num { font-size: 20px; font-weight: 800; }
.lbl { font-size: 12px; color: rgba(255,255,255,.85); }
</style>