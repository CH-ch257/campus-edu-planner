import { defineStore } from 'pinia'

// 用户登录态（阶段一先做轻量版，账号/角色在阶段二完善）
export const useUserStore = defineStore('user', {
  state: () => ({
    username: localStorage.getItem('username') || '',
    userId: localStorage.getItem('user_id') || '',
    isAdmin: localStorage.getItem('adminSecret') === 'admin123456'
  }),
  actions: {
    setUser({ username, user_id }) {
      this.username = username
      this.userId = String(user_id || '')
      localStorage.setItem('username', username)
      localStorage.setItem('user_id', String(user_id || ''))
    },
    setAdmin(v) {
      this.isAdmin = v
      if (v) localStorage.setItem('adminSecret', 'admin123456')
      else localStorage.removeItem('adminSecret')
    },
    logout() {
      this.username = ''
      this.userId = ''
      this.isAdmin = false
      localStorage.removeItem('username')
      localStorage.removeItem('user_id')
      localStorage.removeItem('adminSecret')
    },
    adminSecret() {
      return this.isAdmin ? 'admin123456' : ''
    }
  }
})