import React from 'react'
import { mentorshipApi } from '../../api/client'

export default function MentorshipPage() {
  const [items, setItems] = React.useState<any[]>([])
  const [error, setError] = React.useState('')
  const refresh = () => mentorshipApi.list().then(r => setItems(r.data?.data ?? r.data ?? [])).catch(() => setError('Unable to load mentorship assignments'))
  React.useEffect(() => { refresh() }, [])
  return <section className="space-y-5"><div><h1 className="text-2xl font-bold">Mentorship</h1><p className="text-sm text-gray-500">View your active mentor assignments and progress.</p></div>{error && <p className="text-red-600">{error}</p>}<div className="grid gap-4 md:grid-cols-2">{items.map((a) => <article className="card" key={a.id}><h2 className="font-semibold">Assignment</h2><p className="text-sm text-gray-500 mt-1">Status: {a.status}</p><button className="btn-secondary mt-4" onClick={() => mentorshipApi.updateStatus(a.id, a.status === 'ACTIVE' ? 'COMPLETED' : 'ACTIVE').then(refresh).catch(() => setError('Unable to update assignment'))}>{a.status === 'ACTIVE' ? 'Mark completed' : 'Reactivate'}</button></article>)}{!items.length && !error && <div className="card text-gray-500">No mentorship assignments found.</div>}</div></section>
}
