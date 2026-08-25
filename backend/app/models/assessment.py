import uuid
from datetime import datetime
from sqlalchemy import (
    Column, String, Text, Integer, Boolean, Numeric, 
    ForeignKey, DateTime, ARRAY
)
from sqlalchemy.dialects.postgresql import UUID, JSONB, ENUM
from sqlalchemy.orm import relationship
from app.db.base import Base
from app.models.enums import AssessmentType, QuestionType, DifficultyLevel, SessionStatus

class Assessment(Base):
    __tablename__ = "assessments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    category = Column(ENUM(AssessmentType, name="assessment_type"), nullable=False)
    target_role = Column(String(100))
    target_skills = Column(ARRAY(String), nullable=False)
    duration_minutes = Column(Integer, nullable=False, default=60)
    total_marks = Column(Integer, nullable=False, default=100)
    passing_marks = Column(Integer, nullable=False, default=60)
    is_proctored = Column(Boolean, default=True)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    # Relationships
    questions = relationship("Question", back_populates="assessment", cascade="all, delete-orphan")
    attempts = relationship("AssessmentAttempt", back_populates="assessment", cascade="all, delete-orphan")


class Question(Base):
    __tablename__ = "questions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    assessment_id = Column(UUID(as_uuid=True), ForeignKey("assessments.id", ondelete="CASCADE"), nullable=False)
    q_type = Column(ENUM(QuestionType, name="question_type"), nullable=False)
    difficulty = Column(ENUM(DifficultyLevel, name="difficulty_level"), default=DifficultyLevel.MEDIUM, nullable=False)
    skill_tag = Column(String(100), nullable=False)
    prompt = Column(Text, nullable=False)
    options = Column(JSONB) # e.g. [{"id": "a", "text": "Option A"}]
    correct_answers = Column(JSONB, nullable=False) # e.g. ["a"]
    explanation = Column(Text)
    marks = Column(Integer, default=2)
    negative_marks = Column(Numeric(3, 2), default=0.50)

    # Relationships
    assessment = relationship("Assessment", back_populates="questions")
    coding_challenge = relationship("CodingChallenge", back_populates="question", uselist=False, cascade="all, delete-orphan")
    responses = relationship("AssessmentResponse", back_populates="question")


class CodingChallenge(Base):
    __tablename__ = "coding_challenges"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    question_id = Column(UUID(as_uuid=True), ForeignKey("questions.id", ondelete="CASCADE"), nullable=False, unique=True)
    problem_statement = Column(Text, nullable=False)
    constraints = Column(Text)
    input_format = Column(Text)
    output_format = Column(Text)
    starter_code = Column(JSONB, nullable=False) # {"python": "...", "java": "..."}
    test_cases = Column(JSONB, nullable=False)   # [{"input": "...", "output": "...", "is_hidden": false}]
    time_limit_ms = Column(Integer, default=2000)
    memory_limit_mb = Column(Integer, default=256)

    # Relationships
    question = relationship("Question", back_populates="coding_challenge")


class AssessmentAttempt(Base):
    __tablename__ = "assessment_attempts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    assessment_id = Column(UUID(as_uuid=True), ForeignKey("assessments.id", ondelete="CASCADE"), nullable=False)
    student_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    status = Column(ENUM(SessionStatus, name="session_status"), default=SessionStatus.IN_PROGRESS)
    started_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    submitted_at = Column(DateTime(timezone=True))
    score_obtained = Column(Numeric(5, 2), default=0)
    percentage = Column(Numeric(5, 2), default=0)
    passed = Column(Boolean, default=False)
    skill_breakdown = Column(JSONB) # {"Java": {"score": 85, "status": "proficient"}}
    tab_switches_count = Column(Integer, default=0)

    # Relationships
    assessment = relationship("Assessment", back_populates="attempts")
    responses = relationship("AssessmentResponse", back_populates="attempt", cascade="all, delete-orphan")


class AssessmentResponse(Base):
    __tablename__ = "assessment_responses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    attempt_id = Column(UUID(as_uuid=True), ForeignKey("assessment_attempts.id", ondelete="CASCADE"), nullable=False)
    question_id = Column(UUID(as_uuid=True), ForeignKey("questions.id", ondelete="CASCADE"), nullable=False)
    selected_options = Column(JSONB)
    submitted_code = Column(Text)
    programming_language = Column(String(50))
    is_correct = Column(Boolean)
    marks_awarded = Column(Numeric(5, 2), default=0)
    time_spent_seconds = Column(Integer, default=0)

    # Relationships
    attempt = relationship("AssessmentAttempt", back_populates="responses")
    question = relationship("Question", back_populates="responses")
