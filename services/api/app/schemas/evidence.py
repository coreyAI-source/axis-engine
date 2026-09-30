from datetime import datetime, date
from uuid import UUID
from pydantic import BaseModel


class EvidenceCreate(BaseModel):
    audit_id: UUID | None = None
    audit_prompt_id: UUID | None = None
    monitoring_run_id: UUID | None = None
    process_id: UUID | None = None
    clause_id: UUID | None = None
    evidence_type: str
    file_uri: str | None = None
    note_text: str | None = None


class EvidenceOut(BaseModel):
    id: UUID
    audit_id: UUID | None
    audit_prompt_id: UUID | None
    monitoring_run_id: UUID | None
    process_id: UUID | None
    clause_id: UUID | None
    evidence_type: str
    file_uri: str | None
    note_text: str | None
    uploaded_by: UUID | None
    uploaded_at: datetime

    model_config = {"from_attributes": True}


class FindingCreate(BaseModel):
    audit_id: UUID | None = None
    process_id: UUID | None = None
    clause_id: UUID | None = None
    finding_code: str
    finding_type: str
    title: str
    requirement_text: str | None = None
    evidence_summary: str | None = None
    description: str
    severity_score: int | None = None


class FindingUpdate(BaseModel):
    title: str | None = None
    finding_type: str | None = None
    requirement_text: str | None = None
    evidence_summary: str | None = None
    description: str | None = None
    severity_score: int | None = None


class FindingOut(BaseModel):
    id: UUID
    audit_id: UUID | None
    process_id: UUID | None
    clause_id: UUID | None
    finding_code: str
    finding_type: str
    title: str
    requirement_text: str | None
    evidence_summary: str | None
    description: str
    severity_score: int | None
    created_by: UUID | None
    created_at: datetime

    model_config = {"from_attributes": True}


class ActionCreate(BaseModel):
    finding_id: UUID | None = None
    title: str
    description: str | None = None
    assigned_to_user_id: UUID | None = None
    assigned_to_role_id: UUID | None = None
    due_date: datetime | None = None
    verification_required: bool = True


class ActionUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    assigned_to_user_id: UUID | None = None
    assigned_to_role_id: UUID | None = None
    due_date: datetime | None = None
    status: str | None = None
    lag_status: str | None = None
    verification_required: bool | None = None
    verification_evidence: str | None = None


class ActionOut(BaseModel):
    id: UUID
    finding_id: UUID | None
    title: str
    description: str | None
    assigned_to_user_id: UUID | None
    assigned_to_role_id: UUID | None
    due_date: datetime | None
    status: str
    escalation_level: int
    lag_status: str
    last_activity_at: datetime | None
    verification_required: bool
    verification_evidence: str | None
    closed_at: datetime | None

    model_config = {"from_attributes": True}


class ActionCommentCreate(BaseModel):
    action_id: UUID
    comment_text: str


class ActionCommentOut(BaseModel):
    id: UUID
    action_id: UUID
    comment_text: str
    created_by: UUID | None
    created_at: datetime

    model_config = {"from_attributes": True}


class NotificationOut(BaseModel):
    id: UUID
    action_id: UUID | None
    audit_id: UUID | None
    notification_type: str
    recipient_user_id: UUID | None
    subject: str | None
    body: str | None
    sent_at: datetime | None

    model_config = {"from_attributes": True}
