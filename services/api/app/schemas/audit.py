from datetime import datetime, date
from uuid import UUID
from pydantic import BaseModel


class AuditCreate(BaseModel):
    organisation_id: UUID
    site_id: UUID | None = None
    audit_type: str
    audit_stage: str = "DocumentReview"
    auditee_name: str | None = None
    audit_client: str | None = None
    audit_body: str | None = None
    lead_auditor_user_id: UUID | None = None
    objective: str | None = None
    scope: str | None = None
    criteria_text: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    duration_days: int | None = None
    main_location: str | None = None
    auditee_contact: str | None = None


class AuditUpdate(BaseModel):
    audit_type: str | None = None
    audit_stage: str | None = None
    status: str | None = None
    auditee_name: str | None = None
    audit_client: str | None = None
    audit_body: str | None = None
    lead_auditor_user_id: UUID | None = None
    objective: str | None = None
    scope: str | None = None
    criteria_text: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    duration_days: int | None = None
    main_location: str | None = None
    auditee_contact: str | None = None


class AuditOut(BaseModel):
    id: UUID
    organisation_id: UUID
    site_id: UUID | None
    audit_type: str
    audit_stage: str
    status: str
    auditee_name: str | None
    audit_client: str | None
    audit_body: str | None
    lead_auditor_user_id: UUID | None
    objective: str | None
    scope: str | None
    criteria_text: str | None
    start_date: date | None
    end_date: date | None
    duration_days: int | None
    main_location: str | None
    auditee_contact: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class AuditTeamMemberCreate(BaseModel):
    audit_id: UUID
    user_id: UUID
    role_in_audit: str | None = None


class AuditTeamMemberOut(BaseModel):
    id: UUID
    audit_id: UUID
    user_id: UUID
    role_in_audit: str | None

    model_config = {"from_attributes": True}


class AuditLocationCreate(BaseModel):
    audit_id: UUID
    site_name: str
    is_main_location: bool = False
    confirmed_flag: bool = False


class AuditLocationOut(BaseModel):
    id: UUID
    audit_id: UUID
    site_name: str
    is_main_location: bool
    confirmed_flag: bool

    model_config = {"from_attributes": True}


class AuditProcessCreate(BaseModel):
    audit_id: UUID
    process_id: UUID


class AuditProcessOut(BaseModel):
    id: UUID
    audit_id: UUID
    process_id: UUID

    model_config = {"from_attributes": True}


class AuditPromptCreate(BaseModel):
    audit_id: UUID
    process_id: UUID | None = None
    clause_id: UUID | None = None
    prompt_text: str
    prompt_type: str = "DocumentCheck"
    evidence_required: bool = False
    sequence_no: int | None = None


class AuditPromptUpdate(BaseModel):
    response_status: str | None = None
    comments: str | None = None
    responded_by: UUID | None = None


class AuditPromptOut(BaseModel):
    id: UUID
    audit_id: UUID
    process_id: UUID | None
    clause_id: UUID | None
    prompt_text: str
    prompt_type: str
    evidence_required: bool
    sequence_no: int | None
    response_status: str
    comments: str | None
    responded_at: datetime | None
    responded_by: UUID | None

    model_config = {"from_attributes": True}
