from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.api.deps import get_current_user
from app.models import Notification

router = APIRouter(prefix="/notifications", tags=["Notifications"])

@router.get("")
def list_notifications(db: Session = Depends(get_db), user=Depends(get_current_user)):
    return db.query(Notification).filter_by(user_id=user.id).order_by(Notification.created_at.desc()).limit(100).all()

@router.post("/{notification_id}/read")
def mark_read(notification_id: UUID, db: Session = Depends(get_db), user=Depends(get_current_user)):
    row = db.query(Notification).filter_by(id=notification_id, user_id=user.id).first()
    if not row: raise HTTPException(404, "Notification not found")
    row.is_read = True; db.commit(); db.refresh(row); return row

@router.post("/read-all")
def mark_all_read(db: Session = Depends(get_db), user=Depends(get_current_user)):
    db.query(Notification).filter_by(user_id=user.id, is_read=False).update({"is_read": True})
    db.commit(); return {"updated": True}
