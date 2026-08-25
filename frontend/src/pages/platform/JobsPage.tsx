import React from 'react'
import { jobsApi } from '../../api/client'
import { Briefcase, Send, RefreshCw } from 'lucide-react'

export default function JobsPage() {
  const [jobs, setJobs] = React.useState<any[]>([])
  const [loading, setLoading] = React.useState(true)
  const [error, setError] = React.useState('')
  const [notice, setNotice] = React.useState('')
  const load = React.useCallback(() => { setLoading(true); setError(''); jobsApi.list().then(r => setJobs(Array.isArray(r.data) ? r.data : [])).catch(() => setError('Unable to load jobs')).finally(() => setLoading(false)) }, [])
  React.useEffect(() => { load() }, [load])
  const apply = async (id: string) => { setNotice(''); try { await jobsApi.apply(id); setNotice('Application submitted successfully') } catch (e: any) { setNotice(e?.response?.data?.detail || 'Unable to submit application') } }
  return <div className="space-y-6">
    <div className="flex items-center justify-between"><div><h1 className="text-2xl font-bold text-gray-900">Jobs & Graduate Opportunities</h1><p className="text-sm text-gray-500 mt-1">Discover open roles and apply directly.</p></div><button onClick={load} className="btn-secondary flex items-center gap-2"><RefreshCw size={16}/> Refresh</button></div>
    {notice && <div className="rounded-lg bg-blue-50 text-blue-700 px-4 py-3 text-sm">{notice}</div>}
    {error && <div className="rounded-lg bg-red-50 text-red-700 px-4 py-3">{error}</div>}
    {loading ? <div className="text-gray-500 py-10 text-center">Loading jobs...</div> : jobs.length === 0 ? <div className="card text-center py-12"><Briefcase className="mx-auto text-gray-300" size={36}/><p className="text-gray-500 mt-3">No open jobs right now.</p></div> : <div className="grid gap-4 md:grid-cols-2">{jobs.map(j => <article className="card" key={j.id}><div className="flex justify-between gap-3"><div><h2 className="font-semibold text-gray-900">{j.title}</h2><p className="text-sm text-gray-500">{j.company_name || 'Hiring organization'}{j.location ? ` • ${j.location}` : ''}</p></div><span className="badge bg-green-100 text-green-700">{j.type || 'Job'}</span></div><p className="text-sm text-gray-600 mt-3 line-clamp-3">{j.description || 'No description provided.'}</p><div className="flex flex-wrap gap-2 mt-3">{(j.required_skills || []).map((s: string) => <span className="badge bg-gray-100 text-gray-600" key={s}>{s}</span>)}</div><button onClick={() => apply(j.id)} className="btn-primary mt-4 flex items-center gap-2"><Send size={15}/> Apply</button></article>)}</div>}
  </div>
}
