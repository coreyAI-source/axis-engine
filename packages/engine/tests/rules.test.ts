import { test, describe } from "node:test";
import assert from "node:assert/strict";
import {
  createRequirement, reviewRequirement, reviseRequirement, createAudit, addCriteria, setAuditStatus,
  createEvidence, newAssessment, assess, reconcileFindings, withdrawFinding, closeFinding,
  createAction, changeDueDate, addProgressUpdate, submitImplementation, verifyAction,
  actionFlags, scoreHospitality, reportReadiness, completeAudit, DEFAULT_CONFIG,
  type Requirement, type Audit, type Evidence, type Finding,
} from "../src/index.ts";
import { ctx, must, codes, TARREN, SAM, ALEX, T0 } from "./helpers.ts";
import { addDays } from "../src/util.ts";

const SRC = { documentId: "doc-1", documentTitle: "DEMO Environment Plan", revision: "B", section: "4.2" };

function approvedReq(extra: Partial<Parameters<typeof createRequirement>[0]> = {}): Requirement {
  const c = ctx(TARREN, T0);
  const r = must(createRequirement({ module: "offshore", text: "DEMO: Maintain a chemical register.", source: SRC, ...extra }, c));
  return must(reviewRequirement(r, "approved", "Checked against source", r.version, ctx(ALEX, T0)));
}

function setup(module: "offshore" | "hospitality" = "offshore", reqExtra = {}) {
  const c = ctx(TARREN, T0);
  const req = approvedReq({ module, ...reqExtra });
  let audit = must(createAudit({ module, title: "DEMO audit", siteName: "DEMO Site", startDate: T0 }, c));
  audit = must(addCriteria(audit, [req], audit.version, c));
  audit = must(setAuditStatus(audit, "in_progress", audit.version, c));
  const ev = must(createEvidence({ auditId: audit.id, kind: "record", description: "DEMO register extract", reference: "Register p.1" }, c));
  return { c, req, audit, ev };
}

function toMajorFinding() {
  const s = setup();
  const a0 = newAssessment(s.audit, s.req.id, s.c);
  const a1 = must(assess(a0, s.audit, s.req, [s.ev], { status: "major", rationale: "Register missing 3 chemicals in use", evidenceIds: [s.ev.id] }, 1, s.c));
  const { created } = reconcileFindings(a1, [], s.c);
  return { ...s, a1, finding: created[0]! };
}

describe("requirements", () => {
  test("all requirements start as draft, including AI extraction", () => {
    const r = must(createRequirement({ module: "offshore", text: "x", source: SRC, origin: "ai_extraction" }, ctx(TARREN, T0)));
    assert.equal(r.reviewStatus, "draft");
  });
  test("source document and revision are mandatory", () => {
    const r = createRequirement({ module: "offshore", text: "x", source: { ...SRC, revision: "" } }, ctx(TARREN, T0));
    assert.deepEqual(codes(r), ["SOURCE_REVISION_REQUIRED"]);
  });
  test("draft requirements cannot enter an audit", () => {
    const c = ctx(TARREN, T0);
    const r = must(createRequirement({ module: "offshore", text: "x", source: SRC }, c));
    const audit = must(createAudit({ module: "offshore", title: "t", siteName: "s", startDate: T0 }, c));
    assert.deepEqual(codes(addCriteria(audit, [r], 1, c)), ["REQUIREMENT_NOT_APPROVED"]);
  });
  test("revising an approved requirement sends it back to draft", () => {
    const r = approvedReq();
    const r2 = must(reviseRequirement(r, { text: "changed" }, "Rev C issued", r.version, ctx(TARREN, T0)));
    assert.equal(r2.reviewStatus, "draft");
  });
  test("ISO requirements and audits need a discipline; integrated audits accept several", () => {
    const c = ctx(TARREN, T0);
    assert.deepEqual(codes(createAudit({ module: "iso", title: "t", siteName: "s", startDate: T0 }, c)), ["DISCIPLINE_REQUIRED"]);
    assert.ok(createAudit({ module: "iso", title: "t", siteName: "s", startDate: T0, disciplines: ["environment", "quality", "ohs"] }, c).ok);
  });
});

