import uuid
import enum
from datetime import datetime
from sqlalchemy import Column, String, Text, ForeignKey, DateTime, ARRAY
from sqlalchemy.dialects.postgresql import UUID, ENUM
from app.db.base import Base

class OpportunityType(str, enum.Enum):
    JOB = "job"
    INTERNSHIP = "internship"
    LIVE_PROJECT = "live_project"
    APPRENTICESHIP = "apprenticeship"

class OpportunityStatus(str, enum.Enum):
    OPEN = "open"
    CLOSED = "closed"
    IN_REVIEW = "in_review"

class IndustryOpportunity(Base):
    __tablename__ = "industry_opportunities"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)
    opportunity_type = Column(ENUM(OpportunityType, name="opportunity_type"), nullable=False)
    description = Column(Text, nullable=False)
    required_skills = Column(ARRAY(String), nullable=False)
    experience_level = Column(String(50), default="Entry-Level")
    stipend_or_salary = Column(String(100))
    location = Column(String(100), default="Remote")
    status = Column(ENUM(OpportunityStatus, name="opportunity_status"), default=OpportunityStatus.OPEN)
    deadline = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)


class IndustryFeedback(Base):
    __tablename__ = "industry_feedback"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    target_role = Column(String(100), nullable=False)
    observed_skill_gaps = Column(ARRAY(String), nullable=False)
    feedback_notes = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
