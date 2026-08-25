import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { internshipApi } from '../../api/client'

const SKILL_OPTIONS = ['Java', 'Spring Boot', 'Python', 'SQL', 'React', 'TypeScript', 'Docker', 'Power BI', 'Machine Learning', 'AWS', 'Git', 'Linux', 'CSS', 'REST API']

export default function PostInternship() {
  const navigate = useNavigate()
  const [form, setForm] = useState({
    title: '', type: 'internship', description: '', location: '',
    is_remote: false, duration_weeks: '', stipend_monthly: '',
    required_education: '', required_cgpa: '0', required_year: [] as number[],
    required_skills: [] as string[], required_certifications: '',
    seats_available: '1', application_deadline: '', start_date: '',
  })
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')

  const toggleSkill = (s: string) =>
    setForm(f => ({
      ...f,
      required_skills: f.required_skills.includes(s)
        ? f.required_skills.filter(x => x !== s)
        : [...f.required_skills, s],
    }))

  const toggleYear = (y: number) =>
    setForm(f => ({
      ...f,
      required_year: f.required_year.includes(y)
        ? f.required_year.filter(x => x !== y)
        : [...f.required_year, y],
    }))

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setSaving(true)
    setError('')
    try {
      await internshipApi.createPosting({
        ...form,
        duration_weeks: form.duration_weeks ? Number(form.duration_weeks) : null,
        stipend_monthly: form.stipend_monthly ? Number(form.stipend_monthly) : null,
        required_cgpa: Number(form.required_cgpa),
        seats_available: Number(form.seats_available),
        required_certifications: form.required_certifications
          ? form.required_certifications.split(',').map(s => s.trim()).filter(Boolean)
          : [],
      })
      navigate('/company/internships')
    } catch (e: any) {
      setError(e?.response?.data?.detail || 'Failed to post internship.')
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="max-w-3xl space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Post New Internship</h1>
        <p className="text-gray-500 mt-1">Create an internship, apprenticeship, live project, or industrial training posting.</p>
      </div>

      <form onSubmit={handleSubmit} className="card space-y-5">
        <div className="grid grid-cols-2 gap-4">
          <div className="col-span-2">
            <label className="block text-sm font-medium text-gray-700 mb-1">Title *</label>
            <input className="input" required value={form.title}
              onChange={e => setForm(f => ({ ...f, title: e.target.value }))} placeholder="e.g. Backend Developer Intern" />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Type *</label>
            <select className="input" value={form.type} onChange={e => setForm(f => ({ ...f, type: e.target.value }))}>
              <option value="internship">Internship</option>
              <option value="apprenticeship">Apprenticeship</option>
              <option value="live_project">Live Project</option>
              <option value="industrial_training">Industrial Training</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Location</label>
            <input className="input" value={form.location}
              onChange={e => setForm(f => ({ ...f, location: e.target.value }))} placeholder="Bangalore / Remote" />
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
          <textarea className="input h-28 resize-none" value={form.description}
            onChange={e => setForm(f => ({ ...f, description: e.target.value }))}
            placeholder="Describe the role, responsibilities, tech stack, and what students will learn…" />
        </div>

        <div className="grid grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Duration (weeks)</label>
            <input className="input" type="number" min="1" value={form.duration_weeks}
              onChange={e => setForm(f => ({ ...f, duration_weeks: e.target.value }))} />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Stipend (₹/month)</label>
            <input className="input" type="number" min="0" value={form.stipend_monthly}
              placeholder="0 = unpaid"
              onChange={e => setForm(f => ({ ...f, stipend_monthly: e.target.value }))} />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Seats</label>
            <input className="input" type="number" min="1" value={form.seats_available}
              onChange={e => setForm(f => ({ ...f, seats_available: e.target.value }))} />
          </div>
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Application Deadline</label>
            <input className="input" type="date" value={form.application_deadline}
              onChange={e => setForm(f => ({ ...f, application_deadline: e.target.value }))} />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Start Date</label>
            <input className="input" type="date" value={form.start_date}
              onChange={e => setForm(f => ({ ...f, start_date: e.target.value }))} />
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Required Skills</label>
          <div className="flex flex-wrap gap-2">
            {SKILL_OPTIONS.map(s => (
              <button key={s} type="button"
                onClick={() => toggleSkill(s)}
                className={`badge cursor-pointer border ${
                  form.required_skills.includes(s)
                    ? 'bg-blue-600 text-white border-blue-600'
                    : 'bg-white text-gray-600 border-gray-300'
                }`}>
                {s}
              </button>
            ))}
          </div>
        </div>

        <div className="grid grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Min. Education</label>
            <input className="input" value={form.required_education}
              onChange={e => setForm(f => ({ ...f, required_education: e.target.value }))} placeholder="B.Tech" />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Min. CGPA</label>
            <input className="input" type="number" step="0.1" min="0" max="10" value={form.required_cgpa}
              onChange={e => setForm(f => ({ ...f, required_cgpa: e.target.value }))} />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Year(s) Eligible</label>
            <div className="flex gap-2 mt-2">
              {[1, 2, 3, 4].map(y => (
                <button key={y} type="button" onClick={() => toggleYear(y)}
                  className={`badge cursor-pointer border ${
                    form.required_year.includes(y)
                      ? 'bg-blue-600 text-white border-blue-600'
                      : 'bg-white text-gray-600 border-gray-300'
                  }`}>Year {y}</button>
              ))}
            </div>
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Required Certifications (comma-separated)</label>
          <input className="input" value={form.required_certifications}
            onChange={e => setForm(f => ({ ...f, required_certifications: e.target.value }))}
            placeholder="AWS Cloud Practitioner, Docker Certified, …" />
        </div>

        <div className="flex items-center gap-2">
          <input type="checkbox" id="remote" checked={form.is_remote}
            onChange={e => setForm(f => ({ ...f, is_remote: e.target.checked }))}
            className="rounded border-gray-300" />
          <label htmlFor="remote" className="text-sm text-gray-700">This is a remote opportunity</label>
        </div>

        {error && <p className="text-red-600 text-sm">{error}</p>}

        <div className="flex gap-3">
          <button type="submit" className="btn-primary" disabled={saving}>
            {saving ? 'Posting…' : 'Post Internship'}
          </button>
          <button type="button" className="btn-secondary" onClick={() => navigate(-1)}>Cancel</button>
        </div>
      </form>
    </div>
  )
}
