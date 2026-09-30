from datetime import datetime, date
from uuid import UUID
from pydantic import BaseModel


class RiskFrequencyRuleOut(BaseModel):
    id: UUID
    risk_level: str
    frequency_code: str
    interval_months: int

    model_config = {"from_attributes": True}


class MonitoringMethodOut(BaseModel):
    id: UUID
    code: str
    name: str

    model_config = {"from_attributes": True}


class MonitoringTaskCreate(BaseModel):
    organisation_id: UUID
    site_id: UUID | None = None
    process_id: UUID | None = None
    clause_id: UUID | None = None
    title: str
    description: str | None = None
    owner_user_id: UUID | None = None
    owner_role_id: UUID | None = None
    risk_level: str = "Medium"
    importance_level: str = "Moderate"
    frequency_code: str
    interval_months: int
    method_id: UUID | None = None
    next_due_date: date | None = None


class MonitoringTaskUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    owner_user_id: UUID | None = None
    owner_role_id: UUID | None = None
    risk_level: str | None = None
    importance_level: str | None = None
    frequency_code: str | None = None
    interval_months: int | None = None
    method_id: UUID | None = None
    next_due_date: date | None = None
    status: str | None = None
    active_flag: bool | None = None


class MonitoringTaskOut(BaseModel):
    id: UUID
    organisation_id: UUID
    site_id: UUID | None
    process_id: UUID | None
    clause_id: UUID | None
    title: str
    description: str | None
    owner_user_id: UUID | None
    owner_role_id: UUID | None
    risk_level: str
    importance_level: str
    frequency_code: str
    interval_months: int
    method_id: UUID | None
    next_due_date: date | None
    last_completed_date: date | None
    status: str
    active_flag: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class MonitoringRunCreate(BaseModel):
    monitoring_task_id: UUID
    run_date: date
    due_date: date


class MonitoringRunUpdate(BaseModel):
    status: str | None = None
    summary_notes: str | None = None


class MonitoringRunOut(BaseModel):
    id: UUID
    monitoring_task_id: UUID
    run_date: date
    due_date: date
    status: str
    completed_at: datetime | None
    completed_by: UUID | None
    summary_notes: str | None

    model_config = {"from_attributes": True}
