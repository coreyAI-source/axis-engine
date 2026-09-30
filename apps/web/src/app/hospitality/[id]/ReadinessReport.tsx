"use client";

import { FormEvent, ReactNode, useEffect, useState } from "react";
import { Download, FileText, Printer, Sparkles } from "lucide-react";
import { dateTime, hospitality, ReadinessReport, ReadinessView, saveBlob } from "@/lib/hospitality";
import s from "../hospitality.module.css";

type Field = [key: string, label: string, kind?: "text" | "area", hint?: string];
const FIELD_GROUPS: [string, Field[]][] = [
  ["Cover and letter", [
    ["hotel_name", "Hotel name"], ["location", "Location"], ["hotel_contact_name", "Hotel contact name"], ["hotel_contact_role", "Hotel contact role"],
    ["review_date", "Review date"], ["report_date", "Report date"], ["report_reference", "Report reference", "text", "e.g. AXIS-BALI-2026-001, version 1.0"],
    ["reviewer", "Reviewer"], ["reviewer_contact", "Reviewer email · phone"], ["standard_edition", "Standard edition", "text", "Used in the notice, e.g. v4.0"],
    ["standard_used", "Standard used (cover)"], ["staff_present", "Hotel staff present (for the letter)", "text", "e.g. the General Manager and Chief Engineer"],
    ["purpose", "Purpose"], ["confidentiality", "Confidentiality", "area"],
  ]],
  ["Scope and method", [
    ["review_type", "Review type"], ["duration", "Duration"], ["method", "Method", "area"],
    ["people_interviewed", "People interviewed", "area", "One per line: Role | Name | Topics. Leave junior staff names out."],
    ["areas_inspected", "Areas inspected", "area", "One area per line."], ["areas_not_inspected", "Areas not inspected", "area", "One per line, with the reason."],
    ["plan_changes", "Changes to the review plan", "area", "Late documents and anything not sampled."],
  ]],
  ["Hotel profile and key figures", [
    ["hotel_type", "Type"], ["rooms", "Rooms"], ["staff", "Staff"], ["occupancy", "Occupancy, last 12 months"], ["water_sources", "Water sources"],
    ["wastewater", "Wastewater"], ["existing_certifications", "Existing certifications"], ["facilities", "Facilities", "area"],
    ["key_figures", "Key figures", "area", "One per line: Indicator | Total | Per occupied room night | Data status | What certification needs"],
  ]],
  ["Local legal requirements", [
    ["legal_items", "Legal items to confirm", "area", "One per line: Area | What to confirm | What we saw | Priority. The AI never adds laws; only what you enter here appears in section 6."],
  ]],
  ["Sign-off", [
    ["prepared_by", "Prepared by"], ["reviewed_by", "Reviewed by", "text", "Enter only after checking every statement. Removes the DRAFT banner; cleared when the narrative is regenerated."],
    ["issued_to", "Issued to"], ["next_step", "Next step"],
  ]],
];

function Table({ head, rows }: { head: string[]; rows: ReactNode[][] }) {
  return <div className={s.docTableWrap}><table className={s.docTable}><thead><tr>{head.map((h, i) => <th key={i}>{h}</th>)}</tr></thead><tbody>{rows.map((row, i) => <tr key={i}>{row.map((cell, j) => <td key={j}>{cell}</td>)}</tr>)}</tbody></table></div>;
}
const Pairs = ({ rows }: { rows: [string, string][] }) => <div className={s.docTableWrap}><table className={s.docTable}><tbody>{rows.map(([k, v]) => <tr key={k}><th scope="row">{k}</th><td>{v}</td></tr>)}</tbody></table></div>;
const Placeholder = ({ text }: { text: string }) => text.includes("[Reviewer to complete]") || /^\[.*\]$/.test(text) ? <mark className={s.docMark}>{text}</mark> : <>{text}</>;
const PRIORITY_TONE: Record<string, string> = { Critical: "red", Important: "amber", Improvement: "blue" };

