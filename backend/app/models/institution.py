import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Numeric, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db.base import Base

class InstitutionDepartment(Base):
    __tablename__ = "institution_departments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    institution_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    department_name = Column(String(100), nullable=False)
    batch_year = Column(Integer, nullable=False)
    total_students = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    readiness_records = relationship("StudentPlacementReadiness", back_populates="department", cascade="all, delete-orphan")


class StudentPlacementReadiness(Base):
    __tablename__ = "student_placement_readiness"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    student_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    department_id = Column(UUID(as_uuid=True), ForeignKey("institution_departments.id", ondelete="CASCADE"), nullable=False)
    employability_score = Column(Numeric(5, 2), default=0)
    readiness_status = Column(String(50), default="Needs Improvement")
    technical_rating = Column(Numeric(5, 2), default=0)
    aptitude_rating = Column(Numeric(5, 2), default=0)
    soft_skills_rating = Column(Numeric(5, 2), default=0)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    department = relationship("InstitutionDepartment", back_populates="readiness_records")
