"""Durable extraction jobs, keyed to an immutable saved resume."""
import uuid
from datetime import datetime
from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Integer, JSON, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base


class ProfileResumeAnalysis(Base):
    __tablename__ = "profile_resume_analyses"
    __table_args__ = (CheckConstraint("status IN ('PENDING','PROCESSING','READY','NEEDS_ATTENTION')"),)

    document_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("student_documents.id", ondelete="CASCADE"), primary_key=True)
    student_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    status: Mapped[str] = mapped_column(String(24), default="PENDING", index=True)
    content_hash: Mapped[str | None] = mapped_column(String(64))
    extractor_version: Mapped[str] = mapped_column(String(20), default="1")
    attempts: Mapped[int] = mapped_column(Integer, default=0)
    lease_token: Mapped[str | None] = mapped_column(String(36))
    leased_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    result: Mapped[dict | None] = mapped_column(JSON)
    chunks: Mapped[list | None] = mapped_column(JSON)
    error_message: Mapped[str | None] = mapped_column(Text)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
