from sqlalchemy import *
from sqlalchemy.orm import Mapped,mapped_column
from app.db.base import Base
class CareerRole(Base):
 __tablename__='career_roles'; id: Mapped[int]=mapped_column(primary_key=True); name: Mapped[str]=mapped_column(String(200),unique=True); normalized_name: Mapped[str]=mapped_column(String(200),unique=True,index=True); category: Mapped[str|None]=mapped_column(String(100)); is_active: Mapped[bool]=mapped_column(Boolean,default=True); created_at: Mapped[DateTime]=mapped_column(DateTime(timezone=True),server_default=func.now()); updated_at: Mapped[DateTime]=mapped_column(DateTime(timezone=True),server_default=func.now(),onupdate=func.now())
