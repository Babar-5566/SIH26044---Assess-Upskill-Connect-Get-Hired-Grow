import uuid
from sqlalchemy import *
from sqlalchemy.orm import Mapped,mapped_column
from app.db.base import Base
class AuditLog(Base):
 __tablename__='audit_logs'; id: Mapped[uuid.UUID]=mapped_column(primary_key=True,default=uuid.uuid4); user_id: Mapped[uuid.UUID|None]=mapped_column(ForeignKey('users.id',ondelete='SET NULL')); action: Mapped[str]=mapped_column(String(100)); entity: Mapped[str|None]=mapped_column(String(100)); entity_id: Mapped[str|None]=mapped_column(String(100)); details: Mapped[dict|None]=mapped_column(JSON); ip: Mapped[str|None]=mapped_column(String(50)); created_at: Mapped[DateTime]=mapped_column(DateTime(timezone=True),server_default=func.now())
