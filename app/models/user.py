import uuid
from sqlalchemy import String, Boolean, DateTime, CheckConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base
class User(Base):
    __tablename__='users'; __table_args__=(CheckConstraint("role IN ('STUDENT','INDUSTRY','INSTITUTION','ACADEMICIAN','ADMIN')",name='ck_user_role'),)
    id: Mapped[uuid.UUID]=mapped_column(primary_key=True,default=uuid.uuid4)
    email: Mapped[str]=mapped_column(String(255),unique=True,index=True)
    password_hash: Mapped[str]=mapped_column(String(255)); role: Mapped[str]=mapped_column(String(20),default='STUDENT')
    is_active: Mapped[bool]=mapped_column(Boolean,default=True); created_at: Mapped[DateTime]=mapped_column(DateTime(timezone=True),server_default=func.now()); updated_at: Mapped[DateTime]=mapped_column(DateTime(timezone=True),server_default=func.now(),onupdate=func.now())
    profile=relationship('StudentProfile',back_populates='user',cascade='all, delete-orphan',uselist=False)
