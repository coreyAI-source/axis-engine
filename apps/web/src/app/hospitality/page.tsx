"use client";

import { FormEvent, useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { ChevronRight } from "lucide-react";
import AppShell from "@/components/AppShell";
import { apiError, AuditSummary, canAudit, dateTime, hospitality, httpStatus, label, Member } from "@/lib/hospitality";
import s from "./hospitality.module.css";

export default function HospitalityPage() {
  const router = useRouter();
  const [audits, setAudits] = useState<AuditSummary[]>([]);
  const [me, setMe] = useState<Member | null>(null);
  const [members, setMembers] = useState<Member[]>([]);
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const [showCreate, setShowCreate] = useState(false);
  const [search, setSearch] = useState("");

  function fail(error: unknown) {
    if (httpStatus(error) === 401) { localStorage.removeItem("axis_token"); router.replace("/login"); return; }
    setError(apiError(error));
  }
  async function load() {
    setLoading(true); setError("");
    try {
      const [mine, list, team] = await Promise.all([hospitality.me(), hospitality.list(), hospitality.members()]);
      setMe(mine.data); setAudits(list.data); setMembers(team.data);
    } catch (error) { fail(error); } finally { setLoading(false); }
  }
  useEffect(() => { if (!localStorage.getItem("axis_token")) router.replace("/login"); else void load(); /* eslint-disable-next-line react-hooks/exhaustive-deps */ }, []);

  async function create(event: FormEvent<HTMLFormElement>) {
    event.preventDefault(); const values = new FormData(event.currentTarget); setBusy(true); setError("");
    try {
      const response = await hospitality.create({ title: String(values.get("title")).trim(), site_name: String(values.get("site")).trim(), scope_statement: String(values.get("scope")).trim() });
      router.push(`/hospitality/${response.data.id}`);
    } catch (error) { fail(error); setBusy(false); }
  }
  async function addMember(event: FormEvent<HTMLFormElement>) {
    event.preventDefault(); const form = event.currentTarget; const values = new FormData(form); setBusy(true); setError(""); setMessage("");
    try {
      const response = await hospitality.addMember({ first_name: String(values.get("first")).trim(), last_name: String(values.get("last")).trim(), email: String(values.get("email")).trim(), password: String(values.get("password")), role_code: String(values.get("role")) });
      setMembers((previous) => [...previous, response.data]); form.reset(); setMessage(`Account created for ${response.data.name}. They can sign in with the email and password you entered.`);
    } catch (error) { fail(error); } finally { setBusy(false); }
  }
  const filtered = audits.filter((audit) => `${audit.title} ${audit.site_name}`.toLowerCase().includes(search.toLowerCase()));

  const statusTone: Record<string, string> = { complete: "green", reporting: "amber", in_progress: "blue" };

  return <div className={s.page}><AppShell>
    <header className={s.header}>
      <div><p className={s.eyebrow}>Hotel sustainability · GSTC Hotel Standard v4.0</p><h1 className={s.title}>Hotel audits</h1><p className={s.subtitle}>From evidence to a reviewed hotel audit against all 40 GSTC criteria and their performance indicators.</p></div>
      {canAudit(me) && <button className={showCreate ? s.secondary : s.button} onClick={() => setShowCreate(!showCreate)} aria-expanded={showCreate}>{showCreate ? "Cancel" : "+ New hotel audit"}</button>}
    </header>
    {error && <div role="alert" className={s.error}>{error} <button className={s.secondary} onClick={() => void load()} disabled={loading}>Retry connection</button></div>}
    {message && <p role="status" className={s.success}>{message}</p>}
    {showCreate && <section className={s.card} aria-labelledby="new-audit-title"><div className={s.cardHead}><div><h2 id="new-audit-title">Start a hotel audit</h2><p className={s.muted}>The audit starts with all 40 GSTC Hotel Standard v4.0 criteria. Your changes are saved to your organisation.</p></div></div>
      <form onSubmit={create}><fieldset disabled={busy} style={{ border: 0 }}>
        <div className={s.grid}><label className={s.field}>Hotel name<input name="site" required maxLength={200} placeholder="e.g. Bali Practice Hotel" autoFocus /></label><label className={s.field}>Audit title<input name="title" required maxLength={200} placeholder="e.g. 2026 GSTC readiness assessment" /></label></div>
        <label className={s.field}>Scope and boundaries<textarea name="scope" maxLength={4000} placeholder="Which buildings, operations (rooms, F&B, spa, grounds) and time period are included? Note anything excluded, such as no construction underway." /></label>
        <div className={s.toolbar}><button className={s.button} type="submit">{busy ? "Creating audit…" : "Create audit"}</button><span className={s.small}>Criteria that don’t apply to this property are marked Not applicable during assessment.</span></div>
      </fieldset></form>
    </section>}
    <div className={s.stats}><div className={s.stat}><strong>{audits.length}</strong><span>Hotel audits</span></div><div className={s.stat} style={{ ["--tone" as string]: "var(--blue)" }}><strong>{audits.filter((a) => a.status === "in_progress").length}</strong><span>In progress</span></div><div className={s.stat} style={{ ["--tone" as string]: "var(--amber)" }}><strong>{audits.filter((a) => a.status === "reporting").length}</strong><span>In reporting</span></div><div className={s.stat} style={{ ["--tone" as string]: "var(--green)" }}><strong>{audits.filter((a) => a.status === "complete").length}</strong><span>Reports completed</span></div></div>
    <section aria-labelledby="audits-title"><div className={s.cardHead}><div><h2 id="audits-title" style={{ fontSize: 17 }}>Your hotel audits</h2><p className={s.small}>{me ? `Signed in as ${me.name} · ${label(me.role_code)}` : "Loading your account…"}</p></div><input className={s.search} style={{ maxWidth: 300 }} type="search" value={search} onChange={(e) => setSearch(e.target.value)} placeholder="Search hotel or audit title" aria-label="Search audits" /></div>
      {loading ? <p role="status" className={s.empty}>Loading hotel audits…</p> : filtered.length ? <div className={s.list}>{filtered.map((audit) => <Link key={audit.id} className={s.auditLink} href={`/hospitality/${audit.id}`}><div><p className={s.eyebrow}>{audit.site_name}</p><h3>{audit.title}</h3><p className={s.small}>Saved {dateTime(audit.updated_at)} · version {audit.version}</p></div><div className={s.toolbar}><span className={s.pill} data-tone={statusTone[audit.status]}>{label(audit.status)}</span><ChevronRight size={18} className={s.arrow} aria-hidden="true" /></div></Link>)}</div> : <div className={`${s.card} ${s.empty}`}><h2>{search ? "No matching audits" : "Your first hotel audit starts here"}</h2><p>{search ? "Try another hotel name or title." : "Create an audit, attach evidence and work through the GSTC criteria one by one."}</p>{canAudit(me) && !search && <button className={s.button} onClick={() => setShowCreate(true)}>Create your first audit</button>}</div>}
    </section>
    {me?.role_code === "admin" && <section className={s.card} style={{ marginTop: 28 }}><details><summary style={{ cursor: "pointer", fontWeight: 600 }}>Team accounts · {members.length} members</summary><p className={s.subtitle}>Give each person their own account. The person verifying an action must be different from its owner and the person who submitted it.</p>
      <div className={s.list} style={{ margin: "18px 0", gap: 8 }}>{members.map((member) => <div key={member.id} className={s.team}><strong style={{ fontSize: 13 }}>{member.name}</strong><span className={s.small}>{member.email}</span><span className={s.pill} data-tone="blue">{label(member.role_code)}</span></div>)}</div>
      <h3 style={{ marginBottom: 16 }}>Add a team account</h3><form onSubmit={addMember}><fieldset disabled={busy} style={{ border: 0 }}><div className={s.grid}><label className={s.field}>First name<input name="first" required maxLength={100} /></label><label className={s.field}>Last name<input name="last" required maxLength={100} /></label><label className={s.field}>Email<input type="email" name="email" required autoComplete="off" /></label><label className={s.field}>Password<input type="password" name="password" required minLength={12} maxLength={72} autoComplete="new-password" /><small>At least 12 characters. Share securely with the account owner.</small></label></div><label className={s.field}>Role<select name="role" defaultValue="lead_auditor"><option value="lead_auditor">Lead auditor — review criteria and verify actions</option><option value="auditor">Auditor — assess criteria and manage audits</option><option value="process_owner">Process owner — work on assigned actions</option><option value="viewer">Viewer — read audits and reports</option><option value="compliance_manager">Compliance manager — review and manage audits</option></select></label><button className={s.button} type="submit">{busy ? "Saving…" : "Create team account"}</button></fieldset></form>
    </details></section>}
  </AppShell></div>;
}
