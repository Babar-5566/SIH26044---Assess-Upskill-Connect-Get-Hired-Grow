from sqlalchemy import *
from sqlalchemy.orm import Mapped,mapped_column
from app.db.base import Base
class Skill(Base):
 __tablename__='skills'; __table_args__=(CheckConstraint("skill_type IN ('TECHNICAL','SOFT','APTITUDE','DOMAIN','TOOL')"),); id: Mapped[int]=mapped_column(primary_key=True); name: Mapped[str]=mapped_column(String(150),unique=True); normalized_name: Mapped[str]=mapped_column(String(150),unique=True,index=True); skill_type: Mapped[str]=mapped_column(String(20),default='TECHNICAL'); category: Mapped[str|None]=mapped_column(String(100)); is_active: Mapped[bool]=mapped_column(Boolean,default=True); created_at: Mapped[DateTime]=mapped_column(DateTime(timezone=True),server_default=func.now()); updated_at: Mapped[DateTime]=mapped_column(DateTime(timezone=True),server_default=func.now(),onupdate=func.now())
