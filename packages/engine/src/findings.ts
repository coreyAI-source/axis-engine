import type { CorrectiveAction, EngineContext, Finding, Result } from "./types.ts";
import { blank, bump, checkVersion, fail, ok, v } from "./util.ts";

/** Actions that still count toward resolving the finding. */
const live = (actions: CorrectiveAction[], f: Finding) => actions.filter((a) => a.findingId === f.id && a.auditId === f.auditId && a.status !== "cancelled");

export const needsCorrectiveAction = (f: Finding, actions: CorrectiveAction[]): boolean =>
  f.status === "open" && live(actions, f).length === 0;

/** Withdraw a finding (e.g. the assessment was corrected). Kept on record with its rationale. */
export function withdrawFinding(f: Finding, rationale: string, expectedVersion: number, ctx: EngineContext): Result<Finding> {
  const conflict = checkVersion(f, expectedVersion);
  if (conflict) return fail(conflict);
  if (f.status !== "open") return fail(v("NOT_OPEN", `Finding is already ${f.status}.`));
  if (blank(rationale) || rationale.trim().length < ctx.config.minRationaleLength)
    return fail(v("RATIONALE_REQUIRED", "Explain why this finding is withdrawn.", "rationale"));
  return ok(bump(f, { status: "withdrawn", withdrawal: { rationale: rationale.trim(), by: ctx.actor, at: ctx.now } }, ctx, "finding.withdrawn", { rationale }));
}

/** A finding closes only when it has at least one action and every live action is closed (i.e. verified). */
export function closeFinding(f: Finding, actions: CorrectiveAction[], expectedVersion: number, ctx: EngineContext): Result<Finding> {
  const conflict = checkVersion(f, expectedVersion);
  if (conflict) return fail(conflict);
  if (f.status !== "open") return fail(v("NOT_OPEN", `Finding is already ${f.status}.`));
  const mine = live(actions, f);
  if (mine.length === 0) return fail(v("NO_ACTION", "A finding cannot close without a corrective action."));
  const pending = mine.filter((a) => a.status !== "closed");
  if (pending.length) return fail(v("ACTIONS_OPEN", `${pending.length} corrective action(s) are not yet verified and closed.`));
  return ok(bump(f, { status: "closed", closedAt: ctx.now }, ctx, "finding.closed"));
}
