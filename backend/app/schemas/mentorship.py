from uuid import UUID
from pydantic import BaseModel, ConfigDict
class AssignmentCreate(BaseModel):
    mentor_id: UUID
    student_id: UUID
    organization_id: UUID | None = None
    focus_area: str | None = None
    notes: str | None = None
class AssignmentOut(AssignmentCreate):
    id: UUID
    status: str
    model_config = ConfigDict(from_attributes=True)
