import { api } from '../api'

/**
 * 生成可跨设备访问的站点基地址：
 * - 本机(localhost/127.0.0.1)访问时，分享/主页链接对他人无效，改用局域网IP拼接
 * - 已通过局域网IP访问时，直接用当前 origin
 */
export async function shareBase() {
  const host = window.location.hostname
  if (host === 'localhost' || host === '127.0.0.1') {
    const { ip } = await api.localIp()
    return `http://${ip}:${window.location.port || '5173'}`
  }
  return window.location.origin
}
