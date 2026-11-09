"use client";

import { FormEvent, useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { ArrowRight, ClipboardCheck, Plus, Search } from "lucide-react";
import AppShell from "@/components/AppShell";
import { apiError, AuditSummary, assessmentStatusLabel, canAudit, dateTime, EXAMPLE_FRAMEWORK_ID, Framework, hospitality, httpStatus, Member } from "@/lib/hospitality";
import s from "./hospitality.module.css";

const statusTone: Record<string, string> = { complete: "green", reporting: "amber", in_progress: "blue" };

export default function HospitalityPage() {
  const router = useRouter();
  const [audits, setAudits] = useState<AuditSummary[]>([]);
  const [me, setMe] = useState<Member | null>(null);
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [showCreate, setShowCreate] = useState(false);
  const [search, setSearch] = useState("");
  const [frameworks, setFrameworks] = useState<Framework[]>([]);
  const [framework, setFramework] = useState("");

  function fail(error: unknown) {
    if (httpStatus(error) === 401) { localStorage.removeItem("axis_token"); router.replace("/login"); return; }
    setError(apiError(error));
  }
  async function load() {
    setLoading(true); setError("");
    try {
      const [mine, list, available] = await Promise.all([hospitality.me(), hospitality.list(), hospitality.frameworks()]);
      setMe(mine.data); setAudits(list.data);
      setFrameworks(available.data); setFramework((current) => current || available.data[0]?.id || "");
    } catch (error) { fail(error); } finally { setLoading(false); }
  }
  useEffect(() => { if (!localStorage.getItem("axis_token")) router.replace("/login"); else void load(); /* eslint-disable-next-line react-hooks/exhaustive-deps */ }, []);

  async function create(event: FormEvent<HTMLFormElement>) {
    event.preventDefault(); const values = new FormData(event.currentTarget); setBusy(true); setError("");
    try {
      const response = await hospitality.create({ title: String(values.get("title")).trim(), site_name: String(values.get("site")).trim(), scope_statement: String(values.get("scope")).trim(), framework_id: framework || undefined });
      router.push(`/hospitality/${response.data.id}`);
    } catch (error) { fail(error); setBusy(false); }
  }

  const filtered = audits.filter((audit) => `${audit.title} ${audit.site_name}`.toLowerCase().includes(search.toLowerCase()));
  const count = (status: string) => audits.filter((audit) => audit.status === status).length;

  return <div className={s.page}><AppShell>
    <header className={s.header}>
      <div>
        <p className={s.eyebrow}>Sustainable hospitality</p>
        <h1 className={s.title}>Assessments</h1>
        <p className={s.subtitle}>Check a property against a recognised standard, keep the evidence in one place and track the actions that prepare it for certification.</p>
      </div>
      {canAudit(me) && (
        <button className={showCreate ? s.secondary : s.button} onClick={() => setShowCreate(!showCreate)} aria-expanded={showCreate}>
          {showCreate ? "Cancel" : <><Plus size={16} aria-hidden="true" /> New assessment</>}
        </button>
      )}
    </header>

    {error && <div role="alert" className={s.error}>{error} <button className={s.secondary} onClick={() => void load()} disabled={loading}>Try again</button></div>}

    {showCreate && (
      <section className={s.card} aria-labelledby="new-audit-title">
        <div className={s.cardHead}>
          <div>
            <h2 id="new-audit-title">Start a new assessment</h2>
            <p className={s.muted} style={{ marginTop: 4 }}>Name the property, choose the standard and describe what the assessment covers. Everything is saved to your organisation.</p>
          </div>
        </div>
        <form onSubmit={create}>
          <fieldset disabled={busy} style={{ border: 0, minWidth: 0 }}>
            <div className={s.grid}>
              <label className={s.field}>Property name<input name="site" required maxLength={200} placeholder="e.g. Bali Practice Hotel" autoFocus /></label>
              <label className={s.field}>Assessment name<input name="title" required maxLength={200} placeholder="e.g. 2026 GSTC readiness assessment" /></label>
            </div>
            <fieldset className={s.choiceGroup}>
              <legend>Standard</legend>
              <div className={s.choiceList}>
                {frameworks.map((item) => (
                  <label key={item.id} className={s.choice} data-selected={framework === item.id} htmlFor={`framework-${item.id}`}>
                    <input id={`framework-${item.id}`} type="radio" name="framework" value={item.id} checked={framework === item.id} onChange={() => setFramework(item.id)} />
                    <span className={s.choiceBody}>
                      <strong>{item.label}</strong>
                      <small>{item.id === EXAMPLE_FRAMEWORK_ID
                        ? "A demonstration checklist for training. It is not GSTC criteria and not a certification standard."
                        : "The GSTC criteria for hotels, with performance indicators and guidance for each one."}</small>
                    </span>
                  </label>
                ))}
              </div>
            </fieldset>
            <label className={s.field}>
              Scope
              <textarea name="scope" maxLength={4000} placeholder="Which buildings, areas and operations are included (rooms, food and beverage, spa, grounds), and over what period? Note anything left out, such as works that are not underway." />
              <small>Criteria that do not apply to this property can be marked Not applicable, with a reason, during the assessment.</small>
            </label>
            <div className={s.toolbar}>
              <button className={s.button} type="submit">{busy ? "Creating…" : "Create assessment"}</button>
            </div>
          </fieldset>
        </form>
      </section>
    )}

    <div className={s.stats}>
      <div className={s.stat}><strong>{audits.length}</strong><span>All assessments</span></div>
      <div className={s.stat} style={{ ["--tone" as string]: "var(--accent)" }}><strong>{count("in_progress")}</strong><span>In progress</span></div>
      <div className={s.stat} style={{ ["--tone" as string]: "var(--amber)" }}><strong>{count("reporting")}</strong><span>Preparing report</span></div>
      <div className={s.stat} style={{ ["--tone" as string]: "var(--green)" }}><strong>{count("complete")}</strong><span>Complete</span></div>
    </div>

    <section aria-labelledby="audits-title">
      <div className={s.cardHead} style={{ alignItems: "center" }}>
        <div>
          <h2 id="audits-title" style={{ fontSize: 18 }}>Your assessments</h2>
          <p className={s.small} style={{ marginTop: 3 }}>{me ? `Signed in as ${me.name}` : "Loading your account…"}</p>
        </div>
        <div className={s.searchWrap}>
          <Search size={15} aria-hidden="true" />
          <input className={s.search} type="search" value={search} onChange={(e) => setSearch(e.target.value)} placeholder="Search by property or name" aria-label="Search assessments" />
        </div>
      </div>

      {loading ? <p role="status" className={s.empty}>Loading assessments…</p> : filtered.length ? (
        <div className={s.list}>
          {filtered.map((audit) => (
            <Link key={audit.id} className={s.auditLink} href={`/hospitality/${audit.id}`}>
              <div style={{ minWidth: 0 }}>
                <p className={s.eyebrow} style={{ marginBottom: 6 }}>{audit.site_name}</p>
                <h3>{audit.title}</h3>
                <p className={s.small}>{audit.framework ? `${audit.framework} · ` : ""}Saved {dateTime(audit.updated_at)}</p>
              </div>
              <div className={s.toolbar} style={{ flexShrink: 0 }}>
                <span className={s.pill} data-tone={statusTone[audit.status]}>{assessmentStatusLabel(audit.status)}</span>
                <ArrowRight size={18} className={s.arrow} aria-hidden="true" />
              </div>
            </Link>
          ))}
        </div>
      ) : (
        <div className={`${s.card} ${s.empty}`}>
          <ClipboardCheck size={34} strokeWidth={1.6} color="var(--accent)" style={{ margin: "0 auto 14px" }} aria-hidden="true" />
          <h2>{search ? "No matching assessments" : "Start your first assessment"}</h2>
          <p>{search ? "Try another property or assessment name." : "Choose the standard, add the property, then work through each criterion with the evidence that supports it."}</p>
          {canAudit(me) && !search && <button className={s.button} onClick={() => setShowCreate(true)}>Create an assessment</button>}
        </div>
      )}
    </section>
  </AppShell></div>;
}
