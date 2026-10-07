# GSTC Audit App - Gap Analysis & Fixes

**Status**: ⚠️ **CRITICAL GAPS IDENTIFIED** - Your app is falling short of GSTC v3.0 requirements

---

## 1. ❌ MISSING: Risk Assessment Data

### Required by GSTC (Section 8.5.12.4-6)
- Auditors MUST perform risk assessment to determine audit duration
- Risk level determines whether audit is 1-day or ½-day (for extremely low risk)

### Current State
- ❌ No field for country corruption perception index (Transparency International)
- ❌ No field for sensitive area identification
- ❌ No field for risk level (HIGH, LOW, EXTREMELY_LOW)
- ❌ No field for risk assessment date
- ❌ No field for justification when duration deviates from standard

### Fix Required
Add to Audit model:

```python
# New fields in Audit model
country_code: Mapped[str | None]  # For Transparency International lookup
country_corruption_index: Mapped[int | None]  # 0-100 score
is_sensitive_area: Mapped[bool] = False  # Check UNESCO/IUCN/Ramsar lists
sensitive_area_reason: Mapped[str | None]  # Why marked as sensitive
risk_level: Mapped[str | None]  # HIGH, LOW, EXTREMELY_LOW
risk_assessment_date: Mapped[date | None]
risk_assessment_notes: Mapped[str | None]
has_negative_impacts: Mapped[bool | None]  # Significant likelihood/consequences
duration_justification: Mapped[str | None]  # Explain if deviating from standard
```

---

## 2. ❌ MISSING: Hotel-Specific Characteristics

### Required by GSTC (Section 8.5.12.9 - Extremely Low Risk Exception)
To qualify as "extremely low risk," hotel must have:
- ✓ Fewer than 20 guest rooms
- ✓ Less than 15 staff members
- ✓ No meeting/wedding/function spaces or activities
- ✓ Local ownership (not multi-site)
- ✓ Access to internet/broadband for remote audits
- ✓ Not in sensitive area

### Current State
- ❌ No fields for guest room count
- ❌ No fields for staff count
- ❌ No fields for event space/function space presence
- ❌ No fields for ownership structure (local vs multi-site)
- ❌ No fields for internet connectivity

### Fix Required
Add to Audit model or separate HotelDetails model:

```python
# Hotel-specific fields
guest_room_count: Mapped[int | None]
staff_count: Mapped[int | None]
has_event_spaces: Mapped[bool] = False
has_function_spaces: Mapped[bool] = False
has_meeting_spaces: Mapped[bool] = False
is_local_ownership: Mapped[bool | None]  # Not multi-site
has_internet_access: Mapped[bool] = False  # For remote audits
```

---

## 3. ❌ MISSING: Audit Duration Validation Logic

### Required by GSTC (Section 8.5.12.8-9)
- Low Risk: Normally 1-day audit
- High Risk: More than 1-day audit
- Extremely Low Risk: Can be as short as ½-day (4 hours)
- ANY deviation must be JUSTIFIED

### Current State
- ❌ duration_days field exists but NO VALIDATION
- ❌ No business logic to enforce rules
- ❌ Auditor can enter any number without constraints

### Fix Required
Add validation logic in Audit service:

```python
def validate_audit_duration(
    audit_type: str,
    risk_level: str,
    duration_days: int,
    duration_justification: str | None = None
) -> dict:
    """Validate audit duration against GSTC rules."""
    
    rules = {
        ("LOW", "on-site"): {"min": 1, "max": 2},
        ("HIGH", "on-site"): {"min": 2, "max": None},  # No max
        ("EXTREMELY_LOW", "on-site"): {"min": 0.5, "max": 1},
        ("LOW", "remote"): {"min": 0.5, "max": 1},  # Surveillance only
        ("HIGH", "remote"): None,  # NOT ALLOWED
    }
    
    # If deviation required, duration_justification is MANDATORY
    # Return validation result with error message if invalid
```

---

## 4. ❌ MISSING: Audit Type & 3-Year Certification Cycle

### Required by GSTC (Section 8.5.10.3-4)
- **Initial Audit**: First certification audit
- **Surveillance Audit**: Annually, on-site at least once every 2 years
- **Recertification Audit**: Must begin in year 3 before expiration
- **3-year cycle**: Begins with certification or recertification decision

### Current State
- ✓ audit_type exists but values are: Internal, External, Surveillance, Certification, FollowUp
- ❌ No distinction between Initial vs Recertification audits
- ❌ No tracking of "last audit date" (for 24-month surveillance window)
- ❌ No tracking of "certification expiry date" (for 3-year cycle)
- ❌ No tracking of audit cycle number

### Fix Required
Update Audit model:

```python
# Update audit_type enum
class AuditType(str, enum.Enum):
    INITIAL = "Initial"  # First certification
    SURVEILLANCE = "Surveillance"  # Annual audit
    RECERTIFICATION = "Recertification"  # Year 3 before expiry
    FOLLOW_UP = "FollowUp"  # After NC remediation

# Add cycle tracking fields
certification_start_date: Mapped[date | None]  # When cycle started
certification_expiry_date: Mapped[date | None]  # 3 years from start
last_on_site_audit_date: Mapped[date | None]  # For 2-year on-site requirement
last_audit_date: Mapped[date | None]  # For 24-month surveillance window
audit_cycle_number: Mapped[int | None]  # Which cycle (1, 2, 3...)
```

---

## 5. ❌ MISSING: Audit Section Coverage Tracking

