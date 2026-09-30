import type {
  Assessment, AssessmentStatus, Audit, EngineContext, Evidence, Finding, FindingSeverity, Requirement, RequirementSnapshot, Result, Violation,
} from "./types.ts";
import { blank, bump, checkVersion, entry, fail, ok, v } from "./util.ts";

export const EVIDENCE_REQUIRED: AssessmentStatus[] = ["conforming", "observation", "minor", "major"];
export const FINDING_STATUSES: AssessmentStatus[] = ["minor", "major"];

export function newAssessment(audit: Audit, requirementId: string, ctx: EngineContext): Assessment {
  return {
    id: ctx.newId(),
    version: 1,
    history: [entry(ctx, "assessment.created")],
    auditId: audit.id,
    requirementId,
    status: "unassessed",
    rationale: "",
    evidenceIds: [],
  };
}

export const snapshotOf = (r: Requirement): RequirementSnapshot => ({
  requirementId: r.id,
  requirementVersion: r.version,
  text: r.text,
  source: { ...r.source },
  auditPrompt: r.auditPrompt ?? "",
  category: r.category ?? "Uncategorised",
  critical: r.critical ?? false,
  weight: r.weight ?? 1,
});

export interface AssessInput {
  status: AssessmentStatus;
  rationale: string;
  evidenceIds: string[];
}

/**
 * Record or change an assessment. Rules:
 * - the requirement must be approved and in the audit's scope
 * - every status except "unassessed" needs a rationale (including not applicable)
 * - conforming / observation / minor / major need at least one piece of evidence from this audit
 */
export function assess(
  assessment: Assessment,
  audit: Audit,
  requirement: Requirement,
  evidence: Evidence[],
  input: AssessInput,
  expectedVersion: number,
  ctx: EngineContext,
): Result<Assessment> {
  const conflict = checkVersion(assessment, expectedVersion);
  if (conflict) return fail(conflict);
  const errors: Violation[] = [];

  if (audit.status === "complete") errors.push(v("AUDIT_COMPLETE", "This audit is complete and can no longer be changed."));
  if (assessment.auditId !== audit.id) errors.push(v("AUDIT_MISMATCH", "Assessment belongs to another audit."));
  if (assessment.requirementId !== requirement.id) errors.push(v("REQUIREMENT_MISMATCH", "Requirement does not match this assessment."));
  if (!audit.requirementIds.includes(requirement.id)) errors.push(v("NOT_IN_SCOPE", "Requirement is not in this audit's scope."));
  if (requirement.reviewStatus !== "approved")
    errors.push(v("REQUIREMENT_NOT_APPROVED", "This requirement has not passed competent-person review."));

  if (input.status !== "unassessed" && (blank(input.rationale) || input.rationale.trim().length < ctx.config.minRationaleLength))
    errors.push(
      v(
        "RATIONALE_REQUIRED",
        input.status === "not_applicable"
          ? "Explain why this requirement does not apply."
          : "Give a rationale for this assessment.",
        "rationale",
      ),
    );

  const byId = new Map(evidence.map((e) => [e.id, e]));
  for (const id of input.evidenceIds) {
    const e = byId.get(id);
    if (!e) errors.push(v("EVIDENCE_NOT_FOUND", `Evidence ${id} was not found.`, "evidenceIds"));
    else if (e.auditId !== audit.id) errors.push(v("EVIDENCE_OTHER_AUDIT", `Evidence ${id} belongs to another audit.`, "evidenceIds"));
  }
  if (EVIDENCE_REQUIRED.includes(input.status) && input.evidenceIds.length === 0)
    errors.push(v("EVIDENCE_REQUIRED", "Link at least one piece of supporting evidence.", "evidenceIds"));

  if (errors.length) return fail(...errors);

  const unchanged =
    assessment.status === input.status &&
    assessment.rationale === input.rationale.trim() &&
    assessment.evidenceIds.length === input.evidenceIds.length &&
    assessment.evidenceIds.every((id, index) => id === input.evidenceIds[index]);
  if (unchanged) return ok(assessment);

  return ok(
    bump(
      assessment,
      {
        status: input.status,
        rationale: input.rationale.trim(),
        evidenceIds: [...input.evidenceIds],
        snapshot: snapshotOf(requirement),
        assessedBy: ctx.actor,
        assessedAt: ctx.now,
      },
      ctx,
      "assessment.recorded",
      { from: assessment.status, to: input.status },
    ),
  );
}

/**
 * Keep findings in step with an assessment. Findings are never deleted:
 * - minor/major with no open finding  -> raise one
 * - severity changed                  -> update severity, keep history
 * - moved away from minor/major       -> keep finding open, mark reviewRequired
 *   (a person must withdraw it with a rationale, or close it through verification)
 */
export function reconcileFindings(assessment: Assessment, existing: Finding[], ctx: EngineContext): { changed: Finding[]; created: Finding[] } {
  const mine = existing.filter((f) => f.assessmentId === assessment.id && f.auditId === assessment.auditId);
  const open = mine.filter((f) => f.status === "open");
  const changed: Finding[] = [];
  const created: Finding[] = [];

  if (FINDING_STATUSES.includes(assessment.status)) {
    const severity = assessment.status as FindingSeverity;
    if (open.length === 0) {
      if (!assessment.snapshot || !assessment.assessedBy) throw new Error("Assessment must be recorded before raising a finding.");
      created.push({
        id: ctx.newId(),
        version: 1,
        history: [entry(ctx, "finding.raised", { severity })],
        auditId: assessment.auditId,
        assessmentId: assessment.id,
        requirementId: assessment.requirementId,
        snapshot: assessment.snapshot,
        severity,
        statement: assessment.rationale,
        evidenceIds: [...assessment.evidenceIds],
        status: "open",
        raisedAt: ctx.now,
        raisedBy: ctx.actor,
      });
    } else {
      for (const f of open) {
        if (f.severity !== severity || f.reviewRequired) {
          const next = bump(f, { severity, reviewRequired: undefined }, ctx, "finding.severity_changed", { from: f.severity, to: severity });
          changed.push(next);
        }
      }
    }
  } else {
    for (const f of open) {
      if (!f.reviewRequired) {
        const reason = `Assessment changed to "${assessment.status}". Withdraw this finding with a rationale, or complete and verify its action.`;
        changed.push(bump(f, { reviewRequired: { reason, since: ctx.now } }, ctx, "finding.review_required", { assessmentStatus: assessment.status }));
      }
    }
  }
  return { changed, created };
}
