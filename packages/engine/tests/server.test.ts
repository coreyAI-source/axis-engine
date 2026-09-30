import { test } from "node:test";
import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";
import { fileURLToPath } from "node:url";
import { handleRequest } from "../src/server.ts";
import type { HospitalityBundle, ReportPayload, ServerValue } from "../src/server.ts";
import type { Actor, Result } from "../src/types.ts";

const AUDITOR: Actor = { name: "Pilot auditor", userId: "pilot-auditor", authenticated: true };
const OWNER: Actor = { name: "Pilot action owner", userId: "pilot-owner", authenticated: true };
const VERIFIER: Actor = { name: "Pilot verifier", userId: "pilot-verifier", authenticated: true };
const NOW = "2026-09-29T09:00:00.000Z";

function request(operation: string, bundle?: HospitalityBundle, input: Record<string, unknown> = {}, actor = AUDITOR): Result<ServerValue> {
  return handleRequest({ operation, bundle, input, actor, now: NOW });
}
function value<T extends ServerValue>(result: Result<ServerValue>): T {
  if (!result.ok) assert.fail(JSON.stringify(result.violations));
  return result.value as T;
}
function mutate(operation: string, bundle: HospitalityBundle, input: Record<string, unknown> = {}, actor = AUDITOR): HospitalityBundle {
  return value<HospitalityBundle>(request(operation, bundle, input, actor));
}
function create(): HospitalityBundle {
  return value<HospitalityBundle>(request("create", undefined, { title: "Fictional hotel pilot", siteName: "Fictional Bali hotel" }));
}
function codes(result: Result<ServerValue>): string[] { return result.ok ? [] : result.violations.map((violation) => violation.code); }
function recordEvidence(bundle: HospitalityBundle): HospitalityBundle {
  return mutate("evidence", bundle, { kind: "record", description: "Fictional inspection record", reference: "DEMO-RECORD-01" });
}
function assessed(bundle: HospitalityBundle, major = false): HospitalityBundle {
  let b = recordEvidence(bundle);
  for (const [index, requirement] of b.requirements.entries()) {
    b = mutate("assess", b, { requirementId: requirement.id, status: major && index === 7 ? "major" : "conforming", rationale: major && index === 7 ? "Demo maintenance records have a serious gap." : "Demo records and staff interview support this assessment.", evidenceIds: [b.evidence[0]!.id] });
  }
  return b;
}

test("server creates the GSTC Hotel Standard v4.0 criteria and authenticated audit history without trusting body overrides", () => {
  const b = value<HospitalityBundle>(request("create", undefined, { title: "Hotel", siteName: "Pilot", actor: OWNER, config: { deadlineDays: { major: 0 } } }));
  assert.equal(b.requirements.length, 40);
  assert.equal(b.audit.status, "in_progress");
  assert.equal(b.assessments.length, 40);
  assert.equal(b.audit.leadAuditor.userId, AUDITOR.userId);
  assert.equal(b.config.deadlineDays.major, 14);
  assert.equal(b.template.id, "gstc-hotel-v4");
  assert.equal(b.template.fictional, false);
  assert.match(b.template.disclaimer, /not GSTC certification/);
  const clauses = b.requirements.map((item) => item.source.clause);
  assert.deepEqual(clauses, [
    ...Array.from({ length: 14 }, (_, i) => `A${i + 1}`), ...Array.from({ length: 9 }, (_, i) => `B${i + 1}`),
    ...Array.from({ length: 4 }, (_, i) => `C${i + 1}`), ...Array.from({ length: 13 }, (_, i) => `D${i + 1}`),
  ]);
  assert.equal(b.requirements.reduce((sum, item) => sum + (item.indicators?.length ?? 0), 0), 205);
  const a1 = b.requirements[0]!;
  assert.equal(a1.text, "A1 Sustainability Management System — The hotel operates under a documented sustainability management system proportional to its size and scope, ensuring that sustainability is managed in a systematic manner and continuous improvement is pursued.");
  assert.equal(a1.source.page, "3");
  assert.equal(a1.indicators![1], "The policy is formally approved and communicated to all staff.");
  assert.ok(b.requirements.every((item) => item.reviewStatus === "approved" && item.reviewedBy?.authenticated === false));
  assert.ok(b.requirements.every((item) => !item.critical), "critical flags are an auditor decision, not part of the standard");
  assert.match(b.requirements[0]!.id, /^[0-9a-f-]{36}$/);
  assert.ok(b.assessments.every((item) => item.status === "unassessed"));
});

