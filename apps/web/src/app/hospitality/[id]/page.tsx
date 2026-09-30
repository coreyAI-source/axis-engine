"use client";

import { FormEvent, useEffect, useMemo, useRef, useState } from "react";
import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import { ArrowLeft } from "lucide-react";
import AppShell from "@/components/AppShell";
import { apiError, AssessmentStatus, AuditDetail, AuditReport, canAudit, canReview, CorrectiveAction, criterionHeading, criterionStatement, dateTime, Evidence, hospitality, httpStatus, indicatorsWithGuidance, label, Member, Requirement, saveBlob, sourceLabel, statusLabels, statusTone, Template } from "@/lib/hospitality";
import s from "../hospitality.module.css";
import ReadinessPanel from "./ReadinessReport";

type Command = (operation: string, input?: object) => Promise<boolean>;
type Tab = "overview" | "assessments" | "evidence" | "findings" | "criteria" | "readiness" | "report";

function Pill({ status }: { status: string }) {
  const tone = statusTone[status as AssessmentStatus] ?? (["closed", "complete", "approved", "effective"].includes(status) ? "green" : ["rejected", "not_effective"].includes(status) ? "red" : ["awaiting_verification", "draft", "open", "reporting"].includes(status) ? "amber" : ["in_progress"].includes(status) ? "blue" : undefined);
  return <span className={s.pill} data-tone={tone}>{statusLabels[status as AssessmentStatus] || label(status)}</span>;
}

function SourceNotice({ template, compact }: { template?: Template; compact?: boolean }) {
  if (template?.fictional) return <div className={s.notice}><strong>Earlier demonstration audit</strong>This audit was created with the fictional AXIS pilot criteria. New audits use the GSTC Hotel Standard v4.0.</div>;
  return <div className={s.notice}><strong>GSTC Hotel Standard v4.0 · internal assessment</strong>{compact ? "Criteria, indicators and guidelines are reproduced from the published standard. AXIS scores and deadlines are internal settings, not GSTC rules." : "Assess each criterion against its performance indicators. Mark criteria that do not apply to this property as Not applicable with a reason. AXIS scores and deadlines are internal settings; certification is only awarded by GSTC-accredited certification bodies."}</div>;
}

function EvidencePicker({ evidence, selected, change, id }: { evidence: Evidence[]; selected: string[]; change: (ids: string[]) => void; id: string }) {
  return <fieldset className={s.fieldset}><legend>Linked evidence</legend>{evidence.length ? <div className={s.evidenceList}>{evidence.map((item) => <label key={item.id} className={s.check} htmlFor={`${id}-${item.id}`}><input id={`${id}-${item.id}`} type="checkbox" checked={selected.includes(item.id)} onChange={(event) => change(event.target.checked ? [...selected, item.id] : selected.filter((entry) => entry !== item.id))} /><span>{item.description}<span className={s.small}> · {item.attachment?.fileName || label(item.kind)}</span></span></label>)}</div> : <p className={s.small}>Add a file, observation or interview in the Evidence tab first.</p>}</fieldset>;
}

function CriterionDetail({ requirement }: { requirement: Requirement }) {
  const { notes, indicators } = indicatorsWithGuidance(requirement);
  return <>
    <p className={s.statement}>{criterionStatement(requirement)}</p>
    <p className={s.small}>{sourceLabel(requirement.source)}</p>
    {requirement.auditPrompt && <p className={s.prompt}>{requirement.auditPrompt}</p>}
    {indicators.length > 0 && <>
      <p className={s.sectionTitle}>Performance indicators</p>
      <ol className={s.indicators}>{indicators.map((item, index) => <li className={s.indicator} key={index}>{item.text}{item.guidance && <details className={s.guide}><summary>GSTC guideline</summary><p>{item.guidance}</p></details>}</li>)}</ol>
    </>}
    {notes.map((note) => <p key={note} className={s.prompt} style={{ whiteSpace: "pre-line" }}>{note}</p>)}
  </>;
}

