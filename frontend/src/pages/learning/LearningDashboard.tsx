import React, { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { learningApi } from '../../api/client'
import type { LearningPlan, LearningPlanItem } from '../../types'
import { BookOpen, TrendingUp, Award, ChevronRight, CheckCircle2, Circle, Clock } from 'lucide-react'

const STATUS_COLORS: Record<string, string> = {
  completed: 'bg-green-100 text-green-700',
  in_progress: 'bg-blue-100 text-blue-700',
  not_started: 'bg-gray-100 text-gray-600',
  skipped: 'bg-yellow-100 text-yellow-700',
}

const StatusIcon = ({ status }: { status: string }) => {
  if (status === 'completed') return <CheckCircle2 size={16} className="text-green-500" />
  if (status === 'in_progress') return <Clock size={16} className="text-blue-500" />
  return <Circle size={16} className="text-gray-400" />
}

export default function LearningDashboard() {
  const [plan, setPlan] = useState<LearningPlan | null>(null)
  const [progress, setProgress] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [role, setRole] = useState('Java Backend Developer')

  useEffect(() => {
    Promise.all([
      learningApi.getMyPlan().then(r => setPlan(r.data)).catch(() => setPlan(null)),
      learningApi.getProgress().then(r => setProgress(r.data)).catch(() => setProgress(null)),
    ]).finally(() => setLoading(false))
  }, [])

  const totalItems = plan?.items.length ?? 0
  const completedItems = plan?.items.filter(i => i.status === 'completed').length ?? 0
  const overallProgress = totalItems ? Math.round((completedItems / totalItems) * 100) : 0

  const handleMarkStatus = async (item: LearningPlanItem, status: string) => {
    await learningApi.updatePlanItem(item.id, { status })
    const r = await learningApi.getMyPlan()
    setPlan(r.data)
  }

  const handleCreatePlan = async () => {
    await learningApi.createPlan(role)
    const r = await learningApi.getMyPlan()
    setPlan(r.data)
  }

  if (loading) return <div className="flex items-center justify-center h-64 text-gray-400">Loading…</div>

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Learning & Development</h1>
          <p className="text-gray-500 mt-1">Your personalised skill development journey</p>
        </div>
        <div className="flex gap-3">
          <Link to="/student/learning/recommendations" className="btn-secondary">Browse Resources</Link>
          <Link to="/student/certifications" className="btn-secondary">Certifications</Link>
        </div>
      </div>

      {/* Stats cards */}
      <div className="grid grid-cols-3 gap-4">
        <div className="card flex items-center gap-4">
          <div className="p-3 bg-blue-50 rounded-lg"><BookOpen className="text-blue-600" size={24} /></div>
          <div>
            <p className="text-2xl font-bold text-gray-900">{totalItems}</p>
            <p className="text-sm text-gray-500">Resources in plan</p>
          </div>
        </div>
        <div className="card flex items-center gap-4">
          <div className="p-3 bg-green-50 rounded-lg"><CheckCircle2 className="text-green-600" size={24} /></div>
          <div>
            <p className="text-2xl font-bold text-gray-900">{completedItems}</p>
            <p className="text-sm text-gray-500">Completed</p>
          </div>
        </div>
        <div className="card flex items-center gap-4">
          <div className="p-3 bg-purple-50 rounded-lg"><TrendingUp className="text-purple-600" size={24} /></div>
          <div>
            <p className="text-2xl font-bold text-gray-900">{overallProgress}%</p>
            <p className="text-sm text-gray-500">Overall progress</p>
          </div>
        </div>
      </div>

      {!plan ? (
        <div className="card text-center py-12">
          <BookOpen className="mx-auto text-gray-300 mb-4" size={48} />
          <h3 className="text-lg font-medium text-gray-700 mb-2">No active learning plan</h3>
          <p className="text-gray-500 mb-6">Create a plan based on your target career role to get started.</p>
          <div className="flex gap-3 justify-center">
            <select className="input w-64"
              value={role} onChange={e => setRole(e.target.value)}>
              <option>Java Backend Developer</option>
              <option>Data Analyst</option>
              <option>Frontend Developer</option>
            </select>
            <button className="btn-primary" onClick={handleCreatePlan}>Create Learning Plan</button>
          </div>
        </div>
      ) : (
        <div className="card">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h2 className="text-lg font-semibold text-gray-900">
                Plan: <span className="text-blue-600">{plan.target_role}</span>
              </h2>
              <p className="text-sm text-gray-500">{completedItems} of {totalItems} resources completed</p>
            </div>
            <div className="flex items-center gap-3">
              <div className="w-32 bg-gray-200 rounded-full h-2">
                <div className="bg-blue-600 h-2 rounded-full transition-all" style={{ width: `${overallProgress}%` }} />
              </div>
              <span className="text-sm font-medium text-gray-700">{overallProgress}%</span>
            </div>
          </div>

          <div className="space-y-3">
            {plan.items.map((item) => (
              <div key={item.id} className="flex items-center gap-4 p-4 border border-gray-100 rounded-lg hover:bg-gray-50">
                <StatusIcon status={item.status} />
                <div className="flex-1 min-w-0">
                  <p className="font-medium text-gray-800 truncate">
                    {item.resource?.title ?? 'Resource'}
                  </p>
                  <div className="flex items-center gap-2 mt-1">
                    <span className="text-xs text-gray-500">Skill: {item.skill_gap_addressed}</span>
                    {item.resource?.provider && (
                      <span className="text-xs text-gray-400">• {item.resource.provider}</span>
                    )}
                    {item.resource?.duration_hours && (
                      <span className="text-xs text-gray-400">• {item.resource.duration_hours}h</span>
                    )}
                  </div>
                  <div className="w-full bg-gray-100 rounded-full h-1.5 mt-2">
                    <div className="bg-blue-500 h-1.5 rounded-full" style={{ width: `${item.progress_percent}%` }} />
                  </div>
                </div>
                <span className={`badge ${STATUS_COLORS[item.status] ?? 'bg-gray-100 text-gray-600'}`}>
                  {item.status.replace('_', ' ')}
                </span>
                <div className="flex gap-2">
                  {item.status !== 'in_progress' && item.status !== 'completed' && (
                    <button onClick={() => handleMarkStatus(item, 'in_progress')}
                      className="text-xs text-blue-600 hover:underline">Start</button>
                  )}
                  {item.status !== 'completed' && (
                    <button onClick={() => handleMarkStatus(item, 'completed')}
                      className="text-xs text-green-600 hover:underline">Done</button>
                  )}
                  {item.resource?.url && (
                    <a href={item.resource.url} target="_blank" rel="noreferrer"
                      className="text-xs text-gray-500 hover:underline">Open ↗</a>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Skill progress summary */}
      {progress?.skill_progress && Object.keys(progress.skill_progress).length > 0 && (
        <div className="card">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Skill Progress</h2>
          <div className="space-y-4">
            {Object.entries(progress.skill_progress).map(([skill, data]: [string, any]) => (
              <div key={skill}>
                <div className="flex justify-between text-sm mb-1">
                  <span className="font-medium text-gray-700">{skill}</span>
                  <span className="text-gray-500">{data.completed}/{data.total} done • {data.progress_avg}% avg</span>
                </div>
                <div className="w-full bg-gray-100 rounded-full h-2">
                  <div className="bg-blue-500 h-2 rounded-full"
                    style={{ width: `${data.total ? (data.completed / data.total) * 100 : 0}%` }} />
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
