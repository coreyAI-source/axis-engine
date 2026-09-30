from datetime import datetime
from uuid import UUID
from pydantic import BaseModel


class ProcessCreate(BaseModel):
    organisation_id: UUID
    code: str
    name: str
    category: str
    description: str | None = None
    owner_role_id: UUID | None = None
    site_scope: str | None = None


class ProcessUpdate(BaseModel):
    code: str | None = None
    name: str | None = None
    category: str | None = None
    description: str | None = None
    owner_role_id: UUID | None = None
    site_scope: str | None = None
    active_flag: bool | None = None


class ProcessOut(BaseModel):
    id: UUID
    organisation_id: UUID
    code: str
    name: str
    category: str
    description: str | None
    owner_role_id: UUID | None
    site_scope: str | None
    active_flag: bool
    created_at: datetime

    model_config = {"from_attributes": True}
