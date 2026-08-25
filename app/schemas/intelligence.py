from datetime import date, datetime
from pydantic import BaseModel, ConfigDict, Field

class OutcomeIn(BaseModel):
    status: str = "SEEKING"
    company_name: str | None = None
    job_title: str | None = None
    employment_type: str | None = None
    joined_on: date | None = None
    ended_on: date | None = None
    salary: float | None = Field(default=None, ge=0)
    notes: str | None = None

class OutcomePatch(BaseModel):
    status: str | None = None
    company_name: str | None = None
    job_title: str | None = None
    employment_type: str | None = None
    joined_on: date | None = None
    ended_on: date | None = None
    salary: float | None = Field(default=None, ge=0)
    notes: str | None = None

class RecommendationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    recommendation_type: str
    title: str
    reason: str | None
    priority: int
    source: str
    status: str
    context: dict | None
    expires_at: datetime | None