### Required by GSTC (Section 8.5.19.5)
- **Remote Audits**: Can ONLY cover Sections A, D1, D3
- **On-site Audits**: MUST cover social, cultural, environmental Sections B, C, D3

### Current State
- ❌ No tracking of which GSTC sections were audited
- ❌ No validation that remote audits don't cover B or C sections
- ❌ No documentation of coverage gaps

### Fix Required
Create AuditSectionCoverage model:

```python
class AuditSectionCoverage(Base):
    __tablename__ = "audit_section_coverage"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    audit_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("audits.id"))
    section: Mapped[str]  # A, B, C, D
    audit_method: Mapped[str]  # "OnSite" or "Remote"
    is_covered: Mapped[bool] = False
    coverage_notes: Mapped[str | None]
```

---

## 6. ❌ MISSING: Sensitive Area Assessment

### Required by GSTC (Section 8.5.12.12-14)
Must check against:
- UNESCO World Heritage List
- IUCN Protected Areas Categories System
- Ramsar List (Wetlands of International Importance)
- National legislation where client operates

### Current State
- ❌ No field to identify location against these lists
- ❌ No validation logic
- ❌ If in sensitive area → automatically HIGH RISK

### Fix Required
Add to Audit model:

```python
# Sensitive area fields
sensitive_area_lists: Mapped[str | None]  # CSV: "UNESCO,IUCN,Ramsar"
sensitive_area_coordinates: Mapped[str | None]  # lat,long for verification
national_legislation_reference: Mapped[str | None]
```

---

## 7. ❌ ISSUE: Audit Prompt Response Mapping

### Current Response Statuses
- C = Conform
- NC = Not Conform  
- OBS = Observation
- FUP = Follow-up
- TBA = To Be Assessed
- NA = Not Applicable

### Problem
- Response status "C" doesn't clearly map to auditor's "conclusion"
- GSTC requires auditor to record for EACH criterion: **Conform / Not Conform / Not Assessed**
- Current system is too flexible and doesn't enforce required fields

### Fix Required
Clarify mapping in AuditPrompt:

```python
# Clarify what each response status means per GSTC:
# C (Conform) = requirement is met
# NC (Not Conform) = requirement is NOT met → creates Finding
# NA (Not Applicable) = criterion not applicable to this org
# TBA (To Be Assessed) = need more evidence, incomplete review
# OBS (Observation) = enhancement opportunity, not a NC
# FUP (Follow-up) = needs follow-up audit

# Add auditor_conclusion field (separate from response_status):
auditor_conclusion: Mapped[str]  # Required: "Conform", "NotConform", "NotAssessed"
evidence_assessment: Mapped[str | None]  # How auditor reached conclusion
```

---

## 8. ❌ ISSUE: Missing Auditor Conclusion per Criterion

### Required by GSTC (Section 8.5.12.1)
For EACH criterion, auditor must record:
- ✓ Conclusion: **Conform / Not Conform / Not Assessed**
- ✓ Evidence obtained (type and source)
- ✓ Basis for conclusion

### Current State
- ❌ AuditPrompt has response_status but not explicit auditor_conclusion
- ❌ No structured evidence linking to conclusion
- ❌ No clear audit trail showing why auditor reached conclusion

### Fix Required
Update AuditPrompt schema:

```python
class AuditPromptResponse(BaseModel):
    """Structured auditor response per GSTC requirements."""
    prompt_id: UUID
    
    # MANDATORY
    auditor_conclusion: str  # "Conform" | "NotConform" | "NotAssessed"
    evidence_type: str  # "Document" | "Interview" | "Observation" | "Record"
    evidence_reference: str  # Which docs/records reviewed
    basis_for_conclusion: str  # Why auditor reached this conclusion
    
    # OPTIONAL
    observation_notes: str | None  # If OBS finding
    follow_up_notes: str | None  # If FUP needed
```

---

## Summary of Required Changes

| Requirement | Status | Priority | Effort |
|---|---|---|---|
| Risk Assessment Fields | ❌ Missing | CRITICAL | Medium |
| Hotel Characteristics | ❌ Missing | CRITICAL | Low |
| Duration Validation Logic | ❌ Missing | CRITICAL | Medium |
| Audit Type Enum Fix | ⚠️ Partial | HIGH | Low |
| 3-Year Cycle Tracking | ❌ Missing | HIGH | Medium |
| Section Coverage Tracking | ❌ Missing | HIGH | Medium |
| Sensitive Area Fields | ❌ Missing | HIGH | Low |
| Auditor Conclusion Structure | ⚠️ Unclear | HIGH | Medium |
| Response Mapping Clarity | ⚠️ Ambiguous | MEDIUM | Low |

---

## Implementation Priority

**Phase 1 (CRITICAL):** Risk Assessment & Hotel Data
- Add all missing fields to Audit model
- Add validation logic for duration
- Update schemas

**Phase 2 (HIGH):** Cycle & Coverage Tracking
- Add cycle tracking fields
- Create AuditSectionCoverage model
- Add sensitive area fields

**Phase 3 (HIGH):** Auditor Conclusion Clarity
- Clarify response mapping
- Add explicit auditor_conclusion field
- Structure evidence linkage

---

## Files Needing Changes

1. `services/api/app/models/audit.py` - Add new fields & validators
2. `services/api/app/schemas/audit.py` - Update create/update schemas
3. `services/api/app/services/audit.py` - Add validation logic
4. Create migration file for new database columns
5. `services/api/app/routers/audits.py` - Add audit duration validation endpoint

