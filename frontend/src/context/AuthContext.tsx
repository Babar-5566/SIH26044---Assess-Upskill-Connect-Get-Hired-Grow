import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react'
import { authApi, organizationApi } from '../api/client'
import type { User } from '../types'

interface AuthContextValue {
  user: User | null
  token: string | null
  login: (email: string, password: string) => Promise<void>
  register: (data: { email: string; password: string; first_name: string; last_name: string }) => Promise<void>
  logout: () => void
  isLoading: boolean
  organizations: any[]
  activeOrganizationId: string | null
  switchOrganization: (id: string | null) => void
  refreshOrganizations: () => Promise<void>
  activeOrganizationRole: string | null
  effectiveRole: string | null
}

const AuthContext = createContext<AuthContextValue | null>(null)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [token, setToken] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [organizations, setOrganizations] = useState<any[]>([])
  const [activeOrganizationId, setActiveOrganizationId] = useState<string | null>(localStorage.getItem('organization_id'))
  const activeOrganization = organizations.find((organization: any) => organization.id === activeOrganizationId)
  const activeOrganizationRole = activeOrganization?.membership_role || activeOrganization?.role_for_user || activeOrganization?.membership?.role || activeOrganization?.role || null
  // Organization roles are contextual; global role remains the fallback outside an organization.
  const effectiveRole = activeOrganizationRole || user?.role || null

  const loadOrganizations = async (userId?: string) => {
    try {
      const response = await organizationApi.list()
      const listed = response.data || []
      // Older backends return organizations without the caller's role. Resolve it from members.
      const resolved = await Promise.all(listed.map(async (organization: any) => {
        if (organization.membership_role || organization.role_for_user || organization.membership?.role || organization.role) return organization
        try {
          const members = await organizationApi.members(organization.id)
          const own = (members.data || []).find((member: any) => member.user_id === userId)
          return own ? { ...organization, membership_role: own.role, membership_is_primary: own.is_primary } : organization
        } catch { return organization }
      }))
      setOrganizations(resolved)
      const storedId = localStorage.getItem('organization_id')
      const selected = resolved.find((organization: any) => organization.id === storedId)
        || resolved.find((organization: any) => organization.membership_is_primary)
        || resolved[0]
      if (selected && selected.id !== storedId) switchOrganization(selected.id)
    } catch { setOrganizations([]) }
  }

  const refreshOrganizations = () => loadOrganizations(user?.id)

  useEffect(() => {
    const stored = localStorage.getItem('user')
    const storedToken = localStorage.getItem('access_token')
    if (stored && storedToken) {
      setUser(JSON.parse(stored))
      setToken(storedToken)
      loadOrganizations(JSON.parse(stored).id).finally(() => setIsLoading(false))
    } else {
      setIsLoading(false)
    }
  }, [])

  const login = async (email: string, password: string) => {
    // Organization context belongs to the previous session/user and must not
    // be sent while authenticating a new account.
    localStorage.removeItem('organization_id')
    setActiveOrganizationId(null)
    const response = await authApi.login(email, password)
    const tokenData = response.data.data
    localStorage.setItem('access_token', tokenData.access_token)
    const me = await authApi.me()
    const current = me.data.data
    const userData: User = { id: current.id, email: current.email, full_name: current.email, role: current.role }
    localStorage.setItem('user', JSON.stringify(userData))
    setToken(tokenData.access_token)
    setUser(userData)
    await loadOrganizations(current.id)
  }

  const register = async (form: { email: string; password: string; first_name: string; last_name: string }) => {
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

  const switchOrganization = (id: string | null) => {
    if (id) localStorage.setItem('organization_id', id)
    else localStorage.removeItem('organization_id')
    setActiveOrganizationId(id)
  }

  return (
    <AuthContext.Provider value={{ user, token, register, login, logout, isLoading, organizations, activeOrganizationId, switchOrganization, refreshOrganizations, activeOrganizationRole, effectiveRole }}>
      {children}
    </AuthContext.Provider>
  )
}

export const useAuth = () => {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be inside AuthProvider')
  return ctx
}
