import React, { ReactNode } from 'react'
import Sidebar from './Sidebar'
import { useAuth } from '../../context/AuthContext'

export default function AppLayout({ children }: { children: ReactNode }) {
  const { organizations, activeOrganizationId, switchOrganization } = useAuth()
  return (
    <div className="flex min-h-screen bg-gray-50">
      <Sidebar />
      <main className="flex-1 overflow-y-auto">
        {organizations.length > 0 && (
          <header className="bg-white border-b border-gray-200 px-8 py-3 flex justify-end">
            <select className="border rounded-md px-3 py-2 text-sm" value={activeOrganizationId || ''} onChange={(event) => switchOrganization(event.target.value)}>
              <option value="" disabled>Select organization</option>
              {organizations.map((organization: any) => <option value={organization.id} key={organization.id}>{organization.name}</option>)}
            </select>
          </header>
        )}
        <div className="p-8">{children}</div>
      </main>
    </div>
  )
}
