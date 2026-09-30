/**
 * End-to-end demonstration: one complete audit cycle per module, using clearly
 * labelled FICTIONAL data. Writes the exported reports to demo-output/.
 * No real standard clauses, legal requirements or EP commitments are used.
 */
import { test } from "node:test";
import assert from "node:assert/strict";
import { mkdirSync, writeFileSync } from "node:fs";
import {
  createRequirement, reviewRequirement, createAudit, addCriteria, setAuditStatus, createEvidence, newAssessment,
  assess, reconcileFindings, createAction, addProgressUpdate, submitImplementation, verifyAction, closeFinding,
  completeAudit, buildReport, renderReportMarkdown, DEFAULT_CONFIG,
  type AssessmentStatus, type Finding, type ModuleKind, type IsoDiscipline, type Assessment, type Evidence, type CorrectiveAction,
} from "../src/index.ts";
import { ctx, must, TARREN, SAM, ALEX, T0 } from "./helpers.ts";
import { addDays } from "../src/util.ts";

interface Crit {
  text: string;
  ref: { section?: string; page?: string };
  status: AssessmentStatus;
  rationale: string;
  category?: string;
  disciplines?: IsoDiscipline[];
  critical?: boolean;
}

function runCycle(module: ModuleKind, title: string, site: string, doc: { id: string; title: string; revision: string }, crits: Crit[], disciplines?: IsoDiscipline[]) {
  const day = (d: number) => addDays(T0, d);
  const c = ctx(TARREN, T0);

  // 1. Source -> requirement (draft) -> competent-person review
  const reqs = crits.map((k) => {
    const r = must(createRequirement({
      module, text: k.text, category: k.category, disciplines: k.disciplines, critical: k.critical,
      auditPrompt: `DEMO prompt: ask for records demonstrating "${k.text}"`,
      source: { documentId: doc.id, documentTitle: doc.title, revision: doc.revision, ...k.ref },
    }, c));
    return must(reviewRequirement(r, "approved", "DEMO review against source", r.version, ctx(ALEX, T0)));
  });

  // 2. Audit creation and scope
  let audit = must(createAudit({ module, title, siteName: site, startDate: T0, disciplines, scopeStatement: "DEMO scope: fictional data for workflow verification." }, c));
  audit = must(addCriteria(audit, reqs, audit.version, c));
  audit = must(setAuditStatus(audit, "in_progress", audit.version, c));

  // 3. Evidence, assessment, findings
  const evidence: Evidence[] = [];
  const assessments: Assessment[] = [];
  let findings: Finding[] = [];
  reqs.forEach((r, i) => {
    const k = crits[i]!;
    const ev = must(createEvidence({
      auditId: audit.id, kind: "record", description: `DEMO evidence for criterion ${i + 1}`, reference: `DEMO-REC-${i + 1}`,
      attachment: { key: `demo/${audit.id}/${i + 1}.pdf`, fileName: `demo-evidence-${i + 1}.pdf`, contentType: "application/pdf", sizeBytes: 1024 },
    }, c));
    evidence.push(ev);
    const needsEv = k.status !== "not_applicable";
    const a = must(assess(newAssessment(audit, r.id, c), audit, r, evidence, { status: k.status, rationale: k.rationale, evidenceIds: needsEv ? [ev.id] : [] }, 1, c));
    assessments.push(a);
    findings.push(...reconcileFindings(a, findings, c).created);
  });

  // 4. Corrective actions -> progress -> implementation -> independent verification -> closure
  const actions: CorrectiveAction[] = [];
  findings = findings.map((f) => {
    let a = must(createAction(f, { description: `DEMO corrective action for ${f.severity} finding`, owner: SAM }, c));
    a = must(addProgressUpdate(a, "DEMO: work started", a.version, ctx(SAM, day(1))));
    const sc = ctx(SAM, day(5));
    const proof = must(createEvidence({ auditId: audit.id, kind: "document", description: "DEMO implementation record", reference: "DEMO-IMPL" }, sc));
    evidence.push(proof);
    a = must(submitImplementation(a, "DEMO: implemented", [proof.id], evidence, a.version, sc));
    a = must(verifyAction(a, "effective", "DEMO: verified implementation record on site", a.version, ctx(ALEX, day(6))));
    actions.push(a);
    return must(closeFinding(f, actions, f.version, ctx(ALEX, day(6))));
  });

  // 5. Reporting and completion
  audit = must(setAuditStatus(audit, "reporting", audit.version, ctx(TARREN, day(7))));
  const bundle = { audit, requirements: reqs, assessments, evidence, findings, actions };
  audit = must(completeAudit(bundle, audit.version, ctx(TARREN, day(7))));
  const report = buildReport({ ...bundle, audit }, day(7), DEFAULT_CONFIG);
  const md = renderReportMarkdown(report);
  mkdirSync("demo-output", { recursive: true });
  writeFileSync(`demo-output/${module}-report.md`, md);
  return { audit, report, md, findings, actions };
}

