import { test } from "node:test";
import assert from "node:assert/strict";
import * as engine from "../src/index.ts";
import type { Assessment, AssessmentStatus, AuditBundle, Requirement } from "../src/index.ts";
import { ctx, must, codes, TARREN, SAM, ALEX, T0 } from "./helpers.ts";
import { addDays } from "../src/util.ts";

function setup(status: AssessmentStatus = "conforming") {
  const c = ctx(TARREN, T0);
  let req = must(engine.createRequirement({
    module: "hospitality", text: "DEMO requirement", category: "water", weight: 1,
    source: { documentId: "demo", documentTitle: "DEMO source", revision: "A" },
  }, c));
  req = must(engine.reviewRequirement(req, "approved", "Reviewed", req.version, ctx(ALEX, T0)));
  let audit = must(engine.createAudit({ module: "hospitality", title: "DEMO audit", siteName: "DEMO site", startDate: T0 }, c));
  audit = must(engine.addCriteria(audit, [req], audit.version, c));
  audit = must(engine.setAuditStatus(audit, "in_progress", audit.version, c));
  const evidence = must(engine.createEvidence({ auditId: audit.id, kind: "record", description: "DEMO evidence" }, c));
  const assessment = must(engine.assess(engine.newAssessment(audit, req.id, c), audit, req, [evidence], {
    status, rationale: "DEMO assessment rationale", evidenceIds: [evidence.id],
  }, 1, c));
  const findings = engine.reconcileFindings(assessment, [], c).created;
  const bundle: AuditBundle = { audit, requirements: [req], assessments: [assessment], evidence: [evidence], findings, actions: [] };
  return { c, req, audit, evidence, assessment, findings, bundle };
}

test("completed audit scope stays locked, and repeated criteria are added once", () => {
  const s = setup();
  const empty = { ...s.audit, requirementIds: [] };
  const scoped = must(engine.addCriteria(empty, [s.req, s.req], empty.version, s.c));
  assert.deepEqual(scoped.requirementIds, [s.req.id]);
  const reporting = must(engine.setAuditStatus(s.audit, "reporting", s.audit.version, s.c));
  const complete = must(engine.completeAudit({ ...s.bundle, audit: reporting }, reporting.version, s.c));
  assert.deepEqual(codes(engine.addCriteria(complete, [s.req], complete.version, s.c)), ["AUDIT_COMPLETE"]);
});

test("the public API cannot bypass completion readiness", () => {
  assert.equal("forceComplete" in engine, false);
  const s = setup("major");
  const audit = must(engine.setAuditStatus(s.audit, "reporting", s.audit.version, s.c));
  assert.ok(codes(engine.completeAudit({ ...s.bundle, audit }, audit.version, s.c)).includes("FINDING_WITHOUT_ACTION"));
});

test("assessment cannot borrow another audit's scope and evidence", () => {
  const s = setup();
  const foreign = { ...s.assessment, auditId: "other-audit" };
  assert.ok(codes(engine.assess(foreign, s.audit, s.req, [s.evidence], {
    status: "major", rationale: "DEMO changed assessment", evidenceIds: [s.evidence.id],
  }, foreign.version, s.c)).includes("AUDIT_MISMATCH"));
});

test("an unassessed critical criterion blocks a rating even at the coverage threshold", () => {
  const s = setup();
  const reqs = Array.from({ length: 10 }, (_, i) => ({ ...s.req, id: `r${i}`, critical: i === 9 }));
  const assessments = reqs.slice(0, 9).map((r) => ({ ...s.assessment, requirementId: r.id }));
  const score = engine.scoreHospitality(reqs, assessments, [], engine.DEFAULT_CONFIG.hospitality);
  assert.equal(score.coverage, 0.9);
  assert.equal(score.favourable, false);
  assert.equal(score.rating, "Incomplete: not rated");
});

