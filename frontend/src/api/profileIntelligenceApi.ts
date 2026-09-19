import { assistantHttp as api, type CitationSource } from './aiAssistantApi'

export interface ExtractedSkill { name: string; evidence: { chunk_id: string; page_number: number | null; quote: string } }
export interface ProfileSkill { id: string; name: string; proficiency_level: string; source: string; score: number | null }
export interface ProfileProject { id: string; title: string; description?: string; technologies: string[]; project_url?: string | null; status: string }
export interface ResumeAnalysis {
  warnings?: string[]
  skills: ExtractedSkill[]
  sections: Record<string, { text: string; page_number: number | null }[]>
  links: { url: string; chunk_id: string; page_number: number | null }[]
  word_count: number
  page_count: number | null
  quality: { checks: { id: string; label: string; passed: boolean; detail: string }[]; passed: number; total: number; note: string }
}
export interface LearningLink { id: string; title: string; url: string; provider?: string | null; skills: string[]; level?: string | null; is_free: boolean }
export interface ProfileSnapshot {
  limits?: { resume_max_size_mb: number }
  version: string
  profile: Record<string, string | number | null>
  skills: ProfileSkill[]
  projects: ProfileProject[]
  certifications: { id: string; name: string; issuer?: string }[]
  internships: { id: string; company_name: string; role: string }[]
  achievements: { id: string; title: string }[]
  resume: { id: string; filename: string; status: 'PENDING' | 'PROCESSING' | 'READY' | 'NEEDS_ATTENTION'; updated_at: string | null; error: string | null; analysis: ResumeAnalysis | null } | null
  documents: { id: string; filename: string; status: string; chunk_count: number }[]
  suggested_skills: ExtractedSkill[]
  profile_only_skills: string[]
  summary: string[]
  improvement_summary: string[]
  learning_resources?: LearningLink[]
}
export interface TargetJob { id: string; title: string; company_name: string; required_skills: string[] }
export interface JobTarget { job_id?: string; job_description?: string; required_skills?: string[] }
export interface JobMatch {
  version: string
  target: { title: string; required_skills: string[]; requirements_origin: string }
  requirements: { skill: string; resume_status: 'found' | 'not_found' | 'unknown'; profile_status: string; profile_evidence: string[]; resume_evidence: ExtractedSkill['evidence'] | null }[]
  resume_coverage: { found: number; total: number; percent: number | null }
  profile_coverage: { found: number; total: number }
  note: string
  requirements_note: string
  summary: string[]
  resources: LearningLink[]
  project_suggestions: { title: string; skill: string; description: string }[]
}
export type ProfileScope = 'profile' | 'resume' | 'project' | 'documents' | 'job'
export interface ProfileAnswer {
  provider: string; model: string; answer: string; sources: CitationSource[]; status: string
  error_message?: string | null; latency_ms: number
  answer_kind: 'profile' | 'skill_learning' | 'clarification' | 'out_of_scope' | 'conversation'
  topic?: string | null; knowledge_note?: string | null
}
export interface ProfileChatPayload {
  question: string; provider: string; compare: boolean; scope: ProfileScope; version: string
  project_id?: string; document_id?: string; target?: JobTarget
  conversation_history: { role: 'user' | 'assistant'; content: string }[]
}
type Envelope<T> = { success: boolean; data: T }

export const profileIntelligenceApi = {
  overview: () => api.get<Envelope<ProfileSnapshot>>('/profile-intelligence'),
  refresh: () => api.post<Envelope<ProfileSnapshot>>('/profile-intelligence/refresh'),
  jobs: () => api.get<Envelope<TargetJob[]>>('/profile-intelligence/jobs'),
  match: (target: JobTarget) => api.post<Envelope<JobMatch>>('/profile-intelligence/job-match', target),
  chat: (payload: ProfileChatPayload) => api.post<Envelope<{ version: string; answers: ProfileAnswer[] }>>('/profile-intelligence/chat', payload),
  uploadResume: (file: File, onProgress: (percent: number) => void) => {
    const form = new FormData()
    form.append('file', file)
    return api.post('/students/me/resume', form, { onUploadProgress: event => event.total && onProgress(Math.round(event.loaded / event.total * 100)) })
  },
  deleteResume: () => api.delete('/students/me/resume'),
  saveProfile: (data: Record<string, unknown>) => api.patch('/students/me', data),
  addSkill: (name: string, proficiency_level: string) => api.post('/students/me/skills', { name, proficiency_level }),
  addProject: (project: { title: string; description: string; technologies: string[]; project_url: string | null }) => api.post('/students/me/projects', project),
}
