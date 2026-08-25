from pydantic import BaseModel
from pydantic import ConfigDict
from typing import Optional, List, Any
from uuid import UUID
from datetime import datetime, date

# â”€â”€â”€ Internship Posting â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

class InternshipPostingCreate(BaseModel):
    title: str
    type: str                              # internship|apprenticeship|live_project|industrial_training
    description: Optional[str] = None
    location: Optional[str] = None
    is_remote: bool = False
    duration_weeks: Optional[int] = None
    stipend_monthly: Optional[int] = None
    required_skills: List[str] = []
    required_education: Optional[str] = None
    required_cgpa: float = 0.0
    required_year: List[int] = []
    required_certifications: List[str] = []
    seats_available: int = 1
    application_deadline: Optional[date] = None
    start_date: Optional[date] = None

class InternshipPostingOut(InternshipPostingCreate):
    id: UUID
    company_id: UUID
    company_name: str
    status: str
    posted_at: datetime

    model_config = ConfigDict(from_attributes=True)

class InternshipPostingUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    seats_available: Optional[int] = None
    status: Optional[str] = None
    application_deadline: Optional[date] = None

# â”€â”€â”€ Eligibility â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

class EligibilityCheck(BaseModel):
    eligible: bool
    skill_match_percent: int
    checks: dict
    missing_skills: List[str]
    missing_certifications: List[str]

# â”€â”€â”€ Application â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

class ApplicationCreate(BaseModel):
    cover_letter: Optional[str] = None

class ApplicationOut(BaseModel):
    id: UUID
    student_id: UUID
    internship_id: UUID
    status: str
    skill_match_percent: int
    cover_letter: Optional[str]
    applied_at: datetime
    updated_at: Optional[datetime]
    internship: Optional[InternshipPostingOut] = None

    model_config = ConfigDict(from_attributes=True)

class UpdateApplicationStatus(BaseModel):
    status: str     # shortlisted|assessment|interview|selected|rejected
    company_notes: Optional[str] = None

# â”€â”€â”€ Progress â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

class ProgressUpdate(BaseModel):
    mentor_name: Optional[str] = None
    mentor_email: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    tasks_assigned: Optional[List[Any]] = None
    milestones_completed: Optional[int] = None
    total_milestones: Optional[int] = None
    status: Optional[str] = None

class ProgressOut(BaseModel):
    id: UUID
    application_id: UUID
    mentor_name: Optional[str]
    start_date: Optional[date]
    end_date: Optional[date]
    tasks_assigned: Optional[List[Any]]
    milestones_completed: int
    total_milestones: int
    final_rating: Optional[float]
    completion_certificate_url: Optional[str]
    status: str

    model_config = ConfigDict(from_attributes=True)

# â”€â”€â”€ Mentor Feedback â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

class MentorFeedbackCreate(BaseModel):
    week_number: int
    technical_rating: int
    communication_rating: int
    initiative_rating: int
    overall_rating: int
    comments: Optional[str] = None

class MentorFeedbackOut(MentorFeedbackCreate):
    id: UUID
    progress_id: UUID
    submitted_at: datetime

    model_config = ConfigDict(from_attributes=True)

# â”€â”€â”€ Academician Opportunity â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

class AcademicianOpportunityCreate(BaseModel):
    type: str
    title: str
    description: Optional[str] = None
    duration: Optional[str] = None
    stipend_or_honorarium: Optional[int] = None
    domain: List[str] = []
    eligibility: Optional[str] = None
    application_deadline: Optional[date] = None

class AcademicianOpportunityOut(AcademicianOpportunityCreate):
    id: UUID
    company_id: Optional[UUID]
    company_name: Optional[str]
    status: str
    posted_at: datetime

    model_config = ConfigDict(from_attributes=True)

