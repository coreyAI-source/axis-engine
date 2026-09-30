import type {
  Actor, CorrectiveAction, DeadlineBasis, EngineContext, Evidence, Finding, FindingSeverity, Result, SeparationOfDuties, Violation,
} from "./types.ts";
import { addDays, blank, bump, checkVersion, entry, fail, ok, samePerson, v } from "./util.ts";

/** Proposed internal default. Editable; never statutory. */
export function proposeDeadline(severity: FindingSeverity, from: string, ctx: EngineContext): { dueDate: string; basis: DeadlineBasis } {
  const days = ctx.config.deadlineDays[severity];
  return { dueDate: addDays(from, days), basis: { kind: "internal_default", days } };
}

function validateBasis(basis: DeadlineBasis): Violation | null {
  if (basis.kind === "custom" && blank(basis.reason)) return v("DEADLINE_REASON_REQUIRED", "Explain why the default deadline was changed.", "deadlineBasis");
  if (basis.kind === "external" && blank(basis.reference))
    return v("DEADLINE_REFERENCE_REQUIRED", "An external deadline must cite its source document and section.", "deadlineBasis");
  return null;
}

export interface NewAction {
  description: string;
  owner: Actor;
  /** Omit both to accept the proposed internal default. */
  dueDate?: string;
  deadlineBasis?: DeadlineBasis;
}

export function createAction(finding: Finding, input: NewAction, ctx: EngineContext): Result<CorrectiveAction> {
  const errors: Violation[] = [];
  if (finding.status !== "open") errors.push(v("FINDING_NOT_OPEN", "Actions can only be raised on open findings."));
  if (blank(input.description)) errors.push(v("DESCRIPTION_REQUIRED", "Describe the corrective action.", "description"));
  if (blank(input.owner?.name)) errors.push(v("OWNER_REQUIRED", "Every action needs a named owner.", "owner"));

  const proposed = proposeDeadline(finding.severity, ctx.now, ctx);
  const dueDate = input.dueDate ?? proposed.dueDate;
  const basis = input.deadlineBasis ?? (input.dueDate && input.dueDate !== proposed.dueDate ? undefined : proposed.basis);
  if (!basis) errors.push(v("DEADLINE_REASON_REQUIRED", "A non-default due date needs a reason or an external reference.", "deadlineBasis"));
  else {
    const e = validateBasis(basis);
    if (e) errors.push(e);
    if (basis.kind === "internal_default" &&
        (Date.parse(dueDate) !== Date.parse(proposed.dueDate) || basis.days !== ctx.config.deadlineDays[finding.severity]))
      errors.push(v("DEADLINE_REASON_REQUIRED", "A non-default due date needs a reason or an external reference.", "deadlineBasis"));
  }
  if (Number.isNaN(Date.parse(dueDate))) errors.push(v("DUE_DATE_INVALID", "Due date is invalid.", "dueDate"));
  else if (Date.parse(dueDate) <= Date.parse(ctx.now)) errors.push(v("DUE_DATE_PAST", "Due date must be in the future.", "dueDate"));
  if (errors.length || !basis) return fail(...errors);

  return ok({
    id: ctx.newId(),
    version: 1,
    history: [entry(ctx, "action.created", { dueDate, basis: basis.kind })],
    auditId: finding.auditId,
    findingId: finding.id,
    description: input.description.trim(),
    owner: input.owner,
    createdAt: ctx.now,
    dueDate,
    deadlineBasis: basis,
    status: "not_started",
    updates: [],
    lastActivityAt: ctx.now,
    verifications: [],
  });
}

const closedOrCancelled = (a: CorrectiveAction) => a.status === "closed" || a.status === "cancelled";

export function changeDueDate(a: CorrectiveAction, dueDate: string, basis: DeadlineBasis, expectedVersion: number, ctx: EngineContext): Result<CorrectiveAction> {
  const conflict = checkVersion(a, expectedVersion);
  if (conflict) return fail(conflict);
  if (closedOrCancelled(a)) return fail(v("ACTION_FINISHED", `Action is ${a.status}.`));
  if (basis.kind === "internal_default") return fail(v("DEADLINE_REASON_REQUIRED", "A changed due date needs a reason or an external reference."));
  const e = validateBasis(basis);
  if (e) return fail(e);
  if (Number.isNaN(Date.parse(dueDate))) return fail(v("DUE_DATE_INVALID", "Due date is invalid."));
  return ok(bump(a, { dueDate, deadlineBasis: basis, lastActivityAt: ctx.now }, ctx, "action.due_date_changed", { from: a.dueDate, to: dueDate }));
}

export function addProgressUpdate(a: CorrectiveAction, note: string, expectedVersion: number, ctx: EngineContext): Result<CorrectiveAction> {
  const conflict = checkVersion(a, expectedVersion);
  if (conflict) return fail(conflict);
  if (closedOrCancelled(a)) return fail(v("ACTION_FINISHED", `Action is ${a.status}.`));
  if (blank(note)) return fail(v("NOTE_REQUIRED", "Progress updates need a note.", "note"));
  const starting = a.status === "not_started";
  return ok(
    bump(
      a,
      {
        updates: [...a.updates, { at: ctx.now, by: ctx.actor, note: note.trim() }],
        lastActivityAt: ctx.now,
        status: starting ? "in_progress" : a.status,
        startedAt: a.startedAt ?? ctx.now,
      },
      ctx,
      starting ? "action.started" : "action.updated",
    ),
  );
}