export default function HotelAuditPage() {
  const { id } = useParams<{ id: string }>();
  const router = useRouter();
  const [data, setData] = useState<AuditDetail | null>(null);
  const [me, setMe] = useState<Member | null>(null);
  const [members, setMembers] = useState<Member[]>([]);
  const [tab, setTab] = useState<Tab>("overview");
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [busy, setBusy] = useState(false);
  const [loading, setLoading] = useState(true);
  const [conflict, setConflict] = useState(false);
  const [savedAt, setSavedAt] = useState("");
  const errorRef = useRef<HTMLDivElement>(null);

  function fail(error: unknown) {
    if (httpStatus(error) === 401) { localStorage.removeItem("axis_token"); router.replace("/login"); return; }
    if (httpStatus(error) === 409) { setConflict(true); setError("This audit changed in another session. Your edit was not saved and your input has been kept. Load the latest saved version, review your input, then save again."); }
    else setError(apiError(error));
    setTimeout(() => errorRef.current?.scrollIntoView({ behavior: "smooth", block: "center" }), 0);
  }
  useEffect(() => {
    if (!localStorage.getItem("axis_token")) { router.replace("/login"); return; }
    let alive = true;
    Promise.all([hospitality.get(id), hospitality.me(), hospitality.members()]).then(([audit, mine, team]) => { if (alive) { setData(audit.data); setMe(mine.data); setMembers(team.data); } }).catch((error) => { if (alive) fail(error); }).finally(() => { if (alive) setLoading(false); });
    return () => { alive = false; };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [id]);
  function accept(next: AuditDetail) { setData(next); setSavedAt(new Date().toISOString()); setNotice(next.warnings?.length ? next.warnings.map((w) => w.message).join(" ") : "Changes saved."); }
  const command: Command = async (operation, input = {}) => {
    if (!data || busy || conflict) return false;
    setBusy(true); setError(""); setNotice("");
    try { const response = await hospitality.command(id, data.version, operation, input); accept(response.data); return true; }
    catch (error) { fail(error); return false; } finally { setBusy(false); }
  };
  async function reload() {
    setBusy(true);
    try { const response = await hospitality.get(id); setData(response.data); setConflict(false); setError(""); setNotice("Latest saved audit loaded. Unsaved form input has been kept; review it before saving."); }
    catch (error) { fail(error); } finally { setBusy(false); }
  }
  async function upload(file: File, description: string) {
    if (!data || busy || conflict) return false;
    setBusy(true); setError(""); setNotice("");
    try { const response = await hospitality.upload(id, data.version, file, description); accept(response.data); return true; }
    catch (error) { fail(error); return false; } finally { setBusy(false); }
  }
  async function download(evidence?: Evidence) {
    try { const response = evidence ? await hospitality.file(id, evidence.id) : await hospitality.report(id); saveBlob(response.data, evidence?.attachment?.fileName || `hotel-audit-${id}.md`); }
    catch (error) { fail(error); }
  }
  const editable = canAudit(me);
  const locked = busy || conflict;
  const audit = data?.bundle.audit;
  const score = data?.report.hospitality;
  const complete = audit?.status === "complete";
  const openFindings = data?.bundle.findings.filter((f) => f.status === "open").length || 0;
  const openActions = data?.bundle.actions.filter((a) => !["closed", "cancelled"].includes(a.status)).length || 0;
  const assessedCount = data?.bundle.assessments.filter((a) => a.status !== "unassessed").length || 0;
  const tabs: { id: Tab; title: string; count?: number }[] = [
    { id: "overview", title: "Overview" },
    { id: "assessments", title: "Assessments", count: audit ? audit.requirementIds.length - assessedCount : undefined },
    { id: "evidence", title: "Evidence", count: data?.bundle.evidence.length },
    { id: "findings", title: "Findings & actions", count: openFindings + openActions || undefined },
    { id: "criteria", title: "Criteria" },
    { id: "readiness", title: "Readiness report" },
    { id: "report", title: "Audit record" },
  ];

  return <div className={s.page}><AppShell>
    <div className={s.noPrint}><Link href="/hospitality" className={s.back}><ArrowLeft size={14} /> All hotel audits</Link></div>
    {loading && <p className={s.empty} role="status">Loading the saved audit…</p>}
    {error && <div ref={errorRef} role="alert" className={`${s.error} ${s.noPrint}`}>{error}{conflict && <div className={s.toolbar} style={{ marginTop: 10 }}><button className={s.secondary} disabled={busy} onClick={() => void reload()}>Load latest saved version</button></div>}{!data && !loading && <button className={s.secondary} onClick={() => window.location.reload()}>Retry</button>}</div>}
    {data && audit && <>
      <header className={`${s.header} ${s.noPrint}`}><div><p className={s.eyebrow}>{audit.siteName}</p><h1 className={s.title}>{audit.title}</h1><p className={s.subtitle}>Lead auditor: {audit.leadAuditor.name} · <Pill status={audit.status} /></p></div><div className={s.stack}><span className={s.saved} role="status">{busy ? "Saving…" : savedAt ? `Saved ${dateTime(savedAt)}` : `Saved version ${data.version}`}</span><span className={s.small}>{me?.name} · {label(me?.role_code || "")}</span></div></header>
      {notice && <p role="status" className={`${s.success} ${s.noPrint}`}>{notice}</p>}
      <div className={`${s.stats} ${s.noPrint}`}>
        <div className={s.stat}><strong>{Math.round((score?.coverage || 0) * 100)}%</strong><span>Applicable criteria assessed</span></div>
        <div className={s.stat} style={{ ["--tone" as string]: "var(--accent-2)" }}><strong>{data.bundle.evidence.length}</strong><span>Evidence records</span></div>
        <div className={s.stat} style={{ ["--tone" as string]: openFindings ? "var(--red)" : "var(--green)" }}><strong>{openFindings}</strong><span>Open findings</span></div>
        <div className={s.stat} style={{ ["--tone" as string]: openActions ? "var(--amber)" : "var(--green)" }}><strong>{openActions}</strong><span>Actions to resolve</span></div>
      </div>
      <div className={`${s.tabs} ${s.noPrint}`} role="tablist" aria-label="Hotel audit sections">{tabs.map((item) => <button key={item.id} id={`tab-${item.id}`} role="tab" aria-selected={tab === item.id} aria-controls={`panel-${item.id}`} className={s.tab} onClick={() => setTab(item.id)}>{item.title}{item.count ? <span className={s.tabCount}>{item.count}</span> : null}</button>)}</div>
      <section id="panel-overview" role="tabpanel" aria-labelledby="tab-overview" hidden={tab !== "overview"} className={s.noPrint}>
        <SourceNotice template={data.bundle.template} />
        <div className={s.grid}>
          <div className={s.card}><h2>Work through your hotel audit</h2>{[
            ["evidence", "Collect evidence", "Upload files or record observations and interviews."], ["assessments", "Assess each criterion", "Check the performance indicators, choose an outcome and link evidence."], ["findings", "Resolve findings", "Assign actions, submit implementation and verify independently."], ["readiness", "Write the readiness report", "Fill in report details, generate the AI draft, review it and download it as Word."],
          ].map(([target, title, text], index) => <div className={s.step} key={target}><span className={s.stepNumber}>{index + 1}</span><div><button className={s.linkButton} onClick={() => setTab(target as Tab)}>{title} →</button><p>{text}</p></div></div>)}</div>
          <div className={s.card}><h2>Progress by section</h2><p className={s.small} style={{ marginTop: 4 }}>{audit.requirementIds.length} criteria in scope · {data.bundle.requirements.filter((r) => r.reviewStatus === "draft").length} awaiting review</p>
            <div className={s.bars}>{score?.categories.map((category) => <div className={s.barRow} key={category.category}><span>{category.category}</span><span className={s.small}>{category.assessed}/{category.applicable}{category.score != null ? ` · ${category.score}%` : ""}</span><progress className={s.progress} max={Math.max(category.applicable, 1)} value={category.assessed} aria-label={`${category.category} assessed`} /></div>)}</div>
            <hr className={s.rule} /><h3>Provisional rating</h3><p className={s.subtitle} style={{ marginTop: 4 }}>{score?.rating || "Not rated"} · Score {score?.score == null ? "not available" : `${score.score}%`}</p>{score?.blockers.length ? <ul className={s.bulletList} style={{ marginTop: 10 }}>{score.blockers.map((message) => <li key={message}>{message}</li>)}</ul> : null}
          </div>
        </div>
        <div className={s.card}><h2>Activity record</h2><ul className={s.history} style={{ marginTop: 16 }}>{audit.history?.slice().reverse().map((entry, index) => <li key={`${entry.at}-${index}`}>{dateTime(entry.at)} · {entry.actor.name} · {label(entry.event.replace(/\./g, " "))}</li>)}</ul></div>
      </section>
      <section id="panel-assessments" role="tabpanel" aria-labelledby="tab-assessments" hidden={tab !== "assessments"} className={s.noPrint}><AssessmentPanel data={data} disabled={locked || !editable || complete} command={command} goEvidence={() => setTab("evidence")} /></section>
      <section id="panel-evidence" role="tabpanel" aria-labelledby="tab-evidence" hidden={tab !== "evidence"} className={s.noPrint}><EvidencePanel evidence={data.bundle.evidence} editable={editable || me?.role_code === "process_owner"} disabled={locked} command={command} upload={upload} download={download} /></section>
      <section id="panel-findings" role="tabpanel" aria-labelledby="tab-findings" hidden={tab !== "findings"} className={s.noPrint}><FindingsPanel data={data} me={me} members={members} disabled={locked} command={command} /></section>
      <section id="panel-criteria" role="tabpanel" aria-labelledby="tab-criteria" hidden={tab !== "criteria"} className={s.noPrint}><CriteriaPanel data={data} editable={editable && !complete} reviewer={canReview(me) && !complete} disabled={locked} command={command} /></section>
      <section id="panel-readiness" role="tabpanel" aria-labelledby="tab-readiness" hidden={tab !== "readiness"}>{tab === "readiness" && <ReadinessPanel auditId={id} version={data.version} editable={editable} fail={fail} />}</section>
      <section id="panel-report" role="tabpanel" aria-labelledby="tab-report" hidden={tab !== "report"}><ReportPanel report={data.report} bundle={data.bundle} template={data.bundle.template} editable={editable} disabled={locked} command={command} download={() => download()} /></section>
    </>}
  </AppShell></div>;
}

function FindingsPanel({ data, me, members, disabled, command }: { data: AuditDetail; me: Member | null; members: Member[]; disabled: boolean; command: Command }) {
  const editable = canAudit(me);
  const minLength = data.bundle.config?.minRationaleLength || 20;
  async function newAction(event: FormEvent<HTMLFormElement>, findingId: string) {
    event.preventDefault(); const form = event.currentTarget; const values = new FormData(form);
    if (await command("action.create", { findingId, description: String(values.get("description")).trim(), ownerUserId: String(values.get("owner")) })) form.reset();
  }
  async function withdraw(event: FormEvent<HTMLFormElement>, findingId: string) {
    event.preventDefault(); const form = event.currentTarget;
    if (await command("finding.withdraw", { findingId, rationale: String(new FormData(form).get("rationale")).trim() })) form.reset();
  }
  return <><div className={s.cardHead}><div><h2>Findings & corrective actions</h2><p className={s.muted}>Minor and major assessments create findings. Actions close after independent verification.</p></div></div>
    {!data.bundle.findings.length && <div className={`${s.card} ${s.empty}`}><h2>No findings raised</h2><p>Record a minor or major assessment to create a finding and assign corrective work.</p></div>}
    {data.bundle.findings.map((finding) => {
      const actions = data.bundle.actions.filter((action) => action.findingId === finding.id);
      const live = actions.filter((action) => action.status !== "cancelled");
      const canClose = live.length > 0 && live.every((action) => action.status === "closed");
      return <article className={s.card} key={finding.id}><div className={s.cardHead}><div><div className={s.toolbar}><Pill status={finding.severity} /><Pill status={finding.status} /></div><h2 style={{ marginTop: 13 }}>{finding.snapshot.text}</h2><p className={s.subtitle} style={{ whiteSpace: "pre-wrap" }}>{finding.statement}</p></div><span className={s.small}>Raised {dateTime(finding.raisedAt)}</span></div>
        {finding.reviewRequired && finding.status === "open" && <p className={s.error}>Review needed: {finding.reviewRequired.reason} Reconcile this finding before completing the report.</p>}
        {finding.withdrawal && <p className={s.notice}>Withdrawal reason: {finding.withdrawal.rationale}</p>}
        {actions.map((action) => <ActionCard key={action.id} action={action} me={me} evidence={data.bundle.evidence} disabled={disabled} minLength={minLength} command={command} />)}
        {editable && finding.status === "open" && <>
          <details className={s.details} open={actions.length === 0 ? true : undefined}><summary>Assign corrective action</summary><form onSubmit={(event) => void newAction(event, finding.id)}><fieldset disabled={disabled} style={{ border: 0 }}><label className={s.field}>What needs to change?<textarea name="description" required minLength={10} maxLength={4000} placeholder="Describe the corrective work and what completion will look like." /></label><label className={s.field}>Action owner<select name="owner" required defaultValue=""><option value="" disabled>Choose a team member</option>{members.filter((member) => member.role_code !== "viewer").map((member) => <option key={member.id} value={member.id}>{member.name} · {label(member.role_code)}</option>)}</select><small>The verifier must be a different person. Add team accounts from the Hotel audits page.</small></label><p className={s.small} style={{ marginBottom: 14 }}>Due date uses the internal {finding.severity} default{data.bundle.config?.deadlineDays ? ` (${data.bundle.config.deadlineDays[finding.severity as "minor" | "major"]} days)` : ""}. This is not a statutory deadline.</p><button className={s.button} type="submit">Assign action</button></fieldset></form></details>
          <div className={s.toolbar} style={{ marginTop: 18 }}><button className={s.secondary} disabled={disabled || !canClose} onClick={() => void command("finding.close", { findingId: finding.id })}>Close finding</button>{!canClose && <span className={s.small}>All active actions must be independently verified and closed.</span>}</div>
          <details className={s.details}><summary>Withdraw an incorrect finding</summary><p className={s.small} style={{ marginBottom: 12 }}>Use only when the finding was raised in error. Its history stays in the report. Correct the assessment first if needed.</p><form onSubmit={(event) => void withdraw(event, finding.id)}><fieldset disabled={disabled} style={{ border: 0 }}><label className={s.field}>Withdrawal rationale<textarea name="rationale" required minLength={minLength} maxLength={4000} /></label><button className={s.danger} type="submit">Withdraw finding</button></fieldset></form></details>
        </>}
      </article>;
    })}
  </>;
}

function ActionCard({ action, me, evidence, disabled, minLength, command }: { action: CorrectiveAction; me: Member | null; evidence: Evidence[]; disabled: boolean; minLength: number; command: Command }) {
  const [selectedEvidence, setSelectedEvidence] = useState<string[]>([]);
  const editable = canAudit(me);
  const canImplement = editable || (me?.role_code === "process_owner" && action.owner.userId === me.id);
  const independent = !!me && me.id !== action.owner.userId && me.id !== action.implementation?.submittedBy.userId;
  const canVerify = editable && independent;
  const finished = ["closed", "cancelled"].includes(action.status);
  async function update(event: FormEvent<HTMLFormElement>, operation: string) {
    event.preventDefault(); const form = event.currentTarget; const values = new FormData(form);
    const input = { actionId: action.id, note: String(values.get("note")).trim(), ...(operation === "action.submit" ? { evidenceIds: selectedEvidence } : {}), ...(operation === "action.verify" ? { outcome: String(values.get("outcome")) } : {}) };
    if (await command(operation, input)) { form.reset(); if (operation === "action.submit") setSelectedEvidence([]); }
  }
  return <div className={s.actionCard}><div className={s.cardHead}><div><h3>{action.description}</h3><p className={s.small} style={{ marginTop: 5 }}>Owner: {action.owner.name} · Due: {new Date(action.dueDate).toLocaleDateString()}</p><p className={s.small}>{action.deadlineBasis.kind === "internal_default" ? `Internal default: ${action.deadlineBasis.days} days; not statutory.` : action.deadlineBasis.reason || action.deadlineBasis.reference}</p></div><Pill status={action.status} /></div>
    {action.implementation && <div className={s.notice}><strong>Implementation submitted by {action.implementation.submittedBy.name}</strong><p style={{ whiteSpace: "pre-wrap" }}>{action.implementation.note}</p><p className={s.small} style={{ marginTop: 8 }}>Evidence: {action.implementation.evidenceIds.map((id) => evidence.find((e) => e.id === id)?.description || id).join("; ")}</p></div>}
    {canImplement && !finished && <details className={s.details}><summary>Record progress</summary><form onSubmit={(event) => void update(event, "action.progress")}><fieldset disabled={disabled} style={{ border: 0 }}><label className={s.field}>Progress note<textarea name="note" required minLength={5} maxLength={4000} placeholder="What has changed since the last update?" /></label><button className={s.secondary} type="submit">Save progress</button></fieldset></form></details>}
    {canImplement && ["not_started", "in_progress"].includes(action.status) && <details className={s.details}><summary>Submit for verification</summary><form onSubmit={(event) => void update(event, "action.submit")}><fieldset disabled={disabled} style={{ border: 0 }}><label className={s.field}>What was implemented?<textarea name="note" required minLength={10} maxLength={4000} /></label><EvidencePicker id={`action-${action.id}`} evidence={evidence} selected={selectedEvidence} change={setSelectedEvidence} /><button type="submit" disabled={!selectedEvidence.length} className={s.button}>Submit for verification</button><p className={s.small} style={{ marginTop: 10 }}>Link at least one evidence record showing the work was implemented.</p></fieldset></form></details>}
    {action.status === "awaiting_verification" && (canVerify ? <div className={s.details}><h3 style={{ marginBottom: 14 }}>Independent verification</h3><form onSubmit={(event) => void update(event, "action.verify")}><fieldset disabled={disabled} style={{ border: 0 }}><label className={s.field}>Verification outcome<select name="outcome" defaultValue="effective"><option value="effective">Effective — close this action</option><option value="not_effective">Not effective — return for more work</option></select></label><label className={s.field}>What did you check?<textarea name="note" required minLength={minLength} maxLength={4000} placeholder="Explain how you checked the evidence and verified effectiveness." /></label><button type="submit" className={s.button}>Save verification</button></fieldset></form></div> : <p className={s.notice} style={{ marginTop: 16 }}>Awaiting an independent auditor. The verifier must sign in with an account different from both the action owner and the person who submitted the implementation.</p>)}
    {(action.updates.length > 0 || action.verifications.length > 0) && <details className={s.details}><summary>Progress & verification history</summary><ul className={s.history}>{action.updates.map((entry, index) => <li key={`update-${index}`}><strong>{entry.by.name}</strong> · {dateTime(entry.at)}<br />{entry.note}</li>)}{action.verifications.map((entry, index) => <li key={`verification-${index}`}><strong>{entry.verifier.name}</strong> · {dateTime(entry.at)} · {label(entry.outcome)}<br />{entry.note}<br />Independence: {entry.separation === "enforced" ? "verified with separate signed-in accounts" : "declared only"}</li>)}</ul></details>}
  </div>;
}

function groupByCategory(requirements: Requirement[]) {
  const groups = new Map<string, Requirement[]>();
  for (const requirement of requirements) { const key = requirement.category || "General"; groups.set(key, [...(groups.get(key) || []), requirement]); }
  return [...groups.entries()];
}

function CriteriaPanel({ data, editable, reviewer, disabled, command }: { data: AuditDetail; editable: boolean; reviewer: boolean; disabled: boolean; command: Command }) {
  async function create(event: FormEvent<HTMLFormElement>) {
    event.preventDefault(); const form = event.currentTarget; const values = new FormData(form);
    const input = { text: String(values.get("text")).trim(), category: String(values.get("category")).trim(), auditPrompt: String(values.get("prompt")).trim(), source: { documentId: String(values.get("documentId")).trim(), documentTitle: String(values.get("documentTitle")).trim(), revision: String(values.get("revision")).trim(), section: String(values.get("section")).trim() || undefined }, critical: values.get("critical") === "on", weight: Number(values.get("weight")) };
    if (await command("requirement.create", input)) form.reset();
  }
  async function review(event: FormEvent<HTMLFormElement>, requirement: Requirement) {
    event.preventDefault(); const form = event.currentTarget; const values = new FormData(form);
    if (await command("requirement.review", { requirementId: requirement.id, decision: String(values.get("decision")), note: String(values.get("note")).trim() })) form.reset();
  }
  return <><div className={s.cardHead}><div><h2>Criteria library for this audit</h2><p className={s.muted}>Approved criteria are in scope. Each assessment keeps a copy of the criterion version it used.</p></div></div>
    <SourceNotice template={data.bundle.template} compact />
    {editable && <details className={s.card}><summary style={{ cursor: "pointer", fontWeight: 600 }}>+ Add a custom criterion (e.g. a local regulation or client requirement)</summary><form onSubmit={create} style={{ marginTop: 20 }}><fieldset disabled={disabled} style={{ border: 0 }}><label className={s.field}>Requirement<textarea name="text" required maxLength={12000} placeholder="Write the requirement being assessed." /></label><div className={s.grid}><label className={s.field}>Category<input name="category" required maxLength={100} defaultValue="Custom" /></label><label className={s.field}>Weight (provisional)<input name="weight" type="number" min="0.01" max="100" step="0.01" defaultValue="1" required /></label></div><label className={s.field}>Audit question and suggested evidence<textarea name="prompt" maxLength={4000} /></label><div className={s.grid}><label className={s.field}>Source document identifier<input name="documentId" required maxLength={255} placeholder="e.g. bali-waste-regulation" /></label><label className={s.field}>Source document title<input name="documentTitle" required maxLength={500} /></label><label className={s.field}>Revision or edition<input name="revision" required maxLength={100} placeholder="e.g. 2025" /></label><label className={s.field}>Section (optional)<input name="section" maxLength={100} /></label></div><label className={s.check}><input type="checkbox" name="critical" /><span>Critical criterion — a gap can prevent a favourable internal rating.</span></label><button type="submit" className={s.button} style={{ marginTop: 16 }}>Save draft criterion</button><p className={s.small} style={{ marginTop: 10 }}>Custom criteria stay out of scope until a lead auditor approves them.</p></fieldset></form></details>}
    {groupByCategory(data.bundle.requirements).map(([category, items]) => <div className={s.criteriaGroup} key={category}><p className={s.groupLabel}><span>{category}</span><span>{items.length}</span></p>{items.map((requirement) => <details className={s.criteriaRow} key={requirement.id} open={requirement.reviewStatus === "draft" ? true : undefined}><summary>{requirement.source.clause && <span className={s.code}>{requirement.source.clause}</span>}<span style={{ flex: 1, minWidth: 0 }}>{requirement.title || requirement.text}</span>{requirement.indicators?.length ? <span className={s.small}>{requirement.indicators.length} indicators</span> : null}{requirement.reviewStatus !== "approved" && <Pill status={requirement.reviewStatus} />}</summary><div className={s.criteriaBody}>
      <CriterionDetail requirement={requirement} />
      <p className={s.small} style={{ marginTop: 12 }}>{requirement.critical ? "Critical criterion" : "Standard criterion"} · Weight {requirement.weight || 1} · {data.bundle.audit.requirementIds.includes(requirement.id) ? "In audit scope" : "Outside scope pending approval"}</p>{requirement.reviewNote && <p className={s.small} style={{ marginTop: 6 }}>Review note: {requirement.reviewNote}</p>}
      {reviewer && requirement.reviewStatus === "draft" && <form onSubmit={(event) => void review(event, requirement)} className={s.details}><fieldset disabled={disabled} style={{ border: 0 }}><label className={s.field}>Review decision<select name="decision"><option value="approved">Approve and add to audit scope</option><option value="rejected">Reject requirement</option></select></label><label className={s.field}>Review note<textarea name="note" required minLength={10} maxLength={4000} placeholder="Record how you checked the source and interpretation." /></label><button type="submit" className={s.button}>Save review decision</button></fieldset></form>}
    </div></details>)}</div>)}
  </>;
}

const UUID = /[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}/gi;
function readableBlockers(blockers: { code: string; message: string }[], requirements: Requirement[], findings: { id: string; requirementId: string }[]) {
  const name = (id: string): string => {
    const r = requirements.find((item) => item.id === id);
    if (r) return r.source.clause || r.title || "a criterion";
    const f = findings.find((item) => item.id === id);
    return f ? `on ${name(f.requirementId)}` : id;
  };
  const unassessed = blockers.filter((b) => b.code === "UNASSESSED").map((b) => (b.message.match(UUID) || [])[0]).filter(Boolean).map((id) => name(id!));
  const rest = blockers.filter((b) => b.code !== "UNASSESSED").map((b) => b.message.replace(UUID, name));
  return [...(unassessed.length ? [`${unassessed.length} criteria not yet assessed: ${unassessed.join(", ")}.`] : []), ...rest];
}

function ReportPanel({ report, bundle, template, editable, disabled, command, download }: { report: AuditReport; bundle: AuditDetail["bundle"]; template?: Template; editable: boolean; disabled: boolean; command: Command; download: () => Promise<void> }) {
  const blockers = readableBlockers(report.readiness.blockers, bundle.requirements, bundle.findings);
  return <><div className={`${s.card} ${s.noPrint}`}><div className={s.cardHead}><div><h2>Review and export</h2><p className={s.muted}>Save a Markdown report or print this view to PDF using your browser.</p></div><div className={s.toolbar}><button className={s.secondary} onClick={() => void download()}>Download Markdown</button><button className={s.secondary} onClick={() => window.print()}>Print / save PDF</button></div></div>
    {report.audit.status !== "complete" && <><h3>{report.readiness.ready ? "Ready for report completion" : "Before you complete the report"}</h3>{blockers.length > 0 && <ul className={s.bulletList}>{blockers.map((message, index) => <li key={index}>{message}</li>)}</ul>}{editable && <div className={s.toolbar} style={{ marginTop: 16 }}>{report.audit.status === "in_progress" && <button className={s.button} disabled={disabled} onClick={() => void command("status", { status: "reporting" })}>Move to reporting</button>}{report.audit.status === "reporting" && <><button className={s.button} disabled={disabled || !report.readiness.ready} onClick={() => void command("complete")}>Complete audit</button><button className={s.secondary} disabled={disabled} onClick={() => void command("status", { status: "in_progress" })}>Return to assessment</button></>}</div>}<p className={s.small} style={{ marginTop: 12 }}>Completing the audit locks assessments and criteria. Corrective actions can continue after the report. Open actions remain clearly listed.</p></>}
    {report.readiness.warnings.length > 0 && <ul className={s.bulletList}>{report.readiness.warnings.map((warning, index) => <li key={`${warning.code}-${index}`}>{warning.message}</li>)}</ul>}
  </div><article className={s.card} aria-label="Hotel audit report"><p className={s.eyebrow}>{report.draft ? "Draft audit report" : "Completed audit report"} · {template?.fictional ? "AXIS hospitality pilot" : `${template?.title || "GSTC Hotel Standard"} ${template?.version || ""}`}</p><h1 className={s.title}>{report.audit.title}</h1><p className={s.subtitle}>{report.audit.siteName} · Lead auditor: {report.audit.leadAuditor}</p><p className={s.small}>Started {new Date(report.audit.startDate).toLocaleDateString()}{report.audit.endDate ? ` · Completed ${new Date(report.audit.endDate).toLocaleDateString()}` : ""} · Generated {dateTime(report.generatedAt)}</p>{report.audit.scopeStatement && <p className={s.subtitle}><strong>Scope:</strong> {report.audit.scopeStatement}</p>}
    <div className={s.notice} style={{ marginTop: 20 }}><strong>Internal assessment — not certification</strong>{template?.fictional ? "The demonstration criteria and provisional score do not establish compliance with the GSTC Hotel Standard or any recognised certification scheme." : "Assessed against the GSTC Hotel Standard v4.0. The provisional score is an AXIS internal method; only GSTC-accredited certification bodies can certify a hotel."}</div>
    <h2>Assessment summary</h2><div className={s.toolbar} style={{ margin: "15px 0 22px" }}>{Object.entries(report.counts).map(([status, count]) => <span className={s.pill} data-tone={count ? statusTone[status as AssessmentStatus] : undefined} key={status}>{statusLabels[status as AssessmentStatus]}: {count}</span>)}</div>
    {report.hospitality && <><h2>Provisional sustainability result</h2><p className={s.subtitle}><strong>{report.hospitality.rating}</strong> · Score: {report.hospitality.score == null ? "Not available" : `${report.hospitality.score}%`} · Coverage: {Math.round(report.hospitality.coverage * 100)}%</p><ul className={s.bulletList}>{report.hospitality.blockers.map((message) => <li key={message}>{message}</li>)}</ul><div className={s.toolbar} style={{ marginTop: 14 }}>{report.hospitality.categories.map((category) => <span className={s.pill} key={category.category}>{category.category}: {category.score == null ? "Not rated" : `${category.score}%`} ({category.assessed}/{category.applicable})</span>)}</div></>}
    {report.items.map((item) => <section className={s.reportItem} key={item.requirementId}><Pill status={item.status} /><h3>{item.requirementText}</h3><p className={s.small}>Source: {sourceLabel(item.source)}</p><p>{item.rationale || "No assessment rationale recorded."}</p>{item.evidence.length > 0 && <><p><strong>Evidence</strong></p><ul className={s.bulletList}>{item.evidence.map((entry) => <li key={entry.id}>{entry.description}{entry.reference ? ` · ${entry.reference}` : ""}{entry.fileName ? ` · ${entry.fileName}` : ""}</li>)}</ul></>}{item.findings.map((finding) => <div key={finding.id}><p><strong>{label(finding.severity)} finding · {label(finding.status)}</strong></p><p>{finding.statement}</p>{finding.actions.map((action) => <div key={action.id} className={s.reportAction}><strong style={{ fontSize: 13 }}>{action.description}</strong><p>Owner: {action.owner} · Due {action.dueDate} · {label(action.status)}</p><p className={s.small}>{action.deadlineNote}</p>{action.flags.map((flag) => <p key={flag}>{flag}</p>)}{action.verification && <p>{action.verification}</p>}</div>)}</div>)}</section>)}
    <section className={s.reportItem}><h2>Notes and limitations</h2><ul className={s.bulletList}>{report.disclaimers.map((note) => <li key={note}>{note}</li>)}{report.readiness.warnings.map((warning, index) => <li key={`${warning.code}-${index}`}>{warning.message}</li>)}</ul></section>
  </article></>;
}

interface AssessmentDraft { status: AssessmentStatus; rationale: string; evidenceIds: string[] }
type Filter = "all" | "todo" | "findings" | "done";
function AssessmentPanel({ data, disabled, command, goEvidence }: { data: AuditDetail; disabled: boolean; command: Command; goEvidence: () => void }) {
  const [selected, setSelected] = useState("");
  const [drafts, setDrafts] = useState<Record<string, AssessmentDraft>>({});
  const [query, setQuery] = useState("");
  const [filter, setFilter] = useState<Filter>("all");
  const requirements = useMemo(() => data.bundle.requirements.filter((r) => data.bundle.audit.requirementIds.includes(r.id)), [data]);
  const statusOf = (id: string) => data.bundle.assessments.find((a) => a.requirementId === id)?.status || "unassessed";
  const visible = requirements.filter((item) => {
    const status = statusOf(item.id);
    if (filter === "todo" && status !== "unassessed") return false;
    if (filter === "findings" && !["minor", "major", "observation"].includes(status)) return false;
    if (filter === "done" && status === "unassessed") return false;
    const text = `${item.source.clause || ""} ${item.title || ""} ${item.text}`.toLowerCase();
    return !query || text.includes(query.toLowerCase());
  });
  const requirement = requirements.find((r) => r.id === selected) || visible[0] || requirements[0];
  const assessment = data.bundle.assessments.find((a) => a.requirementId === requirement?.id);
  const draft = requirement ? drafts[requirement.id] || { status: assessment?.status || "unassessed", rationale: assessment?.rationale || "", evidenceIds: assessment?.evidenceIds || [] } : null;
  const dirty = Object.keys(drafts).length > 0;
  useEffect(() => { const warn = (event: BeforeUnloadEvent) => { event.preventDefault(); }; if (dirty) window.addEventListener("beforeunload", warn); return () => window.removeEventListener("beforeunload", warn); }, [dirty]);
  function change(patch: Partial<AssessmentDraft>) { if (requirement && draft) setDrafts((previous) => ({ ...previous, [requirement.id]: { ...draft, ...patch } })); }
  async function save(event: FormEvent) {
    event.preventDefault(); if (!requirement || !draft) return;
    const saved = await command("assess", { requirementId: requirement.id, ...draft });
    if (saved) {
      setDrafts((previous) => { const next = { ...previous }; delete next[requirement.id]; return next; });
      const nextTodo = requirements.find((item, index) => index > requirements.indexOf(requirement) && statusOf(item.id) === "unassessed" && item.id !== requirement.id);
      if (nextTodo && assessment?.status === "unassessed") setSelected(nextTodo.id);
    }
  }
  if (!requirement || !draft) return <div className={s.card}><h2>No approved criteria in scope</h2><p className={s.subtitle}>Create and approve requirements in the Criteria tab.</p></div>;
  const position = requirements.indexOf(requirement);
  return <div className={s.split}>
    <div className={s.navPane}>
      <div className={s.navTools}><input className={s.search} type="search" value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Search A1, water, staff…" aria-label="Search criteria" /><select className={s.search} value={filter} onChange={(event) => setFilter(event.target.value as Filter)} aria-label="Filter criteria"><option value="all">All criteria</option><option value="todo">Not assessed</option><option value="findings">Findings & observations</option><option value="done">Assessed</option></select></div>
      <div className={s.criteriaNav}>{groupByCategory(visible).map(([category, items]) => <div key={category}><p className={s.groupLabel}><span>{category}</span><span>{items.filter((item) => statusOf(item.id) !== "unassessed").length}/{items.length}</span></p>{items.map((item) => { const status = drafts[item.id]?.status || statusOf(item.id); return <button className={s.criterion} key={item.id} aria-current={item.id === requirement.id} onClick={() => setSelected(item.id)}><span className={s.statusDot} data-tone={statusTone[status]} aria-hidden="true" /><span style={{ minWidth: 0 }}><strong>{criterionHeading(item)}</strong><em>{drafts[item.id] ? "Unsaved changes" : statusLabels[statusOf(item.id)]}{item.critical ? " · Critical" : ""}</em></span></button>; })}</div>)}{visible.length === 0 && <p className={s.small} style={{ padding: 12 }}>No criteria match this search.</p>}</div>
    </div>
    <div className={s.card}>
      <div className={s.cardHead}><div><p className={s.eyebrow}>{requirement.category || "Requirement"} · {position + 1} of {requirements.length}</p><h2 style={{ fontSize: 20 }}>{requirement.source.clause && requirement.title && <span className={s.code} style={{ fontSize: 13, marginRight: 10, verticalAlign: "3px" }}>{requirement.source.clause}</span>}{requirement.title || requirement.text}</h2></div><div className={s.toolbar}>{requirement.critical && <span className={s.pill} data-tone="amber">Critical</span>}<Pill status={assessment?.status || "unassessed"} /></div></div>
      <CriterionDetail requirement={requirement} />
      <hr className={s.rule} />
      <form onSubmit={save}><fieldset disabled={disabled} style={{ border: 0 }}><label className={s.field}>Assessment outcome<select value={draft.status} onChange={(event) => change({ status: event.target.value as AssessmentStatus })}><option value="unassessed" disabled>Choose an outcome</option>{(Object.keys(statusLabels) as AssessmentStatus[]).filter((status) => status !== "unassessed").map((status) => <option key={status} value={status}>{statusLabels[status]}</option>)}</select></label><label className={s.field}>Rationale<textarea value={draft.rationale} onChange={(event) => change({ rationale: event.target.value })} required minLength={data.bundle.config?.minRationaleLength || 20} maxLength={10000} placeholder="Which indicators did you verify, what did the evidence show, and which indicators do not apply here (and why)?" /><small>Explain exclusions when choosing Not applicable. Minor and major outcomes create findings.</small></label><EvidencePicker id={`assess-${requirement.id}`} evidence={data.bundle.evidence} selected={draft.evidenceIds} change={(evidenceIds) => change({ evidenceIds })} /><div className={s.toolbar}><button type="submit" className={s.button} disabled={draft.status === "unassessed"}>Save assessment</button><button type="button" className={s.secondary} onClick={goEvidence}>Add evidence</button><span style={{ flex: 1 }} /><button type="button" className={s.secondary} disabled={position <= 0} onClick={() => setSelected(requirements[position - 1]!.id)}>← Previous</button><button type="button" className={s.secondary} disabled={position >= requirements.length - 1} onClick={() => setSelected(requirements[position + 1]!.id)}>Next →</button></div></fieldset></form><p className={s.small} style={{ marginTop: 14 }}>{drafts[requirement.id] ? "Unsaved changes — save this assessment when ready. Your draft is kept while moving between criteria and tabs." : assessment?.assessedAt ? `Saved by ${assessment.assessedBy?.name} on ${dateTime(assessment.assessedAt)}` : "This criterion has not been assessed yet."}</p>
    </div>
  </div>;
}

function EvidencePanel({ evidence, editable, disabled, command, upload, download }: { evidence: Evidence[]; editable: boolean; disabled: boolean; command: Command; upload: (file: File, description: string) => Promise<boolean>; download: (evidence: Evidence) => Promise<void> }) {
  const [mode, setMode] = useState("upload");
  const [validation, setValidation] = useState("");
  async function add(event: FormEvent<HTMLFormElement>) {
    event.preventDefault(); const form = event.currentTarget; const values = new FormData(form); setValidation("");
    let saved = false;
    if (mode === "upload") {
      const file = values.get("file");
      if (!(file instanceof File) || !file.size) { setValidation("Choose a non-empty file to upload."); return; }
      if (file.size > 10 * 1024 * 1024) { setValidation("The file must be 10 MB or smaller."); return; }
      saved = await upload(file, String(values.get("description")).trim());
    } else saved = await command("evidence", { kind: String(values.get("kind")), description: String(values.get("description")).trim(), reference: String(values.get("reference")).trim() || undefined });
    if (saved) form.reset();
  }
  return <><div className={s.cardHead}><div><h2>Evidence register</h2><p className={s.muted}>Record evidence once, then link it to assessments and corrective actions.</p></div><span className={s.pill}>{evidence.length} records</span></div>
    {editable && <div className={s.card}><div className={s.toolbar} style={{ marginBottom: 20 }}><button className={mode === "upload" ? s.button : s.secondary} onClick={() => setMode("upload")}>Upload file</button><button className={mode === "note" ? s.button : s.secondary} onClick={() => setMode("note")}>Record evidence note</button></div>{validation && <p role="alert" className={s.error}>{validation}</p>}<form onSubmit={add}><fieldset disabled={disabled} style={{ border: 0 }}>{mode === "upload" ? <label className={s.field}>Evidence file<input name="file" type="file" required accept=".pdf,.png,.jpg,.jpeg,.txt,.csv" /><small>PDF, PNG, JPEG, TXT or CSV · maximum 10 MB. Files are private to your organisation.</small></label> : <div className={s.grid}><label className={s.field}>Evidence type<select name="kind"><option value="observation">Observation</option><option value="interview">Interview</option><option value="record">Record reference</option><option value="document">Document reference</option><option value="photo">Photo reference</option></select></label><label className={s.field}>Reference (optional)<input name="reference" maxLength={1000} placeholder="e.g. Water meter log, September, page 2" /></label></div>}<label className={s.field}>Description<textarea name="description" required minLength={10} maxLength={4000} placeholder="Describe what this shows, where it came from and when it was collected." /></label><button className={s.button} type="submit">{mode === "upload" ? "Upload and save evidence" : "Save evidence note"}</button></fieldset></form></div>}
    {evidence.length ? <div className={s.list}>{evidence.slice().reverse().map((item) => <article key={item.id} className={s.card} style={{ marginBottom: 0 }}><div className={s.cardHead}><div><span className={s.pill} data-tone="blue">{label(item.kind)}</span><h3 style={{ marginTop: 10, whiteSpace: "pre-wrap" }}>{item.description}</h3></div>{item.attachment && <button className={s.secondary} onClick={() => void download(item)}>Download file</button>}</div>{item.reference && <p className={s.muted}>Reference: {item.reference}</p>}{item.attachment && <p className={s.small}>{item.attachment.fileName} · {(item.attachment.sizeBytes / 1024).toFixed(1)} KB</p>}<p className={s.small} style={{ marginTop: 10 }}>Collected by {item.collectedBy.name} · {dateTime(item.collectedAt)}</p></article>)}</div> : <div className={`${s.card} ${s.empty}`}><h2>No evidence recorded yet</h2><p>Start with an observation, an interview or a supporting file.</p></div>}
  </>;
}
