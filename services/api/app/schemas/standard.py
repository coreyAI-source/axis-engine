from uuid import UUID
from pydantic import BaseModel


class StandardOut(BaseModel):
    id: UUID
    code: str
    title: str
    version: str

    model_config = {"from_attributes": True}


class ClauseOut(BaseModel):
    id: UUID
    standard_id: UUID
    clause_number: str
    clause_title: str
    parent_clause_number: str | None
    requirement_text: str | None
    hls_section: str
    requires_documented_information: bool
    requires_retained_evidence: bool
    evidence_guidance: str | None
    active_flag: bool

    model_config = {"from_attributes": True}
