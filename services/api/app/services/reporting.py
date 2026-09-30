"""
Report generation service.

Builds structured data dicts for all formal audit artefacts.
Conditional logic per spec section 11.
"""
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..models.audit import Audit, AuditTeamMember, AuditLocation
from ..models.evidence import Finding
from ..models.org import User
from ..config import settings


def _fmt_date(d) -> str | None:
    return d.isoformat() if d else None


async def _load_audit(audit_id: UUID, db: AsyncSession) -> Audit | None:
    result = await db.execute(
        select(Audit)
        .where(Audit.id == audit_id)
        .options(
            selectinload(Audit.team_members).selectinload(AuditTeamMember.user),
            selectinload(Audit.locations),
            selectinload(Audit.lead_auditor),
        )
    )
    return result.scalar_one_or_none()


async def _load_findings(audit_id: UUID, db: AsyncSession) -> list[Finding]:
    result = await db.execute(select(Finding).where(Finding.audit_id == audit_id))
    return result.scalars().all()


async def build_document_review_report(audit_id: UUID, db: AsyncSession) -> dict:
    audit = await _load_audit(audit_id, db)
    if not audit:
        return {"error": "Audit not found"}

    findings = await _load_findings(audit_id, db)
    critical = [f for f in findings if f.finding_type == "CriticalDocumentReviewFinding"]
    non_critical = [f for f in findings if f.finding_type == "NonCriticalDocumentReviewFinding"]

    # Conditional narrative
    if not critical:
        critical_statement = "No critical findings were identified during this document review."
    else:
        critical_statement = (
            f"{len(critical)} critical finding(s) were identified during this document review. "
            "These must be addressed prior to or during the site audit."
        )

    if not non_critical:
        non_critical_statement = "No non-critical findings were identified during this document review."
    else:
        non_critical_statement = (
            f"{len(non_critical)} non-critical finding(s) were identified during this document review."
        )

    return {
        "report_type": "DocumentReviewReport",
        "organisation_to_be_audited": audit.auditee_name,
        "audit_client": audit.audit_client,
        "audit_objective": audit.objective,
        "audit_scope": audit.scope,
        "audit_criteria": audit.criteria_text,
        "lead_auditor": _user_name(audit.lead_auditor),
        "team_members": [_user_name(tm.user) for tm in audit.team_members],
        "main_location": audit.main_location,
        "other_locations": [loc.site_name for loc in audit.locations if not loc.is_main_location],
        "start_date": _fmt_date(audit.start_date),
        "results": {
            "critical_findings_identified": len(critical) > 0,
            "critical_statement": critical_statement,
            "non_critical_findings_identified": len(non_critical) > 0,
            "non_critical_statement": non_critical_statement,
            "site_audit_should_proceed": len(critical) == 0,
        },
        "findings": {
            "critical": [_finding_summary(f) for f in critical],
            "non_critical": [_finding_summary(f) for f in non_critical],
        },
    }


async def build_audit_plan(audit_id: UUID, db: AsyncSession) -> dict:
    audit = await _load_audit(audit_id, db)
    if not audit:
        return {"error": "Audit not found"}

    return {
        "report_type": "AuditPlan",
        "audit_body": audit.audit_body,
        "auditee": audit.auditee_name,
        "client_requesting_audit": audit.audit_client,
        "objective": audit.objective,
        "scope": audit.scope,
        "criteria": audit.criteria_text,
        "start_date": _fmt_date(audit.start_date),
        "end_date": _fmt_date(audit.end_date),
        "duration_days": audit.duration_days,
        "main_location": audit.main_location,
        "other_locations": [loc.site_name for loc in audit.locations if not loc.is_main_location],
        "lead_auditor": _user_name(audit.lead_auditor),
        "team_members": [{"name": _user_name(tm.user), "role": tm.role_in_audit} for tm in audit.team_members],
        "auditee_contact": audit.auditee_contact,
        "signature_block": {"lead_auditor": _user_name(audit.lead_auditor), "date": _fmt_date(audit.start_date)},
    }