test("later requirement revisions do not rewrite assessed hospitality scoring metadata", () => {
  const s = setup("minor");
  const goodReq = { ...s.req, id: "good" };
  const goodAssessment: Assessment = { ...s.assessment, id: "good-assessment", requirementId: goodReq.id, status: "conforming" };
  const before = engine.scoreHospitality([s.req, goodReq], [s.assessment, goodAssessment], [], engine.DEFAULT_CONFIG.hospitality);
  const revised: Requirement = { ...s.req, category: "changed", weight: 99, critical: true };
  const after = engine.scoreHospitality([revised, goodReq], [s.assessment, goodAssessment], [], engine.DEFAULT_CONFIG.hospitality);
  assert.deepEqual(after, before);
  assert.equal(after.favourable, true);
});

test("non-default deadlines cannot be labelled as internal defaults", () => {
  const s = setup("major");
  const finding = s.findings[0]!;
  assert.deepEqual(codes(engine.createAction(finding, {
    description: "DEMO fix", owner: SAM, dueDate: addDays(T0, 60), deadlineBasis: { kind: "internal_default", days: 14 },
  }, s.c)), ["DEADLINE_REASON_REQUIRED"]);
  assert.deepEqual(codes(engine.createAction(finding, {
    description: "DEMO fix", owner: SAM, deadlineBasis: { kind: "internal_default", days: 60 },
  }, s.c)), ["DEADLINE_REASON_REQUIRED"]);
});

test("readiness requires scope, source records, and reconciled findings", () => {
  const s = setup("major");
  const codesOf = (b: AuditBundle) => engine.reportReadiness(b).blockers.map((v) => v.code);
  assert.ok(codesOf({ ...s.bundle, audit: { ...s.audit, requirementIds: [] } }).includes("SCOPE_EMPTY"));
  assert.ok(codesOf({ ...s.bundle, requirements: [] }).includes("REQUIREMENT_MISSING"));
  assert.ok(codesOf({ ...s.bundle, findings: [] }).includes("FINDING_MISSING"));
  assert.ok(codesOf({ ...s.bundle, findings: [{ ...s.findings[0]!, auditId: "other-audit" }] }).includes("FINDING_MISSING"));
});

test("a missing requirement remains visible in the draft report using its snapshot", () => {
  const s = setup();
  const report = engine.buildReport({ ...s.bundle, requirements: [] }, T0, engine.DEFAULT_CONFIG);
  assert.equal(report.items.length, 1);
  assert.equal(report.items[0]!.requirementText, s.req.text);
  assert.equal(report.counts.conforming, 1);
  assert.equal(report.readiness.ready, false);
});

test("actions from another audit cannot resolve or cancel a finding in this audit", () => {
  const s = setup("major");
  const finding = s.findings[0]!;
  const action = must(engine.createAction(finding, { description: "DEMO fix", owner: SAM }, s.c));
  const foreignClosed = { ...action, auditId: "other-audit", status: "closed" as const };
  assert.equal(engine.needsCorrectiveAction(finding, [foreignClosed]), true);
  assert.deepEqual(codes(engine.closeFinding(finding, [foreignClosed], finding.version, s.c)), ["NO_ACTION"]);
  assert.deepEqual(codes(engine.cancelAction(action, "DEMO reason", { ...finding, auditId: "other-audit" }, action.version, s.c)), ["FINDING_MISMATCH"]);
  const report = engine.buildReport({ ...s.bundle, actions: [foreignClosed] }, T0, engine.DEFAULT_CONFIG);
  assert.deepEqual(report.items[0]!.findings[0]!.actions, []);
});

test("requirement revisions reject weights that would corrupt scores", () => {
  const s = setup();
  for (const weight of [-1, 0, Infinity, NaN]) {
    assert.deepEqual(codes(engine.reviseRequirement(s.req, { weight }, "DEMO revision", s.req.version, s.c)), ["WEIGHT_INVALID"]);
  }
});