test("server still loads audits saved with the earlier fictional pilot template", () => {
  const legacy = { ...create(), template: { id: "axis-hotel-pilot", version: "2026-09-29", title: "AXIS fictional hotel pilot criteria", fictional: true, disclaimer: "FICTIONAL internal demonstration criteria." } };
  assert.ok(value<ReportPayload>(request("report", legacy)).markdown.includes("FICTIONAL internal demonstration criteria."));
  assert.deepEqual(codes(request("report", { ...legacy, template: { ...legacy.template, id: "unknown-template" } })), ["INVALID_BUNDLE"]);
});

test("server rejects malformed enum values, unknown operations, unauthenticated identities and mismatched stored records", () => {
  const b = create();
  assert.deepEqual(codes(request("delete", b)), ["INVALID_INPUT"]);
  assert.deepEqual(codes(request("status", b, { status: "complete" })), ["INVALID_INPUT"]);
  assert.deepEqual(codes(request("assess", b, { requirementId: b.requirements[0]!.id, status: "great", rationale: "This should not pass", evidenceIds: [] })), ["INVALID_INPUT"]);
  assert.deepEqual(codes(request("evidence", b, { kind: "made-up", description: "Evidence" })), ["INVALID_INPUT"]);
  assert.deepEqual(codes(request("report", b, {}, { ...AUDITOR, authenticated: false })), ["AUTHENTICATED_ACTOR_REQUIRED"]);
  assert.deepEqual(codes(request("report", { ...b, assessments: b.assessments.map((item) => ({ ...item, auditId: "another-audit" })) })), ["INVALID_BUNDLE"]);
  assert.equal(b.evidence.length, 0, "failed operations do not mutate caller state");
});

test("server enforces assessment evidence, readiness and the complete-audit scope lock", () => {
  let b = create();
  assert.deepEqual(codes(request("assess", b, { requirementId: b.requirements[0]!.id, status: "conforming", rationale: "Records were inspected", evidenceIds: [] })), ["EVIDENCE_REQUIRED"]);
  b = mutate("status", b, { status: "reporting" });
  assert.ok(codes(request("complete", b)).includes("UNASSESSED"));
  b = assessed(b);
  b = mutate("complete", b);
  assert.equal(b.audit.status, "complete");
  assert.deepEqual(codes(request("assess", b, {})), ["AUDIT_COMPLETE"]);
  assert.deepEqual(codes(request("requirement.create", b, {})), ["AUDIT_COMPLETE"]);
  assert.deepEqual(codes(request("requirement.review", b, {})), ["AUDIT_COMPLETE"]);
  const payload = value<ReportPayload>(request("report", b));
  assert.equal(payload.report.draft, false);
  assert.equal(payload.report.hospitality?.score, 100);
  assert.match(payload.markdown, /GSTC Hotel Standard v4\.0 \(December 30, 2025\)/);
  assert.match(payload.markdown, /Provisional internal scoring method/);
});

test("server completes a major-finding cycle with authenticated independent verification and idempotent assessment retry", () => {
  let b = assessed(create(), true);
  const auditCopy = structuredClone(b);
  const finding = b.findings[0]!;
  assert.equal(finding.severity, "major");
  b = mutate("action.create", b, { findingId: finding.id, description: "Repair the wastewater controls and document checks.", owner: OWNER });
  const actionId = b.actions[0]!.id;
  assert.equal(b.actions[0]!.deadlineBasis.kind, "internal_default");
  assert.equal(b.actions[0]!.dueDate, "2026-10-13T09:00:00.000Z");
  b = mutate("action.progress", b, { actionId, note: "Repair work started." }, OWNER);
  b = mutate("action.submit", b, { actionId, note: "Controls repaired and inspections recorded.", evidenceIds: [b.evidence[0]!.id] }, OWNER);
  assert.ok(codes(request("action.verify", b, { actionId, outcome: "effective", note: "Inspection confirms control operation." }, OWNER)).includes("VERIFIER_NOT_INDEPENDENT"));
  assert.deepEqual(codes(request("action.verify", b, { actionId, outcome: "approved", note: "Inspection confirms control operation." }, VERIFIER)), ["INVALID_INPUT"]);
  b = mutate("action.verify", b, { actionId, outcome: "effective", note: "Inspection confirms control operation." }, VERIFIER);
  b = mutate("finding.close", b, { findingId: finding.id }, VERIFIER);
  assert.equal(b.actions[0]!.verifications[0]!.separation, "enforced");
  const lastAssessment = b.assessments[7]!;
  const beforeRetry = structuredClone(b);
  b = mutate("assess", b, { requirementId: lastAssessment.requirementId, status: lastAssessment.status, rationale: `  ${lastAssessment.rationale}  `, evidenceIds: lastAssessment.evidenceIds });
  assert.deepEqual(b, beforeRetry, "an unchanged assessment after closure must not create another finding or history entry");
  assert.equal(auditCopy.actions.length, 0, "successful mutations do not alter caller state");
  assert.equal(b.findings.length, 1);
  assert.equal(b.findings[0]!.status, "closed");
  b = mutate("status", b, { status: "reporting" });
  b = mutate("complete", b);
  const payload = value<ReportPayload>(request("report", b));
  assert.equal(payload.report.hospitality?.favourable, false, "closing an action does not erase the major audit result");
  assert.ok(b.actions[0]!.history.length >= 4);
});

