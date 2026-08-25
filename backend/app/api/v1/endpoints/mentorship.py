from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.api.deps import get_current_user, require_role
from app.models import MentorAssignment, User, OrganizationMembership
from app.schemas.mentorship import AssignmentCreate, AssignmentOut

router = APIRouter(prefix="/mentorship", tags=["Mentorship"])
@router.post("/assignments", response_model=AssignmentOut, status_code=201)
def assign(data: AssignmentCreate, db: Session=Depends(get_db), user=Depends(require_role("INSTITUTION_ADMIN"))):
    mentor = db.get(User, data.mentor_id)
    student = db.get(User, data.student_id)
    if not mentor or mentor.role != "MENTOR_TRAINER":
        raise HTTPException(422, "mentor_id must reference an active mentor")
    if not student or student.role != "STUDENT":
        raise HTTPException(422, "student_id must reference an active student")
    if data.organization_id:
        membership = db.query(OrganizationMembership).filter_by(
            user_id=user.id, organization_id=data.organization_id,
            role="INSTITUTION_ADMIN", status="ACTIVE"
        ).first()
        if not membership:
            raise HTTPException(403, "Organization administrator permission required")
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
 if user.id == row.student_id and status not in {"CANCELLED"}:
  raise HTTPException(403, "Only the assigned mentor may change assignment status")
 if status not in {"ACTIVE","COMPLETED","CANCELLED"}: raise HTTPException(422,"Invalid status")
 row.status=status; db.commit(); db.refresh(row); return row
