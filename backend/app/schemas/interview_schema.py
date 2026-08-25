from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
from uuid import UUID
from datetime import datetime
from app.models.enums import InterviewType, DifficultyLevel, SessionStatus

# --- Interview Session Schemas ---
class StartInterviewRequest(BaseModel):
    interview_type: InterviewType
    target_role: str = Field(..., example="Java Backend Developer")
    target_company: Optional[str] = Field(default="Generic", example="Google")
    difficulty: DifficultyLevel = DifficultyLevel.MEDIUM

class InterviewSessionResponse(BaseModel):
    id: UUID
    student_id: UUID
    interview_type: InterviewType
    target_role: str
    target_company: Optional[str]
    difficulty: DifficultyLevel
    status: SessionStatus
    started_at: Optional[datetime]
    model_config = ConfigDict(from_attributes=True)

# --- Dialogue Turns ---
class SubmitAnswerTurnRequest(BaseModel):
    turn_number: int
    student_transcript: str
    code_snippet: Optional[str] = None
    student_audio_url: Optional[str] = None

class InterviewTurnResponse(BaseModel):
    id: UUID
    turn_number: int
    ai_question: str
    expected_competency: Optional[str]
    student_transcript: Optional[str]
    code_snippet: Optional[str]
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

# --- Interview Evaluation Report ---
class InterviewEvaluationResponse(BaseModel):
    session_id: UUID
    technical_score: int
    communication_score: int
    problem_solving_score: int
    behavioral_score: int
    overall_score: int
    strengths: List[str]
    areas_for_improvement: List[str]
    detailed_feedback: str
    star_method_compliance: str
    readiness_status: str # 'Ready' | 'Almost Ready' | 'Needs Improvement'
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
