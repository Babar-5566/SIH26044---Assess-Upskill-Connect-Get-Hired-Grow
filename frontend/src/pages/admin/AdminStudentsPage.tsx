import React, { useEffect, useState } from 'react'
import { adminApi } from '../../api/client'
import {
  Users, Search, RefreshCw, Mail, GraduationCap, Award,
  CheckCircle2, Copy, Check, X, ExternalLink, FileText, Phone, MapPin, Calendar, BookOpen
} from 'lucide-react'

interface StudentDetail {
  user: {
    id: string
    email: string
    role: string
    is_active?: boolean
  }
  profile: {
    user_id?: string
    first_name?: string
    last_name?: string
    phone?: string
    summary?: string
    department?: string
    degree?: string
    institution_name?: string
    graduation_year?: number
    cgpa?: string | number
    city?: string
    state?: string
    linkedin_url?: string
    github_url?: string
    portfolio_url?: string
    resume_file_url?: string
    created_at?: string
    updated_at?: string
  } | null
  counts?: {
    skills?: number
    projects?: number
    certifications?: number
    achievements?: number
    internships?: number
  }
  preferred_roles?: any[]
  resume?: any
}

export default function AdminStudentsPage() {
  const [students, setStudents] = useState<StudentDetail[]>([])
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [selectedStudent, setSelectedStudent] = useState<StudentDetail | null>(null)
  const [copiedId, setCopiedId] = useState<string | null>(null)

  const fetchStudents = async () => {
    setLoading(true)
    setError(null)
    try {
      const res = await adminApi.getStudents({ limit: 100 })
      const data = res.data?.data || res.data || {}
      setStudents(data.items || [])
      setTotal(data.total || 0)
    } catch (err: any) {
      setError(err?.response?.data?.detail || 'Failed to load registered students')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchStudents()
  }, [])

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text)
    setCopiedId(text)
    setTimeout(() => setCopiedId(null), 2000)
  }

  const filtered = students.filter((item) => {
    const id = item.user?.id?.toLowerCase() || ''
    const email = item.user?.email?.toLowerCase() || ''
    const firstName = item.profile?.first_name?.toLowerCase() || ''
    const lastName = item.profile?.last_name?.toLowerCase() || ''
    const institution = item.profile?.institution_name?.toLowerCase() || ''
    const query = search.toLowerCase()
    return (
      id.includes(query) ||
      email.includes(query) ||
      firstName.includes(query) ||
      lastName.includes(query) ||
      institution.includes(query)
    )
  })

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
            <Users className="text-blue-600" size={26} />
            Registered Students (Admin Directory)
          </h1>
          <p className="text-sm text-gray-500 mt-1">
            Total {total} verified students registered • Click on any student to view complete profile & ID
          </p>
        </div>
        <button
          onClick={fetchStudents}
          disabled={loading}
          className="btn-secondary flex items-center gap-2 self-start sm:self-auto text-sm"
        >
          <RefreshCw size={16} className={loading ? 'animate-spin' : ''} />
          Refresh Directory
        </button>
      </div>

      {/* Search Bar & Counter */}
      <div className="card p-4 flex flex-col sm:flex-row gap-3 items-center justify-between">
        <div className="relative w-full sm:w-96">
          <Search size={18} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
          <input
            type="text"
            className="input pl-10"
            placeholder="Search by Name, Email, or Student ID..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>
        <div className="text-sm text-gray-500 flex items-center gap-2">
          <span>Showing</span>
          <span className="font-semibold text-blue-700 bg-blue-50 px-2 py-0.5 rounded border border-blue-100">
            {filtered.length} of {total}
          </span>
          <span>Students</span>
        </div>
      </div>

      {/* Error state */}
      {error && (
        <div className="p-4 bg-red-50 border border-red-200 text-red-700 rounded-lg text-sm">
          {error}
        </div>
      )}

      {/* Table Directory */}
      <div className="card overflow-hidden p-0 border border-gray-200 shadow-sm">
        {loading ? (
          <div className="p-12 text-center text-gray-500 flex flex-col items-center gap-2">
            <RefreshCw size={24} className="animate-spin text-blue-600" />
            <p>Loading candidate directory…</p>
          </div>
        ) : filtered.length === 0 ? (
          <div className="p-12 text-center text-gray-500">
            <Users size={36} className="mx-auto text-gray-300 mb-2" />
            <p className="font-medium text-gray-700">No student records found</p>
            <p className="text-sm text-gray-400 mt-1">
              {search ? 'Try adjusting your search criteria' : 'Newly registered accounts will appear here'}
            </p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm text-gray-600">
              <thead className="bg-gray-50 text-xs uppercase text-gray-500 border-b border-gray-200">
                <tr>
                  <th className="px-6 py-3.5 font-semibold">Student Name (Click to View)</th>
                  <th className="px-6 py-3.5 font-semibold">Student ID (UUID)</th>
                  <th className="px-6 py-3.5 font-semibold">Email</th>
                  <th className="px-6 py-3.5 font-semibold">Institution / Dept</th>
                  <th className="px-6 py-3.5 font-semibold">Profile Metrics</th>
                  <th className="px-6 py-3.5 font-semibold text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {filtered.map((item) => {
                  const fullName =
                    [item.profile?.first_name, item.profile?.last_name]
                      .filter(Boolean)
                      .join(' ') || 'Unnamed Student'
                  const studentId = item.user.id

                  return (
                    <tr
                      key={studentId}
                      className="hover:bg-blue-50/50 transition-colors cursor-pointer group"
                      onClick={() => setSelectedStudent(item)}
                    >
                      {/* Name */}
                      <td className="px-6 py-4">
                        <div className="flex items-center gap-3">
                          <div className="w-10 h-10 rounded-full bg-gradient-to-tr from-blue-600 to-indigo-600 text-white font-bold flex items-center justify-center text-sm shadow-sm group-hover:scale-105 transition-transform">
                            {fullName[0]?.toUpperCase() || 'S'}
                          </div>
                          <div>
                            <p className="font-semibold text-gray-900 group-hover:text-blue-600 transition-colors flex items-center gap-1.5">
                              {fullName}
                            </p>
                            <span className="text-xs text-blue-500 font-medium">Click to view full dossier</span>
                          </div>
                        </div>
                      </td>

                      {/* Student ID */}
                      <td className="px-6 py-4" onClick={(e) => e.stopPropagation()}>
                        <div className="flex items-center gap-2">
                          <span className="font-mono text-xs text-gray-700 bg-gray-100 px-2 py-1 rounded border border-gray-200">
                            {studentId.slice(0, 13)}...
                          </span>
                          <button
                            type="button"
                            onClick={() => copyToClipboard(studentId)}
                            title="Copy full UUID"
                            className="p-1 hover:bg-gray-200 rounded text-gray-500 hover:text-gray-800 transition-colors"
                          >
                            {copiedId === studentId ? (
                              <Check size={14} className="text-green-600" />
                            ) : (
                              <Copy size={14} />
                            )}
                          </button>
                        </div>
                      </td>

                      {/* Email */}
                      <td className="px-6 py-4">
                        <div className="flex items-center gap-1.5 text-gray-700">
                          <Mail size={14} className="text-gray-400" />
                          <span>{item.user.email}</span>
                        </div>
                      </td>

                      {/* Institution / Dept */}
                      <td className="px-6 py-4">
                        <div className="flex items-center gap-1.5">
                          <GraduationCap size={14} className="text-gray-400" />
                          <span className="truncate max-w-[200px]">
                            {item.profile?.institution_name || item.profile?.department || 'Not specified'}
                          </span>
                        </div>
                      </td>

                      {/* Metrics */}
                      <td className="px-6 py-4">
                        <div className="flex items-center gap-2">
                          <span className="badge bg-green-50 text-green-700 border border-green-200 font-medium text-xs">
                            {item.counts?.skills ?? 0} Skills
                          </span>
                          <span className="badge bg-purple-50 text-purple-700 border border-purple-200 font-medium text-xs">
                            {item.counts?.projects ?? 0} Projects
                          </span>
                        </div>
                      </td>

                      {/* Action */}
                      <td className="px-6 py-4 text-right">
                        <button
                          type="button"
                          onClick={(e) => {
                            e.stopPropagation()
                            setSelectedStudent(item)
                          }}
                          className="text-xs bg-blue-50 text-blue-600 hover:bg-blue-100 font-semibold px-3 py-1.5 rounded-lg border border-blue-200 transition-colors"
                        >
                          View Details →
                        </button>
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* STUDENT FULL DETAILS MODAL */}
      {selectedStudent && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-xs p-4 animate-in fade-in duration-150"
          onClick={() => setSelectedStudent(null)}
        >
          <div
            className="bg-white rounded-2xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto no-scrollbar scroll-smooth border border-gray-200"
            onClick={(e) => e.stopPropagation()}
          >
            {/* Modal Header */}
            <div className="bg-gradient-to-r from-blue-700 to-indigo-800 text-white p-6 rounded-t-2xl relative">
              <button
                type="button"
                onClick={() => setSelectedStudent(null)}
                className="absolute top-5 right-5 text-white/80 hover:text-white bg-white/10 hover:bg-white/20 rounded-full p-1.5 transition-colors"
                aria-label="Close modal"
              >
                <X size={20} />
              </button>

              <div className="flex items-start gap-4">
                <div className="w-16 h-16 rounded-2xl bg-white/10 border border-white/20 text-white font-bold text-2xl flex items-center justify-center shadow-inner">
                  {selectedStudent.profile?.first_name?.[0]?.toUpperCase() || selectedStudent.user.email[0]?.toUpperCase()}
                </div>
                <div className="flex-1">
                  <div className="flex items-center gap-2 flex-wrap">
                    <h2 className="text-2xl font-bold text-white">
                      {[selectedStudent.profile?.first_name, selectedStudent.profile?.last_name]
                        .filter(Boolean)
                        .join(' ') || 'Unnamed Candidate'}
                    </h2>
                    <span className="bg-emerald-500/30 text-emerald-200 border border-emerald-400/40 text-xs px-2.5 py-0.5 rounded-full font-semibold flex items-center gap-1">
                      <CheckCircle2 size={12} /> Active Student
                    </span>
                  </div>

                  {/* Student ID Banner */}
                  <div className="mt-3 flex items-center gap-2 bg-black/25 px-3 py-1.5 rounded-lg text-xs font-mono text-blue-100 border border-white/10 w-fit">
                    <span className="text-blue-300 font-bold uppercase tracking-wider">Student ID:</span>
                    <span>{selectedStudent.user.id}</span>
                    <button
                      type="button"
                      onClick={() => copyToClipboard(selectedStudent.user.id)}
                      className="ml-1 text-white hover:text-blue-200 p-0.5"
                      title="Copy Student ID"
                    >
                      {copiedId === selectedStudent.user.id ? (
                        <Check size={14} className="text-emerald-300" />
                      ) : (
                        <Copy size={14} />
                      )}
                    </button>
                  </div>
                </div>
              </div>
            </div>

            {/* Modal Body */}
            <div className="p-6 space-y-6">
              {/* Quick Stats Grid */}
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                <div className="bg-blue-50 border border-blue-100 p-3 rounded-xl text-center">
                  <p className="text-xs text-blue-600 font-medium">Skills</p>
                  <p className="text-xl font-bold text-blue-900 mt-0.5">
                    {selectedStudent.counts?.skills ?? 0}
                  </p>
                </div>
                <div className="bg-purple-50 border border-purple-100 p-3 rounded-xl text-center">
                  <p className="text-xs text-purple-600 font-medium">Projects</p>
                  <p className="text-xl font-bold text-purple-900 mt-0.5">
                    {selectedStudent.counts?.projects ?? 0}
                  </p>
                </div>
                <div className="bg-amber-50 border border-amber-100 p-3 rounded-xl text-center">
                  <p className="text-xs text-amber-600 font-medium">Certificates</p>
                  <p className="text-xl font-bold text-amber-900 mt-0.5">
                    {selectedStudent.counts?.certifications ?? 0}
                  </p>
                </div>
                <div className="bg-emerald-50 border border-emerald-100 p-3 rounded-xl text-center">
                  <p className="text-xs text-emerald-600 font-medium">Internships</p>
                  <p className="text-xl font-bold text-emerald-900 mt-0.5">
                    {selectedStudent.counts?.internships ?? 0}
                  </p>
                </div>
              </div>

              {/* Bio / Summary */}
              {selectedStudent.profile?.summary && (
                <div className="p-4 bg-gray-50 border border-gray-200 rounded-xl">
                  <h4 className="text-xs font-semibold uppercase text-gray-500 tracking-wider mb-1">
                    Candidate Summary / Bio
                  </h4>
                  <p className="text-sm text-gray-700 leading-relaxed">
                    {selectedStudent.profile.summary}
                  </p>
                </div>
              )}

              {/* Contact Information */}
              <div className="space-y-3">
                <h4 className="text-xs font-bold uppercase text-gray-500 tracking-wider border-b pb-1">
                  Contact Information
                </h4>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-sm">
                  <div className="flex items-center gap-2.5 text-gray-700">
                    <Mail size={16} className="text-blue-600 shrink-0" />
                    <span className="font-medium text-gray-900">{selectedStudent.user.email}</span>
                  </div>
                  <div className="flex items-center gap-2.5 text-gray-700">
                    <Phone size={16} className="text-blue-600 shrink-0" />
                    <span>{selectedStudent.profile?.phone || 'Not provided'}</span>
                  </div>
                  <div className="flex items-center gap-2.5 text-gray-700">
                    <MapPin size={16} className="text-blue-600 shrink-0" />
                    <span>
                      {[selectedStudent.profile?.city, selectedStudent.profile?.state]
                        .filter(Boolean)
                        .join(', ') || 'Location not specified'}
                    </span>
                  </div>
                  <div className="flex items-center gap-2.5 text-gray-700">
                    <Calendar size={16} className="text-blue-600 shrink-0" />
                    <span>
                      Registered: {selectedStudent.profile?.created_at ? new Date(selectedStudent.profile.created_at).toLocaleDateString() : 'Active'}
                    </span>
                  </div>
                </div>
              </div>

              {/* Academic Details */}
              <div className="space-y-3">
                <h4 className="text-xs font-bold uppercase text-gray-500 tracking-wider border-b pb-1">
                  Academic Details
                </h4>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-sm">
                  <div>
                    <span className="text-xs text-gray-500 block">Institution / College</span>
                    <span className="font-semibold text-gray-800">
                      {selectedStudent.profile?.institution_name || 'Not provided'}
                    </span>
                  </div>
                  <div>
                    <span className="text-xs text-gray-500 block">Department</span>
                    <span className="font-semibold text-gray-800">
                      {selectedStudent.profile?.department || 'Not provided'}
                    </span>
                  </div>
                  <div>
                    <span className="text-xs text-gray-500 block">Degree</span>
                    <span className="font-semibold text-gray-800">
                      {selectedStudent.profile?.degree || 'Not provided'}
                    </span>
                  </div>
                  <div>
                    <span className="text-xs text-gray-500 block">CGPA / Passing Year</span>
                    <span className="font-semibold text-gray-800">
                      CGPA: {selectedStudent.profile?.cgpa || 'N/A'} • Class of{' '}
                      {selectedStudent.profile?.graduation_year || 'N/A'}
                    </span>
                  </div>
                </div>
              </div>

              {/* Web & Social Links */}
              <div className="space-y-3">
                <h4 className="text-xs font-bold uppercase text-gray-500 tracking-wider border-b pb-1">
                  Social & Professional Profiles
                </h4>
                <div className="flex flex-wrap gap-2 text-sm">
                  {selectedStudent.profile?.linkedin_url ? (
                    <a
                      href={selectedStudent.profile.linkedin_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex items-center gap-1.5 px-3 py-1.5 bg-blue-50 text-blue-700 hover:bg-blue-100 rounded-lg text-xs font-medium transition-colors"
                    >
                      LinkedIn Profile <ExternalLink size={12} />
                    </a>
                  ) : (
                    <span className="text-xs text-gray-400 bg-gray-100 px-3 py-1 rounded">No LinkedIn</span>
                  )}
                  {selectedStudent.profile?.github_url ? (
                    <a
                      href={selectedStudent.profile.github_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex items-center gap-1.5 px-3 py-1.5 bg-gray-100 text-gray-800 hover:bg-gray-200 rounded-lg text-xs font-medium transition-colors"
                    >
                      GitHub Profile <ExternalLink size={12} />
                    </a>
                  ) : (
                    <span className="text-xs text-gray-400 bg-gray-100 px-3 py-1 rounded">No GitHub</span>
                  )}
                  {selectedStudent.profile?.portfolio_url && (
                    <a
                      href={selectedStudent.profile.portfolio_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex items-center gap-1.5 px-3 py-1.5 bg-purple-50 text-purple-700 hover:bg-purple-100 rounded-lg text-xs font-medium transition-colors"
                    >
                      Portfolio <ExternalLink size={12} />
                    </a>
                  )}
                  {selectedStudent.profile?.resume_file_url && (
                    <a
                      href={selectedStudent.profile.resume_file_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex items-center gap-1.5 px-3 py-1.5 bg-emerald-50 text-emerald-700 hover:bg-emerald-100 rounded-lg text-xs font-medium transition-colors"
                    >
                      <FileText size={12} /> View Resume / CV
                    </a>
                  )}
                </div>
              </div>
            </div>

            {/* Modal Footer */}
            <div className="p-4 bg-gray-50 border-t border-gray-100 rounded-b-2xl flex justify-between items-center text-xs text-gray-500">
              <span>Candidate record loaded from verified database</span>
              <button
                type="button"
                onClick={() => setSelectedStudent(null)}
                className="btn-secondary text-xs px-4 py-2"
              >
                Close Dossier
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
