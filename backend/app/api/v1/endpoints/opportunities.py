from fastapi import APIRouter, Depends, Query, Path
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List, Optional

from app.db.session import get_db
from app.api.deps import get_current_user, require_roles, require_role
from app.models.user import User
from app.models.opportunities import InternshipPosting, AcademicianOpportunity
from app.schemas.opportunities import (
    InternshipPostingCreate, InternshipPostingOut, InternshipPostingUpdate,
    ApplicationCreate, ApplicationOut, UpdateApplicationStatus,
    ProgressUpdate, ProgressOut,
    MentorFeedbackCreate, MentorFeedbackOut,
    AcademicianOpportunityCreate, AcademicianOpportunityOut,
    EligibilityCheck,
)
from app.services import internship_service

router = APIRouter(prefix="/internships", tags=["Phase 13 – Internship Module"])


# ─── Student: Discover & Browse ───────────────────────────────────────────────

@router.get("", response_model=List[InternshipPostingOut])
def list_internships(
    type: Optional[str] = Query(None),
    location: Optional[str] = Query(None),
    is_remote: Optional[bool] = Query(None),
    skills: Optional[str] = Query(None, description="Comma-separated skills to filter by"),
    db: Session = Depends(get_db),
):
    """Browse all open internship postings with optional filters."""
    q = db.query(InternshipPosting).filter(InternshipPosting.status == "open")
    if type:
        q = q.filter(InternshipPosting.type == type)
    if location:
        q = q.filter(InternshipPosting.location.ilike(f"%{location}%"))
    if is_remote is not None:
        q = q.filter(InternshipPosting.is_remote == is_remote)
    if skills:
        for skill in skills.split(","):
            q = q.filter(InternshipPosting.required_skills.any(skill.strip()))
    return q.order_by(InternshipPosting.posted_at.desc()).all()


@router.get("/recommended", response_model=List[dict])
def get_recommended_internships(
    current_user: User = Depends(require_role("student")),
    db: Session = Depends(get_db),
):
    """Get personalized ranked internships for the current student."""
    ranked = internship_service.rank_internships_for_student(current_user.id, db)
    # Serialize: replace model object with dict
    result = []
    for item in ranked[:20]:
        posting = item["internship"]
        result.append({
            "id": str(posting.id),
            "title": posting.title,
            "company_name": posting.company_name,
            "type": posting.type,
            "location": posting.location,
            "is_remote": posting.is_remote,
            "stipend_monthly": posting.stipend_monthly,
            "duration_weeks": posting.duration_weeks,
            "required_skills": posting.required_skills,
            "skill_match_percent": item["skill_match_percent"],
            "score": item["score"],
            "application_deadline": str(posting.application_deadline) if posting.application_deadline else None,
        })
    return result

@router.get("/matching/me")
def matching_for_student(current_user: User = Depends(require_role("student")), db: Session = Depends(get_db)):
    ranked = internship_service.rank_internships_for_student(current_user.id, db)
    return [{"id": str(item["internship"].id), "title": item["internship"].title, "match_percent": item["skill_match_percent"], "score": item["score"]} for item in ranked[:20]]


@router.get("/{internship_id}", response_model=InternshipPostingOut)
def get_internship_detail(internship_id: UUID, db: Session = Depends(get_db)):
    """Get full internship details."""
    p = db.query(InternshipPosting).filter(InternshipPosting.id == internship_id).first()
    if not p:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Internship not found")
    return p


@router.get("/{internship_id}/eligibility", response_model=EligibilityCheck)
def check_eligibility(
    internship_id: UUID,
    current_user: User = Depends(require_role("student")),
    db: Session = Depends(get_db),
):
    """Rule-based eligibility check for a student on a specific internship."""
    return internship_service.check_eligibility(current_user.id, internship_id, db)


# ─── Student: Applications ────────────────────────────────────────────────────

@router.post("/{internship_id}/apply", response_model=ApplicationOut, status_code=201)
def apply(
    internship_id: UUID,
    payload: ApplicationCreate,
    current_user: User = Depends(require_role("student")),
    db: Session = Depends(get_db),
):
    """Apply to an internship (eligibility is checked automatically)."""
    return internship_service.apply_to_internship(current_user.id, internship_id, payload, db)


@router.get("/applications/me", response_model=List[ApplicationOut])
def my_applications(
    current_user: User = Depends(require_role("student")),
    db: Session = Depends(get_db),
):
    """Get all internship applications for the current student."""
    return internship_service.get_student_applications(current_user.id, db)


@router.put("/applications/{app_id}/withdraw")
def withdraw(
    app_id: UUID,
    current_user: User = Depends(require_role("student")),
    db: Session = Depends(get_db),
):
    """Withdraw an application."""
    internship_service.withdraw_application(app_id, current_user.id, db)
    return {"message": "Application withdrawn"}


# ─── Student: Progress ────────────────────────────────────────────────────────

@router.get("/applications/{app_id}/progress", response_model=Optional[ProgressOut])
def get_my_progress(
    app_id: UUID,
    current_user: User = Depends(require_role("student")),
    db: Session = Depends(get_db),
):
    """Get internship progress for a student's active internship."""
    return internship_service.get_progress(app_id, db)


# ─── Company: Manage Postings ─────────────────────────────────────────────────

