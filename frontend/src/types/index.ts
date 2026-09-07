// Shared TypeScript types for Phase 12 & 13

export type ActorRole = 'STUDENT' | 'FACULTY' | 'INSTITUTION_ADMIN' | 'MENTOR_TRAINER' | 'INDUSTRY_MEMBER_RECRUITER' | 'INDUSTRY_ADMIN'

export interface User {
  id: string
  email: string
  full_name: string
  role: ActorRole | 'student' | 'company' | 'institution' | 'academician' | 'admin'
  organizations?: OrganizationMembership[]
}

export interface OrganizationMembership {
  id: string
  organization_id: string
  role: ActorRole
  status: string
  is_primary: boolean
}

export interface Organization {
  id: string
  name: string
  organization_type: string
  slug: string
  is_active: boolean
  /** Role of the current user in this organization (contextual, not global). */
  role?: ActorRole | string | null
  membership_role?: ActorRole | string | null
  membership_is_primary?: boolean
}

export interface AuthToken {
  access_token: string
  token_type: string
  role: string
  user_id: string
  full_name: string
}

// ─── Phase 12: Learning ───────────────────────────────────────────────────────

export interface LearningResource {
  id: string
  title: string
  type: string
  provider?: string
  description?: string
  skills_covered: string[]
  target_level?: string
  duration_hours?: number
  url?: string
  thumbnail_url?: string
  industry_relevant: boolean
  is_free: boolean
  completion_rate: number
  avg_assessment_score: number
  placement_outcome_rate: number
}

export interface LearningPlanItem {
  id: string
  resource_id: string
  skill_gap_addressed?: string
  priority: number
  status: 'not_started' | 'in_progress' | 'completed' | 'skipped'
  progress_percent: number
  started_at?: string
  completed_at?: string
  resource?: LearningResource
}

export interface LearningPlan {
  id: string
  student_id: string
  target_role: string
  status: string
  created_at: string
  items: LearningPlanItem[]
}

export interface SkillRecommendation {
  skill_gap: string
  priority: number
  resources: LearningResource[]
}

export interface RecommendationResponse {
  student_id: string
  target_role: string
  recommendations: SkillRecommendation[]
}

export interface Certification {
  id: string
  student_id: string
  resource_id?: string
  certification_name: string
  issuer?: string
  issued_date?: string
  expiry_date?: string
  credential_url?: string
  certificate_file_url?: string
  verified: boolean
  created_at: string
}

// ─── Phase 13: Internship ─────────────────────────────────────────────────────

export interface InternshipPosting {
  id: string
  company_id: string
  company_name: string
  title: string
  type: string
  description?: string
  location?: string
  is_remote: boolean
  duration_weeks?: number
  stipend_monthly?: number
  required_skills: string[]
  required_education?: string
  required_cgpa: number
  required_year: number[]
  required_certifications: string[]
  seats_available: number
  application_deadline?: string
  start_date?: string
  status: string
  posted_at: string
  // client-side enrichment
  skill_match_percent?: number
  score?: number
}

export interface EligibilityCheck {
  eligible: boolean
  skill_match_percent: number
  checks: Record<string, boolean>
  missing_skills: string[]
  missing_certifications: string[]
}

export interface InternshipApplication {
  id: string
  student_id: string
  internship_id: string
  status: string
  skill_match_percent: number
  cover_letter?: string
  applied_at: string
  updated_at?: string
  internship?: InternshipPosting
}

export interface InternshipProgress {
  id: string
  application_id: string
  mentor_name?: string
  start_date?: string
  end_date?: string
  tasks_assigned?: any[]
  milestones_completed: number
  total_milestones: number
  final_rating?: number
  completion_certificate_url?: string
  status: string
}

export interface MentorFeedback {
  id: string
  progress_id: string
  week_number: number
  technical_rating: number
  communication_rating: number
  initiative_rating: number
  overall_rating: number
  comments?: string
  submitted_at: string
}

export interface AcademicianOpportunity {
  id: string
  company_id?: string
  company_name?: string
  type: string
  title: string
  description?: string
  duration?: string
  stipend_or_honorarium?: number
  domain: string[]
  eligibility?: string
  application_deadline?: string
  status: string
  posted_at: string
}
