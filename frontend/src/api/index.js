// 统一后端接口封装，全部使用相对路径（dev 经 vite proxy 转发，生产由 FastAPI 同源托管）
const BASE = ''

async function request(path, { method = 'GET', params, body, isForm = false } = {}) {
  let url = BASE + path
  if (params) {
    const qs = new URLSearchParams()
    Object.entries(params).forEach(([k, v]) => {
      if (v !== undefined && v !== null && v !== '') qs.append(k, v)
    })
    url += '?' + qs.toString()
  }
  const options = { method, headers: {} }
  const token = localStorage.getItem('token')
  if (token) options.headers['Authorization'] = 'Bearer ' + token
  if (body) {
    if (isForm) {
      options.body = body
    } else {
      options.headers['Content-Type'] = 'application/json'
      options.body = JSON.stringify(body)
    }
  }
  const res = await fetch(url, options)
  const data = await res.json().catch(() => ({}))
  if (!res.ok) throw new Error(data.detail || data.error || `请求失败(${res.status})`)
  return data
}

export const api = {
  // 文档
  listDocuments: () => request('/documents/'),
  searchDocuments: (keyword) => request('/documents/search/', { params: { keyword } }),
  getDocument: (id) => request(`/documents/${id}`),
  upload: (file, confirm) => {
    const fd = new FormData()
    fd.append('file', file)
    const params = {}
    if (confirm) params.confirm = confirm
    return request('/upload/', { method: 'POST', params, body: fd, isForm: true })
  },
  deleteDocument: (id) => request(`/documents/${id}`, { method: 'DELETE' }),
  updateCategory: (id, newCategory) =>
    request(`/admin/documents/${id}/category`, { method: 'PUT', params: { new_category: newCategory } }),
  getVersions: (id) => request(`/admin/documents/${id}/versions`),
  rollback: (id) => request(`/admin/documents/${id}/rollback`, { method: 'POST' }),
  // 问答
  ask: (q) => request('/ask/', { method: 'POST', params: { q } }),
  // 用户
  login: (username, password) => request('/login/', { method: 'POST', params: { username, password } }),
  register: (username, password) => request('/register/', { method: 'POST', params: { username, password } }),
  me: () => request('/me/'),
  // 问答历史 / 备注 / 权限 / 分享
  qaHistory: (keyword) => request('/qa/history/', { params: { keyword } }),
  qaNote: (id, note) => request(`/qa/${id}/note`, { method: 'PUT', params: { note } }),
  qaPermission: (id, permission) => request(`/qa/${id}/permission`, { method: 'PUT', params: { permission } }),
  qaShare: (id) => request(`/qa/${id}/share`, { method: 'POST' }),
  qaShareView: (token) => request(`/qa/share/${token}`),
  userProfile: (userId) => request(`/users/${userId}/profile`),
  userPublic: (userId) => request(`/users/${userId}/qa_public`),
  changePassword: (oldPassword, newPassword) =>
    request('/change_password/', { method: 'POST', params: { old_password: oldPassword, new_password: newPassword } }),
  deletePublicQa: (id) => request(`/qa/${id}`, { method: 'DELETE' }),
  // 教师公开内容管理
  teacherPublicQa: () => request('/teacher/qa/public/'),
  // 管理员后台
  adminUsers: () => request('/admin/users/'),
  adminCreateTeacher: (username, password) =>
    request('/admin/teachers/', { method: 'POST', params: { username, password } }),
  adminDeleteUser: (id) => request(`/admin/users/${id}`, { method: 'DELETE' }),
  adminPublicQa: () => request('/admin/qa/public/'),
  adminDeletePublicQa: (id) => request(`/admin/qa/${id}`, { method: 'DELETE' })
}

export function fileUrl(id) {
  return `${BASE}/file/${id}`
}