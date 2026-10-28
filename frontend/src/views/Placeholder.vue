<script setup>
import { useRoute } from 'vue-router'

const route = useRoute()
</script>

<template>
  <el-card shadow="never" class="placeholder">
    <el-empty :description="`「${route.meta.title}」功能开发中，敬请期待`" />
  </el-card>
</template>

<style scoped>
.placeholder { border-radius: 16px; border: 1px solid #e7ebf3; min-height: 400px; display: flex; align-items: center; justify-content: center; }
</style>