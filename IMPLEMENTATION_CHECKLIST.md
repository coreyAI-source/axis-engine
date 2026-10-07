# GSTC Audit App - Implementation Checklist

## ✅ COMPLETED FIXES

### 1. ✅ Updated Audit Model (services/api/app/models/audit.py)
- [x] Updated `AuditType` enum to match GSTC standards:
  - `INITIAL` - First certification audit
  - `SURVEILLANCE` - Annual audit
  - `RECERTIFICATION` - Year 3 before expiry
  - `FOLLOW_UP` - After NC remediation
  
- [x] Added GSTC Risk Assessment Fields:
  - `country_code` - ISO country code
  - `country_corruption_index` - Transparency International 0-100
  - `risk_level` - HIGH, LOW, EXTREMELY_LOW
  - `risk_assessment_date` - When assessment performed
  - `risk_assessment_notes` - Details
  - `has_negative_impacts` - Significant likelihood/consequences
  - `duration_justification` - Why deviating from standard

- [x] Added Sensitive Area Fields:
  - `is_sensitive_area` - Boolean flag
  - `sensitive_area_reason` - UNESCO/IUCN/Ramsar/National law
  - `sensitive_area_coordinates` - lat,long for verification
  - `national_legislation_reference` - Supporting documentation

- [x] Added Hotel Characteristics:
  - `guest_room_count` - For extremely low risk qualification
  - `staff_count` - Must be < 15 for extremely low risk
  - `has_event_spaces` - Meeting/wedding/function spaces
  - `has_function_spaces` - Function space presence
  - `has_meeting_spaces` - Meeting space presence
  - `is_local_ownership` - Local vs multi-site
  - `has_internet_access` - For remote audits

- [x] Added 3-Year Certification Cycle Tracking:
  - `certification_start_date` - When cycle begins
  - `certification_expiry_date` - 3 years from start
  - `last_on_site_audit_date` - For 2-year on-site requirement
  - `last_audit_date` - For 24-month surveillance window
  - `audit_cycle_number` - Which cycle (1, 2, 3...)

### 2. ✅ Added Auditor Conclusion Enum
- [x] Created `AuditorConclusion` enum with three options:
  - `CONFORM` - Requirement is met
  - `NOT_CONFORM` - Requirement NOT met
  - `NOT_ASSESSED` - Insufficient evidence

### 3. ✅ Updated AuditPrompt Model with GSTC Fields
- [x] Added auditor conclusion tracking:
  - `auditor_conclusion` - Mandatory per GSTC
  - `evidence_type` - Document, Interview, Observation, Record
  - `evidence_reference` - Which docs/records reviewed
  - `basis_for_conclusion` - Why auditor reached conclusion
  - `observation_notes` - For OBS findings
  - `follow_up_notes` - For FUP items

---

## ⏳ REMAINING IMPLEMENTATION TASKS

### Phase 1: Database Migration (2-3 hours)

**Task 1.1: Create Alembic Migration**
```bash
cd services/api
alembic revision --autogenerate -m "Add GSTC audit requirements: risk assessment, hotel characteristics, cycle tracking"
```

**Task 1.2: Review & Execute Migration**
- Review the generated migration in `alembic/versions/`
- Verify all new columns are included
- Test on development database
- Apply migration: `alembic upgrade head`

---

### Phase 2: Update Schemas (2-3 hours)

**Task 2.1: Update audit.py Schemas**
File: `services/api/app/schemas/audit.py`

Add new fields to `AuditCreate`:
```python
class AuditCreate(BaseModel):
    # ... existing fields ...
    
    # GSTC Risk Assessment
    country_code: str | None = None
    country_corruption_index: int | None = None
    risk_level: str | None = None
    risk_assessment_date: date | None = None
    risk_assessment_notes: str | None = None
    has_negative_impacts: bool | None = None
    duration_justification: str | None = None
    
    # Sensitive Area
    is_sensitive_area: bool = False
    sensitive_area_reason: str | None = None
    sensitive_area_coordinates: str | None = None
    national_legislation_reference: str | None = None
    
    # Hotel Characteristics
    guest_room_count: int | None = None
    staff_count: int | None = None
    has_event_spaces: bool = False
    has_function_spaces: bool = False
    has_meeting_spaces: bool = False
    is_local_ownership: bool | None = None
    has_internet_access: bool = False
    
    # Certification Cycle
    certification_start_date: date | None = None
    certification_expiry_date: date | None = None
    last_on_site_audit_date: date | None = None
    last_audit_date: date | None = None
    audit_cycle_number: int | None = None
```

