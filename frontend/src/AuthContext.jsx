import { createContext, useContext, useEffect, useState } from 'react'
import api from './api'
const AuthContext = createContext(null)
export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)
  useEffect(() => {
    if (!localStorage.getItem('sb_access')) { setLoading(false); return }
    api.get('/auth/me/').then(r => setUser(r.data)).catch(() => setUser(null)).finally(() => setLoading(false))
  }, [])
  const login = async (email, password) => {
    const { data } = await api.post('/auth/login/', { email, password })
    localStorage.setItem('sb_access', data.access); localStorage.setItem('sb_refresh', data.refresh)
    const me = await api.get('/auth/me/'); setUser(me.data); return me.data
  }
  const register = async form => {
    await api.post('/auth/register/', form)
    return login(form.email, form.password)
  }
  const logout = () => { localStorage.removeItem('sb_access'); localStorage.removeItem('sb_refresh'); setUser(null) }
  return <AuthContext.Provider value={{ user, loading, login, register, logout }}>{children}</AuthContext.Provider>
}
export const useAuth = () => useContext(AuthContext)
