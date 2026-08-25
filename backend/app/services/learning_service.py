"""
Phase 12 — Learning & Development Service Layer
All recommendation logic is rule-based here. AI enhancement deferred to Phase 22.
"""
from typing import List, Optional
from uuid import UUID
from datetime import datetime
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.learning import (
    LearningResource, StudentLearningPlan, LearningPlanItem,
    LearningCertification, LearningOutcome
)
from app.schemas.learning import (
    LearningPlanCreate, UpdatePlanItemRequest, CertificationCreate,
    RecommendationResponse, SkillRecommendation
)


def get_skill_gaps(student_id: UUID, target_role: str, db: Session) -> List[dict]:
    from app.models import CareerRole, StudentSkill, InternshipPosting
    role = db.query(CareerRole).filter(CareerRole.name.ilike(target_role)).first()
    required = []
    if role and getattr(role, "required_skills", None):
        required = role.required_skills
    if not required:
        # Derive requirements from persisted opportunity data for this role.
        required = []
        postings = db.query(InternshipPosting).filter(InternshipPosting.status == "open").all()
        role_tokens = {token for token in target_role.lower().split() if len(token) > 2}
        for posting in postings:
            if role_tokens and not role_tokens.intersection(set((posting.title or "").lower().split())):
                continue
            required.extend(posting.required_skills or [])
        required = list(dict.fromkeys(required))
    owned = {row.skill.name.lower() for row in db.query(StudentSkill).filter_by(student_id=student_id).all() if row.skill}
    return [{"skill": skill, "priority": index, "status": "MET" if skill.lower() in owned else "MISSING"} for index, skill in enumerate(required, 1)]


# ─── Recommendation Engine ───────────────────────────────────────────────────

def get_recommendations(student_id: UUID, target_role: str, db: Session) -> RecommendationResponse:
    """
    Rule-based recommendation:
    1. Identify skill gaps for target_role
    2. For each gap, find resources covering that skill
    3. Sort by placement_outcome_rate → completion_rate → industry_relevant
    """
    gaps = get_skill_gaps(student_id, target_role, db)
    recommendations: List[SkillRecommendation] = []

    for gap in gaps:
        skill = gap["skill"]
        resources = (
            db.query(LearningResource)
            .filter(LearningResource.skills_covered.any(skill))
            .order_by(
                LearningResource.placement_outcome_rate.desc(),
                LearningResource.completion_rate.desc(),
                LearningResource.industry_relevant.desc(),
            )
            .limit(3)
            .all()
        )
        recommendations.append(
            SkillRecommendation(skill_gap=skill, priority=gap["priority"], resources=resources)
        )

    return RecommendationResponse(
        student_id=student_id, target_role=target_role, recommendations=recommendations
    )


# ─── Learning Plan ───────────────────────────────────────────────────────────

def create_or_replace_plan(student_id: UUID, payload: LearningPlanCreate, db: Session, organization_id: UUID | None = None) -> StudentLearningPlan:
    """Creates a new plan (abandons any existing active plan for same role)."""
    existing = (
        db.query(StudentLearningPlan)
        .filter(StudentLearningPlan.student_id == student_id,
                StudentLearningPlan.target_role == payload.target_role,
                StudentLearningPlan.status == "active")
        .first()
    )
    if existing:
        existing.status = "abandoned"

    plan = StudentLearningPlan(student_id=student_id, target_role=payload.target_role, organization_id=organization_id)
    db.add(plan)
    db.flush()

    # Auto-populate plan with recommendations
    gaps = get_skill_gaps(student_id, payload.target_role, db)
    for gap in gaps:
        skill = gap["skill"]
        resources = (
            db.query(LearningResource)
            .filter(LearningResource.skills_covered.any(skill))
            .order_by(LearningResource.placement_outcome_rate.desc())
            .limit(2)
            .all()
        )
        for res in resources:
            item = LearningPlanItem(
                plan_id=plan.id,
                resource_id=res.id,
                skill_gap_addressed=skill,
                priority=gap["priority"],
            )
            db.add(item)

    db.commit()
    db.refresh(plan)
    return plan


def get_plan_with_items(student_id: UUID, db: Session) -> Optional[StudentLearningPlan]:
    plan = (
        db.query(StudentLearningPlan)
        .filter(StudentLearningPlan.student_id == student_id,
                StudentLearningPlan.status == "active")
        .first()
    )
    return plan


def update_plan_item(item_id: UUID, payload: UpdatePlanItemRequest, db: Session, student_id: UUID | None = None) -> LearningPlanItem:
    query = db.query(LearningPlanItem).filter(LearningPlanItem.id == item_id)
    if student_id is not None:
        query = query.join(StudentLearningPlan, LearningPlanItem.plan_id == StudentLearningPlan.id).filter(StudentLearningPlan.student_id == student_id)
    item = query.first()
    if not item:
        raise HTTPException(status_code=404, detail="Plan item not found")
    if payload.status:
        item.status = payload.status
        if payload.status == "in_progress" and not item.started_at:
            item.started_at = datetime.utcnow()
        if payload.status == "completed":
            item.completed_at = datetime.utcnow()
            item.progress_percent = 100
    if payload.progress_percent is not None:
        item.progress_percent = payload.progress_percent
    db.commit()
    db.refresh(item)
    return item


# ─── Certifications ──────────────────────────────────────────────────────────

def add_certification(student_id: UUID, payload: CertificationCreate, db: Session) -> LearningCertification:
    cert = LearningCertification(student_id=student_id, **payload.model_dump())
    db.add(cert)
    db.commit()
    db.refresh(cert)
    return cert


def get_certifications(student_id: UUID, db: Session) -> List[LearningCertification]:
    return db.query(LearningCertification).filter(LearningCertification.student_id == student_id).all()


# ─── Skill Improvement Summary ───────────────────────────────────────────────

def get_skill_improvement(student_id: UUID, db: Session) -> dict:
    """
    Returns a summary of completed resources grouped by skill gap.
    In Phase 22 this will query Phase 10 re-assessment scores.
    """
    plans = db.query(StudentLearningPlan).filter(StudentLearningPlan.student_id == student_id).all()
    result = {}
    for plan in plans:
        items = db.query(LearningPlanItem).filter(LearningPlanItem.plan_id == plan.id).all()
        for item in items:
            skill = item.skill_gap_addressed or "General"
            if skill not in result:
                result[skill] = {"completed": 0, "total": 0, "progress_avg": 0}
            result[skill]["total"] += 1
            if item.status == "completed":
                result[skill]["completed"] += 1
            result[skill]["progress_avg"] += item.progress_percent

    for skill in result:
        total = result[skill]["total"]
        result[skill]["progress_avg"] = round(result[skill]["progress_avg"] / total, 1) if total else 0

    return {"student_id": str(student_id), "skill_progress": result}