describe("assessment", () => {
  test("rationale required for every status except unassessed, including not applicable", () => {
    const s = setup();
    const a = newAssessment(s.audit, s.req.id, s.c);
    assert.ok(codes(assess(a, s.audit, s.req, [s.ev], { status: "not_applicable", rationale: "", evidenceIds: [] }, 1, s.c)).includes("RATIONALE_REQUIRED"));
    assert.ok(assess(a, s.audit, s.req, [s.ev], { status: "not_applicable", rationale: "No chemicals used on this facility", evidenceIds: [] }, 1, s.c).ok);
  });
  test("conforming needs evidence from this audit", () => {
    const s = setup();
    const a = newAssessment(s.audit, s.req.id, s.c);
    assert.deepEqual(codes(assess(a, s.audit, s.req, [s.ev], { status: "conforming", rationale: "Looks fine overall", evidenceIds: [] }, 1, s.c)), ["EVIDENCE_REQUIRED"]);
    const foreign: Evidence = { ...s.ev, id: "ev-x", auditId: "other" };
    assert.deepEqual(codes(assess(a, s.audit, s.req, [foreign], { status: "conforming", rationale: "Looks fine overall", evidenceIds: ["ev-x"] }, 1, s.c)), ["EVIDENCE_OTHER_AUDIT"]);
  });
  test("stale version is rejected (concurrent edit)", () => {
    const s = setup();
    const a = newAssessment(s.audit, s.req.id, s.c);
    const input = { status: "conforming" as const, rationale: "Register complete", evidenceIds: [s.ev.id] };
    const first = must(assess(a, s.audit, s.req, [s.ev], input, 1, s.c));
    assert.deepEqual(codes(assess(first, s.audit, s.req, [s.ev], { ...input, status: "minor" }, 1, s.c)), ["VERSION_CONFLICT"]);
  });
  test("assessment snapshots the requirement so later revisions do not rewrite history", () => {
    const { a1, req } = toMajorFinding();
    assert.equal(a1.snapshot?.text, req.text);
    assert.equal(a1.snapshot?.source.revision, "B");
  });
});

describe("findings survive assessment changes", () => {
  test("major raises a finding; changing to conforming keeps it and flags review", () => {
    const s = toMajorFinding();
    assert.equal(s.finding.severity, "major");
    const a2 = must(assess(s.a1, s.audit, s.req, [s.ev], { status: "conforming", rationale: "Missing items were a data export error", evidenceIds: [s.ev.id] }, s.a1.version, s.c));
    const { changed, created } = reconcileFindings(a2, [s.finding], s.c);
    assert.equal(created.length, 0);
    assert.equal(changed[0]!.status, "open");
    assert.ok(changed[0]!.reviewRequired);
  });
  test("downgrade major to minor keeps the same finding with history", () => {
    const s = toMajorFinding();
    const a2 = must(assess(s.a1, s.audit, s.req, [s.ev], { status: "minor", rationale: "Only one chemical actually missing", evidenceIds: [s.ev.id] }, s.a1.version, s.c));
    const f = reconcileFindings(a2, [s.finding], s.c).changed[0]!;
    assert.equal(f.id, s.finding.id);
    assert.equal(f.severity, "minor");
    assert.ok(f.history.some((h) => h.event === "finding.severity_changed"));
  });
  test("withdrawal needs a rationale and is kept on record", () => {
    const s = toMajorFinding();
    assert.deepEqual(codes(withdrawFinding(s.finding, "", 1, s.c)), ["RATIONALE_REQUIRED"]);
    const w = must(withdrawFinding(s.finding, "Raised against wrong facility", 1, s.c));
    assert.equal(w.status, "withdrawn");
  });
  test("finding cannot close without a corrective action", () => {
    const s = toMajorFinding();
    assert.deepEqual(codes(closeFinding(s.finding, [], 1, s.c)), ["NO_ACTION"]);
  });
});

