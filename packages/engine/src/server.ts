/**
 * Server-only, one-request JSON stdin/stdout adapter for the Python API.
 * The API supplies authenticated identities and a tenant-authorised stored bundle;
 * clients must never supply those values directly. No persistence occurs here.
 */
import { randomUUID } from "node:crypto";
import { resolve } from "node:path";
import { fileURLToPath } from "node:url";
import {
  DEFAULT_CONFIG, createAudit, addCriteria, setAuditStatus, newAssessment, assess,
  reconcileFindings, createEvidence, createAction, addProgressUpdate, submitImplementation,
  verifyAction, closeFinding, withdrawFinding, completeAudit, buildReport, renderReportMarkdown,
  createRequirement, reviewRequirement, saveIndicatorInputs, attachSuggestion,
} from "./index.ts";
import type { IndicatorInputPatch } from "./assessment.ts";
import type { AuditBundle, AuditReport } from "./report.ts";
import type { Actor, AssessmentStatus, AttachmentRef, EngineConfig, EngineContext, EvidenceKind, Result, SourceReference, Violation } from "./types.ts";
import { createGstcHotelRequirements, GSTC_HOTEL_TEMPLATE, HOTEL_TEMPLATES } from "./gstc-hotel.ts";
import type { HotelTemplate } from "./gstc-hotel.ts";

export interface HospitalityBundle extends AuditBundle {
  config: EngineConfig;
  template: HotelTemplate;
}

export interface ReportPayload { report: AuditReport; markdown: string }
export type ServerValue = HospitalityBundle | ReportPayload;

const OPERATIONS = ["create", "assess", "assessment.indicators", "assessment.suggestion", "evidence", "action.create", "action.progress", "action.submit", "action.verify", "finding.close", "finding.withdraw", "status", "complete", "report", "requirement.create", "requirement.review"] as const;
const STATUSES: AssessmentStatus[] = ["unassessed", "conforming", "observation", "minor", "major", "not_applicable"];
const EVIDENCE_KINDS: EvidenceKind[] = ["document", "photo", "record", "interview", "observation"];
const COLLECTED_VIA: readonly ("on_site" | "before_visit" | "after_visit" | "interview" | "calculation")[] = ["on_site", "before_visit", "after_visit", "interview", "calculation"];
const TEMPLATE_NOTICE: Violation = { code: "STANDARD_TEMPLATE", message: `Added ${GSTC_HOTEL_TEMPLATE.title} ${GSTC_HOTEL_TEMPLATE.version} criteria. Mark criteria that do not apply to this property as Not applicable with a reason.` };

class InputError extends Error {
  violation: Violation;
  constructor(code: string, message: string, field?: string) {
    super(message);
    this.violation = { code, message, ...(field ? { field } : {}) };
  }
}

function object(value: unknown, field: string): Record<string, unknown> {
  if (!value || typeof value !== "object" || Array.isArray(value)) throw new InputError("INVALID_INPUT", `${field} must be an object.`, field);
  return value as Record<string, unknown>;
}

function string(value: unknown, field: string, optional = false): string {
  if (optional && (value === undefined || value === null)) return "";
  if (typeof value !== "string" || value.length > 20000) throw new InputError("INVALID_INPUT", `${field} must be text of at most 20,000 characters.`, field);
  return value;
}

function choice<T extends string>(value: unknown, values: readonly T[], field: string): T {
  if (typeof value !== "string" || !values.includes(value as T)) throw new InputError("INVALID_INPUT", `Choose a valid ${field}.`, field);
  return value as T;
}

function ids(value: unknown): string[] {
  if (!Array.isArray(value) || value.length > 1000 || value.some((id) => typeof id !== "string" || !id || id.length > 200))
    throw new InputError("INVALID_INPUT", "evidenceIds must be a list of evidence identifiers.", "evidenceIds");
  return [...new Set(value)] as string[];
}

function actor(value: unknown, field: string): Actor {
  const raw = object(value, field);
  const name = string(raw.name, `${field}.name`).trim();
  const userId = string(raw.userId, `${field}.userId`).trim();
  if (!name || !userId || raw.authenticated !== true) throw new InputError("AUTHENTICATED_ACTOR_REQUIRED", "An authenticated account identity is required.", field);
  return { name, userId, authenticated: true };
}

function take<T>(result: Result<T>, warnings: Violation[]): T {
  if (!result.ok) throw new RuleError(result.violations);
  warnings.push(...result.warnings);
  return result.value;
}

class RuleError extends Error {
  violations: Violation[];
  constructor(violations: Violation[]) { super("Engine rule violation."); this.violations = violations; }
}

