from fastapi import Depends, HTTPException, Header
from uuid import UUID
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models import User
from app.models import OrganizationMembership
from app.core.security import decode_token
bearer=HTTPBearer(auto_error=False)
def get_current_user(credentials=Depends(bearer), db:Session=Depends(get_db), x_organization_id: str|None=Header(default=None,alias="X-Organization-ID")):
 if not credentials: raise HTTPException(401,"Unauthorized")
 p=decode_token(credentials.credentials)
 if not p or not p.get('sub'):
  raise HTTPException(401,"Unauthorized")
 try: user_id = UUID(str(p['sub']))
 except (ValueError, TypeError): raise HTTPException(401,"Unauthorized")
 u=db.get(User,user_id)
 if not u or not u.is_active: raise HTTPException(401,"Unauthorized")
 # Keep the persisted platform role untouched, while exposing the role this
 # user has in the selected organization for authorization/UI decisions.
 # Clients select context explicitly via X-Organization-ID; this allows one
 # account to hold different roles in different organizations.
 u.effective_role = u.role
 u.active_organization_id = None
 if x_organization_id:
  try:
   organization_id = UUID(x_organization_id)
  except (ValueError, TypeError):
   raise HTTPException(400, "Invalid organization context")
  membership = db.query(OrganizationMembership).filter(
   OrganizationMembership.user_id == u.id,
   OrganizationMembership.organization_id == organization_id,
   OrganizationMembership.status == "ACTIVE",
  ).first()
  if not membership:
   raise HTTPException(403, "Active organization membership required")
  u.effective_role = membership.role
  u.active_organization_id = organization_id
 return u
def require_roles(*roles):
 def dep(user=Depends(get_current_user)):
  if user.role == "ADMIN":
   allowed = "ADMIN" in roles
  elif getattr(user, "active_organization_id", None) is not None:
   allowed = getattr(user, "effective_role", None) in roles
  else:
   allowed = user.role in roles
  if not allowed: raise HTTPException(403,"Forbidden")
  return user
 return dep

def require_role(role):
 aliases={
  "student":("STUDENT",),
  "company":("INDUSTRY_MEMBER_RECRUITER","INDUSTRY_ADMIN"),
  "industry":("INDUSTRY_MEMBER_RECRUITER","INDUSTRY_ADMIN"),
  "institution":("INSTITUTION_ADMIN","FACULTY"),
  "academician":("FACULTY",),
  # Platform administration is intentionally distinct from tenant admins.
  "admin":("ADMIN",),
  "faculty":("FACULTY","INSTITUTION_ADMIN"),
 }
 allowed=aliases.get(role.lower(),(role.upper(),))
 def dep(user=Depends(get_current_user), db:Session=Depends(get_db), x_organization_id: str|None=Header(default=None,alias="X-Organization-ID")):
  if x_organization_id:
   # get_current_user has already validated and resolved this context.
   if user.role == "ADMIN" and "ADMIN" in allowed: return user
   if getattr(user, "effective_role", None) in allowed: return user
   raise HTTPException(403,"Insufficient organization permissions")
  if user.role in allowed: return user
  raise HTTPException(403,"Forbidden")
 return dep

def get_active_membership(organization_id: UUID, user=Depends(get_current_user), db: Session=Depends(get_db)):
 m = db.query(OrganizationMembership).filter_by(user_id=user.id, organization_id=organization_id, status="ACTIVE").first()
 if not m: raise HTTPException(403, "Active organization membership required")
 return m

def require_membership_roles(*roles):
 def dep(m=Depends(get_active_membership)):
  if m.role not in roles: raise HTTPException(403, "Insufficient organization permissions")
  return m
 return dep
