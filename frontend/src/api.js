import axios from 'axios'

const api = axios.create({ baseURL: import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000/api' })
api.interceptors.request.use(config => {
  const token = localStorage.getItem('sb_access')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})
api.interceptors.response.use(
  response => response,
  async error => {
    const original = error.config
    if (error.response?.status === 401 && !original._retry && localStorage.getItem('sb_refresh')) {
      original._retry = true
      try {
        const { data } = await axios.post(`${api.defaults.baseURL}/auth/token/refresh/`, { refresh: localStorage.getItem('sb_refresh') })
        localStorage.setItem('sb_access', data.access)
        original.headers.Authorization = `Bearer ${data.access}`
        return api(original)
      } catch {
        localStorage.removeItem('sb_access'); localStorage.removeItem('sb_refresh')
      }
    }
    return Promise.reject(error)
  }
)
export default api
