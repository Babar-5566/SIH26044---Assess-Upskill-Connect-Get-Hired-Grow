import React from 'react'
import { outcomesApi } from '../../api/client'

export default function OutcomesPage() {
  const [items, setItems] = React.useState<any[]>([])
  const [error, setError] = React.useState('')
  React.useEffect(() => { outcomesApi.list().then(r => setItems(r.data?.data ?? r.data ?? [])).catch(() => setError('Unable to load outcomes')) }, [])
  return <section className="space-y-5"><div><h1 className="text-2xl font-bold">Career outcomes</h1><p className="text-sm text-gray-500">Keep your placement and employment milestones up to date.</p></div>{error && <p className="text-red-600">{error}</p>}<div className="space-y-3">{items.map((o) => <article className="card" key={o.id}><h2 className="font-semibold">{o.outcome_type || o.company_name || 'Employment outcome'}</h2><p className="text-sm text-gray-500 mt-1">{o.status || o.role || 'Recorded outcome'}</p></article>)}{!items.length && !error && <div className="card text-gray-500">No outcomes recorded yet.</div>}</div></section>
}