Update `AuditUpdate` with same fields (all optional).

Add to `AuditPromptCreate`:
```python
class AuditPromptCreate(BaseModel):
    # ... existing fields ...
    auditor_conclusion: str | None = None
    evidence_type: str | None = None
    evidence_reference: str | None = None
    basis_for_conclusion: str | None = None
    observation_notes: str | None = None
    follow_up_notes: str | None = None
```

Update `AuditPromptOut` with same fields.

**Task 2.2: Update audit.py Router**
File: `services/api/app/routers/audits.py`
- Router already handles new fields via schemas (no changes needed)

---

### Phase 3: Add Validation Logic (4-5 hours)

**Task 3.1: Create Audit Validation Service**
File: `services/api/app/services/audit_validator.py` (NEW)

```python
"""GSTC audit validation rules per Accreditation Manual v3.0."""
from datetime import date
from typing import Tuple

def validate_risk_level(
    risk_level: str,
    country_corruption_index: int | None = None,
    has_negative_impacts: bool | None = None,
) -> Tuple[bool, str | None]:
    """
    Validate risk level determination per GSTC Section 8.5.12.6.
    
    HIGH RISK if:
    - Negative environmental/social/economic/cultural impacts with 
      significant likelihood and consequences, OR
    - Country corruption perception index < 50
    
    LOW RISK if:
    - Minimal likelihood and consequences of negative impacts, AND
    - Country index >= 50
    
    EXTREMELY_LOW RISK if:
    - All hotel characteristics met:
      - Fewer than 20 guest rooms
      - Less than 15 staff
      - No event/function/meeting spaces
      - Local ownership
      - Has internet access
      - Not in sensitive area
    """
    pass

def validate_audit_duration(
    risk_level: str,
    audit_method: str,  # "OnSite" or "Remote"
    duration_hours: float,
    guest_rooms: int | None = None,
    duration_justification: str | None = None,
) -> Tuple[bool, str | None]:
    """
    Validate audit duration per GSTC Section 8.5.12.8-9.
    
    Rules:
    - LOW + on-site: 1-2 days
    - HIGH + on-site: 2+ days
    - EXTREMELY_LOW + on-site: 0.5-1 day
    - LOW + remote: 0.5-1 day (surveillance only)
    - HIGH + remote: NOT ALLOWED
    
    Any deviation requires duration_justification (MANDATORY).
    """
    pass

def validate_extremely_low_risk_qualification(
    guest_room_count: int | None,
    staff_count: int | None,
    has_event_spaces: bool,
    has_function_spaces: bool,
    has_meeting_spaces: bool,
    is_local_ownership: bool | None,
    has_internet_access: bool,
    is_sensitive_area: bool,
) -> Tuple[bool, list[str]]:
    """
    Check if hotel qualifies for extremely low risk per GSTC 8.5.12.9.
    
    Returns:
    - (True, []) if qualifies
    - (False, ["reason1", "reason2"]) if disqualified
    """
    failures = []
    
    if guest_room_count is None or guest_room_count >= 20:
        failures.append("Guest rooms >= 20 (must be < 20)")
    
    if staff_count is None or staff_count >= 15:
        failures.append("Staff >= 15 (must be < 15)")
    
    if has_event_spaces or has_function_spaces or has_meeting_spaces:
        failures.append("Has event/function/meeting spaces (must have none)")
    
    if is_local_ownership is not True:
        failures.append("Not local ownership (must be locally owned)")
    
    if not has_internet_access:
        failures.append("No internet access (required for remote audits)")
    
    if is_sensitive_area:
        failures.append("Located in sensitive area (UNESCO/IUCN/Ramsar)")
    
    return (len(failures) == 0, failures)

def validate_audit_section_coverage(
    audit_method: str,  # "OnSite" or "Remote"
    sections_covered: list[str],  # ["A", "B", "C", "D"]
) -> Tuple[bool, str | None]:
    """
    Validate section coverage per GSTC 8.5.19.5.
    
    Remote audits can ONLY cover: A, D1, D3
    On-site audits MUST cover: B, C, D3 (social/cultural/environmental)
    """
    if audit_method == "Remote":
        allowed = {"A", "D1", "D3"}
        invalid = set(sections_covered) - allowed
        if invalid:
            return False, f"Remote audit covers disallowed sections: {invalid}"
    
    elif audit_method == "OnSite":
        required = {"B", "C", "D3"}
        covered = set(sections_covered)
        missing = required - covered
        if missing:
            return False, f"On-site audit missing required sections: {missing}"
    
    return True, None

def validate_surveillance_audit_dates(
    audit_type: str,
    last_on_site_audit_date: date | None,
    last_audit_date: date | None,
    today: date | None = None,
) -> Tuple[bool, list[str]]:
    """
    Validate surveillance audit timing per GSTC 8.5.19.
    
    Requirements:
    - On-site audits: at least once every 2 years (24 months)
    - Surveillance audits: at least annually
    - First surveillance: not more than 24 months from initial audit
    """
    if today is None:
        from datetime import date as date_cls
        today = date_cls.today()
    
    failures = []
    
    if audit_type == "Surveillance":
        if last_audit_date:
            months_since = (today - last_audit_date).days / 30
            if months_since > 12:
                failures.append(f"Last audit {months_since:.0f} months ago (must be <= 12)")
        
        if last_on_site_audit_date:
            months_since_onsite = (today - last_on_site_audit_date).days / 30
            if months_since_onsite > 24:
                failures.append(f"Last on-site audit {months_since_onsite:.0f} months ago (must be <= 24)")
    
    return (len(failures) == 0, failures)
```

