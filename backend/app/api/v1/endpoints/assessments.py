from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID
from app.db.session import get_db
from app.api.deps import require_role, get_current_user
from app.models import Assessment, Question, AssessmentAttempt, AssessmentResponse
from app.schemas.assessment_schema import AssessmentCreate, AssessmentResponse as AssessmentOut, QuestionCreate, QuestionPublicResponse, SaveResponseRequest, SubmitAssessmentRequest, AssessmentResultResponse

router = APIRouter(prefix="/assessments", tags=["Assessments"])

@router.get("", response_model=list[AssessmentOut])
def list_assessments(db: Session = Depends(get_db), user=Depends(get_current_user)):
    return db.query(Assessment).order_by(Assessment.created_at.desc()).all()

@router.post("", response_model=AssessmentOut, status_code=201)
def create_assessment(data: AssessmentCreate, db: Session = Depends(get_db), user=Depends(require_role("FACULTY"))):
    row = Assessment(created_by=user.id, **data.model_dump()); db.add(row); db.commit(); db.refresh(row); return row

@router.post("/{assessment_id}/questions", response_model=QuestionPublicResponse, status_code=201)
def add_question(assessment_id: UUID, data: QuestionCreate, db: Session = Depends(get_db), user=Depends(require_role("FACULTY"))):
    if not db.get(Assessment, assessment_id): raise HTTPException(404, "Assessment not found")
    row = Question(assessment_id=assessment_id, **data.model_dump()); db.add(row); db.commit(); db.refresh(row); return row

@router.get("/{assessment_id}/questions", response_model=list[QuestionPublicResponse])
def questions(assessment_id: UUID, db: Session = Depends(get_db), user=Depends(get_current_user)):
    return db.query(Question).filter_by(assessment_id=assessment_id).all()

@router.post("/{assessment_id}/attempts", response_model=AssessmentResultResponse, status_code=201)
def start_attempt(assessment_id: UUID, db: Session = Depends(get_db), user=Depends(require_role("STUDENT"))):
    if not db.get(Assessment, assessment_id): raise HTTPException(404, "Assessment not found")
    row = AssessmentAttempt(assessment_id=assessment_id, student_id=user.id); db.add(row); db.commit(); db.refresh(row); return row

@router.post("/attempts/{attempt_id}/responses")
def save_response(attempt_id: UUID, data: SaveResponseRequest, db: Session = Depends(get_db), user=Depends(require_role("STUDENT"))):
    attempt = db.query(AssessmentAttempt).filter_by(id=attempt_id, student_id=user.id).first()
    if not attempt: raise HTTPException(404, "Attempt not found")
    q = db.get(Question, data.question_id)
    if not q or q.assessment_id != attempt.assessment_id: raise HTTPException(400, "Question is not part of this assessment")
    selected = data.selected_options or []
    correct = sorted(selected) == sorted(q.correct_answers or [])
    row = AssessmentResponse(attempt_id=attempt.id, is_correct=correct, marks_awarded=(q.marks if correct else -q.negative_marks), **data.model_dump())
    db.add(row); db.commit(); db.refresh(row); return {"id": str(row.id), "is_correct": correct, "marks_awarded": float(row.marks_awarded)}

@router.post("/attempts/{attempt_id}/submit", response_model=AssessmentResultResponse)
def submit(attempt_id: UUID, data: SubmitAssessmentRequest, db: Session = Depends(get_db), user=Depends(require_role("STUDENT"))):
    attempt = db.query(AssessmentAttempt).filter_by(id=attempt_id, student_id=user.id).first()
    if not attempt: raise HTTPException(404, "Attempt not found")
    assessment = db.get(Assessment, attempt.assessment_id); responses = db.query(AssessmentResponse).filter_by(attempt_id=attempt.id).all()
    score = sum(float(r.marks_awarded or 0) for r in responses); pct = max(0, score / max(assessment.total_marks, 1) * 100)
    attempt.score_obtained=score; attempt.percentage=pct; attempt.passed=pct >= (assessment.passing_marks / max(assessment.total_marks, 1) * 100); attempt.status="COMPLETED"; attempt.submitted_at=datetime.utcnow(); attempt.tab_switches_count=data.tab_switches_count
    db.commit(); db.refresh(attempt); return attempt
