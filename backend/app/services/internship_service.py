"""
Phase 13 — Internship Module Service Layer
Eligibility checking is 100% rule-based. No AI.
"""
from typing import List, Optional
from uuid import UUID
from datetime import date
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.opportunities import (
    InternshipPosting, AcademicianOpportunity,
    InternshipApplication, InternshipProgress, InternshipMentorFeedback
)
from app.schemas.opportunities import (
    InternshipPostingCreate, InternshipPostingUpdate,
    ApplicationCreate, UpdateApplicationStatus,
    ProgressUpdate, MentorFeedbackCreate,
    AcademicianOpportunityCreate, EligibilityCheck
)


# ─── MOCK Student Profile ─────────────────────────────────────────────────────
# Replace with Phase 9 student profile service call in production.

MOCK_STUDENT_PROFILES = {
    # student_id (str) → profile dict
}

def get_student_profile_mock(student_id: UUID) -> dict:
    return MOCK_STUDENT_PROFILES.get(str(student_id), {
        "cgpa": 7.5,
        "year": 3,
        "degree": "B.Tech",
        "skills": ["Java", "SQL", "Python"],
        "certifications": [],
    })

def get_student_profile(student_id: UUID, db: Session) -> dict:
    from app.models import User, StudentSkill, StudentCertification
    user = db.get(User, student_id)
    profile = user.profile if user else None
    skills = [row.skill.name for row in db.query(StudentSkill).filter_by(student_id=student_id).all() if row.skill]
    certs = [row.name for row in db.query(StudentCertification).filter_by(student_id=student_id).all()]
    if not profile:
        return get_student_profile_mock(student_id)
    year = None
    if profile.graduation_year:
        from datetime import date
        year = max(1, 4 - max(0, profile.graduation_year - date.today().year))
    return {"cgpa": float(profile.cgpa or 0), "year": year, "degree": profile.degree or "", "skills": skills, "certifications": certs}


# ─── Eligibility Checking (Rule-Based) ───────────────────────────────────────

def check_eligibility(student_id: UUID, internship_id: UUID, db: Session) -> EligibilityCheck:
    """
    Pure rule-based eligibility check. Never uses AI.
    Hard checks: education, CGPA, year, deadline, seats.
    Soft check: skill match %.
    """
    posting = db.query(InternshipPosting).filter(InternshipPosting.id == internship_id).first()
    if not posting:
        raise HTTPException(status_code=404, detail="Internship not found")

    student = get_student_profile(student_id, db)
    today = date.today()

    checks = {}
    missing_skills: List[str] = []
    missing_certs: List[str] = []

    # Education
    checks["education_match"] = (
        not posting.required_education or
        posting.required_education.lower() in student.get("degree", "").lower()
    )

    # CGPA
    checks["cgpa_met"] = student.get("cgpa", 0) >= (posting.required_cgpa or 0)

    # Year
    checks["year_match"] = (
        not posting.required_year or
        student.get("year", 0) in posting.required_year
    )

    # Application deadline
    checks["deadline_valid"] = (
        posting.application_deadline is None or
        today <= posting.application_deadline
    )

    # Seats
    current_applicants = (
        db.query(InternshipApplication)
        .filter(InternshipApplication.internship_id == internship_id,
                InternshipApplication.status != "withdrawn")
        .count()
    )
    checks["seats_available"] = current_applicants < (posting.seats_available or 999)

    # Skill match
    required = set(s.lower() for s in (posting.required_skills or []))
    student_skills = set(s.lower() for s in student.get("skills", []))
    matched = required & student_skills
    missing_skills = [s for s in posting.required_skills if s.lower() not in student_skills]
    skill_match_percent = int((len(matched) / len(required)) * 100) if required else 100

    # Certifications
    req_certs = set(c.lower() for c in (posting.required_certifications or []))
    student_certs = set(c.lower() for c in student.get("certifications", []))
    missing_certs = [c for c in posting.required_certifications if c.lower() not in student_certs]
    checks["certifications_met"] = len(missing_certs) == 0

    # Eligible = all HARD checks pass (education, cgpa, year, deadline, seats)
    hard_checks = ["education_match", "cgpa_met", "year_match", "deadline_valid", "seats_available"]
    eligible = all(checks[k] for k in hard_checks)

    return EligibilityCheck(
        eligible=eligible,
        skill_match_percent=skill_match_percent,
        checks=checks,
        missing_skills=missing_skills,
        missing_certifications=missing_certs,
    )


