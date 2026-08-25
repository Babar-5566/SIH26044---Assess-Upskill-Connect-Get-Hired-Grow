from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List, Optional

from app.db.session import get_db
from app.api.deps import get_current_user, require_roles, require_role
from app.models.user import User
from app.schemas.learning import (
    LearningResourceCreate, LearningResourceOut,
    LearningPlanCreate, LearningPlanOut,
    UpdatePlanItemRequest, LearningPlanItemOut,
    CertificationCreate, CertificationOut,
    RecommendationResponse,
)
from app.services import learning_service
from app.models.learning import LearningResource, StudentLearningPlan, LearningPlanItem

router = APIRouter(prefix="/learning", tags=["Phase 12 – Learning & Development"])


# ─── Learning Resources (Admin / Seeding) ────────────────────────────────────

@router.post("/resources", response_model=LearningResourceOut, status_code=201)
def create_resource(
    payload: LearningResourceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin")),
):
    """Add a new learning resource (admin only)."""
    resource = LearningResource(organization_id=getattr(current_user, "active_organization_id", None), **payload.model_dump())
    db.add(resource)
    db.commit()
    db.refresh(resource)
    return resource


@router.get("/resources", response_model=List[LearningResourceOut])
def list_resources(
    skill: Optional[str] = Query(None, description="Filter by skill covered"),
    type: Optional[str] = Query(None, description="Filter by type (course|workshop|fdp|certification|mentorship|project)"),
    level: Optional[str] = Query(None, description="Filter by level (beginner|intermediate|advanced)"),
    is_free: Optional[bool] = Query(None),
    db: Session = Depends(get_db),
):
    """List all learning resources with optional filters."""
    q = db.query(LearningResource)
    if skill:
        q = q.filter(LearningResource.skills_covered.any(skill))
    if type:
        q = q.filter(LearningResource.type == type)
    if level:
        q = q.filter(LearningResource.target_level == level)
    if is_free is not None:
        q = q.filter(LearningResource.is_free == is_free)
    return q.order_by(LearningResource.placement_outcome_rate.desc()).all()


@router.get("/resources/{resource_id}", response_model=LearningResourceOut)
def get_resource(resource_id: UUID, db: Session = Depends(get_db)):
    r = db.query(LearningResource).filter(LearningResource.id == resource_id).first()
    if not r:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Resource not found")
    return r


# ─── Recommendations ─────────────────────────────────────────────────────────

@router.get("/recommendations", response_model=RecommendationResponse)
def get_recommendations(
    role: str = Query(..., description="Target career role"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get personalized learning recommendations based on skill gaps for the target role.
    Rule-based in Phase 12. AI-enhanced in Phase 22.
    """
    return learning_service.get_recommendations(current_user.id, role, db)


# ─── Learning Plans ───────────────────────────────────────────────────────────

@router.post("/plans", response_model=LearningPlanOut, status_code=201)
def create_plan(
    payload: LearningPlanCreate,
    current_user: User = Depends(require_role("student")),
    db: Session = Depends(get_db),
):
    """Create a new learning plan auto-populated from recommendations."""
    return learning_service.create_or_replace_plan(current_user.id, payload, db, getattr(current_user, "active_organization_id", None))


@router.get("/plans/me", response_model=Optional[LearningPlanOut])
def get_my_plan(
    current_user: User = Depends(require_role("student")),
    db: Session = Depends(get_db),
):
    """Get the current student's active learning plan."""
    plan = learning_service.get_plan_with_items(current_user.id, db)
    if not plan:
        return None
    # Attach resource details to each item
    items = db.query(LearningPlanItem).filter(LearningPlanItem.plan_id == plan.id).order_by(LearningPlanItem.priority).all()
    for item in items:
        item.resource = db.query(LearningResource).filter(LearningResource.id == item.resource_id).first()
    plan.items = items
    return plan


@router.put("/plans/items/{item_id}", response_model=LearningPlanItemOut)
def update_item(
    item_id: UUID,
    payload: UpdatePlanItemRequest,
    current_user: User = Depends(require_role("student")),
    db: Session = Depends(get_db),
):
    """Update progress or status of a plan item."""
    return learning_service.update_plan_item(item_id, payload, db, current_user.id)


@router.delete("/plans/me")
def abandon_plan(
    current_user: User = Depends(require_role("student")),
    db: Session = Depends(get_db),
):
    """Abandon the active learning plan."""
    plan = db.query(StudentLearningPlan).filter(
        StudentLearningPlan.student_id == current_user.id,
        StudentLearningPlan.status == "active",
    ).first()
    if plan:
        plan.status = "abandoned"
        db.commit()
    return {"message": "Plan abandoned"}


# ─── Progress Summary ─────────────────────────────────────────────────────────

@router.get("/progress/me")
def get_my_progress(
    current_user: User = Depends(require_role("student")),
    db: Session = Depends(get_db),
):
    """Get skill improvement summary across all learning plans."""
    return learning_service.get_skill_improvement(current_user.id, db)


# ─── Certifications ───────────────────────────────────────────────────────────

@router.post("/certifications", response_model=CertificationOut, status_code=201)
def add_certification(
    payload: CertificationCreate,
    current_user: User = Depends(require_role("student")),
    db: Session = Depends(get_db),
):
    """Add a certification (earned externally or via platform)."""
    return learning_service.add_certification(current_user.id, payload, db)


@router.get("/certifications/me", response_model=List[CertificationOut])
def get_my_certifications(
    current_user: User = Depends(require_role("student")),
    db: Session = Depends(get_db),
):
    """Get all certifications for the current student."""
    return learning_service.get_certifications(current_user.id, db)
