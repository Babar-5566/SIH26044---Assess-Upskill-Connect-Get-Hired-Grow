import React from 'react'
import { dashboardApi } from '../../api/client'
import { useAuth } from '../../context/AuthContext'

export default function RoleDashboard() {
  const { user } = useAuth()
  const [data, setData] = React.useState<Record<string, unknown> | null>(null)
  const [error, setError] = React.useState<string | null>(null)

  React.useEffect(() => {
    const role = user?.role
    const request = role === 'MENTOR_TRAINER'
      ? dashboardApi.mentor()
      : role === 'INDUSTRY_ADMIN' || role === 'INDUSTRY_MEMBER_RECRUITER' || role === 'company'
        ? dashboardApi.industry()
        : dashboardApi.student()
    request.then((response) => setData(response.data)).catch(() => setError('Unable to load dashboard data'))
  }, [user?.role])

  if (error) return <div className="text-red-600">{error}</div>
  if (!data) return <div className="text-gray-500">Loading dashboard…</div>

  return (
    <section className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-sm text-gray-500 mt-1">Role-aware SkillBridge overview</p>
      </div>
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {Object.entries(data).filter(([key]) => key !== 'student_id' && key !== 'mentor_id' && key !== 'organization_user_id').map(([key, value]) => (
          <div className="card" key={key}>
            <p className="text-2xl font-bold text-blue-700">{String(value)}</p>
            <p className="text-sm text-gray-500 mt-1 capitalize">{key.replaceAll('_', ' ')}</p>
          </div>
        ))}
      </div>
    </section>
  )
}
