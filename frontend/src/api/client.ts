import axios from 'axios'

const api = axios.create({ baseURL: import.meta.env.VITE_API_URL || '/api/v1' })

// Attach JWT token from localStorage to every request
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  const organizationId = localStorage.getItem('organization_id')
  if (organizationId) config.headers['X-Organization-ID'] = organizationId
  return config
})

// ─── Auth ─────────────────────────────────────────────────────────────────────

export const authApi = {
  register: (data: { email: string; password: string; first_name: string; last_name: string }) =>
    api.post('/auth/register/student', data),
  login: (email: string, password: string) => api.post('/auth/login', { email, password }),
  me: () => api.get('/auth/me'),
}

// ─── Phase 12: Learning ───────────────────────────────────────────────────────

export const learningApi = {
  getResources: (params?: { skill?: string; type?: string; level?: string; is_free?: boolean }) =>
    api.get('/learning/resources', { params }),
  getResource: (id: string) => api.get(`/learning/resources/${id}`),
  getRecommendations: (role: string) => api.get('/learning/recommendations', { params: { role } }),
  createPlan: (target_role: string) => api.post('/learning/plans', { target_role }),
  getMyPlan: () => api.get('/learning/plans/me'),
  updatePlanItem: (itemId: string, data: { status?: string; progress_percent?: number }) =>
    api.put(`/learning/plans/items/${itemId}`, data),
  abandonPlan: () => api.delete('/learning/plans/me'),
  getProgress: () => api.get('/learning/progress/me'),
  addCertification: (data: any) => api.post('/learning/certifications', data),
  getMyCertifications: () => api.get('/learning/certifications/me'),
}

// ─── Phase 13: Internship ─────────────────────────────────────────────────────

export const internshipApi = {
  // Student
  list: (params?: any) => api.get('/internships', { params }),
  getRecommended: () => api.get('/internships/recommended'),
  getDetail: (id: string) => api.get(`/internships/${id}`),
  checkEligibility: (id: string) => api.get(`/internships/${id}/eligibility`),
  apply: (id: string, data: { cover_letter?: string }) => api.post(`/internships/${id}/apply`, data),
  getMyApplications: () => api.get('/internships/applications/me'),
  withdraw: (appId: string) => api.put(`/internships/applications/${appId}/withdraw`),
  getProgress: (appId: string) => api.get(`/internships/applications/${appId}/progress`),
  // Company
  createPosting: (data: any) => api.post('/internships/company/postings', data),
  getMyPostings: () => api.get('/internships/company/postings'),
  updatePosting: (id: string, data: any) => api.put(`/internships/company/postings/${id}`, data),
  deletePosting: (id: string) => api.delete(`/internships/company/postings/${id}`),
  getApplicants: (postingId: string) => api.get(`/internships/company/postings/${postingId}/applicants`),
  updateAppStatus: (appId: string, data: { status: string; company_notes?: string }) =>
    api.put(`/internships/company/applications/${appId}/status`, data),
  createProgress: (appId: string, data: any) => api.post(`/internships/company/applications/${appId}/progress`, data),
  updateProgress: (appId: string, data: any) => api.put(`/internships/company/applications/${appId}/progress`, data),
  submitFeedback: (progressId: string, data: any) => api.post(`/internships/company/progress/${progressId}/feedback`, data),
  getFeedback: (progressId: string) => api.get(`/internships/company/progress/${progressId}/feedback`),
  // Academician
  getAcademicianOpportunities: (type?: string) =>
    api.get('/internships/academician/opportunities', { params: type ? { type } : {} }),
  // Institution
  getInstitutionStats: () => api.get('/internships/institution/stats'),
}

export const assessmentApi = {
  list: () => api.get('/assessments'),
  questions: (id: string) => api.get(`/assessments/${id}/questions`),
  start: (id: string) => api.post(`/assessments/${id}/attempts`),
  answer: (attemptId: string, data: any) => api.post(`/assessments/attempts/${attemptId}/responses`, data),
  submit: (attemptId: string, data?: any) => api.post(`/assessments/attempts/${attemptId}/submit`, data || {}),
}

export const interviewApi = {
  list: () => api.get('/interviews'),
  create: (data: any) => api.post('/interviews', data),
  start: (id: string) => api.post(`/interviews/${id}/start`),
  addTurn: (id: string, data: any) => api.post(`/interviews/${id}/turns`, data),
  evaluate: (id: string, data: any) => api.post(`/interviews/${id}/evaluate`, data),
}

export const dashboardApi = {
  student: () => api.get('/dashboard/student'),
  mentor: () => api.get('/dashboard/mentor'),
  industry: () => api.get('/dashboard/industry'),
  institution: (organizationId: string) => api.get(`/dashboard/institution/${organizationId}`),
}

export const organizationApi = {
  list: () => api.get('/organizations'),
  create: (data: { name: string; organization_type: string; slug: string }) => api.post('/organizations', data),
  members: (organizationId: string) => api.get(`/organizations/${organizationId}/members`),
  addMember: (organizationId: string, data: { user_id: string; role: string; is_primary?: boolean }) => api.post(`/organizations/${organizationId}/members`, data),
}

export const resumeIntelligenceApi = {
  analyze: (text: string, targetRole?: string) => api.post('/resume-intelligence/analyze', null, { params: { text, target_role: targetRole } }),
}

export const notificationApi = {
  list: () => api.get('/notifications'),
  markRead: (id: string) => api.post(`/notifications/${id}/read`),
  markAllRead: () => api.post('/notifications/read-all'),
}

export const jobsApi = {
  list: () => api.get('/jobs'),
  detail: (id: string) => api.get(`/jobs/${id}`),
  apply: (id: string, cover_letter?: string) => api.post(`/jobs/${id}/apply`, null, { params: cover_letter ? { cover_letter } : {} }),
}

export const mentorshipApi = {
  list: () => api.get('/mentorship/assignments'),
  updateStatus: (id: string, status: string) => api.patch(`/mentorship/assignments/${id}/status`, null, { params: { status } }),
}

export const outcomesApi = {
  list: () => api.get('/outcomes/me'),
  create: (data: Record<string, unknown>) => api.post('/outcomes/me', data),
  update: (id: string, data: Record<string, unknown>) => api.patch(`/outcomes/me/${id}`, data),
}

export const adminApi = {
  getStudents: (params?: { skip?: number; limit?: number }) => api.get('/admin/students', { params }),
  getStudent: (id: string) => api.get(`/admin/students/${id}`),
}
