from datetime import datetime
from uuid import UUID
from pydantic import BaseModel


class ProcessClauseMapCreate(BaseModel):
    process_id: UUID
    clause_id: UUID
    applicability: str = "Full"
    rationale: str | None = None
    risk_modifier: str | None = None


class ProcessClauseMapUpdate(BaseModel):
    applicability: str | None = None
    rationale: str | None = None
    risk_modifier: str | None = None


class ProcessClauseMapOut(BaseModel):
    id: UUID
    process_id: UUID
    clause_id: UUID
    applicability: str
    rationale: str | None
    risk_modifier: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class ControlMappingCreate(BaseModel):
    process_id: UUID
    source_standard_code: str
    source_clause_number: str
    target_standard_code: str
    target_clause_number: str
    mapping_type: str
    notes: str | None = None


class ControlMappingOut(BaseModel):
    id: UUID
    process_id: UUID
    source_standard_code: str
    source_clause_number: str
    target_standard_code: str
    target_clause_number: str
    mapping_type: str
    notes: str | None

    model_config = {"from_attributes": True}
