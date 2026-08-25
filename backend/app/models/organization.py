import uuid
from sqlalchemy import String, Boolean, DateTime, ForeignKey, UniqueConstraint, CheckConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base

ACTOR_ROLES = (
    "STUDENT", "FACULTY", "INSTITUTION_ADMIN", "MENTOR_TRAINER",
    "INDUSTRY_MEMBER_RECRUITER", "INDUSTRY_ADMIN",
)

class Organization(Base):
    __tablename__ = "organizations"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    organization_type: Mapped[str] = mapped_column(String(20), nullable=False)
    slug: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    memberships = relationship("OrganizationMembership", back_populates="organization", cascade="all, delete-orphan")
    __table_args__ = (CheckConstraint("organization_type IN ('INSTITUTION','INDUSTRY')", name="ck_organization_type"),)

class OrganizationMembership(Base):
    __tablename__ = "organization_memberships"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    organization_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    role: Mapped[str] = mapped_column(String(40), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="ACTIVE", nullable=False)
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    user = relationship("User", back_populates="memberships")
    organization = relationship("Organization", back_populates="memberships")
    __table_args__ = (UniqueConstraint("user_id", "organization_id", "role", name="uq_membership_user_org_role"), CheckConstraint("role IN ('STUDENT','FACULTY','INSTITUTION_ADMIN','MENTOR_TRAINER','INDUSTRY_MEMBER_RECRUITER','INDUSTRY_ADMIN')", name="ck_membership_role"))