test("DEMO ISO integrated audit: full cycle", () => {
  const r = runCycle("iso", "DEMO Integrated ISO Audit (fictional)", "DEMO Manufacturing Co. (fictional)",
    { id: "demo-ims", title: "DEMO Integrated Management System Manual (fictional)", revision: "3" },
    [
      { text: "DEMO: Environmental aspects register is maintained", ref: { section: "DEMO-2.1", page: "4" }, status: "conforming", rationale: "Register current and reviewed", disciplines: ["environment"] },
      { text: "DEMO: Nonconforming product is segregated", ref: { section: "DEMO-5.3" }, status: "minor", rationale: "One batch not tagged in holding area", disciplines: ["quality"] },
      { text: "DEMO: Workers are consulted on hazard controls", ref: { section: "DEMO-7.2" }, status: "observation", rationale: "Consultation occurs but is not minuted", disciplines: ["ohs"] },
    ], ["environment", "quality", "ohs"]);
  assert.equal(r.audit.status, "complete");
  assert.equal(r.findings.length, 1);
  assert.ok(r.findings.every((f) => f.status === "closed"));
  assert.match(r.md, /does not claim complete coverage/);
});

test("DEMO offshore EP audit: full cycle", () => {
  const r = runCycle("offshore", "DEMO Offshore EP Compliance Audit (fictional)", "DEMO Platform Alpha (fictional)",
    { id: "demo-ep", title: "DEMO Environment Plan (fictional)", revision: "B" },
    [
      { text: "DEMO: Chemical register maintained for all chemicals used", ref: { section: "DEMO-6.4", page: "58" }, status: "major", rationale: "Three chemicals in use absent from register", category: "chemical management" },
      { text: "DEMO: Produced water discharge monitored per measurement criteria", ref: { section: "DEMO-7.1" }, status: "conforming", rationale: "Monitoring records complete for the period", category: "discharges" },
      { text: "DEMO: Incidents reported within internal timeframe", ref: { section: "DEMO-9.2" }, status: "not_applicable", rationale: "No incidents occurred during the audit period", category: "incidents" },
    ]);
  assert.equal(r.audit.status, "complete");
  assert.equal(r.findings[0]!.severity, "major");
  assert.match(r.md, /\(rev\. B\), section DEMO-6\.4, p\. 58/);
  assert.match(r.md, /Not a statutory deadline/);
});

test("DEMO hospitality audit: full cycle; major finding caps rating", () => {
  const r = runCycle("hospitality", "DEMO Resort Sustainability Audit (fictional)", "DEMO Beach Resort, Bali (fictional)",
    { id: "demo-hsc", title: "DEMO Resort Sustainability Criteria (fictional, internal)", revision: "0.1" },
    [
      { text: "DEMO: Waste destinations documented", ref: { section: "W1" }, status: "conforming", rationale: "Hauler receipts traced to licensed facility", category: "waste" },
      { text: "DEMO: Wastewater treated before discharge", ref: { section: "WW1" }, status: "major", rationale: "Treatment plant bypass observed in use", category: "wastewater", critical: true },
      { text: "DEMO: Water use metered monthly", ref: { section: "WA1" }, status: "conforming", rationale: "Twelve months of meter readings present", category: "water" },
      { text: "DEMO: Energy use tracked", ref: { section: "E1" }, status: "conforming", rationale: "Utility bills reconciled monthly", category: "energy" },
    ]);
  assert.equal(r.audit.status, "complete");
  const h = r.report.hospitality!;
  assert.equal(h.favourable, false, "a major finding must prevent a favourable rating");
  assert.match(r.md, /Provisional internal scoring method/);
});
