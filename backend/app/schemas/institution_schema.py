from pydantic import BaseModel, ConfigDict
from typing import List
from uuid import UUID
from datetime import datetime

class DepartmentCreate(BaseModel):
    department_name: str
    batch_year: int
    total_students: int = 0

class DepartmentResponse(DepartmentCreate):
    id: UUID
    institution_id: UUID
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class SkillHeatmapItem(BaseModel):
    skill_name: str
    proficiency_percentage: float

class InstitutionAnalyticsSummary(BaseModel):
    total_students: int
    ready_count: int
    almost_ready_count: int
    needs_improvement_count: int
    average_employability_score: float
    skill_heatmap: List[SkillHeatmapItem]
