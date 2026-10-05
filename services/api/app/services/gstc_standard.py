"""GSTC Hotel Standard v4.01 - authoritative criteria source.

This module loads and provides access to the official GSTC Hotel Standard
criteria extracted from https://www.gstc.org/wp-content/uploads/GSTC-Hotel-Standard.pdf

All audit templates should map their requirements to these criteria to ensure
alignment with the official standard.
"""
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

# Pillar definitions
PILLARS = {
    "A": {"code": "A", "name": "Demonstrate Effective Sustainable Management"},
    "B": {"code": "B", "name": "Maximize Social and Economic Benefits to the Local Community"},
    "C": {"code": "C", "name": "Maximize Benefits to Cultural Heritage"},
    "D": {"code": "D", "name": "Maximize Environmental Benefits"},
}

# Load the official GSTC criteria
_STANDARD_DATA = None


def _load_standard():
    """Load the GSTC Hotel Standard criteria from JSON."""
    global _STANDARD_DATA
    if _STANDARD_DATA is not None:
        return _STANDARD_DATA

    data_file = Path(__file__).parent.parent / "data" / "gstc-hotel-standard-v4.01.json"
    if not data_file.exists():
        logger.error(f"GSTC standard file not found: {data_file}")
        return {"version": "4.01", "criteria": {}, "total": 0}

    try:
        with open(data_file, 'r', encoding='utf-8') as f:
            _STANDARD_DATA = json.load(f)
        logger.info(f"Loaded GSTC Hotel Standard v{_STANDARD_DATA.get('version')} with {_STANDARD_DATA.get('total', 0)} criteria")
        return _STANDARD_DATA
    except Exception as e:
        logger.error(f"Failed to load GSTC standard: {e}")
        return {"version": "4.01", "criteria": {}, "total": 0}


def get_all_criteria() -> Dict[str, dict]:
    """Get all GSTC criteria keyed by code (A1, B2, etc.)."""
    standard = _load_standard()
    return standard.get("criteria", {})


def get_criterion(code: str) -> Optional[dict]:
    """Get a specific criterion by code (e.g., 'A1', 'B2')."""
    criteria = get_all_criteria()
    return criteria.get(code.upper())


def get_pillar_criteria(pillar_code: str) -> List[dict]:
    """Get all criteria for a pillar (A, B, C, or D)."""
    criteria = get_all_criteria()
    pillar_code = pillar_code.upper()
    return [c for c in criteria.values() if c.get("code", "").startswith(pillar_code)]


def list_criteria_by_pillar() -> Dict[str, List[dict]]:
    """Get criteria organized by pillar."""
    result = {}
    for pillar_code in ["A", "B", "C", "D"]:
        pillar_criteria = get_pillar_criteria(pillar_code)
        if pillar_criteria:
            result[pillar_code] = sorted(pillar_criteria, key=lambda c: c.get("code", ""))
    return result


def get_standard_metadata() -> dict:
    """Get metadata about the GSTC standard."""
    standard = _load_standard()
    return {
        "version": standard.get("version", "4.01"),
        "source": standard.get("source", ""),
        "date": standard.get("date", ""),
        "total_criteria": standard.get("total", 0),
    }


def validate_criteria_codes(codes: List[str]) -> tuple[List[str], List[str]]:
    """Validate a list of criteria codes.

    Returns (valid_codes, invalid_codes).
    """
    criteria = get_all_criteria()
    valid = []
    invalid = []

    for code in codes:
        if code.upper() in criteria:
            valid.append(code.upper())
        else:
            invalid.append(code)

    return valid, invalid


def get_standard_version() -> str:
    """Get the GSTC Hotel Standard version."""
    metadata = get_standard_metadata()
    return metadata["version"]
