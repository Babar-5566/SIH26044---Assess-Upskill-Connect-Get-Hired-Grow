from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field
from app.models.enums import InterviewType, DifficultyLevel

class InterviewCreate(BaseModel):
 interview_type: InterviewType
 target_role: str
 target_company: str = "Generic"
 difficulty: DifficultyLevel = DifficultyLevel.MEDIUM
class TurnCreate(BaseModel):
 ai_question: str
 expected_competency: str | None = None
class EvaluationCreate(BaseModel):
 technical_score: int = Field(0, ge=0, le=100); communication_score: int = Field(0, ge=0, le=100); problem_solving_score: int = Field(0, ge=0, le=100); behavioral_score: int = Field(0, ge=0, le=100)
 strengths: list[str] = []; areas_for_improvement: list[str] = []; detailed_feedback: str | None = None
class InterviewOut(BaseModel):
 id: UUID; student_id: UUID; target_role: str; target_company: str; status: str
 model_config = ConfigDict(from_attributes=True)
