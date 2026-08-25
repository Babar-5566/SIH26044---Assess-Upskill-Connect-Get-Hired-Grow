import React, { useEffect, useState } from 'react'
import { internshipApi } from '../../api/client'
import type { AcademicianOpportunity } from '../../types'
import { BookOpen, Building, Calendar, DollarSign } from 'lucide-react'

const TYPE_LABELS: Record<string, string> = {
  faculty_internship: 'Faculty Internship',
  fdp: 'Faculty Development Program',
  consultancy: 'Consultancy',
  research_collaboration: 'Research Collaboration',
  guest_lecture: 'Guest Lecture',
  workshop: 'Workshop',
}
const TYPE_COLORS: Record<string, string> = {
  faculty_internship: 'bg-blue-100 text-blue-700',
  fdp: 'bg-purple-100 text-purple-700',
  consultancy: 'bg-green-100 text-green-700',
  research_collaboration: 'bg-orange-100 text-orange-700',
  guest_lecture: 'bg-pink-100 text-pink-700',
  workshop: 'bg-yellow-100 text-yellow-700',
}

export default function AcademicianOpportunities() {
  const [opps, setOpps] = useState<AcademicianOpportunity[]>([])
  const [loading, setLoading] = useState(true)
  const [typeFilter, setTypeFilter] = useState('')

  const load = async () => {
    setLoading(true)
    try {
      const r = await internshipApi.getAcademicianOpportunities(typeFilter || undefined)
      setOpps(r.data)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [typeFilter])

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Industry Opportunities</h1>
          <p className="text-gray-500 mt-1">Faculty internships, FDPs, research collaborations, and more</p>
        </div>
        <select className="input w-60" value={typeFilter} onChange={e => setTypeFilter(e.target.value)}>
          <option value="">All Types</option>
          {Object.entries(TYPE_LABELS).map(([v, l]) => <option key={v} value={v}>{l}</option>)}
        </select>
      </div>

      {loading ? (
        <div className="text-center text-gray-400 py-12">Loading…</div>
      ) : opps.length === 0 ? (
        <div className="card text-center py-12">
          <p className="text-gray-500">No opportunities found for the selected type.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {opps.map(opp => (
            <div key={opp.id} className="card">
              <div className="flex items-start justify-between mb-3">
                <span className={`badge ${TYPE_COLORS[opp.type] ?? 'bg-gray-100 text-gray-600'}`}>
                  {TYPE_LABELS[opp.type] ?? opp.type}
                </span>
              </div>
              <h3 className="font-semibold text-gray-900 mb-1">{opp.title}</h3>
              {opp.company_name && (
                <p className="text-sm text-blue-600 mb-2 flex items-center gap-1">
                  <Building size={14} />{opp.company_name}
                </p>
              )}
              {opp.description && (
                <p className="text-sm text-gray-600 mb-3 line-clamp-2">{opp.description}</p>
              )}
              <div className="flex flex-wrap gap-3 text-xs text-gray-500 mb-3">
                {opp.duration && <span className="flex items-center gap-1"><Calendar size={12} />{opp.duration}</span>}
                {opp.stipend_or_honorarium !== undefined && opp.stipend_or_honorarium !== null && (
                  <span className="flex items-center gap-1">
                    <DollarSign size={12} />₹{opp.stipend_or_honorarium.toLocaleString()}
                  </span>
                )}
              </div>
              {opp.domain.length > 0 && (
                <div className="flex flex-wrap gap-1 mb-3">
                  {opp.domain.map(d => (
                    <span key={d} className="badge bg-gray-100 text-gray-600">{d}</span>
                  ))}
                </div>
              )}
              {opp.eligibility && (
                <p className="text-xs text-gray-500 bg-gray-50 rounded p-2"><strong>Eligibility:</strong> {opp.eligibility}</p>
              )}
              {opp.application_deadline && (
                <p className="text-xs text-gray-400 mt-2">
                  Deadline: {new Date(opp.application_deadline).toLocaleDateString()}
                </p>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
