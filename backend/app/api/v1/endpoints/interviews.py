from datetime import datetime
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.api.deps import require_role, get_current_user
from app.models import InterviewSession, InterviewTurn, InterviewEvaluation
from app.schemas.interview import InterviewCreate, TurnCreate, EvaluationCreate, InterviewOut
from app.models.enums import SessionStatus

router = APIRouter(prefix="/interviews", tags=["Interviews"])
@router.post("", response_model=InterviewOut, status_code=201)
def create(data: InterviewCreate, db: Session=Depends(get_db), user=Depends(require_role("STUDENT"))):
 row=InterviewSession(student_id=user.id, organization_id=getattr(user, "active_organization_id", None), **data.model_dump()); db.add(row); db.commit(); db.refresh(row); return row
@router.get("", response_model=list[InterviewOut])
def mine(db: Session=Depends(get_db), user=Depends(get_current_user)):
 return db.query(InterviewSession).filter_by(student_id=user.id).order_by(InterviewSession.started_at.desc()).all()
@router.post("/{session_id}/start", response_model=InterviewOut)
def start(session_id: UUID, db: Session=Depends(get_db), user=Depends(get_current_user)):
 row=db.query(InterviewSession).filter_by(id=session_id, student_id=user.id).first()
 if not row: raise HTTPException(404,"Interview not found")
 if row.status != SessionStatus.NOT_STARTED: raise HTTPException(409, "Interview has already started or ended")
 row.status="IN_PROGRESS"; row.started_at=datetime.utcnow(); db.commit(); db.refresh(row); return row
@router.post("/{session_id}/turns")
def turn(session_id: UUID, data: TurnCreate, db: Session=Depends(get_db), user=Depends(get_current_user)):
 row=db.query(InterviewSession).filter_by(id=session_id, student_id=user.id).first()
 if not row: raise HTTPException(404,"Interview not found")
 if row.status != SessionStatus.IN_PROGRESS: raise HTTPException(409, "Interview is not in progress")
 n=db.query(InterviewTurn).filter_by(session_id=session_id).count()+1
 item=InterviewTurn(session_id=session_id, turn_number=n, **data.model_dump()); db.add(item); db.commit(); db.refresh(item); return {"id":str(item.id),"turn_number":n}
@router.post("/{session_id}/evaluate", response_model=InterviewOut)
def evaluate(session_id: UUID, data: EvaluationCreate, db: Session=Depends(get_db), user=Depends(get_current_user)):
 row=db.query(InterviewSession).filter_by(id=session_id, student_id=user.id).first()
 if not row: raise HTTPException(404,"Interview not found")
 if row.status != SessionStatus.IN_PROGRESS: raise HTTPException(409, "Interview is not in progress")
 vals=[data.technical_score,data.communication_score,data.problem_solving_score,data.behavioral_score]
 ev=InterviewEvaluation(session_id=session_id, overall_score=round(sum(vals)/4), readiness_status="Ready" if sum(vals)/4>=75 else "Almost Ready", **data.model_dump()); row.status="EVALUATED"; row.ended_at=datetime.utcnow(); db.add(ev); db.commit(); db.refresh(row); return row
