import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react'
import { authApi, organizationApi } from '../api/client'
import type { User } from '../types'

interface AuthContextValue {
  user: User | null
  token: string | null
  login: (email: string, password: string) => Promise<void>
  register: (data: { email: string; password: string; full_name: string; role: string }) => Promise<void>
  logout: () => void
  isLoading: boolean
  organizations: any[]
  activeOrganizationId: string | null
  switchOrganization: (id: string) => void
}

const AuthContext = createContext<AuthContextValue | null>(null)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [token, setToken] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [organizations, setOrganizations] = useState<any[]>([])
  const [activeOrganizationId, setActiveOrganizationId] = useState<string | null>(localStorage.getItem('organization_id'))

  useEffect(() => {
    const stored = localStorage.getItem('user')
    const storedToken = localStorage.getItem('access_token')
    if (stored && storedToken) {
      setUser(JSON.parse(stored))
      setToken(storedToken)
      organizationApi.list().then(({ data }) => {
        setOrganizations(data || [])
        if (!localStorage.getItem('organization_id') && data?.[0]) switchOrganization(data[0].id)
      }).catch(() => setOrganizations([]))
    }
    setIsLoading(false)
  }, [])

  const login = async (email: string, password: string) => {
    const response = await authApi.login(email, password)
    const tokenData = response.data.data
    localStorage.setItem('access_token', tokenData.access_token)
    const me = await authApi.me()
    const current = me.data.data
    const userData: User = { id: current.id, email: current.email, full_name: current.email, role: current.role }
    localStorage.setItem('user', JSON.stringify(userData))
    setToken(tokenData.access_token)
    setUser(userData)
    try {
      const orgs = await organizationApi.list()
      setOrganizations(orgs.data)
      if (!activeOrganizationId && orgs.data[0]) switchOrganization(orgs.data[0].id)
    } catch { setOrganizations([]) }
  }

  const register = async (form: { email: string; password: string; full_name: string; role: string }) => {
    await authApi.register(form)
    await login(form.email, form.password)
  }

  const logout = () => {
    localStorage.removeItem('access_token')
    localStorage.removeItem('user')
    setToken(null)
    setUser(null)
    setOrganizations([])
    localStorage.removeItem('organization_id')
  }

  const switchOrganization = (id: string) => {
    localStorage.setItem('organization_id', id)
    setActiveOrganizationId(id)
  }

  return (
    <AuthContext.Provider value={{ user, token, login, register, logout, isLoading, organizations, activeOrganizationId, switchOrganization }}>
      {children}
    </AuthContext.Provider>
  )
}

export const useAuth = () => {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be inside AuthProvider')
  return ctx
}