export default function ReadinessPanel({ auditId, version, editable, fail }: { auditId: string; version: number; editable: boolean; fail: (error: unknown) => void }) {
  const [view, setView] = useState<ReadinessView | null>(null);
  const [busy, setBusy] = useState<"" | "load" | "save" | "generate" | "docx" | "markdown">("load");
  const [message, setMessage] = useState("");

  useEffect(() => {
    let alive = true;
    hospitality.readiness(auditId).then((response) => { if (alive) setView(response.data); }).catch((error) => { if (alive) fail(error); }).finally(() => { if (alive) setBusy(""); });
    return () => { alive = false; };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [auditId, version]);

  async function run(kind: typeof busy, task: () => Promise<void>) {
    setBusy(kind); setMessage("");
    try { await task(); } catch (error) { fail(error); } finally { setBusy(""); }
  }
  const save = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const values = Object.fromEntries([...new FormData(event.currentTarget).entries()].map(([k, v]) => [k, String(v).trim()]));
    void run("save", async () => { setView((await hospitality.saveReadinessProfile(auditId, values)).data); setMessage("Report details saved."); });
  };
  const generate = () => run("generate", async () => { setView((await hospitality.generateReadiness(auditId)).data); setMessage("AI draft generated. Review every section before issuing."); });
  const exportAs = (format: "docx" | "markdown") => run(format, async () => {
    const response = await hospitality.exportReadiness(auditId, format);
    saveBlob(response.data, `AXIS-readiness-review-${(view?.report.hotel || "hotel").replace(/[^A-Za-z0-9]+/g, "-")}.${format === "docx" ? "docx" : "md"}`);
  });

  if (!view) return <div className={`${s.card} ${s.empty}`}><p>{busy === "load" ? "Loading the readiness report…" : "The readiness report could not be loaded."}</p></div>;
  const r = view.report;
  const saved = { ...r.profile, ...view.saved_profile };

  return <>
    <div className={`${s.card} ${s.noPrint}`}>
      <div className={s.cardHead}>
        <div><h2>Sustainability Readiness Review</h2><p className={s.muted}>What this hotel must address to achieve GSTC certification. Statuses, counts and evidence IDs come straight from your assessments; AI drafts only the wording.</p></div>
        <div className={s.toolbar}>
          {editable && <button className={s.button} disabled={!!busy || !view.ai_configured} onClick={() => void generate()}><Sparkles size={15} />{busy === "generate" ? "Drafting… (up to 2 min)" : r.ai ? "Regenerate AI draft" : "Generate AI draft"}</button>}
          <button className={s.secondary} disabled={!!busy} onClick={() => void exportAs("docx")}><FileText size={15} />{busy === "docx" ? "Preparing…" : "Download Word"}</button>
          <button className={s.secondary} disabled={!!busy} onClick={() => void exportAs("markdown")}><Download size={15} />Markdown</button>
          <button className={s.secondary} onClick={() => window.print()}><Printer size={15} />Print / PDF</button>
        </div>
      </div>
      {message && <p role="status" className={s.success}>{message}</p>}
      {!view.ai_configured && <div className={s.notice}><strong>AI drafting is off</strong>Add <code>OPENROUTER_API_KEY=…</code> to <code>services/api/.env</code> and restart the API to enable it. The report below still works: sections needing wording are highlighted for you to write.</div>}
      {r.ai && <p className={s.small}>AI draft by {r.ai.generated_by} · {dateTime(r.ai.generated_at)} · model {r.ai.model}</p>}
      {r.ai?.stale && <p className={s.error} style={{ marginTop: 12 }}>The audit has changed since this draft was generated. Regenerate it, or check the wording against the current assessments.</p>}
      {r.review_notes.length > 0 && <><h3 style={{ marginTop: 16 }}>Before issuing</h3><ul className={s.bulletList}>{r.review_notes.map((note) => <li key={note}>{note}</li>)}</ul></>}
      <details className={s.details}>
        <summary>Report details (cover, interviews, hotel profile, legal items, sign-off)</summary>
        <form onSubmit={save}><fieldset disabled={!editable || !!busy} style={{ border: 0 }}>
          {FIELD_GROUPS.map(([group, fields]) => <div key={group}><p className={s.sectionTitle}>{group}</p><div className={s.grid}>{fields.map(([key, labelText, kind, hint]) =>
            <label className={s.field} key={key} style={kind === "area" ? { gridColumn: "1 / -1" } : undefined}>{labelText}
              {kind === "area" ? <textarea name={key} defaultValue={saved[key] || ""} maxLength={8000} /> : <input name={key} defaultValue={saved[key] || ""} maxLength={500} />}
              {hint && <small>{hint}</small>}</label>)}</div></div>)}
          {editable && <button className={s.button} type="submit">{busy === "save" ? "Saving…" : "Save report details"}</button>}
        </fieldset></form>
      </details>
    </div>
    <ReadinessDocument r={r} />
  </>;
}

