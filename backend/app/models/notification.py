import uuid
from datetime import datetime
from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base

class Notification(Base):
    __tablename__ = "notifications"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    kind: Mapped[str] = mapped_column(String(40), default="INFO")
    is_read: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    delivery_status: Mapped[str] = mapped_column(String(20), default="PENDING", nullable=False)
    delivery_attempts: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    delivered_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_delivery_error: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
