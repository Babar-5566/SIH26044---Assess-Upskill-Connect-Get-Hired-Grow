import React, { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import { internshipApi } from '../../api/client'
import type { InternshipApplication } from '../../types'

const STATUS_COLORS: Record<string, string> = {
  applied: 'bg-blue-100 text-blue-700',
  shortlisted: 'bg-indigo-100 text-indigo-700',
  assessment: 'bg-yellow-100 text-yellow-700',
  interview: 'bg-orange-100 text-orange-700',
  selected: 'bg-green-100 text-green-700',
  rejected: 'bg-red-100 text-red-700',
  withdrawn: 'bg-gray-100 text-gray-500',
}

const NEXT_STATUSES: Record<string, string[]> = {
  applied: ['shortlisted', 'rejected'],
  shortlisted: ['assessment', 'rejected'],
  assessment: ['interview', 'rejected'],
  interview: ['selected', 'rejected'],
}

export default function ApplicantsList() {
  const { postingId } = useParams<{ postingId: string }>()
  const [apps, setApps] = useState<InternshipApplication[]>([])
  const [loading, setLoading] = useState(true)
  const [updating, setUpdating] = useState<string | null>(null)

  const load = () => {
    if (!postingId) return
    internshipApi.getApplicants(postingId).then(r => setApps(r.data)).finally(() => setLoading(false))
  }
  useEffect(() => { load() }, [postingId])

  const handleStatus = async (appId: string, status: string) => {
    setUpdating(appId)
    try {
      await internshipApi.updateAppStatus(appId, { status })
      load()
    } finally {
      setUpdating(null)
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Applicants</h1>
        <p className="text-gray-500 mt-1">Manage and evaluate applicants for this posting. Sorted by skill match.</p>
      </div>

      {loading ? (
        <div className="text-center text-gray-400 py-12">Loading…</div>
      ) : apps.length === 0 ? (
        <div className="card text-center py-12">
          <p className="text-gray-500">No applicants yet for this posting.</p>
        </div>
      ) : (
        <div className="space-y-3">
          {apps.map(app => (
            <div key={app.id} className="card flex items-center gap-4">
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-3 mb-1">
                  <p className="font-medium text-gray-900 truncate">
                    Student ID: {app.student_id}
                  </p>
                  <span className={`badge ${STATUS_COLORS[app.status] ?? 'bg-gray-100'}`}>
                    {app.status}
                  </span>
                  <span className={`badge font-semibold ${
                    app.skill_match_percent >= 70 ? 'bg-green-100 text-green-700' :
                    app.skill_match_percent >= 40 ? 'bg-yellow-100 text-yellow-700' :
                    'bg-red-100 text-red-700'
                  }`}>
                    {app.skill_match_percent}% skill match
                  </span>
                </div>
                {app.cover_letter && (
                  <p className="text-sm text-gray-500 line-clamp-1">"{app.cover_letter}"</p>
                )}
                <p className="text-xs text-gray-400 mt-1">
                  Applied: {new Date(app.applied_at).toLocaleDateString()}
                </p>
              </div>
              <div className="flex gap-2 shrink-0">
                {(NEXT_STATUSES[app.status] ?? []).map(ns => (
                  <button key={ns}
                    onClick={() => handleStatus(app.id, ns)}
                    disabled={updating === app.id}
                    className={`text-xs px-3 py-1.5 rounded-lg font-medium border ${
                      ns === 'rejected'
                        ? 'border-red-200 text-red-600 hover:bg-red-50'
                        : 'border-blue-200 text-blue-600 hover:bg-blue-50'
                    }`}>
                    {ns.charAt(0).toUpperCase() + ns.slice(1)}
                  </button>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
