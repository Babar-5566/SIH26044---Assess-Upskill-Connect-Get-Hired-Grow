from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.api.deps import get_current_user, require_role
from app.models import Organization, OrganizationMembership, User
from app.schemas.organization import OrganizationCreate, OrganizationOut, MembershipCreate, MembershipOut

router = APIRouter(prefix="/organizations", tags=["Organizations"])

@router.post("", response_model=OrganizationOut, status_code=201)
def create_organization(data: OrganizationCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    if data.organization_type not in {"INSTITUTION", "INDUSTRY"}:
        raise HTTPException(422, "organization_type must be INSTITUTION or INDUSTRY")
    row = Organization(**data.model_dump()); db.add(row); db.flush()
    role = "INSTITUTION_ADMIN" if row.organization_type == "INSTITUTION" else "INDUSTRY_ADMIN"
    db.add(OrganizationMembership(user_id=user.id, organization_id=row.id, role=role, is_primary=True))
    db.commit(); db.refresh(row); return row

@router.get("", response_model=list[OrganizationOut])
def my_organizations(db: Session = Depends(get_db), user=Depends(get_current_user)):
    memberships = db.query(OrganizationMembership).filter_by(user_id=user.id, status="ACTIVE").all()
    # Include the membership role so clients can select an organization and
    # send X-Organization-ID without conflating it with users.role.
    return [{
        "id": m.organization.id,
        "name": m.organization.name,
        "organization_type": m.organization.organization_type,
        "slug": m.organization.slug,
        "is_active": m.organization.is_active,
        "role": m.role,
    } for m in memberships]

@router.post("/{organization_id}/members", response_model=MembershipOut, status_code=201)
def add_member(organization_id: UUID, data: MembershipCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    org = db.get(Organization, organization_id)
    if not org: raise HTTPException(404, "Organization not found")
    admin_role = "INSTITUTION_ADMIN" if org.organization_type == "INSTITUTION" else "INDUSTRY_ADMIN"
    admin = db.query(OrganizationMembership).filter_by(user_id=user.id, organization_id=organization_id, role=admin_role, status="ACTIVE").first()
    if not admin: raise HTTPException(403, "Organization administrator permission required")
    target_user = db.get(User, data.user_id)
    if not target_user or not target_user.is_active: raise HTTPException(404, "Active user not found")
    allowed_roles = ({"STUDENT", "FACULTY", "INSTITUTION_ADMIN", "MENTOR_TRAINER"}
                     if org.organization_type == "INSTITUTION"
                     else {"INDUSTRY_MEMBER_RECRUITER", "INDUSTRY_ADMIN"})
    if data.role not in allowed_roles:
        raise HTTPException(422, "Role is not valid for this organization type")
    duplicate = db.query(OrganizationMembership).filter_by(
        user_id=data.user_id, organization_id=organization_id, role=data.role
    ).first()
    if duplicate:
        raise HTTPException(409, "Membership already exists")
    row = OrganizationMembership(organization_id=organization_id, **data.model_dump()); db.add(row); db.commit(); db.refresh(row); return row

@router.get("/{organization_id}/members", response_model=list[MembershipOut])
def members(organization_id: UUID, db: Session = Depends(get_db), user=Depends(get_current_user)):
    allowed = db.query(OrganizationMembership).filter_by(user_id=user.id, organization_id=organization_id, status="ACTIVE").first()
    if not allowed: raise HTTPException(403, "Active organization membership required")
    return db.query(OrganizationMembership).filter_by(organization_id=organization_id, status="ACTIVE").all()
