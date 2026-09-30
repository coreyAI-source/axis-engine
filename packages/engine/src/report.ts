import type {
  Assessment, Audit, CorrectiveAction, EngineConfig, EngineContext, Evidence, Finding, Requirement, Result, SourceReference, Violation,
} from "./types.ts";
import { needsCorrectiveAction } from "./findings.ts";
import { actionFlags } from "./monitoring.ts";
import { scoreHospitality, type HospitalityResult } from "./hospitality.ts";
import { bump, checkVersion, fail, ok, v } from "./util.ts";

export interface AuditBundle {
  audit: Audit;
  requirements: Requirement[];
  assessments: Assessment[];
  evidence: Evidence[];
  findings: Finding[];
  actions: CorrectiveAction[];
}

export interface Readiness {
  ready: boolean;
  blockers: Violation[];
  warnings: Violation[];
}

export function reportReadiness(b: AuditBundle): Readiness {
  const blockers: Violation[] = [];
  const warnings: Violation[] = [];
  const aByReq = new Map(b.assessments.filter((a) => a.auditId === b.audit.id).map((a) => [a.requirementId, a]));
  const rById = new Map(b.requirements.map((r) => [r.id, r]));
  const findings = b.findings.filter((f) => f.auditId === b.audit.id);
  if (b.audit.requirementIds.length === 0) blockers.push(v("SCOPE_EMPTY", "Add approved criteria before completing the audit."));

  for (const id of b.audit.requirementIds) {
    const a = aByReq.get(id);
    if (!a || a.status === "unassessed") blockers.push(v("UNASSESSED", `Requirement ${id} has not been assessed.`));
    const r = rById.get(id);
    if (!r) blockers.push(v("REQUIREMENT_MISSING", `Requirement ${id} is missing from the audit data.`));
    if (a && (a.status === "major" || a.status === "minor") &&
        !findings.some((f) => f.assessmentId === a.id && f.requirementId === id && f.status !== "withdrawn" && f.severity === a.status))
      blockers.push(v("FINDING_MISSING", `Assessment ${a.id} needs a matching ${a.status} finding. Reconcile findings before completing the audit.`));
    if (r && r.reviewStatus !== "approved" && a && a.status !== "unassessed")
      warnings.push(v("REQUIREMENT_REVISED", `Requirement ${id} was revised after assessment; the report uses the assessed version.`));
  }
  for (const f of findings) {
    if (needsCorrectiveAction(f, b.actions)) blockers.push(v("FINDING_WITHOUT_ACTION", `Finding ${f.id} (${f.severity}) has no corrective action.`));
    if (f.status === "open" && f.reviewRequired) blockers.push(v("FINDING_REVIEW_REQUIRED", `Finding ${f.id}: ${f.reviewRequired.reason}`));
  }
  const openActions = b.actions.filter((a) => a.auditId === b.audit.id && a.status !== "closed" && a.status !== "cancelled");
  if (openActions.length) warnings.push(v("ACTIONS_OPEN", `${openActions.length} corrective action(s) remain open and will be monitored after the report.`));
  if (b.actions.some((a) => a.auditId === b.audit.id && a.verifications.some((x) => x.separation === "declared_only")))
    warnings.push(v("SEPARATION_NOT_AUTHENTICATED", "Some verifications rely on typed names, not authenticated accounts."));

  return { ready: blockers.length === 0, blockers, warnings };
}

export function completeAudit(b: AuditBundle, expectedVersion: number, ctx: EngineContext): Result<Audit> {
  const conflict = checkVersion(b.audit, expectedVersion);
  if (conflict) return fail(conflict);
  if (b.audit.status !== "reporting") return fail(v("INVALID_TRANSITION", "Only an audit in reporting can be completed."));
  const r = reportReadiness(b);
  if (!r.ready) return fail(...r.blockers);
  return ok(bump(b.audit, { status: "complete", endDate: b.audit.endDate ?? ctx.now }, ctx, "audit.completed"), r.warnings);
}

// ------------------------------------------------------------------ report model

export interface ReportItem {
  requirementId: string;
  requirementText: string;
  source: SourceReference;
  auditPrompt?: string;
  status: Assessment["status"];
  rationale: string;
  evidence: { id: string; description: string; reference?: string; fileName?: string }[];
  findings: {
    id: string;
    severity: string;
    status: string;
    statement: string;
    actions: {
      id: string;
      description: string;
      owner: string;
      dueDate: string;
      deadlineNote: string;
      status: string;
      flags: string[];
      verification?: string;
    }[];
  }[];
}

