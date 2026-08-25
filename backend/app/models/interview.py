import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, Integer, ForeignKey, DateTime, ARRAY
from sqlalchemy.dialects.postgresql import UUID, ENUM
from sqlalchemy.orm import relationship
from app.db.base import Base
from app.models.enums import InterviewType, DifficultyLevel, SessionStatus

class InterviewSession(Base):
    __tablename__ = "interview_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="SET NULL"), index=True)
    student_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    interview_type = Column(ENUM(InterviewType, name="interview_type"), nullable=False)
    target_role = Column(String(100), nullable=False)
    target_company = Column(String(100), default="Generic")
    difficulty = Column(ENUM(DifficultyLevel, name="difficulty_level"), default=DifficultyLevel.MEDIUM)
    status = Column(ENUM(SessionStatus, name="session_status"), default=SessionStatus.NOT_STARTED)
    started_at = Column(DateTime(timezone=True))
    ended_at = Column(DateTime(timezone=True))

    # Relationships
    turns = relationship("InterviewTurn", back_populates="session", cascade="all, delete-orphan", order_by="InterviewTurn.turn_number")
    evaluation = relationship("InterviewEvaluation", back_populates="session", uselist=False, cascade="all, delete-orphan")


class InterviewTurn(Base):
    __tablename__ = "interview_turns"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("interview_sessions.id", ondelete="CASCADE"), nullable=False)
    turn_number = Column(Integer, nullable=False)
    ai_question = Column(Text, nullable=False)
    expected_competency = Column(String(100))
    student_audio_url = Column(String(500))
    student_transcript = Column(Text)
    code_snippet = Column(Text)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    # Relationships
    session = relationship("InterviewSession", back_populates="turns")


class InterviewEvaluation(Base):
    __tablename__ = "interview_evaluations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("interview_sessions.id", ondelete="CASCADE"), nullable=False, unique=True)
    technical_score = Column(Integer) # 0 to 100
    communication_score = Column(Integer)
    problem_solving_score = Column(Integer)
    behavioral_score = Column(Integer)
    overall_score = Column(Integer)
    strengths = Column(ARRAY(Text))
    areas_for_improvement = Column(ARRAY(Text))
    detailed_feedback = Column(Text)
    star_method_compliance = Column(String(50)) # 'Strong', 'Moderate', 'Needs Work'
    readiness_status = Column(String(50)) # 'Ready', 'Almost Ready', 'Needs Improvement'
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    # Relationships
    session = relationship("InterviewSession", back_populates="evaluation")
