import React, { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { internshipApi } from '../../api/client'
import type { InternshipPosting } from '../../types'
import { MapPin, Clock, Banknote, Wifi, Search, Filter } from 'lucide-react'

const TYPE_LABELS: Record<string, string> = {
  internship: 'Internship',
  apprenticeship: 'Apprenticeship',
  live_project: 'Live Project',
  industrial_training: 'Industrial Training',
}
const TYPE_COLORS: Record<string, string> = {
  internship: 'bg-blue-100 text-blue-700',
  apprenticeship: 'bg-purple-100 text-purple-700',
  live_project: 'bg-orange-100 text-orange-700',
  industrial_training: 'bg-green-100 text-green-700',
}

function InternshipCard({ internship }: { internship: InternshipPosting }) {
  const deadline = internship.application_deadline
    ? new Date(internship.application_deadline)
    : null
  const daysLeft = deadline
    ? Math.max(0, Math.ceil((deadline.getTime() - Date.now()) / 86400000))
    : null

  return (
    <Link to={`/student/internships/${internship.id}`}
      className="card hover:shadow-md transition-shadow block">
      <div className="flex items-start justify-between mb-3">
        <span className={`badge ${TYPE_COLORS[internship.type] ?? 'bg-gray-100 text-gray-600'}`}>
          {TYPE_LABELS[internship.type] ?? internship.type}
        </span>
        <div className="flex items-center gap-2">
          {internship.skill_match_percent !== undefined && (
            <span className={`badge font-semibold ${
              internship.skill_match_percent >= 70 ? 'bg-green-100 text-green-700' :
              internship.skill_match_percent >= 40 ? 'bg-yellow-100 text-yellow-700' :
              'bg-red-100 text-red-700'
            }`}>
              {internship.skill_match_percent}% match
            </span>
          )}
          {internship.is_remote && (
            <span className="badge bg-blue-50 text-blue-500 flex items-center gap-1">
              <Wifi size={12} /> Remote
            </span>
          )}
        </div>
      </div>
      <h3 className="font-semibold text-gray-900 text-lg">{internship.title}</h3>
      <p className="text-blue-600 font-medium text-sm mt-1">{internship.company_name}</p>
      <div className="flex flex-wrap gap-3 mt-3 text-sm text-gray-500">
        {internship.location && (
          <span className="flex items-center gap-1"><MapPin size={14} />{internship.location}</span>
        )}
        {internship.duration_weeks && (
          <span className="flex items-center gap-1"><Clock size={14} />{internship.duration_weeks} weeks</span>
        )}
        {internship.stipend_monthly !== undefined && internship.stipend_monthly !== null ? (
          <span className="flex items-center gap-1">
            <Banknote size={14} />₹{internship.stipend_monthly.toLocaleString()}/month
          </span>
        ) : (
          <span className="flex items-center gap-1 text-gray-400"><Banknote size={14} />Unpaid</span>
        )}
      </div>
      <div className="flex flex-wrap gap-1 mt-3">
        {internship.required_skills.slice(0, 4).map(s => (
          <span key={s} className="badge bg-gray-100 text-gray-600">{s}</span>
        ))}
        {internship.required_skills.length > 4 && (
          <span className="badge bg-gray-100 text-gray-500">+{internship.required_skills.length - 4} more</span>
        )}
      </div>
      {daysLeft !== null && (
        <p className={`text-xs mt-3 font-medium ${daysLeft <= 5 ? 'text-red-500' : 'text-gray-400'}`}>
          {daysLeft === 0 ? 'Deadline today!' : `${daysLeft} days left to apply`}
        </p>
      )}
    </Link>
  )
}

export default function InternshipDiscovery() {
  const [internships, setInternships] = useState<InternshipPosting[]>([])
  const [recommended, setRecommended] = useState<InternshipPosting[]>([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')
  const [typeFilter, setTypeFilter] = useState('')
  const [remoteOnly, setRemoteOnly] = useState(false)
  const [tab, setTab] = useState<'recommended' | 'all'>('recommended')

  useEffect(() => {
    Promise.all([
      internshipApi.getRecommended().then(r => setRecommended(r.data)),
      internshipApi.list().then(r => setInternships(r.data)),
    ]).finally(() => setLoading(false))
  }, [])

  const filtered = (tab === 'recommended' ? recommended : internships).filter(i => {
    const matchSearch = !search || i.title.toLowerCase().includes(search.toLowerCase()) ||
      i.company_name.toLowerCase().includes(search.toLowerCase())
    const matchType = !typeFilter || i.type === typeFilter
    const matchRemote = !remoteOnly || i.is_remote
    return matchSearch && matchType && matchRemote
  })

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Internship Discovery</h1>
        <p className="text-gray-500 mt-1">Find internships, live projects, and industrial training opportunities</p>
      </div>

      {/* Filters */}
      <div className="flex flex-wrap gap-3">
        <div className="relative flex-1 min-w-48">
          <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
          <input className="input pl-9" placeholder="Search by title or company…"
            value={search} onChange={e => setSearch(e.target.value)} />
        </div>
        <select className="input w-52" value={typeFilter} onChange={e => setTypeFilter(e.target.value)}>
          <option value="">All Types</option>
          <option value="internship">Internship</option>
          <option value="apprenticeship">Apprenticeship</option>
          <option value="live_project">Live Project</option>
          <option value="industrial_training">Industrial Training</option>
        </select>
        <label className="flex items-center gap-2 text-sm text-gray-600 cursor-pointer">
          <input type="checkbox" checked={remoteOnly} onChange={e => setRemoteOnly(e.target.checked)}
            className="rounded border-gray-300" />
          Remote only
        </label>
      </div>

      {/* Tabs */}
      <div className="flex gap-1 bg-gray-100 rounded-lg p-1 w-fit">
        {(['recommended', 'all'] as const).map(t => (
          <button key={t} onClick={() => setTab(t)}
            className={`px-4 py-1.5 rounded-md text-sm font-medium transition-colors ${
              tab === t ? 'bg-white text-gray-900 shadow-sm' : 'text-gray-600 hover:text-gray-900'
            }`}>
            {t === 'recommended' ? '✨ Recommended for You' : 'All Internships'}
          </button>
        ))}
      </div>

      {loading ? (
        <div className="text-center text-gray-400 py-12">Loading opportunities…</div>
      ) : filtered.length === 0 ? (
        <div className="text-center text-gray-400 py-12">No internships found. Try adjusting filters.</div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
          {filtered.map(i => <InternshipCard key={i.id} internship={i} />)}
        </div>
      )}
    </div>
  )
}
