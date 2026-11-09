"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { AlertTriangle, ArrowRight, CircleAlert, ClipboardCheck, ListChecks, ChevronRight } from "lucide-react";
import AppShell from "@/components/AppShell";
import { dashboard } from "@/lib/api";
import { AuditSummary, assessmentStatusLabel, assessmentStatusTone, dateTime, firstName, hospitality, Member } from "@/lib/hospitality";

interface Summary {
  overdue_actions: number;
  at_risk_actions: number;
  open_actions: number;
  active_audits: number;
}

const toneBadge: Record<string, string> = { green: "badge-green", amber: "badge-yellow", blue: "badge-blue" };

const steps = [
  { title: "Gather evidence", text: "Upload documents, photos and notes that show how the property meets each criterion." },
  { title: "Assess each criterion", text: "Check the performance indicators against your evidence and record an outcome." },
  { title: "Close the gaps", text: "Agree an action and an owner for every gap, then record what was done." },
  { title: "Confirm the actions", text: "A second person checks each completed action before it is closed." },
  { title: "Prepare the readiness report", text: "Download a report to take to a GSTC-accredited certification body." },
];

export default function DashboardPage() {
  const router = useRouter();
  const [data, setData] = useState<Summary | null>(null);
  const [assessments, setAssessments] = useState<AuditSummary[] | null>(null);
  const [me, setMe] = useState<Member | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!localStorage.getItem("axis_token")) { router.push("/login"); return; }
    hospitality.me().then((r) => setMe(r.data)).catch(() => setMe(null));
    hospitality.list().then((r) => setAssessments(r.data)).catch(() => setAssessments(null));
    dashboard.summary()
      .then((r) => setData(r.data))
      .catch((e) => {
        const status = e?.response?.status;
        if (status === 401) {
          localStorage.removeItem("axis_token");
          router.push("/login");
        } else if (status === 403) {
          setError("Your account can't open the overview yet. Ask your organisation admin for access.");
        } else if (status) {
          setError("AXIS couldn't load your overview. Refresh the page, or try again in a few minutes.");
        } else {
          setError("AXIS can't be reached right now. Check your connection, then refresh the page.");
        }
      })
      .finally(() => setLoading(false));
  }, []); // eslint-disable-line

  if (loading) return (
    <AppShell>
      <div style={{ display: "flex", alignItems: "center", justifyContent: "center", height: "50vh" }}>
        <div className="spinner" style={{ width: 26, height: 26 }} />
      </div>
    </AppShell>
  );

  if (error) return (
    <AppShell>
      <div className="alert-error">{error}</div>
    </AppShell>
  );

  if (!data) return null;

  const hour = new Date().getHours();
  const greeting = hour < 12 ? "Good morning" : hour < 18 ? "Good afternoon" : "Good evening";
  const sorted = (assessments || []).slice().sort((a, b) => b.updated_at.localeCompare(a.updated_at));
  const inProgress = sorted.filter((a) => a.status !== "complete");
  const next = inProgress[0] ?? null;
  const recent = sorted.slice(0, 5);

  const stats = [
    { label: "Open actions", hint: "Still to complete", value: data.open_actions, tone: "var(--accent)", Icon: ListChecks },
    { label: "Overdue", hint: "Past their due date", value: data.overdue_actions, tone: data.overdue_actions ? "var(--red)" : "var(--green)", Icon: CircleAlert },
    { label: "Due soon", hint: "Close to their due date", value: data.at_risk_actions, tone: data.at_risk_actions ? "var(--amber)" : "var(--green)", Icon: AlertTriangle },
    { label: "Active assessments", hint: "Not yet complete", value: data.active_audits, tone: "var(--accent-2)", Icon: ClipboardCheck },
  ];

  return (
    <AppShell>
      <header style={{ display: "flex", alignItems: "flex-end", justifyContent: "space-between", gap: 20, flexWrap: "wrap", marginBottom: 28 }}>
        <div>
          <div className="eyebrow">Overview</div>
          <h1 className="page-heading">{greeting}{me ? `, ${firstName(me.name)}` : ""}</h1>
          <p className="page-subheading">Here is where your property stands on sustainability readiness, and what needs doing next.</p>
        </div>
      </header>

      <section className="hero" aria-labelledby="next-step-title">
        <div style={{ minWidth: 0 }}>
          <p className="hero-eyebrow">{next ? "Next step" : "Get started"}</p>
          <h2 className="hero-title" id="next-step-title">{next ? next.title : "Start your first readiness assessment"}</h2>
          <p className="hero-text">
            {next
              ? `${next.site_name} · last saved ${dateTime(next.updated_at)}`
              : "Check your property against the GSTC Hotel Standard and see what stands between you and certification."}
          </p>
        </div>
        <Link href={next ? `/hospitality/${next.id}` : "/hospitality"} className="hero-btn">
          {next ? "Continue assessment" : "Open assessments"} <ArrowRight size={17} />
        </Link>
      </section>

      <div className="grid-4" style={{ margin: "22px 0 24px" }}>
        {stats.map(({ label, hint, value, tone, Icon }) => (
          <div key={label} className="stat-card" style={{ ["--tone" as string]: tone }}>
            <div className="stat-icon" style={{ background: `color-mix(in srgb, ${tone} 13%, transparent)`, color: tone }}>
              <Icon size={18} strokeWidth={2.1} />
            </div>
            <div className="stat-number">{value}</div>
            <div className="stat-label">{label}</div>
            <div className="stat-hint">{hint}</div>
          </div>
        ))}
      </div>

      <div className="overview-grid">
        <section className="card" aria-labelledby="assessments-title">
          <div className="card-header">
            <div>
              <h2 className="card-title" id="assessments-title">Your assessments</h2>
              <div className="card-subtitle">GSTC Hotel Standard v4.0 · 40 criteria</div>
            </div>
            <Link href="/hospitality" className="btn btn-ghost" style={{ padding: "7px 13px", fontSize: 13 }}>View all</Link>
          </div>
          {assessments === null ? (
            <div style={{ padding: "32px 24px", fontSize: 14, color: "var(--muted)" }}>Assessments are unavailable right now.</div>
          ) : recent.length === 0 ? (
            <div style={{ padding: "40px 24px", textAlign: "center" }}>
              <div style={{ fontFamily: "var(--font-head)", fontSize: 16, fontWeight: 700, color: "var(--text)" }}>No assessments yet</div>
              <p style={{ fontSize: 14, color: "var(--text-3)", margin: "6px 0 18px" }}>An assessment is the place to record your property&apos;s evidence, gaps and actions.</p>
              <Link href="/hospitality" className="btn btn-primary">Start an assessment</Link>
            </div>
          ) : recent.map((audit) => (
            <Link key={audit.id} href={`/hospitality/${audit.id}`} className="row-item">
              <div style={{ minWidth: 0 }}>
                <div style={{ fontSize: 15, fontWeight: 600, color: "var(--text)" }}>{audit.title}</div>
                <div style={{ fontSize: 13, color: "var(--muted)", marginTop: 3 }}>{audit.site_name} · saved {dateTime(audit.updated_at)}</div>
              </div>
              <div style={{ display: "flex", alignItems: "center", gap: 10, flexShrink: 0 }}>
                <span className={`badge ${toneBadge[assessmentStatusTone(audit.status)] || "badge-slate"}`}>{assessmentStatusLabel(audit.status)}</span>
                <ChevronRight size={16} color="var(--faint)" />
              </div>
            </Link>
          ))}
        </section>

        <section className="card" aria-labelledby="how-title">
          <div className="card-header">
            <div>
              <h2 className="card-title" id="how-title">How readiness works</h2>
              <div className="card-subtitle">Five steps from first check to report</div>
            </div>
          </div>
          <ol className="timeline">
            {steps.map((step, index) => (
              <li key={step.title}>
                <span className="timeline-num">{index + 1}</span>
                <div>
                  <strong>{step.title}</strong>
                  <p>{step.text}</p>
                </div>
              </li>
            ))}
          </ol>
          <p className="timeline-note">
            AXIS prepares your property for certification. Only GSTC-accredited certification bodies can certify it.
          </p>
        </section>
      </div>
    </AppShell>
  );
}