# ─── Internship Ranking ───────────────────────────────────────────────────────

def rank_internships_for_student(student_id: UUID, db: Session) -> List[dict]:
    """
    Weighted scoring: skill_match 50%, career_alignment 25%, stipend 10%, etc.
    Returns ranked list of open internships with match details.
    """
    postings = db.query(InternshipPosting).filter(InternshipPosting.status == "open").all()
    student = get_student_profile(student_id, db)
    student_skills = set(s.lower() for s in student.get("skills", []))

    ranked = []
    for p in postings:
        required = set(s.lower() for s in (p.required_skills or []))
        matched = required & student_skills
        skill_match = (len(matched) / len(required)) if required else 1.0

        # Stipend score (normalised to 0-1, assume max 50000)
        stipend_score = min((p.stipend_monthly or 0) / 50000, 1.0)

        score = (
            skill_match * 0.50 +
            stipend_score * 0.10 +
            (1.0 if not p.required_cgpa or student.get("cgpa", 0) >= p.required_cgpa else 0.3) * 0.15 +
            (1.0 if not p.required_year or student.get("year") in p.required_year else 0.0) * 0.25
        )

        ranked.append({
            "internship": p,
            "skill_match_percent": int(skill_match * 100),
            "score": round(score, 3),
        })

    ranked.sort(key=lambda x: x["score"], reverse=True)
    return ranked


# ─── CRUD: Internship Postings (Company) ─────────────────────────────────────

def create_posting(company_id: UUID, company_name: str, payload: InternshipPostingCreate, db: Session):
    posting = InternshipPosting(company_id=company_id, company_name=company_name, **payload.model_dump())
    db.add(posting)
    db.commit()
    db.refresh(posting)
    return posting

def get_company_postings(company_id: UUID, db: Session):
    return db.query(InternshipPosting).filter(InternshipPosting.company_id == company_id).all()

def update_posting(posting_id: UUID, company_id: UUID, payload: InternshipPostingUpdate, db: Session):
    p = db.query(InternshipPosting).filter(
        InternshipPosting.id == posting_id, InternshipPosting.company_id == company_id
    ).first()
    if not p:
        raise HTTPException(status_code=404, detail="Posting not found")
    for k, v in payload.model_dump(exclude_none=True).items():
        setattr(p, k, v)
    db.commit()
    db.refresh(p)
    return p

def delete_posting(posting_id: UUID, company_id: UUID, db: Session):
    p = db.query(InternshipPosting).filter(
        InternshipPosting.id == posting_id, InternshipPosting.company_id == company_id
    ).first()
    if not p:
        raise HTTPException(status_code=404, detail="Posting not found")
    db.delete(p)
    db.commit()

def get_applicants_for_posting(posting_id: UUID, db: Session, company_id: UUID | None = None):
    if company_id and not db.query(InternshipPosting).filter_by(id=posting_id, company_id=company_id).first():
        raise HTTPException(status_code=404, detail="Posting not found")
    return db.query(InternshipApplication).filter(
        InternshipApplication.internship_id == posting_id
    ).order_by(InternshipApplication.skill_match_percent.desc()).all()


# ─── Applications (Student) ───────────────────────────────────────────────────

def apply_to_internship(student_id: UUID, internship_id: UUID, payload: ApplicationCreate, db: Session):
    # Check if already applied
    existing = db.query(InternshipApplication).filter(
        InternshipApplication.student_id == student_id,
        InternshipApplication.internship_id == internship_id,
    ).first()
    if existing:
        raise HTTPException(status_code=409, detail="Already applied to this internship")

    eligibility = check_eligibility(student_id, internship_id, db)
    if not eligibility.eligible:
        raise HTTPException(status_code=400, detail="You are not eligible for this internship")

    app = InternshipApplication(
        student_id=student_id,
        internship_id=internship_id,
        skill_match_percent=eligibility.skill_match_percent,
        cover_letter=payload.cover_letter,
    )
    db.add(app)
    db.commit()
    db.refresh(app)
    return app

