from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.api.deps import get_current_user, require_role
from app.models import EmploymentOutcome, Recommendation, Notification
from app.schemas.intelligence import OutcomeIn, OutcomePatch

router=APIRouter(prefix="/outcomes", tags=["Employment Outcomes"])
@router.get("/me")
def mine(db: Session=Depends(get_db), user=Depends(require_role("STUDENT"))):
 return db.query(EmploymentOutcome).filter_by(student_id=user.id).order_by(EmploymentOutcome.created_at.desc()).all()
@router.post("/me", status_code=201)
def create(data: OutcomeIn, db: Session=Depends(get_db), user=Depends(require_role("STUDENT"))):
 row=EmploymentOutcome(student_id=user.id, organization_id=getattr(user, "active_organization_id", None), **data.model_dump()); db.add(row); db.flush(); db.add(Notification(user_id=user.id,title="Employment outcome recorded",message="Your employment outcome was saved.",kind="OUTCOME")); db.commit(); db.refresh(row); return row
@router.patch("/me/{outcome_id}")
def update(outcome_id: UUID,data: OutcomePatch,db: Session=Depends(get_db),user=Depends(require_role("STUDENT"))):
 row=db.query(EmploymentOutcome).filter_by(id=outcome_id,student_id=user.id).first()
 if not row: raise HTTPException(404,"Outcome not found")
 for k,v in data.model_dump(exclude_unset=True).items(): setattr(row,k,v)
 db.commit(); db.refresh(row); return row
@router.post("/me/{outcome_id}/feedback")
def feedback(outcome_id: UUID, rating: int, notes: str|None=None, db: Session=Depends(get_db), user=Depends(require_role("STUDENT"))):
 row=db.query(EmploymentOutcome).filter_by(id=outcome_id,student_id=user.id).first()
 if not row: raise HTTPException(404,"Outcome not found")
 rec=Recommendation(student_id=user.id,recommendation_type="CAREER",title="Employment outcome follow-up",reason=notes,priority=max(0,min(5,6-rating)),source="OUTCOME_FEEDBACK",context={"outcome_id":str(outcome_id),"rating":rating})
 db.add(rec); db.commit(); return {"recorded":True,"recommendation_id":str(rec.id)}
