import React, { useEffect, useState } from 'react'
import { learningApi } from '../../api/client'
import type { RecommendationResponse, LearningResource } from '../../types'
import { ExternalLink, Star, Users, TrendingUp } from 'lucide-react'

const TYPE_COLORS: Record<string, string> = {
  course: 'bg-blue-100 text-blue-700',
  workshop: 'bg-purple-100 text-purple-700',
  fdp: 'bg-orange-100 text-orange-700',
  certification: 'bg-green-100 text-green-700',
  mentorship: 'bg-pink-100 text-pink-700',
  project: 'bg-yellow-100 text-yellow-700',
}

function ResourceCard({ resource }: { resource: LearningResource }) {
  return (
    <div className="border border-gray-200 rounded-xl p-4 hover:shadow-md transition-shadow bg-white">
      <div className="flex items-start justify-between mb-3">
        <span className={`badge ${TYPE_COLORS[resource.type] ?? 'bg-gray-100 text-gray-600'}`}>
          {resource.type}
        </span>
        {resource.is_free && (
          <span className="badge bg-green-100 text-green-700">Free</span>
        )}
      </div>
      <h3 className="font-semibold text-gray-900 mb-1">{resource.title}</h3>
      {resource.provider && <p className="text-sm text-gray-500 mb-2">{resource.provider}</p>}
      {resource.description && (
        <p className="text-xs text-gray-500 mb-3 line-clamp-2">{resource.description}</p>
      )}
      <div className="flex flex-wrap gap-1 mb-3">
        {resource.skills_covered.map(s => (
          <span key={s} className="badge bg-gray-100 text-gray-600">{s}</span>
        ))}
      </div>
      <div className="grid grid-cols-3 gap-2 text-xs text-center mb-3">
        <div className="bg-gray-50 rounded p-2">
          <p className="font-bold text-blue-600">{Math.round(resource.completion_rate * 100)}%</p>
          <p className="text-gray-500">Completion</p>
        </div>
        <div className="bg-gray-50 rounded p-2">
          <p className="font-bold text-green-600">{Math.round(resource.placement_outcome_rate * 100)}%</p>
          <p className="text-gray-500">Placement</p>
        </div>
        <div className="bg-gray-50 rounded p-2">
          <p className="font-bold text-purple-600">{resource.duration_hours ?? '—'}h</p>
          <p className="text-gray-500">Duration</p>
        </div>
      </div>
      {resource.url && (
        <a href={resource.url} target="_blank" rel="noreferrer"
          className="flex items-center gap-1 text-sm text-blue-600 hover:underline">
          <ExternalLink size={14} /> Open Resource
        </a>
      )}
    </div>
  )
}

const ROLES = ['Java Backend Developer', 'Data Analyst', 'Frontend Developer']

export default function RecommendationsPage() {
  const [role, setRole] = useState('Java Backend Developer')
  const [data, setData] = useState<RecommendationResponse | null>(null)
  const [loading, setLoading] = useState(false)

  const fetch = async () => {
    setLoading(true)
    try {
      const r = await learningApi.getRecommendations(role)
      setData(r.data)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { fetch() }, [role])

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Learning Recommendations</h1>
          <p className="text-gray-500 mt-1">Resources ranked by placement outcomes for your target role</p>
        </div>
        <select className="input w-60" value={role} onChange={e => setRole(e.target.value)}>
          {ROLES.map(r => <option key={r}>{r}</option>)}
        </select>
      </div>

      {loading && <div className="text-center text-gray-400 py-12">Loading recommendations…</div>}

      {data?.recommendations.map((rec) => (
        <div key={rec.skill_gap} className="space-y-3">
          <div className="flex items-center gap-3">
            <span className="inline-flex items-center justify-center w-6 h-6 rounded-full bg-blue-600 text-white text-xs font-bold">
              {rec.priority}
            </span>
            <h2 className="text-lg font-semibold text-gray-800">
              Skill Gap: <span className="text-blue-600">{rec.skill_gap}</span>
            </h2>
          </div>
          {rec.resources.length === 0 ? (
            <p className="text-gray-400 text-sm">No resources found for this skill yet.</p>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {rec.resources.map(r => <ResourceCard key={r.id} resource={r} />)}
            </div>
          )}
        </div>
      ))}
    </div>
  )
}
