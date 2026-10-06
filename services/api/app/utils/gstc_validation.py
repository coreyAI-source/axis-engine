"""GSTC Hotel Standard validation utilities for audit enforcement."""
from typing import List, Tuple
from fastapi import HTTPException
from ..services import gstc_standard


def validate_criteria_code(code: str) -> Tuple[bool, str]:
    """
    Validate a single criteria code.

    Returns (is_valid, reason)
    - Official GSTC codes (A1-A14, B1-B9, C1-C4, D1-D13) are valid
    - Custom codes (X1, X2, etc.) are valid but need explicit approval
    - Invalid codes return False
    """
    if not isinstance(code, str) or not code.strip():
        return False, "Criteria code must be a non-empty string"

    code = code.upper().strip()

    # Check if it's an official GSTC criterion
    valid, invalid = gstc_standard.validate_criteria_codes([code])
    if code in valid:
        return True, f"Official GSTC criterion: {code}"

    # Check if it's a custom criterion (X1, X2, etc.)
    if code.startswith("X") and len(code) > 1 and code[1:].isdigit():
        return True, f"Custom criterion: {code} (requires explicit reviewer approval)"

    return False, f"'{code}' is not a valid GSTC criterion or recognized custom code"


def validate_criteria_codes(codes: List[str]) -> dict:
    """
    Validate a list of criteria codes for an audit.

    Returns {
        "valid": [...],          # Official and approved custom codes
        "invalid": [...],        # Codes that don't match any standard
        "custom": [...],         # Custom codes that need approval
        "errors": [...]          # Validation error messages
    }
    """
    if not isinstance(codes, list):
        return {
            "valid": [],
            "invalid": [],
            "custom": [],
            "errors": ["Criteria codes must be a list"]
        }

    valid = []
    invalid = []
    custom = []
    errors = []
    seen = set()

    for code in codes:
        if not isinstance(code, str):
            continue

        normalized = code.upper().strip()
        if normalized in seen:
            continue
        seen.add(normalized)

        is_valid, reason = validate_criteria_code(code)

        if not is_valid:
            invalid.append(normalized)
            errors.append(f"{normalized}: {reason}")
        elif normalized.startswith("X"):
            custom.append(normalized)
        else:
            valid.append(normalized)

    return {
        "valid": valid,
        "invalid": invalid,
        "custom": custom,
        "errors": errors
    }


def enforce_gstc_criteria(bundle: dict) -> List[str]:
    """
    Validate that an audit bundle only uses approved GSTC criteria.

    Returns a list of validation warnings/errors.

    Note: This is informational. The engine enforces its own rules.
    This utility helps catch issues early before submission to the engine.
    """
    warnings = []

    if not isinstance(bundle, dict):
        return ["Invalid audit bundle"]

    requirements = bundle.get("requirements", [])
    if not isinstance(requirements, list):
        return ["Requirements must be a list"]

    gstc_criteria = set(gstc_standard.get_all_criteria().keys())
    found_invalid = []
    found_custom = []

    for req in requirements:
        if not isinstance(req, dict):
            continue

        source = req.get("source", {})
        if not isinstance(source, dict):
            continue

        clause = source.get("clause", "").upper()
        if not clause:
            continue

        # Skip if it's an official GSTC criterion
        if clause in gstc_criteria:
            continue

        # Check if it's a custom criterion
        if clause.startswith("X"):
            review_status = req.get("reviewStatus", "draft")
            if review_status != "approved":
                found_custom.append({
                    "code": clause,
                    "status": review_status,
                    "message": f"Custom criterion {clause} has status '{review_status}', not 'approved'"
                })
        else:
            found_invalid.append(clause)

    if found_invalid:
        warnings.append(f"Found non-GSTC criteria codes: {', '.join(set(found_invalid))}")

    if found_custom:
        for item in found_custom:
            warnings.append(f"Custom criterion {item['code']}: {item['message']}")

    return warnings


def get_gstc_standard_info() -> dict:
    """Get comprehensive GSTC standard information for API responses."""
    all_criteria = gstc_standard.get_all_criteria()
    by_pillar = gstc_standard.list_criteria_by_pillar()
    metadata = gstc_standard.get_standard_metadata()

    # Count criteria by pillar
    pillar_counts = {
        pillar: len(criteria)
        for pillar, criteria in by_pillar.items()
    }

    return {
        "metadata": metadata,
        "criteria_by_pillar": pillar_counts,
        "total_criteria": len(all_criteria),
        "valid_pillar_codes": ["A", "B", "C", "D"],
        "custom_criteria_pattern": "X<number> (e.g., X1, X2)",
        "sample_criteria": {
            "A1": all_criteria.get("A1", {}),
            "B1": all_criteria.get("B1", {}),
            "C1": all_criteria.get("C1", {}),
            "D1": all_criteria.get("D1", {}),
        }
    }