function find<T extends { id: string }>(items: T[], id: unknown, field: string): T {
  const key = string(id, field);
  const record = items.find((item) => item.id === key);
  if (!record) throw new InputError("NOT_FOUND", `The selected ${field.replace(/Id$/, "")} was not found in this audit.`, field);
  return record;
}

function config(value: unknown): EngineConfig {
  const cfg = object(value, "bundle.config");
  const deadlines = object(cfg.deadlineDays, "bundle.config.deadlineDays");
  const hospitality = object(cfg.hospitality, "bundle.config.hospitality");
  const points = object(hospitality.points, "bundle.config.hospitality.points");
  const positive = [deadlines.major, deadlines.minor, cfg.inactivityDays, cfg.majorUnstartedHours, cfg.unstartedWindowFraction, cfg.minRationaleLength];
  if (positive.some((n) => typeof n !== "number" || !Number.isFinite(n) || n <= 0) ||
      typeof hospitality.minCoverage !== "number" || hospitality.minCoverage <= 0 || hospitality.minCoverage > 1 ||
      [points.conforming, points.observation, points.minor, points.major].some((n) => typeof n !== "number" || !Number.isFinite(n) || n < 0 || n > 1) ||
      !Array.isArray(hospitality.bands) || !hospitality.bands.length ||
      hospitality.bands.some((band) => !band || typeof band !== "object" || typeof band.minScore !== "number" || !Number.isFinite(band.minScore) || band.minScore < 0 || band.minScore > 100 || typeof band.label !== "string" || typeof band.favourable !== "boolean") ||
      !Array.isArray(hospitality.criticalGapStatuses) || hospitality.criticalGapStatuses.some((status) => !STATUSES.includes(status)))
    throw new InputError("INVALID_BUNDLE", "The saved audit configuration is invalid.", "bundle.config");
  return structuredClone(cfg) as unknown as EngineConfig;
}

function bundle(value: unknown): HospitalityBundle {
  const raw = object(value, "bundle");
  const savedAudit = object(raw.audit, "bundle.audit");
  if (savedAudit.module !== "hospitality" || typeof savedAudit.id !== "string" || !Array.isArray(savedAudit.requirementIds) ||
      !["planned", "in_progress", "reporting", "complete"].includes(String(savedAudit.status)))
    throw new InputError("INVALID_BUNDLE", "A saved hospitality audit is required.", "bundle");
  for (const field of ["requirements", "assessments", "evidence", "findings", "actions"] as const) {
    const items = raw[field];
    if (!Array.isArray(items) || items.some((item) => !item || typeof item !== "object" || typeof item.id !== "string"))
      throw new InputError("INVALID_BUNDLE", `Saved ${field} are invalid.`, `bundle.${field}`);
    if (field !== "requirements" && items.some((item) => item.auditId !== savedAudit.id))
      throw new InputError("INVALID_BUNDLE", "Saved records belong to a different audit.", `bundle.${field}`);
  }
  const result = structuredClone(raw) as unknown as HospitalityBundle;
  result.config = config(raw.config);
  const templateId = raw.template ? object(raw.template, "bundle.template").id : undefined;
  if (!HOTEL_TEMPLATES.some((template) => template.id === templateId))
    throw new InputError("INVALID_BUNDLE", "Saved audit template metadata is missing.", "bundle.template");
  return result;
}

function source(value: unknown): SourceReference {
  const raw = object(value, "source");
  return {
    documentId: string(raw.documentId, "source.documentId"), documentTitle: string(raw.documentTitle, "source.documentTitle"), revision: string(raw.revision, "source.revision"),
    section: string(raw.section, "source.section", true) || undefined, clause: string(raw.clause, "source.clause", true) || undefined, page: string(raw.page, "source.page", true) || undefined,
  };
}

function attachment(value: unknown): AttachmentRef | undefined {
  if (value === undefined || value === null) return undefined;
  const raw = object(value, "attachment");
  if (typeof raw.sizeBytes !== "number" || !Number.isSafeInteger(raw.sizeBytes)) throw new InputError("INVALID_INPUT", "Attachment size must be an integer.", "attachment.sizeBytes");
  return { key: string(raw.key, "attachment.key"), fileName: string(raw.fileName, "attachment.fileName"), contentType: string(raw.contentType, "attachment.contentType"), sizeBytes: raw.sizeBytes, sha256: string(raw.sha256, "attachment.sha256", true) || undefined };
}

