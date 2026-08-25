from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
from uuid import UUID
from datetime import datetime
from app.models.industry import OpportunityType, OpportunityStatus

class OpportunityCreate(BaseModel):
    title: str = Field(..., max_length=255)
    opportunity_type: OpportunityType
    description: str
    required_skills: List[str]
    experience_level: Optional[str] = "Entry-Level"
    stipend_or_salary: Optional[str] = None
    location: Optional[str] = "Remote"
    deadline: Optional[datetime] = None

class OpportunityResponse(OpportunityCreate):
    id: UUID
    company_id: UUID
    status: OpportunityStatus
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class FeedbackCreate(BaseModel):
    target_role: str
    observed_skill_gaps: List[str]
    feedback_notes: str

class FeedbackResponse(FeedbackCreate):
    id: UUID
    company_id: UUID
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
