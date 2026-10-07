"""
Audit lifecycle service layer.

Handles:
- Prompt response rules (NC → finding + action, OBS, FUP, TBA)
- Auto-creation of findings and actions from prompt responses
- Prompt generation from process-clause mappings
"""
from datetime import datetime, timedelta, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.audit import Audit, AuditProcess, AuditPrompt
from ..models.mapping import ProcessClauseMap
from ..models.standard import Clause
from ..models.evidence import Finding, Action
from ..config import settings
from ..utils.scoring import ACTION_DUE_DAYS


# --- Prompt generation ---

PROMPT_TEMPLATES = {
    "DocumentCheck": [
        "Verify that documented information for {clause_title} is established, maintained, and available where needed.",
        "Confirm that the document is current, reviewed, and approved in accordance with documented information control requirements.",
        "Check that records required by {clause_title} are retained and protected.",
    ],
    "Interview": [
        "Ask the process owner to explain how {clause_title} requirements are understood and implemented in this process.",
        "Confirm that personnel responsible for {clause_title} are aware of their obligations and have received appropriate training.",
    ],
    "Observation": [
        "Observe the process in operation and verify that controls required by {clause_title} are implemented as described.",
        "Verify that the physical environment and conditions are consistent with the management system requirements for this process.",
    ],
    "RecordReview": [
        "Review records retained as evidence of conformance with {clause_title} requirements.",
        "Confirm that records demonstrate the process is being implemented effectively and results are achieving planned outcomes.",
    ],
}

EFFECTIVENESS_PROMPTS = [
    "Verify that the process achieves its intended outcomes.",
    "Confirm that the organisation has evaluated the effectiveness of actions taken.",
    "Check that results are being monitored, measured, and reviewed for continual improvement.",
]


async def generate_audit_prompts(audit_id: UUID, db: AsyncSession) -> int:
    """
    Generate AuditPrompt records from AuditProcess + ProcessClauseMap entries.
    Returns count of prompts created.
    """
    audit = await db.get(Audit, audit_id)
    if not audit:
        return 0

    # Get processes in scope for this audit
    ap_result = await db.execute(
        select(AuditProcess).where(AuditProcess.audit_id == audit_id)
    )
    audit_processes = ap_result.scalars().all()

    seq = 1
    created = 0

    for ap in audit_processes:
        # Get clause mappings for this process
        map_result = await db.execute(
            select(ProcessClauseMap).where(
                ProcessClauseMap.process_id == ap.process_id,
                ProcessClauseMap.applicability != "NotApplicable",
            )
        )
        maps = map_result.scalars().all()

        for pcm in maps:
            clause = await db.get(Clause, pcm.clause_id)
            if not clause:
                continue

            # Generate prompts for each type
            for prompt_type, templates in PROMPT_TEMPLATES.items():
                # Only generate DocumentCheck if clause requires documented info
                if prompt_type == "DocumentCheck" and not clause.requires_documented_information:
                    continue

                template = templates[seq % len(templates)]
                prompt_text = template.format(clause_title=clause.clause_title)

                evidence_required = clause.requires_retained_evidence or clause.requires_documented_information

                prompt = AuditPrompt(
                    audit_id=audit_id,
                    process_id=ap.process_id,
                    clause_id=pcm.clause_id,
                    prompt_text=prompt_text,
                    prompt_type=prompt_type,
                    evidence_required=evidence_required,
                    sequence_no=seq,
                    response_status="Pending",
                )
                db.add(prompt)
                seq += 1
                created += 1

    await db.flush()
    return created


# --- Response rules ---

async def handle_prompt_response(
    prompt: AuditPrompt,
    current_user,
    db: AsyncSession,
) -> None:
    """
    Apply business rules when a prompt response is recorded (GSTC Section 8.5.12.1).

    Auditor conclusion mapping (mandatory):
    - Conform (C): Requirement is met → no finding
    - NotConform (NC): Requirement NOT met → mandatory finding + action
    - NotAssessed (NA): Insufficient evidence → flag for follow-up

    Response status workflow:
    - NC → mandatory finding + action (with evidence_reference required)
    - OBS → optional action (observation, not a non-conformity)
    - FUP → follow-up audit flag
    - TBA → incomplete review (no action)
    - C → no action
    - NA → no action
    """
    status = prompt.response_status
    conclusion = prompt.auditor_conclusion

    if not prompt.responded_at and status != "Pending":
        from datetime import datetime, timezone
        prompt.responded_at = datetime.now(timezone.utc)

    if status == "NC":
        if conclusion != "NotConform":
            prompt.auditor_conclusion = "NotConform"
        if not prompt.evidence_reference:
            prompt.evidence_reference = prompt.comments or "Finding raised from non-conformance response"
        await _create_finding_and_action(prompt, current_user, db, mandatory=True)
    elif status == "OBS":
        if conclusion != "Conform" and conclusion != "NotAssessed":
            prompt.auditor_conclusion = "Conform"
        await _create_finding_and_action(prompt, current_user, db, mandatory=False)
    elif status == "C":
        if conclusion != "Conform":
            prompt.auditor_conclusion = "Conform"
    elif status == "NA":
        if conclusion != "NotAssessed":
            prompt.auditor_conclusion = "NotAssessed"
    elif status == "FUP":
        if not prompt.follow_up_notes:
            prompt.follow_up_notes = prompt.comments or "Follow-up audit required"
    elif status == "TBA":
        if conclusion != "NotAssessed":
            prompt.auditor_conclusion = "NotAssessed"


async def _create_finding_and_action(
    prompt: AuditPrompt,
    current_user,
    db: AsyncSession,
    mandatory: bool,
) -> None:
    # Determine finding type
    if mandatory:
        finding_type = "MinorNC"  # Default — auditor can upgrade to MajorNC
    else:
        finding_type = "Observation"

    # Auto-generate finding code
    from sqlalchemy import func
    count_result = await db.scalar(
        select(func.count()).select_from(Finding).where(Finding.audit_id == prompt.audit_id)
    )
    finding_code = f"NC{(count_result or 0) + 1:02d}" if mandatory else f"OBS{(count_result or 0) + 1:02d}"

    finding = Finding(
        audit_id=prompt.audit_id,
        process_id=prompt.process_id,
        clause_id=prompt.clause_id,
        finding_code=finding_code,
        finding_type=finding_type,
        title=f"Finding against {prompt.prompt_text[:80]}",
        description=prompt.comments or "Finding raised from audit prompt response.",
        created_by=current_user.id,
    )
    db.add(finding)
    await db.flush()
    await db.refresh(finding)

    if mandatory:
        await create_action_for_finding(finding, db)


async def create_action_for_finding(finding: Finding, db: AsyncSession) -> Action:
    """Create a mandatory corrective action for a finding."""
    days = ACTION_DUE_DAYS.get(finding.finding_type, 30)
    due = datetime.now(timezone.utc) + timedelta(days=days) if days else None

    action = Action(
        finding_id=finding.id,
        title=f"Corrective action for {finding.finding_code}: {finding.title[:80]}",
        description=f"Address nonconformance identified in finding {finding.finding_code}.",
        due_date=due,
        status="Open",
        lag_status="OnTrack",
        verification_required=True,
    )
    db.add(action)
    await db.flush()
    await db.refresh(action)
    return action
