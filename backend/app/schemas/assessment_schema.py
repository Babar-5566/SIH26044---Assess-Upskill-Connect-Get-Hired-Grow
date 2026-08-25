from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Any, Dict
from uuid import UUID
from datetime import datetime
from app.models.enums import AssessmentType, QuestionType, DifficultyLevel, SessionStatus

# --- Question Schemas ---
class OptionItem(BaseModel):
    id: str
    text: str

class QuestionBase(BaseModel):
    q_type: QuestionType
    difficulty: DifficultyLevel = DifficultyLevel.MEDIUM
    skill_tag: str
    prompt: str
    options: Optional[List[OptionItem]] = None
    marks: int = 2
    negative_marks: float = 0.50

class QuestionCreate(QuestionBase):
    correct_answers: List[str]
    explanation: Optional[str] = None

class QuestionPublicResponse(QuestionBase):
    """Hidden answer for student taking the test"""
    id: UUID
    model_config = ConfigDict(from_attributes=True)

# --- Assessment Schemas ---
class AssessmentCreate(BaseModel):
    title: str = Field(..., max_length=255)
    description: Optional[str] = None
    category: AssessmentType
    target_role: Optional[str] = None
    target_skills: List[str]
    duration_minutes: int = 60
    total_marks: int = 100
    passing_marks: int = 60
    is_proctored: bool = True

class AssessmentResponse(AssessmentCreate):
    id: UUID
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

# --- Assessment Attempt & Responses ---
class SaveResponseRequest(BaseModel):
    question_id: UUID
    selected_options: Optional[List[str]] = None
    submitted_code: Optional[str] = None
    programming_language: Optional[str] = None
    time_spent_seconds: int = 0

class SubmitAssessmentRequest(BaseModel):
    tab_switches_count: int = 0

class AssessmentResultResponse(BaseModel):
    attempt_id: UUID
    assessment_id: UUID
    status: SessionStatus
    score_obtained: float
    percentage: float
    passed: bool
    skill_breakdown: Optional[Dict[str, Any]]
    tab_switches_count: int
    started_at: datetime
    submitted_at: Optional[datetime]
    model_config = ConfigDict(from_attributes=True)