**Task 3.2: Add Validators to Audit Router**
File: `services/api/app/routers/audits.py`

Add validation endpoint:
```python
@router.post("/{audit_id}/validate-gstc")
async def validate_gstc_requirements(
    audit_id: UUID,
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_user)
):
    """Validate audit against all GSTC requirements."""
    audit = await db.get(Audit, audit_id)
    if not audit:
        raise HTTPException(status_code=404, detail="Audit not found")
    
    # Run all validators
    errors = []
    
    # Validate risk level
    risk_valid, risk_msg = validate_risk_level(
        audit.risk_level,
        audit.country_corruption_index,
        audit.has_negative_impacts
    )
    if not risk_valid:
        errors.append(f"Risk level: {risk_msg}")
    
    # Validate duration
    duration_valid, duration_msg = validate_audit_duration(
        audit.risk_level,
        audit.audit_stage,
        audit.duration_days,
        audit.guest_room_count,
        audit.duration_justification
    )
    if not duration_valid:
        errors.append(f"Duration: {duration_msg}")
    
    # Validate extremely low risk qualification
    if audit.risk_level == "EXTREMELY_LOW":
        very_low_valid, reasons = validate_extremely_low_risk_qualification(
            audit.guest_room_count,
            audit.staff_count,
            audit.has_event_spaces,
            audit.has_function_spaces,
            audit.has_meeting_spaces,
            audit.is_local_ownership,
            audit.has_internet_access,
            audit.is_sensitive_area
        )
        if not very_low_valid:
            errors.append(f"Extremely low risk not qualified: {'; '.join(reasons)}")
    
    return {
        "audit_id": audit_id,
        "is_valid": len(errors) == 0,
        "errors": errors,
        "audit_type": audit.audit_type,
        "risk_level": audit.risk_level,
        "duration_days": audit.duration_days,
    }
```

---

### Phase 4: Documentation & Testing (3-4 hours)

