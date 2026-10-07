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

    # GSTC Risk Assessment Fields (Section 8.5.12.4-6)
    country_code: str | None = None
    country_corruption_index: int | None = None
    risk_level: str | None = None
    risk_assessment_date: date | None = None
    risk_assessment_notes: str | None = None
    has_negative_impacts: bool | None = None
    duration_justification: str | None = None

    # GSTC Sensitive Area Fields (Section 8.5.12.12-14)
    is_sensitive_area: bool = False
    sensitive_area_reason: str | None = None
    sensitive_area_coordinates: str | None = None
    national_legislation_reference: str | None = None

    # Hotel-Specific Characteristics (Section 8.5.12.9)
    guest_room_count: int | None = None
    staff_count: int | None = None
    has_event_spaces: bool = False
    has_function_spaces: bool = False
    has_meeting_spaces: bool = False
    is_local_ownership: bool | None = None
    has_internet_access: bool = False

    # GSTC 3-Year Certification Cycle Tracking (Section 8.5.10.3-4)
    certification_start_date: date | None = None
    certification_expiry_date: date | None = None
    last_on_site_audit_date: date | None = None
    last_audit_date: date | None = None
    audit_cycle_number: int | None = None


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

    # GSTC Risk Assessment Fields (Section 8.5.12.4-6)
    country_code: str | None = None
    country_corruption_index: int | None = None
    risk_level: str | None = None
    risk_assessment_date: date | None = None
    risk_assessment_notes: str | None = None
    has_negative_impacts: bool | None = None
    duration_justification: str | None = None

    # GSTC Sensitive Area Fields (Section 8.5.12.12-14)
    is_sensitive_area: bool | None = None
    sensitive_area_reason: str | None = None
    sensitive_area_coordinates: str | None = None
    national_legislation_reference: str | None = None

    # Hotel-Specific Characteristics (Section 8.5.12.9)
    guest_room_count: int | None = None
    staff_count: int | None = None
    has_event_spaces: bool | None = None
    has_function_spaces: bool | None = None
    has_meeting_spaces: bool | None = None
    is_local_ownership: bool | None = None
    has_internet_access: bool | None = None

    # GSTC 3-Year Certification Cycle Tracking (Section 8.5.10.3-4)
    certification_start_date: date | None = None
    certification_expiry_date: date | None = None
    last_on_site_audit_date: date | None = None
    last_audit_date: date | None = None
    audit_cycle_number: int | None = None


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

    # GSTC Risk Assessment Fields
    country_code: str | None
    country_corruption_index: int | None
    risk_level: str | None
    risk_assessment_date: date | None
    risk_assessment_notes: str | None
    has_negative_impacts: bool | None
    duration_justification: str | None

    # GSTC Sensitive Area Fields
    is_sensitive_area: bool
    sensitive_area_reason: str | None
    sensitive_area_coordinates: str | None
    national_legislation_reference: str | None

    # Hotel-Specific Characteristics
    guest_room_count: int | None
    staff_count: int | None
    has_event_spaces: bool
    has_function_spaces: bool
    has_meeting_spaces: bool
    is_local_ownership: bool | None
    has_internet_access: bool

    # GSTC 3-Year Certification Cycle Tracking
    certification_start_date: date | None
    certification_expiry_date: date | None
    last_on_site_audit_date: date | None
    last_audit_date: date | None
    audit_cycle_number: int | None

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

    # GSTC Auditor Conclusion Fields (Section 8.5.12.1)
    auditor_conclusion: str | None = None
    evidence_type: str | None = None
    evidence_reference: str | None = None
    basis_for_conclusion: str | None = None
    observation_notes: str | None = None
    follow_up_notes: str | None = None


class AuditPromptUpdate(BaseModel):
    response_status: str | None = None
    comments: str | None = None
    responded_by: UUID | None = None

    # GSTC Auditor Conclusion Fields
    auditor_conclusion: str | None = None
    evidence_type: str | None = None
    evidence_reference: str | None = None
    basis_for_conclusion: str | None = None
    observation_notes: str | None = None
    follow_up_notes: str | None = None


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

    # GSTC Auditor Conclusion Fields
    auditor_conclusion: str | None
    evidence_type: str | None
    evidence_reference: str | None
    basis_for_conclusion: str | None
    observation_notes: str | None
    follow_up_notes: str | None

    model_config = {"from_attributes": True}
