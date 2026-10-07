"""GSTC audit validation rules per Accreditation Manual v3.0, Section 8.5."""
from datetime import date, datetime, timezone
from typing import Tuple


def validate_risk_level(
    risk_level: str | None,
    country_corruption_index: int | None = None,
    has_negative_impacts: bool | None = None,
) -> Tuple[bool, str | None]:
    """
    Validate risk level determination per GSTC Section 8.5.12.6.

    Returns:
    - (True, None) if valid
    - (False, "reason") if invalid

    HIGH RISK if:
    - Significant likelihood and consequences of negative environmental/social/
      economic/cultural impacts, OR
    - Country corruption perception index < 50

    LOW RISK if:
    - Minimal likelihood/consequences AND country index >= 50

    EXTREMELY_LOW RISK:
    - All hotel characteristics must be met (validated separately)
    """
    valid_levels = {"HIGH", "LOW", "EXTREMELY_LOW"}

    if not risk_level:
        return False, "Risk level is required"

    if risk_level not in valid_levels:
        return False, f"Invalid risk level: {risk_level}. Must be HIGH, LOW, or EXTREMELY_LOW"

    if risk_level == "HIGH":
        if has_negative_impacts is False and (country_corruption_index is None or country_corruption_index >= 50):
            return False, "HIGH risk cannot be assigned when no negative impacts and country index >= 50"

    if risk_level == "LOW":
        if has_negative_impacts is True:
            return False, "LOW risk cannot be assigned with significant negative impacts"
        if country_corruption_index is not None and country_corruption_index < 50:
            return False, "LOW risk cannot be assigned when country corruption index < 50"

    return True, None


