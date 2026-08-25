import uuid
from sqlalchemy import Column, String, Float, Integer, Boolean, DateTime, ARRAY, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.db.base import Base

class LearningResource(Base):
    """A course, workshop, certification, FDP, mentorship, or project resource."""
    __tablename__ = "learning_resources"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="SET NULL"), index=True)
    title = Column(String, nullable=False)
    type = Column(String, nullable=False)            # course|workshop|fdp|certification|mentorship|project
    provider = Column(String)                        # Coursera, NPTEL, internal, industry_partner
    description = Column(Text)
    skills_covered = Column(ARRAY(String), default=[])
    target_level = Column(String)                    # beginner|intermediate|advanced
    duration_hours = Column(Integer)
    url = Column(String)
    thumbnail_url = Column(String)
    industry_relevant = Column(Boolean, default=True)
    is_free = Column(Boolean, default=False)
    completion_rate = Column(Float, default=0.0)     # 0.0 – 1.0
    avg_assessment_score = Column(Float, default=0.0)
    placement_outcome_rate = Column(Float, default=0.0)  # fraction of completers placed
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class StudentLearningPlan(Base):
    """One active learning plan per student per target role."""
    __tablename__ = "student_learning_plans"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="SET NULL"), index=True)
    student_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    target_role = Column(String, nullable=False)
    status = Column(String, default="active")        # active|completed|abandoned
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class LearningPlanItem(Base):
    """One resource item inside a student's learning plan."""
    __tablename__ = "learning_plan_items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    plan_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    resource_id = Column(UUID(as_uuid=True), nullable=False)
    skill_gap_addressed = Column(String)
    priority = Column(Integer, default=1)
    status = Column(String, default="not_started")   # not_started|in_progress|completed|skipped
    progress_percent = Column(Integer, default=0)
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))


class LearningCertification(Base):
    """Certifications earned or uploaded by a student."""
    __tablename__ = "learning_certifications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    student_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    resource_id = Column(UUID(as_uuid=True))          # nullable – can be external cert
    certification_name = Column(String, nullable=False)
    issuer = Column(String)
    issued_date = Column(DateTime(timezone=True))
    expiry_date = Column(DateTime(timezone=True))
    credential_url = Column(String)
    certificate_file_url = Column(String)
    verified = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class LearningOutcome(Base):
    """Aggregated outcome data per resource × target_role (fed by Phase 21)."""
    __tablename__ = "learning_outcomes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    resource_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    target_role = Column(String, nullable=False)
    completion_count = Column(Integer, default=0)
    placement_count = Column(Integer, default=0)
    avg_time_to_placement_days = Column(Integer)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
