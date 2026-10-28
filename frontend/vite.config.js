import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    host: '0.0.0.0',
    port: 5173,
    proxy: {
      // 后端接口统一走相对路径，dev 时转发到本地 FastAPI
      '/documents': { target: 'http://127.0.0.1:8000', changeOrigin: true },
      '/ask': { target: 'http://127.0.0.1:8000', changeOrigin: true },
      '/login': { target: 'http://127.0.0.1:8000', changeOrigin: true },
      '/register': { target: 'http://127.0.0.1:8000', changeOrigin: true },
      '/upload': { target: 'http://127.0.0.1:8000', changeOrigin: true },
      '/file': { target: 'http://127.0.0.1:8000', changeOrigin: true },
      '/admin': { target: 'http://127.0.0.1:8000', changeOrigin: true },
      '/static': { target: 'http://127.0.0.1:8000', changeOrigin: true }
    }
  }
})