import React, { useEffect, useState } from 'react'
import { internshipApi } from '../../api/client'
import type { InternshipApplication } from '../../types'
import { Link } from 'react-router-dom'
import { ChevronRight } from 'lucide-react'

const PIPELINE = ['applied', 'shortlisted', 'assessment', 'interview', 'selected', 'rejected', 'withdrawn']

const STATUS_COLORS: Record<string, string> = {
  applied: 'bg-blue-100 text-blue-700',
  shortlisted: 'bg-indigo-100 text-indigo-700',
  assessment: 'bg-yellow-100 text-yellow-700',
  interview: 'bg-orange-100 text-orange-700',
  selected: 'bg-green-100 text-green-700',
  rejected: 'bg-red-100 text-red-700',
  withdrawn: 'bg-gray-100 text-gray-500',
}

function PipelineBar({ status }: { status: string }) {
  const steps = ['applied', 'shortlisted', 'assessment', 'interview', 'selected']
  const idx = steps.indexOf(status)
  if (idx === -1) return null
  return (
    <div className="flex items-center gap-1 mt-3">
      {steps.map((s, i) => (
        <React.Fragment key={s}>
          <div className={`flex-1 h-1.5 rounded-full ${i <= idx ? 'bg-blue-500' : 'bg-gray-200'}`} />
          {i < steps.length - 1 && <ChevronRight size={12} className="text-gray-300 shrink-0" />}
        </React.Fragment>
      ))}
    </div>
  )
}

export default function MyApplications() {
  const [apps, setApps] = useState<InternshipApplication[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    internshipApi.getMyApplications().then(r => setApps(r.data)).finally(() => setLoading(false))
  }, [])

  const handleWithdraw = async (appId: string) => {
    if (!confirm('Withdraw this application?')) return
    await internshipApi.withdraw(appId)
    setApps(prev => prev.map(a => a.id === appId ? { ...a, status: 'withdrawn' } : a))
  }

  if (loading) return <div className="text-center text-gray-400 py-12">Loading…</div>

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">My Applications</h1>
        <p className="text-gray-500 mt-1">Track the status of your internship applications</p>
      </div>

      {apps.length === 0 ? (
        <div className="card text-center py-12">
          <p className="text-gray-500 mb-4">You haven't applied to any internships yet.</p>
          <Link to="/student/internships" className="btn-primary">Browse Internships</Link>
        </div>
      ) : (
        <div className="space-y-4">
          {apps.map(app => (
            <div key={app.id} className="card">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-1">
                    <h3 className="font-semibold text-gray-900">
                      {app.internship?.title ?? 'Internship'}
                    </h3>
                    <span className={`badge ${STATUS_COLORS[app.status] ?? 'bg-gray-100 text-gray-600'}`}>
                      {app.status.charAt(0).toUpperCase() + app.status.slice(1)}
                    </span>
                  </div>
                  <p className="text-blue-600 text-sm">
                    {app.internship?.company_name ?? ''}
                  </p>
                  <div className="flex items-center gap-3 mt-2 text-xs text-gray-500">
                    <span>Skill match: <strong>{app.skill_match_percent}%</strong></span>
                    <span>Applied: {new Date(app.applied_at).toLocaleDateString()}</span>
                  </div>
                  <PipelineBar status={app.status} />
                </div>
                <div className="flex flex-col gap-2 ml-4">
                  <Link to={`/student/internships/${app.internship_id}`}
                    className="text-sm text-blue-600 hover:underline">View Posting</Link>
                  {app.status === 'selected' && (
                    <Link to={`/student/internships/progress/${app.id}`}
                      className="text-sm text-green-600 hover:underline">View Progress</Link>
                  )}
                  {['applied', 'shortlisted'].includes(app.status) && (
                    <button onClick={() => handleWithdraw(app.id)}
                      className="text-sm text-red-500 hover:underline text-left">Withdraw</button>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