export function handleRequest(raw: unknown): Result<ServerValue> {
  try {
    const request = object(raw, "request");
    const operation = choice(request.operation, OPERATIONS, "operation");
    const authenticatedActor = actor(request.actor, "actor");
    const now = string(request.now, "now");
    if (!/^\d{4}-\d{2}-\d{2}T/.test(now) || !Number.isFinite(Date.parse(now))) throw new InputError("INVALID_INPUT", "now must be an ISO timestamp.", "now");
    const input = object(request.input ?? {}, "input");
    const warnings: Violation[] = [];
    const saved = operation === "create" ? undefined : bundle(request.bundle);
    const ctx: EngineContext = { actor: authenticatedActor, now, newId: randomUUID, config: saved?.config ?? structuredClone(DEFAULT_CONFIG) };
    const use = <T>(result: Result<T>) => take(result, warnings);

    if (operation === "create") {
      const requirements = createGstcHotelRequirements(ctx);
      let audit = use(createAudit({ module: "hospitality", title: string(input.title, "title"), siteName: string(input.siteName, "siteName"), scopeStatement: string(input.scopeStatement, "scopeStatement", true) || `Hotel sustainability assessment against the ${GSTC_HOTEL_TEMPLATE.title} ${GSTC_HOTEL_TEMPLATE.version}.`, startDate: now }, ctx));
      audit = use(addCriteria(audit, requirements, audit.version, ctx));
      audit = use(setAuditStatus(audit, "in_progress", audit.version, ctx));
      return { ok: true, value: { audit, requirements, assessments: requirements.map((requirement) => newAssessment(audit, requirement.id, ctx)), evidence: [], findings: [], actions: [], config: ctx.config, template: structuredClone(GSTC_HOTEL_TEMPLATE) }, warnings: [TEMPLATE_NOTICE, ...warnings] };
    }

    const b = saved!;
    if (b.audit.status === "complete" && ["assess", "assessment.indicators", "assessment.suggestion", "requirement.create", "requirement.review"].includes(operation))
      throw new InputError("AUDIT_COMPLETE", "This audit is complete; its assessments and criteria are locked.");

    switch (operation) {
      case "assess": {
        const requirement = find(b.requirements, input.requirementId, "requirementId");
        const previous = b.assessments.find((item) => item.requirementId === requirement.id);
        if (!previous) throw new InputError("NOT_IN_SCOPE", "Approve this requirement before assessing it.", "requirementId");
        const next = use(assess(previous, b.audit, requirement, b.evidence, { status: choice(input.status, STATUSES, "status"), rationale: string(input.rationale, "rationale"), evidenceIds: ids(input.evidenceIds) }, previous.version, ctx));
        b.assessments = b.assessments.map((item) => item.id === next.id ? next : item);
        // A retry after verified closure must not reopen a finding. Reconcile only new assessments.
        if (next.version !== previous.version) {
          const changes = reconcileFindings(next, b.findings, ctx);
          b.findings = b.findings.map((item) => changes.changed.find((changed) => changed.id === item.id) ?? item).concat(changes.created);
        }
        break;
      }
      case "assessment.indicators": {
        const requirement = find(b.requirements, input.requirementId, "requirementId");
        const previous = b.assessments.find((item) => item.requirementId === requirement.id);
        if (!previous) throw new InputError("NOT_IN_SCOPE", "Approve this requirement before recording indicator notes.", "requirementId");
        if (!Array.isArray(input.indicatorInputs)) throw new InputError("INVALID_INPUT", "indicatorInputs must be a list.", "indicatorInputs");
        const patches: IndicatorInputPatch[] = input.indicatorInputs.map((raw, position) => {
          const item = object(raw, `indicatorInputs[${position}]`);
          if (!Number.isInteger(item.index)) throw new InputError("INVALID_INPUT", `indicatorInputs[${position}].index must be an integer.`, `indicatorInputs[${position}].index`);
          return { index: item.index as number, notes: string(item.notes, `indicatorInputs[${position}].notes`, true), evidenceIds: ids(item.evidenceIds ?? []) };
        });
        const next = use(saveIndicatorInputs(previous, b.audit, requirement, b.evidence, patches, previous.version, ctx));
        b.assessments = b.assessments.map((item) => item.id === next.id ? next : item);
        break;
      }
      case "assessment.suggestion": {
        const requirement = find(b.requirements, input.requirementId, "requirementId");
        const previous = b.assessments.find((item) => item.requirementId === requirement.id);
        if (!previous) throw new InputError("NOT_IN_SCOPE", "Approve this requirement before attaching a suggestion.", "requirementId");
        const next = use(attachSuggestion(previous, b.audit, {
          status: choice(input.status, STATUSES, "status"),
          rationale: string(input.rationale, "rationale"),
          model: string(input.model, "model"),
        }, previous.version, ctx));
        b.assessments = b.assessments.map((item) => item.id === next.id ? next : item);
        break;
      }
      case "evidence": {
        const via = input.collectedVia === undefined || input.collectedVia === null || input.collectedVia === ""
          ? undefined
          : choice(input.collectedVia, COLLECTED_VIA, "collectedVia");
        b.evidence.push(use(createEvidence({ auditId: b.audit.id, kind: choice(input.kind, EVIDENCE_KINDS, "kind"), description: string(input.description, "description"), reference: string(input.reference, "reference", true) || undefined, attachment: attachment(input.attachment), collectedVia: via }, ctx)));
        break;
      }
      case "action.create": {
        const finding = find(b.findings, input.findingId, "findingId");
        b.actions.push(use(createAction(finding, { description: string(input.description, "description"), owner: actor(input.owner, "owner") }, ctx)));
        break;
      }
      case "action.progress": case "action.submit": case "action.verify": {
        const previous = find(b.actions, input.actionId, "actionId");
        const note = string(input.note, "note");
        const next = operation === "action.progress" ? use(addProgressUpdate(previous, note, previous.version, ctx))
          : operation === "action.submit" ? use(submitImplementation(previous, note, ids(input.evidenceIds), b.evidence, previous.version, ctx))
          : use(verifyAction(previous, choice(input.outcome, ["effective", "not_effective"], "outcome"), note, previous.version, ctx));
        b.actions = b.actions.map((item) => item.id === next.id ? next : item);
        break;
      }
      case "finding.close": case "finding.withdraw": {
        const previous = find(b.findings, input.findingId, "findingId");
        const next = operation === "finding.close" ? use(closeFinding(previous, b.actions, previous.version, ctx))
          : use(withdrawFinding(previous, string(input.rationale, "rationale"), previous.version, ctx));
        b.findings = b.findings.map((item) => item.id === next.id ? next : item);
        break;
      }
      case "status": {
        const status = choice(input.status, ["in_progress", "reporting"], "status");
        if (b.audit.status !== status) b.audit = use(setAuditStatus(b.audit, status, b.audit.version, ctx));
        break;
      }
      case "complete": b.audit = use(completeAudit(b, b.audit.version, ctx)); break;
      case "requirement.create": {
        if (input.critical !== undefined && typeof input.critical !== "boolean") throw new InputError("INVALID_INPUT", "critical must be true or false.", "critical");
        if (input.weight !== undefined && typeof input.weight !== "number") throw new InputError("INVALID_INPUT", "weight must be a number.", "weight");
        b.requirements.push(use(createRequirement({ module: "hospitality", text: string(input.text, "text"), category: string(input.category, "category", true), auditPrompt: string(input.auditPrompt, "auditPrompt", true), source: source(input.source), critical: input.critical as boolean | undefined, weight: input.weight as number | undefined }, ctx)));
        break;
      }
      case "requirement.review": {
        const previous = find(b.requirements, input.requirementId, "requirementId");
        const next = use(reviewRequirement(previous, choice(input.decision, ["approved", "rejected"], "decision"), string(input.note, "note", true), previous.version, ctx));
        b.requirements = b.requirements.map((item) => item.id === next.id ? next : item);
        if (next.reviewStatus === "approved") {
          b.audit = use(addCriteria(b.audit, [next], b.audit.version, ctx));
          b.assessments.push(newAssessment(b.audit, next.id, ctx));
        }
        break;
      }
      case "report": {
        const report = buildReport(b, now, b.config);
        report.disclaimers.unshift(b.template.disclaimer);
        return { ok: true, value: { report, markdown: renderReportMarkdown(report) }, warnings };
      }
    }
    return { ok: true, value: b, warnings };
  } catch (error) {
    if (error instanceof RuleError) return { ok: false, violations: error.violations };
    if (error instanceof InputError) return { ok: false, violations: [error.violation] };
    return { ok: false, violations: [{ code: "INVALID_REQUEST", message: "The audit request could not be processed. Check the saved data and request fields." }] };
  }
}

async function main(): Promise<void> {
  let result: Result<ServerValue>;
  try {
    const chunks: Buffer[] = [];
    let bytes = 0;
    for await (const chunk of process.stdin) {
      const buffer = Buffer.isBuffer(chunk) ? chunk : Buffer.from(chunk);
      bytes += buffer.length;
      if (bytes > 20 * 1024 * 1024) throw new Error("Request too large.");
      chunks.push(buffer);
    }
    result = handleRequest(JSON.parse(Buffer.concat(chunks).toString("utf8")));
  } catch {
    result = { ok: false, violations: [{ code: "INVALID_JSON", message: "Supply one valid JSON request of no more than 20 MiB." }] };
  }
  process.stdout.write(JSON.stringify(result));
}

if (process.argv[1] && resolve(process.argv[1]) === resolve(fileURLToPath(import.meta.url))) await main();
