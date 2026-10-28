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
  const options = { method }
  if (body) {
    if (isForm) {
      options.body = body
    } else {
      options.headers = { 'Content-Type': 'application/json' }
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
  upload: (file, adminSecret, confirm) => {
    const fd = new FormData()
    fd.append('file', file)
    const params = { admin_secret: adminSecret }
    if (confirm) params.confirm = confirm
    return request('/upload/', { method: 'POST', params, body: fd, isForm: true })
  },
  deleteDocument: (id, adminSecret) =>
    request(`/documents/${id}`, { method: 'DELETE', params: { admin_secret: adminSecret } }),
  updateCategory: (id, newCategory, adminSecret) =>
    request(`/admin/documents/${id}/category`, { method: 'PUT', params: { new_category: newCategory, admin_secret: adminSecret } }),
  getVersions: (id, adminSecret) =>
    request(`/admin/documents/${id}/versions`, { params: { admin_secret: adminSecret } }),
  rollback: (id, adminSecret) =>
    request(`/admin/documents/${id}/rollback`, { method: 'POST', params: { admin_secret: adminSecret } }),
  // 问答
  ask: (q) => request('/ask/', { method: 'POST', params: { q } }),
  // 用户
  login: (username, password) => request('/login/', { method: 'POST', params: { username, password } }),
  register: (username, password) => request('/register/', { method: 'POST', params: { username, password } })
}

export function fileUrl(id) {
  return `${BASE}/file/${id}`
}