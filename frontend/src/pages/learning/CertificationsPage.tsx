import React, { useEffect, useState } from 'react'
import { learningApi } from '../../api/client'
import type { Certification } from '../../types'
import { Award, Plus, ExternalLink, CheckCircle } from 'lucide-react'

export default function CertificationsPage() {
  const [certs, setCerts] = useState<Certification[]>([])
  const [loading, setLoading] = useState(true)
  const [showForm, setShowForm] = useState(false)
  const [form, setForm] = useState({
    certification_name: '', issuer: '', issued_date: '',
    expiry_date: '', credential_url: '',
  })
  const [saving, setSaving] = useState(false)

  const load = async () => {
    setLoading(true)
    try {
      const r = await learningApi.getMyCertifications()
      setCerts(r.data)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setSaving(true)
    try {
      await learningApi.addCertification(form)
      setShowForm(false)
      setForm({ certification_name: '', issuer: '', issued_date: '', expiry_date: '', credential_url: '' })
      await load()
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Certifications</h1>
          <p className="text-gray-500 mt-1">Track your earned and uploaded certifications</p>
        </div>
        <button className="btn-primary flex items-center gap-2" onClick={() => setShowForm(s => !s)}>
          <Plus size={16} /> Add Certification
        </button>
      </div>

      {showForm && (
        <div className="card">
          <h3 className="font-semibold text-gray-800 mb-4">Add New Certification</h3>
          <form onSubmit={handleSubmit} className="grid grid-cols-2 gap-4">
            <div className="col-span-2">
              <label className="block text-sm font-medium text-gray-700 mb-1">Certification Name *</label>
              <input className="input" required value={form.certification_name}
                onChange={e => setForm(f => ({ ...f, certification_name: e.target.value }))} />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Issuer</label>
              <input className="input" value={form.issuer}
                onChange={e => setForm(f => ({ ...f, issuer: e.target.value }))} />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Issue Date</label>
              <input className="input" type="date" value={form.issued_date}
                onChange={e => setForm(f => ({ ...f, issued_date: e.target.value }))} />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Expiry Date</label>
              <input className="input" type="date" value={form.expiry_date}
                onChange={e => setForm(f => ({ ...f, expiry_date: e.target.value }))} />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Credential URL</label>
              <input className="input" type="url" value={form.credential_url}
                onChange={e => setForm(f => ({ ...f, credential_url: e.target.value }))} />
            </div>
            <div className="col-span-2 flex gap-3">
              <button type="submit" className="btn-primary" disabled={saving}>
                {saving ? 'Saving…' : 'Save Certification'}
              </button>
              <button type="button" className="btn-secondary" onClick={() => setShowForm(false)}>Cancel</button>
            </div>
          </form>
        </div>
      )}

      {loading ? (
        <div className="text-center text-gray-400 py-12">Loading…</div>
      ) : certs.length === 0 ? (
        <div className="card text-center py-12">
          <Award className="mx-auto text-gray-300 mb-4" size={48} />
          <p className="text-gray-500">No certifications yet. Add your first one!</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {certs.map(cert => (
            <div key={cert.id} className="card relative">
              {cert.verified && (
                <div className="absolute top-4 right-4 flex items-center gap-1 text-green-600 text-xs">
                  <CheckCircle size={14} /> Verified
                </div>
              )}
              <Award className="text-blue-500 mb-3" size={32} />
              <h3 className="font-semibold text-gray-900">{cert.certification_name}</h3>
              {cert.issuer && <p className="text-sm text-gray-500 mt-1">{cert.issuer}</p>}
              {cert.issued_date && (
                <p className="text-xs text-gray-400 mt-1">
                  Issued: {new Date(cert.issued_date).toLocaleDateString()}
                  {cert.expiry_date && ` · Expires: ${new Date(cert.expiry_date).toLocaleDateString()}`}
                </p>
              )}
              {cert.credential_url && (
                <a href={cert.credential_url} target="_blank" rel="noreferrer"
                  className="flex items-center gap-1 text-sm text-blue-600 hover:underline mt-3">
                  <ExternalLink size={14} /> View Credential
                </a>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