export interface AuditReport {
  generatedAt: string;
  draft: boolean;
  audit: Pick<Audit, "id" | "title" | "siteName" | "module" | "disciplines" | "scopeStatement" | "startDate" | "endDate" | "status"> & { leadAuditor: string };
  counts: Record<Assessment["status"], number>;
  items: ReportItem[];
  hospitality?: HospitalityResult;
  readiness: Readiness;
  disclaimers: string[];
}

const moduleName = { iso: "General ISO audit", offshore: "Offshore environmental audit", hospitality: "Hospitality sustainability audit" } as const;

function deadlineNote(a: CorrectiveAction): string {
  const b = a.deadlineBasis;
  if (b.kind === "internal_default") return `Internal default (${b.days} days). Not a statutory deadline.`;
  if (b.kind === "custom") return `Adjusted: ${b.reason}`;
  return `External requirement: ${b.reference}`;
}

export function buildReport(b: AuditBundle, now: string, config: EngineConfig): AuditReport {
  const aByReq = new Map(b.assessments.filter((a) => a.auditId === b.audit.id).map((a) => [a.requirementId, a]));
  const inScope = b.audit.requirementIds.map((id) => {
    const r = b.requirements.find((r) => r.id === id);
    const snap = aByReq.get(id)?.snapshot;
    return r ?? {
      id, text: snap?.text ?? `(missing requirement ${id})`,
      source: snap?.source ?? { documentId: "", documentTitle: "Missing source record", revision: "unknown" },
      auditPrompt: snap?.auditPrompt, category: snap?.category, critical: snap?.critical, weight: snap?.weight,
    };
  });
  const evById = new Map(b.evidence.filter((e) => e.auditId === b.audit.id).map((e) => [e.id, e]));
  const counts = { unassessed: 0, conforming: 0, observation: 0, minor: 0, major: 0, not_applicable: 0 };

  const items: ReportItem[] = inScope.map((r) => {
    const a = aByReq.get(r.id);
    const status = a?.status ?? "unassessed";
    counts[status]++;
    const snap = a?.snapshot;
    const findings = b.findings.filter((f) => f.requirementId === r.id && f.auditId === b.audit.id);
    return {
      requirementId: r.id,
      requirementText: snap?.text ?? r.text,
      source: snap?.source ?? r.source,
      auditPrompt: snap?.auditPrompt ?? r.auditPrompt,
      status,
      rationale: a?.rationale ?? "",
      evidence: (a?.evidenceIds ?? []).map((id) => {
        const e = evById.get(id);
        return { id, description: e?.description ?? "(missing evidence record)", reference: e?.reference, fileName: e?.attachment?.fileName };
      }),
      findings: findings.map((f) => ({
        id: f.id,
        severity: f.severity,
        status: f.status === "withdrawn" ? `withdrawn: ${f.withdrawal?.rationale ?? ""}` : f.status,
        statement: f.statement,
        actions: b.actions
          .filter((x) => x.findingId === f.id && x.auditId === b.audit.id)
          .map((x) => {
            const last = x.verifications[x.verifications.length - 1];
            return {
              id: x.id,
              description: x.description,
              owner: x.owner.name,
              dueDate: x.dueDate.slice(0, 10),
              deadlineNote: deadlineNote(x),
              status: x.status,
              flags: actionFlags(x, f, now, config).map((fl) => fl.message),
              verification: last
                ? `${last.outcome} per ${last.verifier.name} on ${last.at.slice(0, 10)}${last.separation === "declared_only" ? " (independence declared, not authenticated)" : ""}`
                : undefined,
            };
          }),
      })),
    };
  });

  const disclaimers = [
    `This audit assessed ${inScope.length} selected requirement(s). It does not claim complete coverage of any standard, plan or legal obligation.`,
    "Default corrective action deadlines are internal defaults, not statutory deadlines, unless an external source is cited.",
  ];
  if (b.actions.some((a) => a.auditId === b.audit.id && a.verifications.some((x) => x.separation === "declared_only")))
    disclaimers.push("Verifier independence is based on recorded names. Authenticated separation of duties is not yet implemented.");

  let hospitality: HospitalityResult | undefined;
  if (b.audit.module === "hospitality") {
    hospitality = scoreHospitality(inScope, b.assessments.filter((a) => a.auditId === b.audit.id), b.findings.filter((f) => f.auditId === b.audit.id), config.hospitality);
    disclaimers.push(hospitality.methodNote);
  }

  return {
    generatedAt: now,
    draft: b.audit.status !== "complete",
    audit: {
      id: b.audit.id,
      title: b.audit.title,
      siteName: b.audit.siteName,
      module: b.audit.module,
      disciplines: b.audit.disciplines,
      scopeStatement: b.audit.scopeStatement,
      startDate: b.audit.startDate,
      endDate: b.audit.endDate,
      status: b.audit.status,
      leadAuditor: b.audit.leadAuditor.name,
    },
    counts,
    items,
    hospitality,
    readiness: reportReadiness(b),
    disclaimers,
  };
}

