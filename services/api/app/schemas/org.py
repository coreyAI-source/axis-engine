from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, EmailStr, Field


class OrganisationCreate(BaseModel):
    name: str
    legal_name: str | None = None


class OrganisationUpdate(BaseModel):
    name: str | None = None
    legal_name: str | None = None
    active_flag: bool | None = None


class OrganisationOut(BaseModel):
    id: UUID
    name: str
    legal_name: str | None
    active_flag: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class SiteCreate(BaseModel):
    organisation_id: UUID
    name: str
    description: str | None = None


class SiteUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    active_flag: bool | None = None


class SiteOut(BaseModel):
    id: UUID
    organisation_id: UUID
    name: str
    description: str | None
    active_flag: bool

    model_config = {"from_attributes": True}


class RoleCreate(BaseModel):
    code: str
    name: str
    description: str | None = None


class RoleOut(BaseModel):
    id: UUID
    code: str
    name: str
    description: str | None

    model_config = {"from_attributes": True}


class UserCreate(BaseModel):
    organisation_id: UUID
    first_name: str
    last_name: str
    email: EmailStr
    password: str = Field(min_length=12, max_length=72)
    role_id: UUID | None = None
    role_code: str | None = None


class UserUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    email: EmailStr | None = None
    role_id: UUID | None = None
    role_code: str | None = None
    active_flag: bool | None = None


class UserOut(BaseModel):
    id: UUID
    organisation_id: UUID
    first_name: str
    last_name: str
    email: str
    role_id: UUID | None
    role_code: str | None
    active_flag: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    user_id: str | None = None
    email: str | None = None
