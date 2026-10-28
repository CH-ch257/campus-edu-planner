import { defineStore } from 'pinia'

// 用户登录态：token + 角色（student / teacher / admin）
export const useUserStore = defineStore('user', {
  state: () => ({
    token: localStorage.getItem('token') || '',
    username: localStorage.getItem('username') || '',
    userId: localStorage.getItem('user_id') || '',
    role: localStorage.getItem('role') || ''
  }),
  getters: {
    isLoggedIn: (state) => !!state.token,
    isStudent: (state) => state.role === 'student',
    isTeacher: (state) => state.role === 'teacher',
    isAdmin: (state) => state.role === 'admin'
  },
  actions: {
    setAuth({ token, user_id, username, role }) {
      this.token = token
      this.username = username
      this.userId = String(user_id || '')
      this.role = role
      localStorage.setItem('token', token)
      localStorage.setItem('username', username)
      localStorage.setItem('user_id', String(user_id || ''))
      localStorage.setItem('role', role)
    },
    logout() {
      this.token = ''
      this.username = ''
      this.userId = ''
      this.role = ''
      localStorage.removeItem('token')
      localStorage.removeItem('username')
      localStorage.removeItem('user_id')
      localStorage.removeItem('role')
    },
    // 文档管理密钥沿用原有硬编码逻辑，仅教师可用
    adminSecret() {
      return this.role === 'teacher' ? 'admin123456' : ''
    }
  }
})