import uuid
from sqlalchemy import Column, String, Float, Integer, Boolean, DateTime, ARRAY, Text, Date, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.db.base import Base

class InternshipPosting(Base):
    """Internship / apprenticeship / live project posted by a company."""
    __tablename__ = "internship_postings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    organization_id = Column(UUID(as_uuid=True), index=True)
    company_name = Column(String, nullable=False)
    title = Column(String, nullable=False)
    type = Column(String, nullable=False)            # internship|apprenticeship|live_project|industrial_training
    description = Column(Text)
    location = Column(String)
    is_remote = Column(Boolean, default=False)
    duration_weeks = Column(Integer)
    stipend_monthly = Column(Integer)                # NULL = unpaid
    required_skills = Column(ARRAY(String), default=[])
    required_education = Column(String)              # B.Tech, MBA …
    required_cgpa = Column(Float, default=0.0)
    required_year = Column(ARRAY(Integer), default=[])  # [2,3] = 2nd & 3rd year
    required_certifications = Column(ARRAY(String), default=[])
    seats_available = Column(Integer, default=1)
    application_deadline = Column(Date)
    start_date = Column(Date)
    status = Column(String, default="open")          # open|closed|draft
    posted_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class AcademicianOpportunity(Base):
    """Faculty internships, FDPs, research collaborations, etc."""
    __tablename__ = "academician_opportunities"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), index=True)
    organization_id = Column(UUID(as_uuid=True), index=True)
    company_name = Column(String)
    type = Column(String, nullable=False)            # faculty_internship|fdp|consultancy|research_collaboration|guest_lecture|workshop
    title = Column(String, nullable=False)
    description = Column(Text)
    duration = Column(String)
    stipend_or_honorarium = Column(Integer)
    domain = Column(ARRAY(String), default=[])
    eligibility = Column(Text)
    application_deadline = Column(Date)
    status = Column(String, default="open")
    posted_at = Column(DateTime(timezone=True), server_default=func.now())


class InternshipApplication(Base):
    """Student application to an internship."""
    __tablename__ = "internship_applications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    student_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    internship_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    # applied→shortlisted→assessment→interview→selected→rejected→withdrawn
    status = Column(String, default="applied")
    skill_match_percent = Column(Integer, default=0)
    cover_letter = Column(Text)
    applied_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    company_notes = Column(Text)


class InternshipProgress(Base):
    """Tracks an ongoing/completed internship after selection."""
    __tablename__ = "internship_progress"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    application_id = Column(UUID(as_uuid=True), nullable=False, unique=True, index=True)
    mentor_name = Column(String)
    mentor_email = Column(String)
    start_date = Column(Date)
    end_date = Column(Date)
    tasks_assigned = Column(JSON, default=[])        # list of {task, due_date, done}
    milestones_completed = Column(Integer, default=0)
    total_milestones = Column(Integer, default=0)
    mentor_feedback = Column(Text)
    final_rating = Column(Float)                     # 1–5
    completion_certificate_url = Column(String)
    status = Column(String, default="ongoing")       # ongoing|completed|dropped
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class InternshipMentorFeedback(Base):
    """Weekly structured feedback from mentor."""
    __tablename__ = "internship_mentor_feedback"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    progress_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    week_number = Column(Integer, nullable=False)
    technical_rating = Column(Integer)               # 1–5
    communication_rating = Column(Integer)
    initiative_rating = Column(Integer)
    overall_rating = Column(Integer)
    comments = Column(Text)
    submitted_at = Column(DateTime(timezone=True), server_default=func.now())
