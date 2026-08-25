import React from 'react'
import { assessmentApi } from '../../api/client'

export default function AssessmentsPage() {
  const [items, setItems] = React.useState<any[]>([])
  const [loading, setLoading] = React.useState(true)
  const [error, setError] = React.useState('')
  React.useEffect(() => { assessmentApi.list().then(r => setItems(r.data?.data ?? r.data ?? [])).catch(() => setError('Unable to load assessments')).finally(() => setLoading(false)) }, [])
  return <section className="space-y-5"><div><h1 className="text-2xl font-bold">Assessments</h1><p className="text-sm text-gray-500">Measure your readiness and track results.</p></div>{loading && <p className="text-gray-500">Loading assessments...</p>}{error && <p className="text-red-600">{error}</p>}<div className="grid gap-4 md:grid-cols-2">{items.map((a) => <article className="card" key={a.id}><h2 className="font-semibold">{a.title || a.name || 'Assessment'}</h2><p className="text-sm text-gray-500 mt-1">{a.description || 'Skill readiness assessment'}</p><button className="btn-primary mt-4" onClick={() => assessmentApi.start(a.id).catch(() => setError('Unable to start assessment'))}>Start assessment</button></article>)}{!loading && !items.length && <div className="card text-gray-500">No assessments are available yet.</div>}</div></section>
}
