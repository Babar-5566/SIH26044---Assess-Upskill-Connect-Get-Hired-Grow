import React, { useEffect, useState } from 'react'
import { internshipApi } from '../../api/client'
import type { InternshipPosting, InternshipApplication } from '../../types'
import { Link } from 'react-router-dom'
import { Plus, Eye, Users, Pencil, Trash2 } from 'lucide-react'

const STATUS_COLORS: Record<string, string> = {
  open: 'bg-green-100 text-green-700',
  closed: 'bg-gray-100 text-gray-600',
  draft: 'bg-yellow-100 text-yellow-700',
}

export default function CompanyInternships() {
  const [postings, setPostings] = useState<InternshipPosting[]>([])
  const [loading, setLoading] = useState(true)

  const load = () => internshipApi.getMyPostings().then(r => setPostings(r.data)).finally(() => setLoading(false))

  useEffect(() => { load() }, [])

  const handleToggle = async (p: InternshipPosting) => {
    const newStatus = p.status === 'open' ? 'closed' : 'open'
    await internshipApi.updatePosting(p.id, { status: newStatus })
    load()
  }

  const handleDelete = async (id: string) => {
    if (!confirm('Delete this posting?')) return
    await internshipApi.deletePosting(id)
    load()
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">My Internship Postings</h1>
          <p className="text-gray-500 mt-1">Manage your internship and opportunity listings</p>
        </div>
        <Link to="/company/internships/new" className="btn-primary flex items-center gap-2">
          <Plus size={16} /> Post Internship
        </Link>
      </div>

      {loading ? (
        <div className="text-center text-gray-400 py-12">Loading…</div>
      ) : postings.length === 0 ? (
        <div className="card text-center py-12">
          <p className="text-gray-500 mb-4">No postings yet. Create your first internship listing.</p>
          <Link to="/company/internships/new" className="btn-primary">Post Internship</Link>
        </div>
      ) : (
        <div className="space-y-3">
          {postings.map(p => (
            <div key={p.id} className="card flex items-center gap-4">
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-3 mb-1">
                  <h3 className="font-semibold text-gray-900 truncate">{p.title}</h3>
                  <span className={`badge ${STATUS_COLORS[p.status] ?? 'bg-gray-100'}`}>
                    {p.status}
                  </span>
                  <span className="badge bg-blue-50 text-blue-600">{p.type}</span>
                </div>
                <div className="flex gap-4 text-xs text-gray-500">
                  {p.location && <span>{p.location}</span>}
                  {p.duration_weeks && <span>{p.duration_weeks} weeks</span>}
                  {p.stipend_monthly !== undefined && p.stipend_monthly !== null
                    ? <span>₹{p.stipend_monthly.toLocaleString()}/mo</span>
                    : <span>Unpaid</span>}
                  <span>{p.seats_available} seats</span>
                  {p.application_deadline && (
                    <span>Deadline: {new Date(p.application_deadline).toLocaleDateString()}</span>
                  )}
                </div>
                <div className="flex flex-wrap gap-1 mt-2">
                  {p.required_skills.slice(0, 5).map(s => (
                    <span key={s} className="badge bg-gray-100 text-gray-600">{s}</span>
                  ))}
                </div>
              </div>
              <div className="flex items-center gap-3 shrink-0">
                <Link to={`/company/internships/${p.id}/applicants`}
                  className="flex items-center gap-1 text-sm text-blue-600 hover:underline">
                  <Users size={14} /> Applicants
                </Link>
                <button onClick={() => handleToggle(p)}
                  className={`text-sm ${p.status === 'open' ? 'text-orange-600' : 'text-green-600'} hover:underline`}>
                  {p.status === 'open' ? 'Close' : 'Reopen'}
                </button>
                <button onClick={() => handleDelete(p.id)}
                  className="text-sm text-red-500 hover:underline">Delete</button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
