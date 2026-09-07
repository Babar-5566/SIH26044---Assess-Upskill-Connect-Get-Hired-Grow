import React from 'react'
import { Link } from 'react-router-dom'
import { dashboardApi, adminApi } from '../../api/client'
import { useAuth } from '../../context/AuthContext'
import { Users, ArrowRight } from 'lucide-react'

export default function RoleDashboard() {
  const { effectiveRole, activeOrganizationId } = useAuth()
  const [data, setData] = React.useState<Record<string, unknown> | null>(null)
  const [error, setError] = React.useState<string | null>(null)

  React.useEffect(() => {
    const role = effectiveRole
    if (role === 'ADMIN' || role === 'admin') {
      adminApi.getStudents({ limit: 1 })
        .then((res) => {
          const total = res.data?.data?.total ?? res.data?.total ?? 0
          setData({ total_registered_students: total, system_status: 'Active', admin_role: 'Platform Administrator' })
        })
        .catch(() => setError('Unable to load admin dashboard data'))
      return
    }

    if ((role === 'INSTITUTION_ADMIN' || role === 'FACULTY' || role === 'institution') && !activeOrganizationId) {
      setError('Select or create an organization to view this dashboard')
      return
    }
    setError(null)
    const request = role === 'MENTOR_TRAINER'
      ? dashboardApi.mentor()
      : role === 'INSTITUTION_ADMIN' || role === 'FACULTY' || role === 'institution'
        ? dashboardApi.institution(activeOrganizationId as string)
      : role === 'INDUSTRY_ADMIN' || role === 'INDUSTRY_MEMBER_RECRUITER' || role === 'company'
        ? dashboardApi.industry()
        : dashboardApi.student()
    request.then((response) => setData(response.data)).catch(() => setError('Unable to load dashboard data'))
  }, [effectiveRole, activeOrganizationId])

  if (error) return <div className="text-red-600">{error}</div>
  if (!data) return <div className="text-gray-500">Loading dashboard…</div>

  return (
    <section className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
          <p className="text-sm text-gray-500 mt-1">Role-aware SkillBridge overview</p>
        </div>
        {(effectiveRole === 'ADMIN' || effectiveRole === 'admin') && (
          <Link to="/admin/students" className="btn-primary flex items-center gap-2 self-start sm:self-auto text-sm">
            <Users size={16} />
            View Registered Students
            <ArrowRight size={14} />
          </Link>
        )}
      </div>
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {Object.entries(data).filter(([key]) => key !== 'student_id' && key !== 'mentor_id' && key !== 'organization_user_id').map(([key, value]) => (
          <div className="card" key={key}>
            <p className="text-2xl font-bold text-blue-700">{String(value)}</p>
            <p className="text-sm text-gray-500 mt-1 capitalize">{key.replace(/_/g, ' ')}</p>
          </div>
        ))}
      </div>
    </section>
  )
}
