from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.api.deps import require_role
from app.services.resume_intelligence import analyze_resume_text

router=APIRouter(prefix="/resume-intelligence", tags=["Resume Intelligence"])
@router.post("/analyze")
def analyze(text: str, target_role: str|None=None, db: Session=Depends(get_db), user=Depends(require_role("STUDENT"))):
 if not text.strip(): raise HTTPException(422,"Resume text is required")
 return analyze_resume_text(text, target_role, db)