def get_student_applications(student_id: UUID, db: Session):
    return db.query(InternshipApplication).filter(
        InternshipApplication.student_id == student_id
    ).order_by(InternshipApplication.applied_at.desc()).all()

def withdraw_application(app_id: UUID, student_id: UUID, db: Session):
    app = db.query(InternshipApplication).filter(
        InternshipApplication.id == app_id,
        InternshipApplication.student_id == student_id,
    ).first()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    app.status = "withdrawn"
    db.commit()

def update_application_status(app_id: UUID, payload: UpdateApplicationStatus, db: Session, company_id: UUID | None = None):
    app = db.query(InternshipApplication).filter(InternshipApplication.id == app_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    if company_id and not db.query(InternshipPosting).filter_by(id=app.internship_id, company_id=company_id).first():
        raise HTTPException(status_code=404, detail="Application not found")
    allowed = {
        "applied": {"shortlisted", "withdrawn", "rejected"},
        "shortlisted": {"assessment", "interview", "rejected"},
        "assessment": {"interview", "rejected"},
        "interview": {"selected", "rejected"},
        "selected": {"placed", "rejected"},
        "placed": set(),
        "rejected": set(),
        "withdrawn": set(),
    }
    if payload.status not in allowed.get(app.status, set()):
        raise HTTPException(status_code=422, detail=f"Invalid application transition: {app.status} -> {payload.status}")
    app.status = payload.status
    if payload.company_notes:
        app.company_notes = payload.company_notes
    db.commit()
    db.refresh(app)
    return app


# ─── Progress (Company + Student) ─────────────────────────────────────────────

def create_progress(application_id: UUID, payload: ProgressUpdate, db: Session):
    prog = InternshipProgress(application_id=application_id, **payload.model_dump(exclude_none=True))
    db.add(prog)
    db.commit()
    db.refresh(prog)
    return prog

def get_progress(application_id: UUID, db: Session):
    return db.query(InternshipProgress).filter(
        InternshipProgress.application_id == application_id
    ).first()

def update_progress(application_id: UUID, payload: ProgressUpdate, db: Session):
    prog = get_progress(application_id, db)
    if not prog:
        raise HTTPException(status_code=404, detail="Progress record not found")
    for k, v in payload.model_dump(exclude_none=True).items():
        setattr(prog, k, v)
    db.commit()
    db.refresh(prog)
    return prog


# ─── Mentor Feedback ──────────────────────────────────────────────────────────

def submit_feedback(progress_id: UUID, payload: MentorFeedbackCreate, db: Session):
    fb = InternshipMentorFeedback(progress_id=progress_id, **payload.model_dump())
    db.add(fb)
    db.commit()
    db.refresh(fb)
    return fb

def get_feedback_for_progress(progress_id: UUID, db: Session):
    return db.query(InternshipMentorFeedback).filter(
        InternshipMentorFeedback.progress_id == progress_id
    ).order_by(InternshipMentorFeedback.week_number).all()


# ─── Academician Opportunities ────────────────────────────────────────────────

def get_academician_opportunities(type_filter: Optional[str], db: Session):
    q = db.query(AcademicianOpportunity).filter(AcademicianOpportunity.status == "open")
    if type_filter:
        q = q.filter(AcademicianOpportunity.type == type_filter)
    return q.order_by(AcademicianOpportunity.posted_at.desc()).all()

def create_academician_opportunity(company_id: UUID, company_name: str, payload: AcademicianOpportunityCreate, db: Session):
    opp = AcademicianOpportunity(company_id=company_id, company_name=company_name, **payload.model_dump())
    db.add(opp)
    db.commit()
    db.refresh(opp)
    return opp
