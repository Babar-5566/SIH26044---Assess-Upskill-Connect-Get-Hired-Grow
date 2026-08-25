import React from 'react'
import { interviewApi } from '../../api/client'

export default function InterviewsPage() {
  const [items, setItems] = React.useState<any[]>([])
  const [error, setError] = React.useState('')
  React.useEffect(() => { interviewApi.list().then(r => setItems(r.data?.data ?? r.data ?? [])).catch(() => setError('Unable to load interviews')) }, [])
  return <section className="space-y-5"><div><h1 className="text-2xl font-bold">Interview practice</h1><p className="text-sm text-gray-500">Prepare with structured, evaluated interview sessions.</p></div>{error && <p className="text-red-600">{error}</p>}<div className="space-y-3">{items.map((i) => <article className="card flex items-center justify-between gap-4" key={i.id}><div><h2 className="font-semibold">{i.title || i.role || 'Practice interview'}</h2><p className="text-sm text-gray-500">Status: {i.status || 'ready'}</p></div><button className="btn-primary" onClick={() => interviewApi.start(i.id).catch(() => setError('Unable to start interview'))}>Begin</button></article>)}{!items.length && !error && <div className="card text-gray-500">No interview sessions found.</div>}</div></section>
}
