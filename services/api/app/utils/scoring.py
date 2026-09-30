"""
Severity scoring engine.

Status weights:   Excellent=1, Good=2, OK=3, Poor=4
Importance weights: Low=1, Moderate=2, High=3, Critical=4
Severity = status_weight * importance_weight

Range: 1 (Excellent+Low) to 16 (Poor+Critical)
"""

STATUS_WEIGHTS = {
    "Excellent": 1,
    "Good": 2,
    "OK": 3,
    "Poor": 4,
}

IMPORTANCE_WEIGHTS = {
    "Low": 1,
    "Moderate": 2,
    "High": 3,
    "Critical": 4,
}


def calculate_severity_score(status: str, importance: str) -> int:
    sw = STATUS_WEIGHTS.get(status, 3)
    iw = IMPORTANCE_WEIGHTS.get(importance, 2)
    return sw * iw


def score_to_colour(score: int) -> str:
    """Map severity score to a dashboard colour bucket."""
    if score <= 2:
        return "green"
    elif score <= 6:
        return "yellow"
    elif score <= 9:
        return "orange"
    else:
        return "red"


# Action default due dates by finding type (days)
ACTION_DUE_DAYS = {
    "MajorNC": 90,
    "MinorNC": 30,
    "Observation": 60,
    "Positive": None,
    "CriticalDocumentReviewFinding": 90,
    "NonCriticalDocumentReviewFinding": 30,
}
