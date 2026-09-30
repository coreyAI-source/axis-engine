import type { EngineContext, IsoDiscipline, ModuleKind, Requirement, RequirementOrigin, Result, SourceReference, Violation } from "./types.ts";
import { blank, bump, checkVersion, entry, fail, ok, samePerson, v } from "./util.ts";

export interface NewRequirement {
  module: ModuleKind;
  text: string;
  title?: string;
  indicators?: string[];
  guidance?: string[];
  source: SourceReference;
  origin?: RequirementOrigin;
  disciplines?: IsoDiscipline[];
  category?: string;
  auditPrompt?: string;
  controls?: string[];
  performanceStandard?: string;
  measurementCriteria?: string;
  critical?: boolean;
  weight?: number;
}

function validateSource(s: SourceReference): Violation[] {
  const out: Violation[] = [];
  if (blank(s.documentId)) out.push(v("SOURCE_DOCUMENT_REQUIRED", "A requirement must cite its source document.", "source.documentId"));
  if (blank(s.documentTitle)) out.push(v("SOURCE_TITLE_REQUIRED", "Source document title is required.", "source.documentTitle"));
  if (blank(s.revision)) out.push(v("SOURCE_REVISION_REQUIRED", "Source document revision is required.", "source.revision"));
  return out;
}

/** Every requirement starts as a draft, whatever its origin, including future AI extraction. */
export function createRequirement(input: NewRequirement, ctx: EngineContext): Result<Requirement> {
  const errors = validateSource(input.source);
  if (blank(input.text)) errors.push(v("TEXT_REQUIRED", "Requirement text is required.", "text"));
  if (input.module === "iso" && (!input.disciplines || input.disciplines.length === 0))
    errors.push(v("DISCIPLINE_REQUIRED", "ISO requirements must name at least one discipline.", "disciplines"));
  if (input.weight !== undefined && (!Number.isFinite(input.weight) || !(input.weight > 0)))
    errors.push(v("WEIGHT_INVALID", "Weight must be a finite positive number.", "weight"));
  if (errors.length) return fail(...errors);

  const warnings: Violation[] = [];
  const s = input.source;
  if (blank(s.section) && blank(s.clause) && blank(s.page))
    warnings.push(v("SOURCE_LOCATION_MISSING", "No section, clause or page given. Add one if the source has it."));

  const req: Requirement = {
    ...input,
    id: ctx.newId(),
    version: 1,
    history: [entry(ctx, "requirement.created", { origin: input.origin ?? "manual" })],
    origin: input.origin ?? "manual",
    createdBy: ctx.actor,
    reviewStatus: "draft",
  };
  return ok(req, warnings);
}

/** Competent-person review. Rejection needs a note. Self-review is allowed but warned. */
export function reviewRequirement(
  req: Requirement,
  decision: "approved" | "rejected",
  note: string,
  expectedVersion: number,
  ctx: EngineContext,
): Result<Requirement> {
  const conflict = checkVersion(req, expectedVersion);
  if (conflict) return fail(conflict);
  if (req.reviewStatus !== "draft") return fail(v("NOT_DRAFT", `Only drafts can be reviewed (this one is ${req.reviewStatus}).`));
  if (decision === "rejected" && blank(note)) return fail(v("NOTE_REQUIRED", "Explain why the requirement is rejected.", "note"));

  const warnings: Violation[] = [];
  if (samePerson(req.createdBy, ctx.actor))
    warnings.push(v("SELF_REVIEW", "The reviewer is also the author. Independent review is preferable."));
  if (!ctx.actor.authenticated)
    warnings.push(v("REVIEWER_UNAUTHENTICATED", "Reviewer identity is not authenticated. Reviewer roles are a later milestone."));

  return ok(
    bump(req, { reviewStatus: decision, reviewedBy: ctx.actor, reviewedAt: ctx.now, reviewNote: note }, ctx, `requirement.${decision}`, { note }),
    warnings,
  );
}

/** Editing text or source sends an approved requirement back to draft. Old assessments keep their snapshot. */
export function reviseRequirement(
  req: Requirement,
  changes: Partial<Pick<Requirement, "text" | "source" | "auditPrompt" | "controls" | "category" | "critical" | "weight" | "performanceStandard" | "measurementCriteria" | "disciplines">>,
  reason: string,
  expectedVersion: number,
  ctx: EngineContext,
): Result<Requirement> {
  const conflict = checkVersion(req, expectedVersion);
  if (conflict) return fail(conflict);
  if (blank(reason)) return fail(v("REASON_REQUIRED", "Give a reason for the revision.", "reason"));
  if (changes.source) {
    const errs = validateSource(changes.source);
    if (errs.length) return fail(...errs);
  }
  if (changes.text !== undefined && blank(changes.text)) return fail(v("TEXT_REQUIRED", "Requirement text is required.", "text"));
  if (changes.weight !== undefined && (!Number.isFinite(changes.weight) || !(changes.weight > 0)))
    return fail(v("WEIGHT_INVALID", "Weight must be a finite positive number.", "weight"));
  if (req.module === "iso" && changes.disciplines !== undefined && changes.disciplines.length === 0)
    return fail(v("DISCIPLINE_REQUIRED", "ISO requirements must name at least one discipline.", "disciplines"));

  const next = bump(req, { ...changes }, ctx, "requirement.revised", { reason, fields: Object.keys(changes) });
  const reset = req.reviewStatus !== "draft";
  return ok(
    reset ? { ...next, reviewStatus: "draft", reviewedBy: undefined, reviewedAt: undefined, reviewNote: undefined } : next,
    reset ? [v("REVIEW_RESET", "Revised requirement returned to draft and needs review before further use.")] : [],
  );
}

export const isUsable = (req: Requirement): boolean => req.reviewStatus === "approved";
