from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.api.deps import require_role
from app.services.learning_service import get_skill_gaps
from app.models import CareerRole, StudentSkill

router=APIRouter(prefix="/skill-gaps", tags=["Skill Gap"])
@router.get("/me")
def mine(target_role: str=Query(...), db: Session=Depends(get_db), user=Depends(require_role("STUDENT"))):
 gaps=get_skill_gaps(user.id,target_role,db); missing=[x for x in gaps if x["status"] != "MET"]
 return {"target_role":target_role,"gaps":gaps,"missing_count":len(missing),"match_percent":round((len(gaps)-len(missing))/max(len(gaps),1)*100,1)}
