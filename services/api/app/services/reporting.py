"""
Report generation service.

Builds structured data dicts for all formal audit artefacts.
Conditional logic per spec section 11.

KEY: High-quality GSTC reports require ACTUAL audit data from AuditPrompts.
This service extracts real responses, evidence, and conclusions to feed the AI.
"""
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..models.audit import Audit, AuditTeamMember, AuditLocation, AuditPrompt
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


async def _load_audit_prompts(audit_id: UUID, db: AsyncSession) -> list[AuditPrompt]:
    """Load all audit prompts with responses for this audit."""
    result = await db.execute(
        select(AuditPrompt).where(AuditPrompt.audit_id == audit_id)
    )
    return result.scalars().all()


async def _extract_audit_facts(audit: Audit, prompts: list[AuditPrompt]) -> dict:
    """Extract ACTUAL audit data from prompts to feed AI report generation.

    This ensures the report uses REAL findings, not made-up data.
    Each finding includes actual evidence references and auditor conclusions.
    """
    conform_count = sum(1 for p in prompts if p.response_status == "C")
    nc_count = sum(1 for p in prompts if p.response_status == "NC")
    obs_count = sum(1 for p in prompts if p.response_status == "OBS")

    # Extract real evidence references
    evidence_refs = []
    for p in prompts:
        if p.evidence_reference:
            evidence_refs.extend(p.evidence_reference.split(","))
    evidence_ids = list(set(ref.strip() for ref in evidence_refs if ref.strip()))

    # Extract real conclusions
    conclusions_data = []
    for p in prompts:
        if p.auditor_conclusion and p.response_status in ("C", "NC", "OBS"):
            conclusions_data.append({
                "status": p.response_status,
                "conclusion": p.auditor_conclusion,
                "evidence": p.evidence_reference or "Not specified",
                "basis": p.basis_for_conclusion or "Evidence reviewed",
            })

    return {
        "audit_property": audit.auditee_name,
        "audit_location": audit.main_location,
        "audit_type": audit.audit_type,
        "audit_date": _fmt_date(audit.start_date),
        "duration_days": audit.duration_days,
        "risk_level": audit.risk_level,
        "summary": {
            "total_prompts": len(prompts),
            "conform_count": conform_count,
            "notconform_count": nc_count,
            "observation_count": obs_count,
            "conform_percentage": round(100 * conform_count / len(prompts)) if prompts else 0,
        },
        "evidence_ids": evidence_ids,
        "conclusions": conclusions_data,
        "audit_scope": audit.scope,
        "audit_objective": audit.objective,
        "standard": "GSTC Hotel Standard v4.01",
        "pillars": ["A: Sustainable Management", "B: Socioeconomic Benefits", "C: Cultural Heritage", "D: Environmental Benefits"],
    }


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
    """Build comprehensive audit report with ACTUAL audit data from prompts.

    CRITICAL: This function now extracts real audit responses, evidence references,
    and conclusions from AuditPrompts. This ensures any AI report generation receives
    FACTS, not made-up data.
    """
    audit = await _load_audit(audit_id, db)
    if not audit:
        return {"error": "Audit not found"}

    # Load ACTUAL audit data from prompts
    prompts = await _load_audit_prompts(audit_id, db)
    actual_facts = await _extract_audit_facts(audit, prompts)

    findings = await _load_findings(audit_id, db)
    major_ncs = [f for f in findings if f.finding_type == "MajorNC"]
    minor_ncs = [f for f in findings if f.finding_type == "MinorNC"]
    observations = [f for f in findings if f.finding_type == "Observation"]
    positives = [f for f in findings if f.finding_type == "Positive"]

    # Conditional narrative based on ACTUAL findings
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
        # ✅ CRITICAL FIX: Include ACTUAL audit facts for AI report generation
        # This data feeds the AI so it generates reports based on REAL findings, not fiction
        "actual_audit_facts": actual_facts,
        "prompt_responses": {
            "total": len(prompts),
            "conform": actual_facts["summary"]["conform_count"],
            "notconform": actual_facts["summary"]["notconform_count"],
            "observations": actual_facts["summary"]["observation_count"],
            "evidence_references": actual_facts["evidence_ids"],
        },
        # ✅ GSTC v5.0 COMPLIANCE: Mandatory disclaimer for readiness reports
        "disclaimer": (
            "This is a self-assessment and readiness review. It is not a GSTC certification, "
            "verification or endorsement, and it does not predict the outcome of an audit by a "
            "GSTC-accredited certification body."
        ),
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