function ReadinessDocument({ r }: { r: ReadinessReport }) {
  const sm = r.summary;
  return <article className={s.paper} aria-label="Readiness review document">
    {r.draft && <p className={s.docDraft}>DRAFT — not reviewed.{r.ai ? " Narrative drafted with AI assistance from the audit record." : ""} Check every statement against the evidence before issue.</p>}
    <h1>{r.title}</h1>
    <Pairs rows={r.cover} />

    <h2>Covering letter</h2>
    <p>{r.letter.salutation}</p>
    {r.letter.paragraphs.map((p, i) => <p key={i}><Placeholder text={p} /></p>)}
    <p>{r.letter.signoff.filter(Boolean).map((line, i) => <span key={i}>{line}<br /></span>)}</p>

    <h2>1. Important notice</h2>
    {r.notice.map((p) => <p key={p}>{p}</p>)}

    <h2>2. Summary of results</h2>
    <p>{sm.statement} {sm.readiness_statement}</p>
    <Table head={["Pillar", "Readiness", "Met", "Partly met", "Not met", "Not evidenced", "Not sampled", "Headline"]}
      rows={sm.pillars.map((p) => [`${p.code}. ${p.name}`, p.level, p.counts["Met"], p.counts["Partly met"], p.counts["Not met"], p.counts["Not evidenced"], p.counts["Not sampled"], <Placeholder key="h" text={p.headline} />])} />
    {sm.strengths.length > 0 && <><h4>Main strengths</h4><ul>{sm.strengths.map((x) => <li key={x.text}>{x.text} <em>({x.evidence})</em></li>)}</ul></>}
    {sm.top_gaps.length > 0 && <><h4>Top gaps to close before a certification audit</h4><ol>{sm.top_gaps.map((g) => <li key={g.criterion + g.text}><Placeholder text={g.text} /> ({g.criterion})</li>)}</ol></>}
    {sm.limitations && <p><strong>What one day could not establish.</strong> {sm.limitations}</p>}

    <h2>3. Scope and method</h2>
    <p><strong>How GSTC certification works.</strong> {r.scope.certification_works}</p>
    <Pairs rows={r.scope.table} />
    {r.scope.people.length > 0 && <><h4>People interviewed</h4><Table head={["Role", "Name", "Topics"]} rows={r.scope.people} /></>}
    {(r.scope.areas_inspected.length > 0 || r.scope.areas_not_inspected.length > 0) && <><h4>Areas inspected</h4><ul className={s.docChecks}>{r.scope.areas_inspected.map((a) => <li key={a}>☒ {a}</li>)}{r.scope.areas_not_inspected.map((a) => <li key={a}>☐ {a} — not inspected</li>)}</ul></>}
    <h4>How findings are rated</h4>
    <Table head={["Status", "Meaning"]} rows={r.scope.status_meanings} />
    <Table head={["Priority", "Meaning for certification"]} rows={r.scope.priority_meanings} />
    {r.scope.method_notes.map((n) => <p key={n}>{n}</p>)}
    <p><strong>Changes to the review plan.</strong> {r.scope.plan_changes}</p>

    <h2>4. Hotel profile and key figures</h2>
    {r.hotel_profile.length ? <Pairs rows={r.hotel_profile} /> : <p><mark className={s.docMark}>Add the hotel profile in Report details.</mark></p>}
    {r.key_figures.length > 0 && <Table head={["Indicator (last 12 months)", "Total", "Per occupied room night", "Data status", "What certification needs"]} rows={r.key_figures} />}

    <h2>5. Gap analysis: what to address for certification</h2>
    <p>For each criterion, the “Gap to close” column says what must exist on the day of a certification audit. Gaps marked Critical are the ones most likely to stop certification. Appendix C records a status for every criterion.</p>
    {r.gaps.map((p) => <section key={p.code}>
      <h3>{p.code}. {p.name}</h3>
      {(p.in_place || p.missing) && <p>{p.in_place && <><strong>In place:</strong> {p.in_place} </>}{p.missing && <><strong>Missing:</strong> {p.missing}</>}</p>}
      {p.rows.length ? <Table head={["Code", "Criterion", "Status", "Evidence seen", "Gap to close", "Priority"]}
        rows={p.rows.map((x) => [<strong key="c">{x.code}</strong>, x.title, x.status, x.evidence_seen, <Placeholder key="g" text={x.gap} />, x.priority ? <span key="p" className={s.pill} data-tone={PRIORITY_TONE[x.priority]}>{x.priority}</span> : "—"])} /> : <p className={s.docMuted}>No gaps recorded in this pillar.</p>}
    </section>)}

    <h2>6. Local legal requirements an auditor will check</h2>
    <p>GSTC criterion A2 requires the hotel to know and comply with every law that applies to it. AXIS does not make legal compliance determinations: the hotel should confirm each item with the relevant authority or its own adviser.</p>
    {r.legal.length ? <Table head={["Area", "What to confirm", "What we saw", "Priority"]} rows={r.legal} /> : <p><mark className={s.docMark}>Add local legal items in Report details.</mark></p>}

    <h2>7. Certification action plan</h2>
    <p>Close all Critical gaps first, then build up the records an auditor will want to see. Ask your chosen certification body how many months of records it expects.</p>
    {([["Months 1–3: close the Critical gaps", r.plan.phase1], ["Months 4–6: build the evidence", r.plan.phase2]] as const).map(([title, items]) => <div key={title}>
      <h4>{title}</h4>
      {items.length ? <Table head={["#", "Action", "Criterion", "Owner", "Evidence the auditor will want"]} rows={items.map((a) => [a.number, <Placeholder key="a" text={a.action} />, a.criteria.join(", "), <Placeholder key="o" text={a.owner} />, <Placeholder key="e" text={a.evidence} />])} /> : <p className={s.docMuted}>None.</p>}
    </div>)}
    <p><em>{r.plan.closure_note}</em></p>
    {r.assigned_actions.length > 0 && <><h4>Corrective actions already assigned in AXIS</h4><Table head={["Criterion", "Action", "Owner", "Due", "Status"]} rows={r.assigned_actions.map((a) => [a.criterion, a.description, a.owner, a.due, a.status])} /></>}
    <h4>Month 6: check readiness, then book</h4>
    <ul className={s.docChecks}><li>☐ AXIS follow-up review against the same criteria</li><li>☐ Choose a GSTC-accredited certification body and request a quote (section 8)</li><li>☐ Book the certification audit once no Critical gaps remain</li></ul>

    <h2>8. Route to GSTC certification</h2>
    <p>Once the Critical gaps are closed, the hotel chooses a GSTC-accredited certification body, which audits it and issues the certificate. AXIS cannot certify the hotel and has no commercial link with any certification body.</p>
    <ol>{r.route.steps.map((step) => <li key={step}>{step}</li>)}</ol>
    <h4>Questions to ask each certification body</h4>
    <ul className={s.docChecks}>{r.route.questions.map((q) => <li key={q}>☐ {q}</li>)}</ul>
    <p>{r.route.schemes}</p>

    <h2>Appendix A: Evidence register</h2>
    {r.evidence_register.length ? <Table head={["ID", "Evidence", "Criterion", "Type", "Reference", "Date"]} rows={r.evidence_register.map((e) => [e.id, e.description, e.criteria, e.kind, e.reference, e.date])} /> : <p className={s.docMuted}>No documents or interviews recorded.</p>}
    <h2>Appendix B: Observation and photo log</h2>
    {r.observations.length ? <Table head={["ID", "What was observed", "Criterion", "Type", "Reference"]} rows={r.observations.map((e) => [e.id, e.description, e.criteria, e.kind, e.reference])} /> : <p className={s.docMuted}>No observations or photos recorded.</p>}
    <h2>Appendix C: Criterion coverage register</h2>
    <Table head={["Code", "Criterion", "Status", "Action (section 7)"]} rows={r.coverage.map((c) => [c.code, c.title, c.status, c.actions])} />

    <h2>Sign-off</h2>
    <Pairs rows={r.signoff} />
    {r.disclaimer && <p className={s.docMuted}><em>{r.disclaimer}</em></p>}
  </article>;
}
