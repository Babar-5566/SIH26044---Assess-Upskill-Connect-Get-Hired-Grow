from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field

class OrganizationCreate(BaseModel):
    name: str = Field(min_length=2, max_length=255)
    organization_type: str
    slug: str = Field(pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$", min_length=2, max_length=255)

class OrganizationOut(OrganizationCreate):
    id: UUID
    is_active: bool
    # Role is populated when this model is returned in the current user's
    # organization list. It remains optional for backwards compatibility.
    role: str | None = None
    model_config = ConfigDict(from_attributes=True)

class MembershipCreate(BaseModel):
    user_id: UUID
    role: str
    is_primary: bool = False

class MembershipOut(BaseModel):
    id: UUID
    user_id: UUID
    organization_id: UUID
    role: str
    status: str
    is_primary: bool
    name: str | None = None
    email: str | None = None
    profile: dict | None = None
    model_config = ConfigDict(from_attributes=True)
