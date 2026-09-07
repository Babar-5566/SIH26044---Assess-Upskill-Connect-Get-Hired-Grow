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
    user_id: UUID | None = None
    user_identifier: str | None = Field(default=None, min_length=1, max_length=255)
    role: str
    is_primary: bool = False

    def identifier(self) -> str:
        value = self.user_identifier or (str(self.user_id) if self.user_id else None)
        if not value:
            raise ValueError("user_identifier or user_id is required")
        return value.strip()

class MembershipOut(BaseModel):
    id: UUID
    user_id: UUID
    organization_id: UUID
    role: str
    status: str
    is_primary: bool
    model_config = ConfigDict(from_attributes=True)
