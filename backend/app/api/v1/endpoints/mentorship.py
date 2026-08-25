from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.api.deps import get_current_user, require_role
from app.models import MentorAssignment
from app.schemas.mentorship import AssignmentCreate, AssignmentOut

router = APIRouter(prefix="/mentorship", tags=["Mentorship"])
@router.post("/assignments", response_model=AssignmentOut, status_code=201)
def assign(data: AssignmentCreate, db: Session=Depends(get_db), user=Depends(require_role("INSTITUTION_ADMIN"))):
 row=MentorAssignment(**data.model_dump()); db.add(row); db.commit(); db.refresh(row); return row
@router.get("/assignments", response_model=list[AssignmentOut])
def assignments(db: Session=Depends(get_db), user=Depends(get_current_user)):
 q=db.query(MentorAssignment)
 if user.role == "MENTOR_TRAINER": q=q.filter_by(mentor_id=user.id)
 elif user.role == "STUDENT": q=q.filter_by(student_id=user.id)
 return q.order_by(MentorAssignment.created_at.desc()).all()
@router.patch("/assignments/{assignment_id}/status", response_model=AssignmentOut)
def update_status(assignment_id: UUID, status: str, db: Session=Depends(get_db), user=Depends(get_current_user)):
 row=db.get(MentorAssignment, assignment_id)
 if not row or user.id not in {row.mentor_id,row.student_id}: raise HTTPException(404,"Assignment not found")
 if status not in {"ACTIVE","COMPLETED","CANCELLED"}: raise HTTPException(422,"Invalid status")
 row.status=status; db.commit(); db.refresh(row); return row
