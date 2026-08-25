from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.api.deps import get_current_user
from app.models import StudentSkill, Recommendation, InternshipApplication, InterviewSession, EmploymentOutcome
from app.models import InternshipPosting, MentorAssignment, OrganizationMembership, User

router=APIRouter(prefix="/dashboard", tags=["Dashboards"])
@router.get("/student")
def student(db: Session=Depends(get_db), user=Depends(get_current_user)):
 return {"student_id":str(user.id),"skills":db.query(StudentSkill).filter_by(student_id=user.id).count(),"recommendations":db.query(Recommendation).filter_by(student_id=user.id,status="ACTIVE").count(),"applications":db.query(InternshipApplication).filter_by(student_id=user.id).count(),"interviews":db.query(InterviewSession).filter_by(student_id=user.id).count(),"outcomes":db.query(EmploymentOutcome).filter_by(student_id=user.id).count()}

@router.get("/industry")
def industry(db: Session=Depends(get_db), user=Depends(get_current_user)):
 return {"organization_user_id":str(user.id),"open_opportunities":db.query(InternshipPosting).filter_by(company_id=user.id,status="open").count()}

@router.get("/mentor")
def mentor(db: Session=Depends(get_db), user=Depends(get_current_user)):
 return {"mentor_id":str(user.id),"active_assignments":db.query(MentorAssignment).filter_by(mentor_id=user.id,status="ACTIVE").count(),"completed_assignments":db.query(MentorAssignment).filter_by(mentor_id=user.id,status="COMPLETED").count()}

@router.get("/institution/{organization_id}")
def institution(organization_id: str, db: Session=Depends(get_db), user=Depends(get_current_user)):
 membership=db.query(OrganizationMembership).filter_by(user_id=user.id,organization_id=organization_id,status="ACTIVE").first()
 if not membership: from fastapi import HTTPException; raise HTTPException(403,"Active organization membership required")
 return {"organization_id":organization_id,"active_members":db.query(OrganizationMembership).filter_by(organization_id=organization_id,status="ACTIVE").count(),"students":db.query(OrganizationMembership).filter_by(organization_id=organization_id,status="ACTIVE",role="STUDENT").count()}