test("server preserves frozen scoring config and supports action evidence after report completion", () => {
  let b = assessed(create(), true);
  b.config.deadlineDays.major = 9; // Stored, server-controlled config for an audit created under a different internal policy.
  b = mutate("action.create", b, { findingId: b.findings[0]!.id, description: "Implement a maintenance schedule.", owner: OWNER });
  assert.equal(b.actions[0]!.dueDate, "2026-10-08T09:00:00.000Z");
  b = mutate("status", b, { status: "reporting" });
  b = mutate("complete", b);
  const count = b.evidence.length;
  b = recordEvidence(b);
  assert.equal(b.evidence.length, count + 1);
  b = mutate("action.submit", b, { actionId: b.actions[0]!.id, note: "Schedule implemented after the audit report.", evidenceIds: [b.evidence.at(-1)!.id] }, OWNER);
  b = mutate("action.verify", b, { actionId: b.actions[0]!.id, outcome: "effective", note: "Inspected a completed maintenance cycle." }, VERIFIER);
  b = mutate("finding.close", b, { findingId: b.findings[0]!.id }, VERIFIER);
  assert.equal(b.audit.status, "complete");
  assert.equal(b.findings[0]!.status, "closed");
  assert.equal(b.config.deadlineDays.major, 9);
  assert.equal(create().config.deadlineDays.major, 14, "saved config cannot modify the defaults for other audits");
});

test("server keeps custom requirements out of scope until reviewed and preserves withdrawn finding history", () => {
  let b = create();
  b = mutate("requirement.create", b, { text: "Internal pilot review record is maintained.", category: "Management", auditPrompt: "Show the review record.", source: { documentId: "pilot-source", documentTitle: "Internal policy", revision: "1", section: "1" } });
  const requirementId = b.requirements.at(-1)!.id;
  assert.equal(b.audit.requirementIds.length, 40);
  assert.equal(b.requirements.at(-1)!.reviewStatus, "draft");
  assert.deepEqual(codes(request("assess", b, { requirementId, status: "not_applicable", rationale: "No activity in this fictional pilot.", evidenceIds: [] })), ["NOT_IN_SCOPE"]);
  b = mutate("requirement.review", b, { requirementId, decision: "approved", note: "Reviewed for this internal fictional pilot." }, VERIFIER);
  assert.equal(b.audit.requirementIds.length, 41);
  b = recordEvidence(b);
  b = mutate("assess", b, { requirementId, status: "minor", rationale: "Missing a required internal review record.", evidenceIds: [b.evidence[0]!.id] });
  b = mutate("assess", b, { requirementId, status: "conforming", rationale: "Located the review record in the archive.", evidenceIds: [b.evidence[0]!.id] });
  assert.ok(b.findings[0]!.reviewRequired);
  b = mutate("finding.withdraw", b, { findingId: b.findings[0]!.id, rationale: "Initial assessment was corrected after inspecting the archived record." });
  assert.equal(b.findings[0]!.status, "withdrawn");
  assert.equal(b.findings[0]!.history.at(-1)!.event, "finding.withdrawn");
});

test("stdin adapter emits a single JSON object and safe malformed-input failure", () => {
  const file = fileURLToPath(new URL("../src/server.ts", import.meta.url));
  const created = spawnSync(process.execPath, ["--experimental-strip-types", "--no-warnings", file], { input: JSON.stringify({ operation: "create", actor: AUDITOR, now: NOW, input: { title: "CLI hotel", siteName: "CLI site" } }), encoding: "utf8" });
  assert.equal(created.status, 0, created.stderr);
  assert.equal(created.stderr, "");
  assert.equal(JSON.parse(created.stdout).value.requirements.length, 40);
  const invalid = spawnSync(process.execPath, ["--experimental-strip-types", "--no-warnings", file], { input: "not json", encoding: "utf8" });
  assert.equal(invalid.status, 0);
  assert.deepEqual(JSON.parse(invalid.stdout).violations.map((violation: { code: string }) => violation.code), ["INVALID_JSON"]);
  assert.doesNotMatch(invalid.stdout, /Error:|at main|server\.ts/);
});