**Task 4.1: Add Docstrings to Models**
- Document each new field with GSTC section reference
- Example:
  ```python
  guest_room_count: Mapped[int | None] = mapped_column(Integer)
  """Guest room count. GSTC 8.5.12.9: Must be < 20 for extremely low risk."""
  ```

**Task 4.2: Create Test Suite**
File: `services/api/tests/test_audit_gstc_validation.py` (NEW)

Test cases:
- `test_high_risk_requires_2days_onsite`
- `test_extremely_low_risk_qualification`
- `test_remote_audit_section_coverage`
- `test_surveillance_audit_dates`
- `test_country_index_determines_risk`
- `test_sensitive_area_marked_high_risk`

**Task 4.3: Update API Documentation**
- Document new audit fields in openapi schema
- Add examples of risk assessment workflows
- Document validation endpoint

---

## Implementation Order

1. **Priority 1 (Day 1)**: Database migration + tests
2. **Priority 2 (Day 2)**: Validation service + router integration
3. **Priority 3 (Day 3)**: Documentation + QA testing

---

## Validation Workflow (Post-Implementation)

Once implemented, audit creation workflow becomes:

```
1. Auditor creates audit with basic info
   ↓
2. Auditor fills risk assessment fields:
   - Country code → System looks up corruption index
   - Sensitive area → Checked against UNESCO/IUCN/Ramsar
   - Hotel characteristics → Checked for extremely low risk qualification
   ↓
3. System auto-calculates:
   - Risk level (HIGH, LOW, or EXTREMELY_LOW)
   - Recommended audit duration
   - Which audit methods allowed (on-site, remote, or both)
   ↓
4. Auditor enters planned duration
   ↓
5. System validates (endpoint: POST /audits/{id}/validate-gstc)
   - If valid: shows "✓ Compliant with GSTC"
   - If invalid: shows specific errors with remediation steps
   ↓
6. Audit proceeds with prompt generation (already working)
   - Each prompt now requires auditor_conclusion + evidence
   - Conclusions MUST be: Conform, NotConform, or NotAssessed
   ↓
7. Findings auto-created on NotConform (already working)
```

---

## GSTC Manual References

| Task | GSTC Section | Requirement |
|------|---|---|
| Risk Assessment | 8.5.12.4-6 | Auditor must determine risk level |
| Audit Duration | 8.5.12.8-9 | 1-day low-risk, 2+ days high-risk, ½-day extremely low |
| Extremely Low Risk | 8.5.12.9 | All hotel characteristics must be met |
| Sensitive Areas | 8.5.12.12-14 | Check UNESCO/IUCN/Ramsar → auto mark HIGH RISK |
| Auditor Conclusion | 8.5.12.1 | For each criterion: Conform, NotConform, or NotAssessed |
| 3-Year Cycle | 8.5.10.3-4 | Surveillance annually, on-site every 2 years |
| Section Coverage | 8.5.19.5 | Remote: A,D1,D3 only; On-site: must include B,C,D3 |

---

## Completed Phases

✅ **Phase 1: Database Migration** (COMPLETE)
- [x] Updated Audit model with all GSTC fields
- [x] Updated AuditPrompt model with auditor conclusion fields
- [x] Generated Alembic migration file
- [x] Migration file: `alembic/versions/0a08660c259d_add_gstc_audit_requirements_risk_.py`

✅ **Phase 2: Update Schemas** (COMPLETE)
- [x] Updated AuditCreate with all GSTC fields
- [x] Updated AuditUpdate with all GSTC fields
- [x] Updated AuditOut with all GSTC fields
- [x] Updated AuditPromptCreate with auditor conclusion fields
- [x] Updated AuditPromptUpdate with auditor conclusion fields
- [x] Updated AuditPromptOut with auditor conclusion fields

## Next Steps

3. ⏳ **In Progress**: Implement validation service (audit_validator.py)
4. ⏳ **Waiting**: Add validation endpoint to router
5. ⏳ **Waiting**: Create test suite
6. ⏳ **Waiting**: QA verification

**Remaining time estimate**: 6-10 hours