/** Owner (or delegate) submits implementation evidence. Required before verification. */
export function submitImplementation(
  a: CorrectiveAction,
  note: string,
  evidenceIds: string[],
  evidence: Evidence[],
  expectedVersion: number,
  ctx: EngineContext,
): Result<CorrectiveAction> {
  const conflict = checkVersion(a, expectedVersion);
  if (conflict) return fail(conflict);
  if (a.status !== "in_progress" && a.status !== "not_started")
    return fail(v("INVALID_TRANSITION", `Cannot submit implementation while action is ${a.status}.`));
  const errors: Violation[] = [];
  if (blank(note)) errors.push(v("NOTE_REQUIRED", "Describe what was implemented.", "note"));
  if (evidenceIds.length === 0) errors.push(v("IMPLEMENTATION_EVIDENCE_REQUIRED", "Attach evidence that the action was implemented.", "evidenceIds"));
  const byId = new Map(evidence.map((e) => [e.id, e]));
  for (const id of evidenceIds) {
    const e = byId.get(id);
    if (!e) errors.push(v("EVIDENCE_NOT_FOUND", `Evidence ${id} was not found.`, "evidenceIds"));
    else if (e.auditId !== a.auditId) errors.push(v("EVIDENCE_OTHER_AUDIT", `Evidence ${id} belongs to another audit.`, "evidenceIds"));
  }
  if (errors.length) return fail(...errors);
  return ok(
    bump(
      a,
      {
        status: "awaiting_verification",
        implementation: { note: note.trim(), evidenceIds: [...evidenceIds], submittedBy: ctx.actor, at: ctx.now },
        startedAt: a.startedAt ?? ctx.now,
        lastActivityAt: ctx.now,
      },
      ctx,
      "action.implementation_submitted",
    ),
  );
}

/**
 * Independent verification. The verifier (ctx.actor) must differ from the owner and the submitter.
 * "enforced" separation only when all three are authenticated with user IDs.
 * Otherwise the check compares typed names and is recorded as "declared_only".
 */
export function verifyAction(
  a: CorrectiveAction,
  outcome: "effective" | "not_effective",
  note: string,
  expectedVersion: number,
  ctx: EngineContext,
): Result<CorrectiveAction> {
  const conflict = checkVersion(a, expectedVersion);
  if (conflict) return fail(conflict);
  if (a.status !== "awaiting_verification" || !a.implementation)
    return fail(v("NOT_AWAITING_VERIFICATION", "Implementation evidence must be submitted before verification."));
  const verifier = ctx.actor;
  const errors: Violation[] = [];
  if (blank(verifier.name)) errors.push(v("VERIFIER_REQUIRED", "Verifier name is required."));
  if (samePerson(verifier, a.owner)) errors.push(v("VERIFIER_NOT_INDEPENDENT", "The action owner cannot verify their own action."));
  if (samePerson(verifier, a.implementation.submittedBy))
    errors.push(v("VERIFIER_NOT_INDEPENDENT", "The person who submitted the implementation cannot verify it."));
  if (blank(note) || note.trim().length < ctx.config.minRationaleLength)
    errors.push(v("NOTE_REQUIRED", "Record what was checked during verification.", "note"));
  if (errors.length) return fail(...errors);

  const people = [verifier, a.owner, a.implementation.submittedBy];
  const separation: SeparationOfDuties = people.every((p) => p.authenticated && !blank(p.userId)) ? "enforced" : "declared_only";
  const warnings = separation === "declared_only"
    ? [v("SEPARATION_NOT_AUTHENTICATED", "Independence is based on typed names, not authenticated accounts.")]
    : [];

  const verification = { verifier, at: ctx.now, outcome, note: note.trim(), separation };
  const effective = outcome === "effective";
  return ok(
    bump(
      a,
      {
        verifications: [...a.verifications, verification],
        status: effective ? "closed" : "in_progress",
        closedAt: effective ? ctx.now : undefined,
        lastActivityAt: ctx.now,
      },
      ctx,
      effective ? "action.verified_closed" : "action.verification_failed",
      { separation },
    ),
    warnings,
  );
}

export function cancelAction(a: CorrectiveAction, reason: string, finding: Finding, expectedVersion: number, ctx: EngineContext): Result<CorrectiveAction> {
  const conflict = checkVersion(a, expectedVersion);
  if (conflict) return fail(conflict);
  if (a.findingId !== finding.id || a.auditId !== finding.auditId)
    return fail(v("FINDING_MISMATCH", "Finding does not belong to this action and audit."));
  if (closedOrCancelled(a)) return fail(v("ACTION_FINISHED", `Action is ${a.status}.`));
  if (blank(reason)) return fail(v("REASON_REQUIRED", "Give a reason for cancelling.", "reason"));
  const warnings = finding.status === "open"
    ? [v("FINDING_STILL_OPEN", "The finding is still open and will need another corrective action.")]
    : [];
  return ok(bump(a, { status: "cancelled", cancellation: { reason: reason.trim(), by: ctx.actor, at: ctx.now } }, ctx, "action.cancelled", { reason }), warnings);
}