async def build_audit_timetable(audit_id: UUID, db: AsyncSession) -> dict:
    audit = await _load_audit(audit_id, db)
    if not audit:
        return {"error": "Audit not found"}

    # Generate 30-minute slots from 08:00 to 17:00
    slots = []
    hour, minute = 8, 0
    while (hour, minute) < (17, 0):
        slots.append(f"{hour:02d}:{minute:02d}")
        minute += 30
        if minute == 60:
            minute = 0
            hour += 1

    return {
        "report_type": "AuditTimetable",
        "audit_date": _fmt_date(audit.start_date),
        "lead_auditor": _user_name(audit.lead_auditor),
        "team_members": [_user_name(tm.user) for tm in audit.team_members],
        "time_slots": [
            {"time": slot, "activity": "", "location": audit.main_location}
            for slot in slots
        ],
    }


async def build_audit_report(audit_id: UUID, db: AsyncSession) -> dict:
    audit = await _load_audit(audit_id, db)
    if not audit:
        return {"error": "Audit not found"}

    findings = await _load_findings(audit_id, db)
    major_ncs = [f for f in findings if f.finding_type == "MajorNC"]
    minor_ncs = [f for f in findings if f.finding_type == "MinorNC"]
    observations = [f for f in findings if f.finding_type == "Observation"]
    positives = [f for f in findings if f.finding_type == "Positive"]

    # Conditional narrative
    if not major_ncs:
        major_nc_statement = "No major nonconformances were identified during this audit."
    else:
        major_nc_statement = (
            f"{len(major_ncs)} major nonconformance(s) were identified during this audit and "
            f"will need to be corrected and verified within {settings.major_nc_due_days} days of the date of this report."
        )

    if not minor_ncs:
        minor_nc_statement = "No minor nonconformances were identified during this audit."
    else:
        minor_nc_statement = (
            f"{len(minor_ncs)} minor nonconformance(s) were identified and must be addressed "
            f"within {settings.minor_nc_due_days} days."
        )

    return {
        "report_type": "AuditReport",
        "audit_id": str(audit_id),
        "organisation": audit.auditee_name,
        "audit_type": audit.audit_type,
        "audit_stage": audit.audit_stage,
        "start_date": _fmt_date(audit.start_date),
        "end_date": _fmt_date(audit.end_date),
        "lead_auditor": _user_name(audit.lead_auditor),
        "team_members": [_user_name(tm.user) for tm in audit.team_members],
        "summary": {
            "major_nc_count": len(major_ncs),
            "major_nc_statement": major_nc_statement,
            "minor_nc_count": len(minor_ncs),
            "minor_nc_statement": minor_nc_statement,
            "observation_count": len(observations),
            "positive_count": len(positives),
        },
        "verification_method": "Your actions will be verified by submitting appropriate evidence.",
        "confidentiality": (
            "This report is confidential and prepared for the exclusive use of the audit client. "
            "It must not be distributed or reproduced without authorisation."
        ),
        "signature_block": {"lead_auditor": _user_name(audit.lead_auditor), "date": _fmt_date(audit.end_date)},
    }


async def build_findings_register(audit_id: UUID, db: AsyncSession) -> dict:
    findings = await _load_findings(audit_id, db)

    def _group(ftype):
        return [_finding_detail(f) for f in findings if f.finding_type == ftype]

    return {
        "report_type": "FindingsRegister",
        "audit_id": str(audit_id),
        "major_nonconformances": _group("MajorNC"),
        "minor_nonconformances": _group("MinorNC"),
        "observations": _group("Observation"),
        "positive_findings": _group("Positive"),
    }


# --- Helpers ---

def _user_name(user: User | None) -> str:
    if not user:
        return ""
    return f"{user.first_name} {user.last_name}"


def _finding_summary(f: Finding) -> dict:
    return {
        "code": f.finding_code,
        "type": f.finding_type,
        "title": f.title,
    }


def _finding_detail(f: Finding) -> dict:
    return {
        "code": f.finding_code,
        "type": f.finding_type,
        "title": f.title,
        "requirement": f.requirement_text,
        "evidence_summary": f.evidence_summary,
        "description": f.description,
        "severity_score": f.severity_score,
    }
