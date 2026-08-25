from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from uuid import UUID
from datetime import datetime

# ─── Learning Resource ───────────────────────────────────────────────────────

class LearningResourceBase(BaseModel):
    title: str
    type: str
    provider: Optional[str] = None
    description: Optional[str] = None
    skills_covered: List[str] = []
    target_level: Optional[str] = None  # beginner|intermediate|advanced
    duration_hours: Optional[int] = None
    url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    industry_relevant: bool = True
    is_free: bool = False

class LearningResourceCreate(LearningResourceBase):
    pass

class LearningResourceOut(LearningResourceBase):
    id: UUID
    completion_rate: float
    avg_assessment_score: float
    placement_outcome_rate: float
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

# ─── Learning Plan ───────────────────────────────────────────────────────────

class LearningPlanCreate(BaseModel):
    target_role: str

class LearningPlanItemOut(BaseModel):
    id: UUID
    resource_id: UUID
    skill_gap_addressed: Optional[str]
    priority: int
    status: str
    progress_percent: int
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    resource: Optional[LearningResourceOut] = None

    model_config = ConfigDict(from_attributes=True)

class LearningPlanOut(BaseModel):
    id: UUID
    student_id: UUID
    target_role: str
    status: str
    created_at: datetime
    items: List[LearningPlanItemOut] = []

    model_config = ConfigDict(from_attributes=True)

class UpdatePlanItemRequest(BaseModel):
    status: Optional[str] = None        # not_started|in_progress|completed|skipped
    progress_percent: Optional[int] = None

# ─── Certification ───────────────────────────────────────────────────────────

class CertificationCreate(BaseModel):
    resource_id: Optional[UUID] = None
    certification_name: str
    issuer: Optional[str] = None
    issued_date: Optional[datetime] = None
    expiry_date: Optional[datetime] = None
    credential_url: Optional[str] = None
    certificate_file_url: Optional[str] = None

class CertificationOut(CertificationCreate):
    id: UUID
    student_id: UUID
    verified: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

# ─── Recommendation Response ─────────────────────────────────────────────────

class SkillRecommendation(BaseModel):
    skill_gap: str
    priority: int
    resources: List[LearningResourceOut]

class RecommendationResponse(BaseModel):
    student_id: UUID
    target_role: str
    recommendations: List[SkillRecommendation]