@router.post("/company/postings", response_model=InternshipPostingOut, status_code=201)
def create_posting(
    payload: InternshipPostingCreate,
    current_user: User = Depends(require_role("company")),
    db: Session = Depends(get_db),
):
    """Company: Post a new internship."""
    posting = internship_service.create_posting(current_user.id, current_user.email, payload, db)
    if getattr(current_user, "active_organization_id", None):
        posting.organization_id = current_user.active_organization_id
        db.commit(); db.refresh(posting)
    return posting


@router.get("/company/postings", response_model=List[InternshipPostingOut])
def get_my_postings(
    current_user: User = Depends(require_role("company")),
    db: Session = Depends(get_db),
):
    """Company: List all their internship postings."""
    rows = internship_service.get_company_postings(current_user.id, db)
    org_id = getattr(current_user, "active_organization_id", None)
    return [row for row in rows if not org_id or row.organization_id == org_id]


@router.put("/company/postings/{posting_id}", response_model=InternshipPostingOut)
def update_posting(
    posting_id: UUID,
    payload: InternshipPostingUpdate,
    current_user: User = Depends(require_role("company")),
    db: Session = Depends(get_db),
):
    """Company: Update an internship posting."""
    return internship_service.update_posting(posting_id, current_user.id, payload, db)


@router.delete("/company/postings/{posting_id}")
def delete_posting(
    posting_id: UUID,
    current_user: User = Depends(require_role("company")),
    db: Session = Depends(get_db),
):
    """Company: Delete an internship posting."""
    internship_service.delete_posting(posting_id, current_user.id, db)
    return {"message": "Posting deleted"}


@router.get("/company/postings/{posting_id}/applicants", response_model=List[ApplicationOut])
def get_applicants(
    posting_id: UUID,
    current_user: User = Depends(require_role("company")),
    db: Session = Depends(get_db),
):
    """Company: Get all applicants for a posting, sorted by skill match."""
    return internship_service.get_applicants_for_posting(posting_id, db, current_user.id)


@router.put("/company/applications/{app_id}/status", response_model=ApplicationOut)
def update_application_status(
    app_id: UUID,
    payload: UpdateApplicationStatus,
    current_user: User = Depends(require_role("company")),
    db: Session = Depends(get_db),
):
    """Company: Move an application through the status pipeline."""
    return internship_service.update_application_status(app_id, payload, db, current_user.id)


# ─── Company: Progress & Feedback ────────────────────────────────────────────

@router.post("/company/applications/{app_id}/progress", response_model=ProgressOut, status_code=201)
def create_progress(
    app_id: UUID,
    payload: ProgressUpdate,
    current_user: User = Depends(require_role("company")),
    db: Session = Depends(get_db),
):
    """Company: Initialize internship progress record for a selected applicant."""
    return internship_service.create_progress(app_id, payload, db)


@router.put("/company/applications/{app_id}/progress", response_model=ProgressOut)
def update_progress(
    app_id: UUID,
    payload: ProgressUpdate,
    current_user: User = Depends(require_role("company")),
    db: Session = Depends(get_db),
):
    """Company: Update internship progress (milestones, status, final rating)."""
    return internship_service.update_progress(app_id, payload, db)


@router.post("/company/progress/{progress_id}/feedback", response_model=MentorFeedbackOut, status_code=201)
def submit_feedback(
    progress_id: UUID,
    payload: MentorFeedbackCreate,
    current_user: User = Depends(require_role("company")),
    db: Session = Depends(get_db),
):
    """Company: Submit weekly mentor feedback for an intern."""
    return internship_service.submit_feedback(progress_id, payload, db)


@router.get("/company/progress/{progress_id}/feedback", response_model=List[MentorFeedbackOut])
def get_feedback(
    progress_id: UUID,
    current_user: User = Depends(require_role("company")),
    db: Session = Depends(get_db),
):
    """Company/Student: Get all feedback for an internship progress record."""
    return internship_service.get_feedback_for_progress(progress_id, db)


# ─── Academician Opportunities ────────────────────────────────────────────────

@router.get("/academician/opportunities", response_model=List[AcademicianOpportunityOut])
def list_academician_opportunities(
    type: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Academician: Browse faculty internships, FDPs, research collaborations, etc."""
    return internship_service.get_academician_opportunities(type, db)


@router.post("/academician/opportunities", response_model=AcademicianOpportunityOut, status_code=201)
def post_academician_opportunity(
    payload: AcademicianOpportunityCreate,
    current_user: User = Depends(require_role("company")),
    db: Session = Depends(get_db),
):
    """Company: Post an academician opportunity (FDP, guest lecture, etc.)."""
    return internship_service.create_academician_opportunity(
        current_user.id, current_user.email, payload, db
    )


# ─── Institution Stats ────────────────────────────────────────────────────────

@router.get("/institution/stats")
def institution_internship_stats(
    current_user: User = Depends(require_role("institution")),
    db: Session = Depends(get_db),
):
    """Institution: Get aggregate internship participation statistics."""
    from app.models.internship import InternshipApplication, InternshipProgress
    total_applications = db.query(InternshipApplication).count()
    active_internships = db.query(InternshipProgress).filter(InternshipProgress.status == "ongoing").count()
    completed_internships = db.query(InternshipProgress).filter(InternshipProgress.status == "completed").count()
    return {
        "total_applications": total_applications,
        "active_internships": active_internships,
        "completed_internships": completed_internships,
        "completion_rate": round(completed_internships / max(total_applications, 1) * 100, 1),
    }
