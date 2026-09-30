"""
Seed core reference data:
- Risk frequency rules
- Monitoring methods
- Roles
"""
from sqlalchemy.orm import Session

from app.models.monitoring import RiskFrequencyRule, MonitoringMethod
from app.models.org import Role


RISK_FREQUENCY_RULES = [
    {"risk_level": "Low",     "frequency_code": "Annual",    "interval_months": 12},
    {"risk_level": "Medium",  "frequency_code": "Biannual",  "interval_months": 6},
    {"risk_level": "High",    "frequency_code": "Quarterly", "interval_months": 3},
    {"risk_level": "Extreme", "frequency_code": "Monthly",   "interval_months": 1},
]

MONITORING_METHODS = [
    {"code": "DATA_ANALYSIS",   "name": "Data analysis"},
    {"code": "DOCUMENT_REVIEW", "name": "Document review"},
    {"code": "EXTERNAL_AUDIT",  "name": "External audit"},
    {"code": "INSPECTION",      "name": "Inspection"},
    {"code": "INTERNAL_AUDIT",  "name": "Internal audit"},
    {"code": "SELF_ASSESSMENT", "name": "Self assessment"},
    {"code": "SYSTEMS_REVIEW",  "name": "Systems review"},
    {"code": "VISUAL",          "name": "Visual inspection"},
]

ROLES = [
    {"code": "admin",               "name": "Administrator",           "description": "Full system access"},
    {"code": "compliance_manager",  "name": "Compliance Manager",      "description": "Manages compliance programme, reviews findings and actions"},
    {"code": "lead_auditor",        "name": "Lead Auditor",            "description": "Plans and leads audit activities"},
    {"code": "auditor",             "name": "Auditor",                 "description": "Conducts audit activities and records findings"},
    {"code": "process_owner",       "name": "Process Owner",           "description": "Owns and manages designated business processes"},
    {"code": "viewer",              "name": "Viewer",                  "description": "Read-only access to reports and dashboards"},
]


def seed_core(db: Session) -> None:
    for rule in RISK_FREQUENCY_RULES:
        if not db.query(RiskFrequencyRule).filter_by(risk_level=rule["risk_level"]).first():
            db.add(RiskFrequencyRule(**rule))

    for method in MONITORING_METHODS:
        if not db.query(MonitoringMethod).filter_by(code=method["code"]).first():
            db.add(MonitoringMethod(**method))

    for role in ROLES:
        if not db.query(Role).filter_by(code=role["code"]).first():
            db.add(Role(**role))

    db.flush()
