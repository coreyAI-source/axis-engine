from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class StrictInput(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


Role = Literal["admin", "compliance_manager", "lead_auditor", "auditor", "process_owner", "viewer"]


class MemberCreate(StrictInput):
    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    email: EmailStr
    password: str = Field(min_length=12, max_length=72)
    role_code: Role = "auditor"


class AuditCreate(StrictInput):
    title: str = Field(min_length=1, max_length=255)
    site_name: str = Field(min_length=1, max_length=255)
    scope_statement: str = Field(default="", max_length=4000)


class Command(StrictInput):
    expected_version: int = Field(ge=1)
    operation: Literal["assess", "evidence", "action.create", "action.progress", "action.submit", "action.verify", "finding.close", "finding.withdraw", "status", "complete", "requirement.create", "requirement.review"]
    input: dict = Field(default_factory=dict)


class Assess(StrictInput):
    requirementId: UUID
    status: Literal["unassessed", "conforming", "observation", "minor", "major", "not_applicable"]
    rationale: str = Field(max_length=12000)
    evidenceIds: list[UUID] = Field(default_factory=list, max_length=100)


class EvidenceInput(StrictInput):
    kind: Literal["document", "photo", "record", "interview", "observation"]
    description: str = Field(min_length=1, max_length=4000)
    reference: str | None = Field(default=None, max_length=1000)


class NewAction(StrictInput):
    findingId: UUID
    description: str = Field(min_length=1, max_length=4000)
    ownerUserId: UUID


class Progress(StrictInput):
    actionId: UUID
    note: str = Field(min_length=1, max_length=4000)


class Implementation(Progress):
    evidenceIds: list[UUID] = Field(min_length=1, max_length=100)


class Verify(Progress):
    outcome: Literal["effective", "not_effective"]


class FindingInput(StrictInput):
    findingId: UUID


class Withdrawal(FindingInput):
    rationale: str = Field(min_length=1, max_length=4000)


class StatusInput(StrictInput):
    status: Literal["in_progress", "reporting"]


class Source(StrictInput):
    documentId: str = Field(min_length=1, max_length=255)
    documentTitle: str = Field(min_length=1, max_length=500)
    revision: str = Field(min_length=1, max_length=100)
    section: str | None = Field(default=None, max_length=100)
    clause: str | None = Field(default=None, max_length=100)
    page: str | None = Field(default=None, max_length=100)


class NewRequirement(StrictInput):
    text: str = Field(min_length=1, max_length=12000)
    category: str = Field(default="Custom", max_length=100)
    auditPrompt: str = Field(default="", max_length=4000)
    source: Source
    critical: bool = False
    weight: float = Field(default=1, gt=0, le=100, allow_inf_nan=False)


class Review(StrictInput):
    requirementId: UUID
    decision: Literal["approved", "rejected"]
    note: str = Field(min_length=1, max_length=4000)


INPUT_MODELS = {
    "assess": Assess, "evidence": EvidenceInput, "action.create": NewAction,
    "action.progress": Progress, "action.submit": Implementation, "action.verify": Verify,
    "finding.close": FindingInput, "finding.withdraw": Withdrawal, "status": StatusInput,
    "complete": StrictInput, "requirement.create": NewRequirement, "requirement.review": Review,
}
