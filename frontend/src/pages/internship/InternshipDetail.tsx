import React, { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { internshipApi } from '../../api/client'
import type { InternshipPosting, EligibilityCheck } from '../../types'
import { MapPin, Clock, Banknote, CheckCircle, XCircle, AlertCircle, ArrowLeft } from 'lucide-react'

function CheckRow({ label, ok }: { label: string; ok: boolean }) {
  return (
    <div className="flex items-center gap-3 py-2 border-b border-gray-50 last:border-0">
      {ok
        ? <CheckCircle size={18} className="text-green-500 shrink-0" />
        : <XCircle size={18} className="text-red-500 shrink-0" />}
      <span className={`text-sm ${ok ? 'text-gray-700' : 'text-red-600'}`}>{label}</span>
    </div>
  )
}

const CHECK_LABELS: Record<string, string> = {
  education_match: 'Education Qualification',
  cgpa_met: 'CGPA Requirement',
  year_match: 'Academic Year',
  deadline_valid: 'Application Deadline Open',
  seats_available: 'Seats Available',
  certifications_met: 'Required Certifications',
}

export default function InternshipDetail() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const [posting, setPosting] = useState<InternshipPosting | null>(null)
  const [eligibility, setEligibility] = useState<EligibilityCheck | null>(null)
  const [coverLetter, setCoverLetter] = useState('')
  const [applying, setApplying] = useState(false)
  const [applied, setApplied] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    if (!id) return
    Promise.all([
      internshipApi.getDetail(id).then(r => setPosting(r.data)),
      internshipApi.checkEligibility(id).then(r => setEligibility(r.data)).catch(() => {}),
    ])
  }, [id])

  const handleApply = async () => {
    if (!id) return
    setApplying(true)
    setError('')
    try {
      await internshipApi.apply(id, { cover_letter: coverLetter })
      setApplied(true)
    } catch (e: any) {
      setError(e?.response?.data?.detail || 'Application failed.')
    } finally {
      setApplying(false)
    }
  }

  if (!posting) return <div className="text-center text-gray-400 py-12">Loading…</div>

  return (
    <div className="max-w-4xl space-y-6">
      <button onClick={() => navigate(-1)}
        className="flex items-center gap-2 text-gray-500 hover:text-gray-700 text-sm">
        <ArrowLeft size={16} /> Back
      </button>

      <div className="card">
        <div className="flex items-start justify-between mb-4">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">{posting.title}</h1>
            <p className="text-blue-600 font-medium mt-1">{posting.company_name}</p>
          </div>
          <span className="badge bg-green-100 text-green-700 text-sm">
            {posting.status.toUpperCase()}
          </span>
        </div>

        <div className="flex flex-wrap gap-4 text-sm text-gray-600 mb-4">
          {posting.location && (
            <span className="flex items-center gap-1"><MapPin size={14} />{posting.location}</span>
          )}
          {posting.duration_weeks && (
            <span className="flex items-center gap-1"><Clock size={14} />{posting.duration_weeks} weeks</span>
          )}
          <span className="flex items-center gap-1">
            <Banknote size={14} />
            {posting.stipend_monthly ? `₹${posting.stipend_monthly.toLocaleString()}/month` : 'Unpaid'}
          </span>
        </div>

        {posting.description && (
          <p className="text-gray-700 leading-relaxed mb-4">{posting.description}</p>
        )}

        <div className="grid grid-cols-2 gap-6">
          <div>
            <h3 className="font-semibold text-gray-800 mb-2">Required Skills</h3>
            <div className="flex flex-wrap gap-2">
              {posting.required_skills.map(s => (
                <span key={s} className="badge bg-blue-50 text-blue-700">{s}</span>
              ))}
            </div>
          </div>
          <div>
            <h3 className="font-semibold text-gray-800 mb-2">Eligibility</h3>
            <ul className="text-sm text-gray-600 space-y-1">
              {posting.required_education && <li>Education: {posting.required_education}</li>}
              {posting.required_cgpa > 0 && <li>Min CGPA: {posting.required_cgpa}</li>}
              {posting.required_year.length > 0 && <li>Year: {posting.required_year.join(', ')}</li>}
              <li>Seats: {posting.seats_available}</li>
              {posting.application_deadline && (
                <li>Deadline: {new Date(posting.application_deadline).toLocaleDateString()}</li>
              )}
            </ul>
          </div>
        </div>
      </div>

      {/* Eligibility Panel */}
      {eligibility && (
        <div className={`card border-2 ${eligibility.eligible ? 'border-green-200' : 'border-red-200'}`}>
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-gray-900">Your Eligibility</h2>
            <div className="flex items-center gap-3">
              <div className="text-right">
                <p className="text-2xl font-bold text-blue-600">{eligibility.skill_match_percent}%</p>
                <p className="text-xs text-gray-500">Skill Match</p>
              </div>
              <div className={`px-4 py-2 rounded-lg font-semibold text-sm ${
                eligibility.eligible ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'
              }`}>
                {eligibility.eligible ? '✅ Eligible' : '❌ Not Eligible'}
              </div>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-6">
            <div>
              <h3 className="text-sm font-semibold text-gray-600 mb-2">Requirement Checks</h3>
              {Object.entries(eligibility.checks).map(([key, ok]) => (
                <CheckRow key={key} label={CHECK_LABELS[key] ?? key} ok={ok as boolean} />
              ))}
            </div>
            <div className="space-y-4">
              {eligibility.missing_skills.length > 0 && (
                <div>
                  <h3 className="text-sm font-semibold text-red-600 mb-2">Missing Skills</h3>
                  <div className="flex flex-wrap gap-1">
                    {eligibility.missing_skills.map(s => (
                      <span key={s} className="badge bg-red-50 text-red-600">{s}</span>
                    ))}
                  </div>
                  <p className="text-xs text-gray-400 mt-2">
                    Visit Learning & Development to close these gaps.
                  </p>
                </div>
              )}
              {eligibility.missing_certifications.length > 0 && (
                <div>
                  <h3 className="text-sm font-semibold text-orange-600 mb-2">Missing Certifications</h3>
                  <div className="flex flex-wrap gap-1">
                    {eligibility.missing_certifications.map(c => (
                      <span key={c} className="badge bg-orange-50 text-orange-600">{c}</span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Apply */}
      {!applied ? (
        <div className="card">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Apply Now</h2>
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-1">Cover Letter (optional)</label>
            <textarea className="input h-32 resize-none" value={coverLetter}
              onChange={e => setCoverLetter(e.target.value)}
              placeholder="Tell the company why you are interested in this opportunity…" />
          </div>
          {error && <p className="text-red-600 text-sm mb-3">{error}</p>}
          <button
            className="btn-primary"
            onClick={handleApply}
            disabled={applying || !eligibility?.eligible}>
            {applying ? 'Submitting…' : eligibility?.eligible ? 'Submit Application' : 'Not Eligible to Apply'}
          </button>
          {!eligibility?.eligible && (
            <p className="text-xs text-gray-400 mt-2">
              You don't meet the hard requirements (CGPA, year, education, deadline).
            </p>
          )}
        </div>
      ) : (
        <div className="card bg-green-50 border-green-200 border-2 text-center py-8">
          <CheckCircle className="mx-auto text-green-500 mb-3" size={40} />
          <h2 className="text-xl font-bold text-green-700">Application Submitted!</h2>
          <p className="text-green-600 mt-2">Track your application status in My Applications.</p>
        </div>
      )}
    </div>
  )
}