const LABEL: Record<Assessment["status"], string> = {
  unassessed: "Unassessed",
  conforming: "Conforming",
  observation: "Observation",
  minor: "Minor finding",
  major: "Major finding",
  not_applicable: "Not applicable",
};

const ref = (s: SourceReference) =>
  [`${s.documentTitle} (rev. ${s.revision})`, s.clause && `clause ${s.clause}`, s.section && `section ${s.section}`, s.page && `p. ${s.page}`]
    .filter(Boolean)
    .join(", ");

export function renderReportMarkdown(r: AuditReport): string {
  const L: string[] = [];
  L.push(`# ${r.draft ? "DRAFT: " : ""}${r.audit.title}`, "");
  L.push(`**Site:** ${r.audit.siteName}  `, `**Module:** ${moduleName[r.audit.module]}${r.audit.disciplines?.length ? ` (${r.audit.disciplines.join(", ")})` : ""}  `);
  L.push(`**Lead auditor:** ${r.audit.leadAuditor}  `, `**Dates:** ${r.audit.startDate.slice(0, 10)}${r.audit.endDate ? ` to ${r.audit.endDate.slice(0, 10)}` : ""}  `);
  L.push(`**Generated:** ${r.generatedAt}`, "");
  if (r.audit.scopeStatement) L.push(`**Scope:** ${r.audit.scopeStatement}`, "");
  L.push("## Summary", "");
  for (const [k, n] of Object.entries(r.counts)) if (n) L.push(`- ${LABEL[k as Assessment["status"]]}: ${n}`);
  L.push("");
  if (r.hospitality) {
    const h = r.hospitality;
    L.push("## Sustainability rating (provisional)", "");
    L.push(`**Rating:** ${h.rating}  `, `**Score:** ${h.score ?? "n/a"}%  `, `**Coverage:** ${Math.round(h.coverage * 100)}%`, "");
    for (const blk of h.blockers) L.push(`- ${blk}`);
    L.push("");
  }
  L.push("## Results", "");
  for (const it of r.items) {
    L.push(`### ${LABEL[it.status]}: ${it.requirementText}`, "");
    L.push(`*Source:* ${ref(it.source)}`, "");
    if (it.rationale) L.push(`*Rationale:* ${it.rationale}`, "");
    if (it.evidence.length) {
      L.push("*Evidence:*");
      for (const e of it.evidence) L.push(`- ${e.description}${e.reference ? ` (${e.reference})` : ""}${e.fileName ? ` [${e.fileName}]` : ""}`);
      L.push("");
    }
    for (const f of it.findings) {
      L.push(`**Finding (${f.severity}, ${f.status}):** ${f.statement}`, "");
      for (const a of f.actions) {
        L.push(`- Action: ${a.description}`, `  - Owner: ${a.owner}; due ${a.dueDate} (${a.deadlineNote}); status: ${a.status}`);
        if (a.flags.length) L.push(`  - Monitoring: ${a.flags.join(" ")}`);
        if (a.verification) L.push(`  - Verification: ${a.verification}`);
      }
      L.push("");
    }
  }
  L.push("## Notes and limitations", "");
  for (const d of r.disclaimers) L.push(`- ${d}`);
  for (const w of r.readiness.warnings) L.push(`- ${w.message}`);
  return L.join("\n") + "\n";
}
