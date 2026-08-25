from uuid import UUID
from sqlalchemy.orm import Session
from app.models import Notification


def queue(db: Session, user_id: UUID, title: str, message: str, kind: str = "INFO") -> Notification:
    """Persist a notification transactionally; a worker can deliver it later."""
    item = Notification(user_id=user_id, title=title, message=message, kind=kind)
    db.add(item)
    return item
