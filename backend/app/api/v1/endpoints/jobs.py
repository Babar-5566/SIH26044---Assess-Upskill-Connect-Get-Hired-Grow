from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.api.deps import get_current_user, require_role
from app.models import InternshipPosting, InternshipApplication

router=APIRouter(prefix="/jobs", tags=["Jobs and Placement"])
@router.get("")
def list_jobs(db: Session=Depends(get_db), user=Depends(get_current_user)):
 return db.query(InternshipPosting).filter(InternshipPosting.status=="open", InternshipPosting.type.in_(["job","graduate_opportunity","full_time"])).all()
@router.get("/{job_id}")
def detail(job_id: UUID, db: Session=Depends(get_db), user=Depends(get_current_user)):
 row=db.get(InternshipPosting,job_id)
 if not row: raise HTTPException(404,"Job not found")
 return row
@router.post("/{job_id}/apply")
def apply(job_id: UUID, cover_letter: str|None=None, db: Session=Depends(get_db), user=Depends(require_role("STUDENT"))):
 job=db.get(InternshipPosting,job_id)
 if not job or job.type not in {"job","graduate_opportunity","full_time"}: raise HTTPException(404,"Job not found")
 if db.query(InternshipApplication).filter_by(internship_id=job_id,student_id=user.id).first(): raise HTTPException(409,"Already applied")
 row=InternshipApplication(internship_id=job_id, organization_id=job.organization_id, student_id=user.id,cover_letter=cover_letter); db.add(row); db.commit(); db.refresh(row); return row
