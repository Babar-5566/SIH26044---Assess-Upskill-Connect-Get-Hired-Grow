import React from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider, useAuth } from './context/AuthContext'
import AppLayout from './components/layout/AppLayout'

// Auth pages
import LoginPage from './pages/auth/LoginPage'
import RegisterPage from './pages/auth/RegisterPage'

// Phase 12: Learning pages
import LearningDashboard from './pages/learning/LearningDashboard'
import RecommendationsPage from './pages/learning/RecommendationsPage'
import CertificationsPage from './pages/learning/CertificationsPage'

// Phase 13: Internship pages
import InternshipDiscovery from './pages/internship/InternshipDiscovery'
import InternshipDetail from './pages/internship/InternshipDetail'
import MyApplications from './pages/internship/MyApplications'
import CompanyInternships from './pages/internship/CompanyInternships'
import PostInternship from './pages/internship/PostInternship'
import ApplicantsList from './pages/internship/ApplicantsList'
import AcademicianOpportunities from './pages/internship/AcademicianOpportunities'
import RoleDashboard from './pages/dashboard/RoleDashboard'

function RequireAuth({ children }: { children: React.ReactNode }) {
  const { user, isLoading } = useAuth()
  if (isLoading) return <div className="min-h-screen flex items-center justify-center text-gray-400">Loading…</div>
  if (!user) return <Navigate to="/login" replace />
  return <AppLayout>{children}</AppLayout>
}

function InstitutionStats() {
  const [stats, setStats] = React.useState<any>(null)
  React.useEffect(() => {
    import('./api/client').then(({ internshipApi }) =>
      internshipApi.getInstitutionStats().then(r => setStats(r.data))
    )
  }, [])
  if (!stats) return <div className="text-gray-400">Loading stats…</div>
  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">Internship Statistics</h1>
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {[
          { label: 'Total Applications', value: stats.total_applications },
          { label: 'Active Internships', value: stats.active_internships },
          { label: 'Completed', value: stats.completed_internships },
          { label: 'Completion Rate', value: `${stats.completion_rate}%` },
        ].map(s => (
          <div key={s.label} className="card text-center">
            <p className="text-3xl font-bold text-blue-600">{s.value}</p>
            <p className="text-sm text-gray-500 mt-1">{s.label}</p>
          </div>
        ))}
      </div>
    </div>
  )
}

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          {/* Public */}
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />

          {/* Student routes */}
          <Route path="/student/learning" element={<RequireAuth><LearningDashboard /></RequireAuth>} />
          <Route path="/student/learning/recommendations" element={<RequireAuth><RecommendationsPage /></RequireAuth>} />
          <Route path="/student/certifications" element={<RequireAuth><CertificationsPage /></RequireAuth>} />
          <Route path="/student/internships" element={<RequireAuth><InternshipDiscovery /></RequireAuth>} />
          <Route path="/student/internships/:id" element={<RequireAuth><InternshipDetail /></RequireAuth>} />
          <Route path="/student/internships/applications" element={<RequireAuth><MyApplications /></RequireAuth>} />

          {/* Company routes */}
          <Route path="/company/internships" element={<RequireAuth><CompanyInternships /></RequireAuth>} />
          <Route path="/company/internships/new" element={<RequireAuth><PostInternship /></RequireAuth>} />
          <Route path="/company/internships/:postingId/applicants" element={<RequireAuth><ApplicantsList /></RequireAuth>} />

          {/* Academician routes */}
          <Route path="/academician/opportunities" element={<RequireAuth><AcademicianOpportunities /></RequireAuth>} />

          {/* Institution routes */}
          <Route path="/institution/stats" element={<RequireAuth><InstitutionStats /></RequireAuth>} />
          <Route path="/dashboard" element={<RequireAuth><RoleDashboard /></RequireAuth>} />
          <Route path="/mentor/dashboard" element={<RequireAuth><RoleDashboard /></RequireAuth>} />
          <Route path="/faculty/dashboard" element={<RequireAuth><RoleDashboard /></RequireAuth>} />

          {/* Fallback */}
          <Route path="*" element={<Navigate to="/login" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  )
}