describe("corrective actions", () => {
  test("default deadline is an editable internal default (major 14 days)", () => {
    const s = toMajorFinding();
    const a = must(createAction(s.finding, { description: "Update register", owner: SAM }, s.c));
    assert.equal(a.dueDate, addDays(T0, 14));
    assert.deepEqual(a.deadlineBasis, { kind: "internal_default", days: 14 });
  });
  test("non-default due date needs a reason; external deadline needs a cited reference", () => {
    const s = toMajorFinding();
    assert.deepEqual(codes(createAction(s.finding, { description: "d", owner: SAM, dueDate: addDays(T0, 60) }, s.c)), ["DEADLINE_REASON_REQUIRED"]);
    assert.deepEqual(
      codes(createAction(s.finding, { description: "d", owner: SAM, dueDate: addDays(T0, 60), deadlineBasis: { kind: "external", reference: "" } }, s.c)),
      ["DEADLINE_REFERENCE_REQUIRED"],
    );
    const a = must(createAction(s.finding, { description: "d", owner: SAM }, s.c));
    assert.deepEqual(codes(changeDueDate(a, addDays(T0, 40), { kind: "internal_default", days: 40 }, a.version, s.c)), ["DEADLINE_REASON_REQUIRED"]);
  });
  test("closure requires implementation evidence and an independent verifier", () => {
    const s = toMajorFinding();
    let a = must(createAction(s.finding, { description: "Update register", owner: SAM }, s.c));
    const samCtx = ctx(SAM, addDays(T0, 2));
    assert.deepEqual(codes(verifyAction(a, "effective", "Checked the register", a.version, ctx(ALEX, T0))), ["NOT_AWAITING_VERIFICATION"]);
    assert.deepEqual(codes(submitImplementation(a, "Done", [], [], a.version, samCtx)), ["IMPLEMENTATION_EVIDENCE_REQUIRED"]);
    const proof = must(createEvidence({ auditId: s.audit.id, kind: "document", description: "Updated register rev 2" }, samCtx));
    a = must(submitImplementation(a, "Register updated", [proof.id], [proof], a.version, samCtx));
    assert.deepEqual(codes(verifyAction(a, "effective", "I checked it myself", a.version, samCtx)), ["VERIFIER_NOT_INDEPENDENT", "VERIFIER_NOT_INDEPENDENT"]);
    const sneaky = { name: "  demo sam   OWNER ", authenticated: false };
    assert.ok(codes(verifyAction(a, "effective", "Checked the register", a.version, ctx(sneaky, T0))).includes("VERIFIER_NOT_INDEPENDENT"));
    const res = verifyAction(a, "effective", "Sampled 5 entries against SDS", a.version, ctx(ALEX, addDays(T0, 3)));
    assert.ok(res.ok);
    if (res.ok) {
      assert.equal(res.value.status, "closed");
      assert.equal(res.value.verifications[0]!.separation, "declared_only");
      assert.ok(res.warnings.some((w) => w.code === "SEPARATION_NOT_AUTHENTICATED"));
    }
  });
  test("separation is 'enforced' only with authenticated distinct users", () => {
    const s = toMajorFinding();
    const owner = { name: "O", userId: "u1", authenticated: true };
    const ver = { name: "V", userId: "u2", authenticated: true };
    let a = must(createAction(s.finding, { description: "d", owner }, s.c));
    const oc = ctx(owner, T0);
    const proof = must(createEvidence({ auditId: s.audit.id, kind: "document", description: "p" }, oc));
    a = must(submitImplementation(a, "done", [proof.id], [proof], a.version, oc));
    const sameId = { name: "Different Name", userId: "u1", authenticated: true };
    assert.ok(codes(verifyAction(a, "effective", "Checked evidence", a.version, ctx(sameId, T0))).includes("VERIFIER_NOT_INDEPENDENT"));
    const done = must(verifyAction(a, "effective", "Checked evidence", a.version, ctx(ver, T0)));
    assert.equal(done.verifications[0]!.separation, "enforced");
  });
  test("failed verification returns the action to in progress", () => {
    const s = toMajorFinding();
    let a = must(createAction(s.finding, { description: "d", owner: SAM }, s.c));
    const sc = ctx(SAM, T0);
    const p = must(createEvidence({ auditId: s.audit.id, kind: "document", description: "p" }, sc));
    a = must(submitImplementation(a, "done", [p.id], [p], a.version, sc));
    a = must(verifyAction(a, "not_effective", "Register still missing two items", a.version, ctx(ALEX, T0)));
    assert.equal(a.status, "in_progress");
  });
});

describe("monitoring", () => {
  const f = (sev: "major" | "minor") => ({ severity: sev }) as Finding;
  const base = () => {
    const s = toMajorFinding();
    return must(createAction(s.finding, { description: "d", owner: SAM }, s.c));
  };
  test("major unstarted after 48 hours", () => {
    const a = base();
    assert.deepEqual(actionFlags(a, f("major"), addDays(T0, 1.9), DEFAULT_CONFIG), []);
    assert.deepEqual(actionFlags(a, f("major"), addDays(T0, 2), DEFAULT_CONFIG).map((x) => x.code), ["major_unstarted_48h"]);
  });
  test("unstarted past half the window, then inactive 7 days, then overdue", () => {
    const a = base(); // 14-day window
    const at = (d: number) => actionFlags(a, f("minor"), addDays(T0, d), DEFAULT_CONFIG).map((x) => x.code);
    assert.deepEqual(at(6.9), []);
    assert.deepEqual(at(7.1), ["inactive", "unstarted_past_half_window"]);
    assert.deepEqual(at(15), ["overdue", "inactive", "unstarted_past_half_window"]);
  });
  test("a progress update resets inactivity", () => {
    let a = base();
    a = must(addProgressUpdate(a, "Started review", a.version, ctx(SAM, addDays(T0, 6))));
    assert.deepEqual(actionFlags(a, f("minor"), addDays(T0, 10), DEFAULT_CONFIG).map((x) => x.code), []);
    assert.deepEqual(actionFlags(a, f("minor"), addDays(T0, 13), DEFAULT_CONFIG).map((x) => x.code), ["inactive"]);
  });
  test("closed actions raise no flags", () => {
    const a = { ...base(), status: "closed" as const };
    assert.deepEqual(actionFlags(a, f("major"), addDays(T0, 99), DEFAULT_CONFIG), []);
  });
});

