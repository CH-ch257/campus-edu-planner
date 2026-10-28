import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    host: '0.0.0.0',
    port: 5173,
    proxy: {
      // ===== 后端独有 API 路径：前缀代理 =====
      '/documents': { target: 'http://127.0.0.1:8000', changeOrigin: true },
      '/ask': { target: 'http://127.0.0.1:8000', changeOrigin: true },
      '/upload': { target: 'http://127.0.0.1:8000', changeOrigin: true },
      '/file': { target: 'http://127.0.0.1:8000', changeOrigin: true },
      '/static': { target: 'http://127.0.0.1:8000', changeOrigin: true },
      '/me': { target: 'http://127.0.0.1:8000', changeOrigin: true },
      '/change_password': { target: 'http://127.0.0.1:8000', changeOrigin: true },
      '/users/': { target: 'http://127.0.0.1:8000', changeOrigin: true },
      '/teacher/qa': { target: 'http://127.0.0.1:8000', changeOrigin: true },
      '/qa': { target: 'http://127.0.0.1:8000', changeOrigin: true },
      // ===== 与前端路由同前缀的后端接口：正则精确匹配（后端均带尾斜杠或特征子路径）=====
      // /login、/register 是前端页面路由（无尾斜杠），后端接口带尾斜杠 /login/ /register/
      '^/login/$': { target: 'http://127.0.0.1:8000', changeOrigin: true },
      '^/register/$': { target: 'http://127.0.0.1:8000', changeOrigin: true },
      // /admin 为前端路由（/admin /admin/users /admin/public），后端管理接口均带特征子路径
      '^/admin/users/\\d+/status$': { target: 'http://127.0.0.1:8000', changeOrigin: true },
      '^/admin/users/$': { target: 'http://127.0.0.1:8000', changeOrigin: true },
      '^/admin/documents': { target: 'http://127.0.0.1:8000', changeOrigin: true },
      '^/admin/qa': { target: 'http://127.0.0.1:8000', changeOrigin: true },
      '^/admin/teachers': { target: 'http://127.0.0.1:8000', changeOrigin: true }
    }
  }
})
