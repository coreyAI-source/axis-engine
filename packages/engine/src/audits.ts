import type { Actor, Audit, AuditStatus, EngineContext, IsoDiscipline, ModuleKind, Requirement, Result, Violation } from "./types.ts";
import { blank, bump, checkVersion, entry, fail, ok, v } from "./util.ts";

export interface NewAudit {
  module: ModuleKind;
  title: string;
  siteName: string;
  startDate: string;
  leadAuditor?: Actor;
  disciplines?: IsoDiscipline[];
  scopeStatement?: string;
}

export function createAudit(input: NewAudit, ctx: EngineContext): Result<Audit> {
  const errors: Violation[] = [];
  if (blank(input.title)) errors.push(v("TITLE_REQUIRED", "Audit title is required.", "title"));
  if (blank(input.siteName)) errors.push(v("SITE_REQUIRED", "Site name is required.", "siteName"));
  if (Number.isNaN(Date.parse(input.startDate))) errors.push(v("START_DATE_INVALID", "Start date is invalid.", "startDate"));
  if (input.module === "iso" && (!input.disciplines || input.disciplines.length === 0))
    errors.push(v("DISCIPLINE_REQUIRED", "Choose at least one ISO discipline. Choose several for an integrated audit.", "disciplines"));
  if (input.module !== "iso" && input.disciplines?.length)
    errors.push(v("DISCIPLINE_NOT_APPLICABLE", "Disciplines apply to ISO audits only.", "disciplines"));
  if (errors.length) return fail(...errors);

  return ok({
    ...input,
    id: ctx.newId(),
    version: 1,
    history: [entry(ctx, "audit.created")],
    status: "planned",
    leadAuditor: input.leadAuditor ?? ctx.actor,
    requirementIds: [],
  });
}

/** Only approved requirements of the same module (and, for ISO, a matching discipline) may enter scope. */
export function addCriteria(audit: Audit, reqs: Requirement[], expectedVersion: number, ctx: EngineContext): Result<Audit> {
  const conflict = checkVersion(audit, expectedVersion);
  if (conflict) return fail(conflict);
  if (audit.status === "complete") return fail(v("AUDIT_COMPLETE", "This audit is complete and its scope can no longer be changed."));
  const errors: Violation[] = [];
  for (const r of reqs) {
    if (r.module !== audit.module) errors.push(v("MODULE_MISMATCH", `Requirement ${r.id} belongs to the ${r.module} module.`));
    if (r.reviewStatus !== "approved")
      errors.push(v("REQUIREMENT_NOT_APPROVED", `Requirement ${r.id} has not passed competent-person review.`));
    if (audit.module === "iso" && !r.disciplines?.some((d) => audit.disciplines?.includes(d)))
      errors.push(v("DISCIPLINE_MISMATCH", `Requirement ${r.id} does not match this audit's disciplines.`));
  }
  if (errors.length) return fail(...errors);
  const added = [...new Set(reqs.map((r) => r.id))].filter((id) => !audit.requirementIds.includes(id));
  return ok(bump(audit, { requirementIds: [...audit.requirementIds, ...added] }, ctx, "audit.criteria_added", { added }));
}

const FLOW: Record<AuditStatus, AuditStatus[]> = {
  planned: ["in_progress"],
  in_progress: ["reporting"],
  reporting: ["in_progress", "complete"],
  complete: [],
};

export function setAuditStatus(audit: Audit, to: AuditStatus, expectedVersion: number, ctx: EngineContext): Result<Audit> {
  const conflict = checkVersion(audit, expectedVersion);
  if (conflict) return fail(conflict);
  if (!FLOW[audit.status].includes(to)) return fail(v("INVALID_TRANSITION", `Audit cannot move from ${audit.status} to ${to}.`));
  if (to === "complete") return fail(v("USE_COMPLETE_AUDIT", "Use completeAudit(), which checks report readiness first."));
  return ok(bump(audit, { status: to }, ctx, "audit.status_changed", { from: audit.status, to }));
}