describe("hospitality scoring", () => {
  const mkReq = (id: string, extra: Partial<Requirement> = {}) => ({ id, category: "water", critical: false, ...extra }) as Requirement;
  const mkA = (requirementId: string, status: any) => ({ requirementId, status }) as any;
  const H = DEFAULT_CONFIG.hospitality;

  test("high score with a major finding is not favourable", () => {
    const reqs = Array.from({ length: 10 }, (_, i) => mkReq(`r${i}`));
    const as = reqs.map((r, i) => mkA(r.id, i === 0 ? "major" : "conforming"));
    const res = scoreHospitality(reqs, as, [], H);
    assert.equal(res.score, 90);
    assert.equal(res.favourable, false);
    assert.match(res.rating, /capped/);
  });
  test("critical gap blocks a favourable rating", () => {
    const reqs = [mkReq("a", { critical: true }), ...Array.from({ length: 9 }, (_, i) => mkReq(`r${i}`))];
    const as = reqs.map((r) => mkA(r.id, r.id === "a" ? "minor" : "conforming"));
    const res = scoreHospitality(reqs, as, [], H);
    assert.equal(res.favourable, false);
    assert.equal(res.criticalGaps.length, 1);
  });
  test("low coverage gives no rating", () => {
    const reqs = Array.from({ length: 10 }, (_, i) => mkReq(`r${i}`));
    const as = reqs.slice(0, 5).map((r) => mkA(r.id, "conforming"));
    const res = scoreHospitality(reqs, as, [], H);
    assert.equal(res.rating, "Incomplete: not rated");
    assert.equal(res.favourable, false);
  });
  test("not applicable is excluded from the score and coverage", () => {
    const reqs = [mkReq("a"), mkReq("b")];
    const res = scoreHospitality(reqs, [mkA("a", "conforming"), mkA("b", "not_applicable")], [], H);
    assert.equal(res.score, 100);
    assert.equal(res.coverage, 1);
    assert.equal(res.favourable, true);
  });
});

describe("report readiness", () => {
  test("cannot complete with unassessed criteria or findings lacking actions", () => {
    const s = toMajorFinding();
    const audit: Audit = must(setAuditStatus(s.audit, "reporting", s.audit.version, s.c));
    const bundle = { audit, requirements: [s.req], assessments: [s.a1], evidence: [s.ev], findings: [s.finding], actions: [] };
    assert.deepEqual(reportReadiness(bundle).blockers.map((b) => b.code), ["FINDING_WITHOUT_ACTION"]);
    assert.deepEqual(codes(completeAudit(bundle, audit.version, s.c)), ["FINDING_WITHOUT_ACTION"]);
    assert.deepEqual(codes(setAuditStatus(audit, "complete", audit.version, s.c)), ["USE_COMPLETE_AUDIT"]);
  });
  test("completed audit rejects further assessment changes", () => {
    const s = setup();
    const a = must(assess(newAssessment(s.audit, s.req.id, s.c), s.audit, s.req, [s.ev], { status: "conforming", rationale: "Register complete", evidenceIds: [s.ev.id] }, 1, s.c));
    let audit = must(setAuditStatus(s.audit, "reporting", s.audit.version, s.c));
    audit = must(completeAudit({ audit, requirements: [s.req], assessments: [a], evidence: [s.ev], findings: [], actions: [] }, audit.version, s.c));
    assert.ok(codes(assess(a, audit, s.req, [s.ev], { status: "minor", rationale: "Changed my mind later", evidenceIds: [s.ev.id] }, a.version, s.c)).includes("AUDIT_COMPLETE"));
  });
});
