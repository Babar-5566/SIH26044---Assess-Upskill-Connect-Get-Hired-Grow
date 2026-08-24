import uuid
from sqlalchemy import *
from sqlalchemy.orm import Mapped,mapped_column
from app.db.base import Base
class StudentDocument(Base):
 __tablename__='student_documents'; __table_args__=(CheckConstraint("document_type IN ('RESUME','CERTIFICATE','TRANSCRIPT','OTHER')"),); id: Mapped[uuid.UUID]=mapped_column(primary_key=True,default=uuid.uuid4); student_id: Mapped[uuid.UUID]=mapped_column(ForeignKey('users.id',ondelete='CASCADE')); document_type: Mapped[str]=mapped_column(String(20),default='RESUME'); file_name: Mapped[str]=mapped_column(String(255)); file_path: Mapped[str]=mapped_column(String(500)); file_size: Mapped[int]=mapped_column(Integer); mime_type: Mapped[str|None]=mapped_column(String(100)); is_active: Mapped[bool]=mapped_column(Boolean,default=True); uploaded_at: Mapped[DateTime]=mapped_column(DateTime(timezone=True),server_default=func.now())