def validate_audit_duration(
    risk_level: str | None,
    audit_method: str | None,
    duration_days: float | int | None,
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

    Any deviation from standard duration requires duration_justification (MANDATORY).

    Returns:
    - (True, None) if valid
    - (False, "reason") if invalid
    """
    if not duration_days:
        return False, "Audit duration is required"

    if not risk_level:
        return False, "Risk level must be set before validating duration"

    if not audit_method:
        return False, "Audit method (OnSite or Remote) must be specified"

    duration = float(duration_days)
    audit_method = audit_method.lower()

    rules = {
        ("LOW", "onsite"): {"min": 1.0, "max": 2.0, "standard": 1},
        ("HIGH", "onsite"): {"min": 2.0, "max": None, "standard": 2},
        ("EXTREMELY_LOW", "onsite"): {"min": 0.5, "max": 1.0, "standard": 0.5},
        ("LOW", "remote"): {"min": 0.5, "max": 1.0, "standard": 0.5},
        ("HIGH", "remote"): None,  # NOT ALLOWED
    }

    key = (risk_level, audit_method.replace(" ", ""))

    if key not in rules:
        return False, f"Invalid combination: {risk_level} risk + {audit_method} audit"

    rule = rules[key]

    if rule is None:
        return False, f"HIGH risk audits cannot be conducted remotely (GSTC 8.5.12.8)"

    standard = rule["standard"]
    min_days = rule["min"]
    max_days = rule["max"]

    if duration < min_days or (max_days and duration > max_days):
        msg = f"{risk_level} + {audit_method}: {min_days}-{max_days or 'unlimited'} days standard "
        msg += f"(got {duration})"

        if duration == standard:
            return True, None

        if not duration_justification or not duration_justification.strip():
            return False, f"{msg}. Deviation requires duration_justification"

    return True, None


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

    ALL criteria must be met:
    - Fewer than 20 guest rooms
    - Less than 15 staff
    - No event/function/meeting spaces
    - Local ownership
    - Internet access
    - Not in sensitive area

    Returns:
    - (True, []) if qualifies
    - (False, ["reason1", "reason2"]) if disqualified
    """
    failures = []

    if guest_room_count is None or guest_room_count >= 20:
        failures.append("Guest rooms >= 20 (GSTC 8.5.12.9 requires < 20)")

    if staff_count is None or staff_count >= 15:
        failures.append("Staff >= 15 (GSTC 8.5.12.9 requires < 15)")

    if has_event_spaces or has_function_spaces or has_meeting_spaces:
        failures.append("Has event/function/meeting spaces (must have none)")

    if is_local_ownership is not True:
        failures.append("Not local ownership (must be locally owned, not multi-site)")

    if not has_internet_access:
        failures.append("No internet access (required for remote audits)")

    if is_sensitive_area:
        failures.append("Located in sensitive area (UNESCO/IUCN/Ramsar/national law)")

    return (len(failures) == 0, failures)


def validate_sensitive_area_assignment(
    is_sensitive_area: bool,
    sensitive_area_reason: str | None,
    risk_level: str | None,
) -> Tuple[bool, str | None]:
    """
    Validate sensitive area assignment per GSTC 8.5.12.12-14.

    If marked as sensitive area → MUST be HIGH RISK per GSTC 8.5.12.14.
    If marked as sensitive → must have reason documented.

    Returns:
    - (True, None) if valid
    - (False, "reason") if invalid
    """
    if is_sensitive_area:
        if not sensitive_area_reason or not sensitive_area_reason.strip():
            return False, "Sensitive area marked but reason not provided"

        if risk_level != "HIGH":
            return False, "Sensitive area must be classified as HIGH RISK per GSTC 8.5.12.14"

    return True, None


def validate_audit_section_coverage(
    audit_method: str | None,
    sections_covered: list[str] | None = None,
) -> Tuple[bool, str | None]:
    """
    Validate section coverage per GSTC 8.5.19.5.

    Remote audits can ONLY cover: A, D1, D3
    On-site audits MUST cover: B, C, D3 (social/cultural/environmental)

    Returns:
    - (True, None) if valid
    - (False, "reason") if invalid
    """
    if not audit_method or not sections_covered:
        return True, None

    audit_method = audit_method.lower()
    sections_set = set(sections_covered)

    if audit_method == "remote":
        allowed = {"A", "D1", "D3"}
        invalid = sections_set - allowed
        if invalid:
            return False, f"Remote audit covers disallowed sections: {invalid} (GSTC 8.5.19.5 allows A, D1, D3 only)"

    elif audit_method == "onsite":
        required = {"B", "C", "D3"}
        missing = required - sections_set
        if missing:
            return False, f"On-site audit missing required sections: {missing} (GSTC 8.5.19.5 requires B, C, D3)"

    return True, None


def validate_surveillance_audit_dates(
    audit_type: str | None,
    last_on_site_audit_date: date | None = None,
    last_audit_date: date | None = None,
    today: date | None = None,
) -> Tuple[bool, list[str]]:
    """
    Validate surveillance audit timing per GSTC 8.5.19.

    Requirements:
    - On-site audits: at least once every 2 years (24 months)
    - Surveillance audits: at least annually (12 months)
    - First surveillance: not more than 24 months from initial audit

    Returns:
    - (True, []) if valid
    - (False, ["reason1", "reason2"]) if invalid
    """
    if today is None:
        today = datetime.now(timezone.utc).date()

    failures = []

    if audit_type == "Surveillance":
        if last_audit_date:
            days_since = (today - last_audit_date).days
            months_since = days_since / 30.0
            if months_since > 12.5:
                failures.append(f"Last audit {months_since:.1f} months ago (must be <= 12 per GSTC 8.5.19.1)")

        if last_on_site_audit_date:
            days_since_onsite = (today - last_on_site_audit_date).days
            months_since_onsite = days_since_onsite / 30.0
            if months_since_onsite > 24.5:
                failures.append(f"Last on-site audit {months_since_onsite:.1f} months ago (must be <= 24 per GSTC 8.5.19.1)")

    return (len(failures) == 0, failures)


async def validate_audit_against_gstc(
    audit_id,
    audit,
) -> dict:
    """
    Comprehensive GSTC validation for an audit.

    Runs all validators and returns complete validation report.

    Returns:
    {
        "audit_id": uuid,
        "is_valid": bool,
        "errors": [{"category": str, "message": str}],
        "warnings": [{"category": str, "message": str}],
        "summary": str,
    }
    """
    errors = []
    warnings = []

    if not audit.risk_level:
        errors.append({"category": "risk_assessment", "message": "Risk level not set"})
    else:
        risk_valid, risk_msg = validate_risk_level(
            audit.risk_level,
            audit.country_corruption_index,
            audit.has_negative_impacts
        )
        if not risk_valid:
            errors.append({"category": "risk_level", "message": risk_msg})

    if audit.duration_days:
        duration_valid, duration_msg = validate_audit_duration(
            audit.risk_level,
            audit.audit_stage,
            audit.duration_days,
            audit.guest_room_count,
            audit.duration_justification
        )
        if not duration_valid:
            errors.append({"category": "duration", "message": duration_msg})

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
            errors.append({
                "category": "extremely_low_risk",
                "message": f"Does not qualify for extremely low risk: {'; '.join(reasons)}"
            })

    sensitive_valid, sensitive_msg = validate_sensitive_area_assignment(
        audit.is_sensitive_area,
        audit.sensitive_area_reason,
        audit.risk_level
    )
    if not sensitive_valid:
        errors.append({"category": "sensitive_area", "message": sensitive_msg})

    if audit.audit_type == "Surveillance":
        surv_valid, surv_reasons = validate_surveillance_audit_dates(
            audit.audit_type,
            audit.last_on_site_audit_date,
            audit.last_audit_date
        )
        if not surv_valid:
            for reason in surv_reasons:
                errors.append({"category": "surveillance_timing", "message": reason})

    is_valid = len(errors) == 0

    return {
        "audit_id": str(audit_id),
        "is_valid": is_valid,
        "errors": errors,
        "warnings": warnings,
        "audit_type": audit.audit_type,
        "risk_level": audit.risk_level,
        "duration_days": audit.duration_days,
    }
