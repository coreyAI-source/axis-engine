"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { AlertTriangle, CalendarClock, ChevronRight, CircleAlert, ClipboardCheck, FileText, Hotel } from "lucide-react";
import AppShell from "@/components/AppShell";
import { dashboard } from "@/lib/api";
import { AuditSummary, dateTime, hospitality, label } from "@/lib/hospitality";

interface Summary {
  overdue_actions: number;
  at_risk_actions: number;
  open_actions: number;
  due_monitoring_tasks: number;
  active_audits: number;
  findings_by_type: Record<string, number>;
}

export default function DashboardPage() {
  const router = useRouter();
  const [data, setData] = useState<Summary | null>(null);
  const [hotels, setHotels] = useState<AuditSummary[] | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!localStorage.getItem("axis_token")) { router.push("/login"); return; }
    hospitality.list().then((r) => setHotels(r.data)).catch(() => setHotels(null));
    dashboard.summary()
      .then((r) => setData(r.data))
      .catch((e) => {
        const status = e?.response?.status;
        if (status === 401) {
          localStorage.removeItem("axis_token");
          router.push("/login");
        } else if (status === 403) {
          setError("Your account does not have permission to view the dashboard.");
        } else if (status >= 500) {
          setError("The API is running, but could not load the dashboard. Check the API terminal for the server error, then refresh.");
        } else if (status) {
          setError(`The dashboard request failed (HTTP ${status}). Please refresh and try again.`);
        } else {
          setError("Could not connect to the API. Check that it is running and that the website's API address is correct.");
        }
      })
      .finally(() => setLoading(false));
  }, []); // eslint-disable-line

  const hour = new Date().getHours();
  const greeting = hour < 12 ? "Good morning" : hour < 18 ? "Good afternoon" : "Good evening";

  if (loading) return (
    <AppShell>
      <div style={{ display:"flex", alignItems:"center", justifyContent:"center", height:"50vh" }}>
        <div className="spinner" style={{ width:24, height:24 }} />
      </div>
    </AppShell>
  );

  if (error) return (
    <AppShell>
      <div className="alert-error">{error}</div>
    </AppShell>
  );

  if (!data) return null;

  const stats = [
    { label:"Overdue actions", value:data.overdue_actions,      tone:"var(--red)",    Icon:CircleAlert },
    { label:"At-risk actions", value:data.at_risk_actions,      tone:"var(--orange)", Icon:AlertTriangle },
    { label:"Open actions",    value:data.open_actions,         tone:"var(--blue)",   Icon:FileText },
    { label:"Monitoring due",  value:data.due_monitoring_tasks, tone:"var(--amber)",  Icon:CalendarClock, href:"/monitoring" },
    { label:"Active audits",   value:data.active_audits,        tone:"var(--green)",  Icon:ClipboardCheck },
  ];
  const recentHotels = (hotels || []).slice().sort((a, b) => b.updated_at.localeCompare(a.updated_at)).slice(0, 4);
  const hotelTone: Record<string, string> = { complete: "badge-green", reporting: "badge-yellow", in_progress: "badge-blue" };

  return (
    <AppShell>
      <div style={{ marginBottom:28 }}>
        <div className="eyebrow">Compliance overview</div>
        <div className="page-heading">{greeting}</div>
        <div className="page-subheading">Here&apos;s where your audits, actions and monitoring stand today.</div>
      </div>

      <div className="grid-5" style={{ marginBottom:18 }}>
        {stats.map(({ label: name, value, tone, Icon, href }) => {
          const card = (
            <div className="stat-card" style={{ ["--tone" as string]: tone }}>
              <div className="stat-icon" style={{ background:`color-mix(in srgb, ${tone} 14%, transparent)`, color:tone }}><Icon size={17} strokeWidth={2.1} /></div>
              <div className="stat-number">{value}</div>
              <div className="stat-label">{name}</div>
            </div>
          );
          return href
            ? <Link key={name} href={href} style={{ display:"block" }}>{card}</Link>
            : <div key={name}>{card}</div>;
        })}
      </div>

      <div className="grid-2">
        <div className="card">
          <div className="card-header">
            <div style={{ display:"flex", alignItems:"center", gap:10 }}>
              <div className="stat-icon" style={{ margin:0, background:"var(--accent-soft)", color:"var(--accent)" }}><Hotel size={17} /></div>
              <div>
                <div className="card-title">Hotel audits</div>
                <div className="card-subtitle">GSTC Hotel Standard v4.0 · 40 criteria</div>
              </div>
            </div>
            <Link href="/hospitality" className="btn btn-ghost" style={{ padding:"6px 12px", fontSize:12 }}>Open</Link>
          </div>
          <div style={{ padding:"6px 10px 10px" }}>
            {hotels === null ? (
              <div style={{ padding:"28px 12px", textAlign:"center", fontSize:13, color:"var(--muted)" }}>Hotel audits are unavailable for this account.</div>
            ) : recentHotels.length === 0 ? (
              <div style={{ padding:"28px 12px", textAlign:"center" }}>
                <div style={{ fontSize:13, color:"var(--text-3)" }}>No hotel audits yet</div>
                <Link href="/hospitality" className="btn btn-primary" style={{ marginTop:14 }}>Start a hotel audit</Link>
              </div>
            ) : recentHotels.map((audit) => (
              <Link key={audit.id} href={`/hospitality/${audit.id}`} className="row-item" style={{ borderRadius:10 }}>
                <div style={{ minWidth:0 }}>
                  <div style={{ fontSize:13.5, fontWeight:550, color:"var(--text)" }}>{audit.title}</div>
                  <div style={{ fontSize:12, color:"var(--muted)", marginTop:2 }}>{audit.site_name} · saved {dateTime(audit.updated_at)}</div>
                </div>
                <span className={`badge ${hotelTone[audit.status] || "badge-slate"}`}>{label(audit.status)}</span>
              </Link>
            ))}
          </div>
        </div>

        <div className="card">
          <div className="card-header">
            <div>
              <div className="card-title">ISO findings by type</div>
              <div className="card-subtitle">From completed ISO audits</div>
            </div>
          </div>
          <div style={{ padding:"4px 0 8px" }}>
            {Object.keys(data.findings_by_type).length === 0 ? (
              <div style={{ padding:"32px 20px", textAlign:"center" }}>
                <div style={{ fontSize:13, color:"var(--text-3)" }}>No findings recorded yet</div>
                <div style={{ fontSize:12, color:"var(--muted)", marginTop:4 }}>Complete an audit to generate findings</div>
              </div>
            ) : Object.entries(data.findings_by_type).map(([type, count]) => (
              <div key={type} className="hover-row" style={{ display:"flex", justifyContent:"space-between", alignItems:"center", padding:"10px 20px", borderBottom:"1px solid var(--border-soft)" }}>
                <span style={{ fontSize:13, color:"var(--text-2)" }}>{type}</span>
                <span className="badge badge-slate">{count}</span>
              </div>
            ))}
          </div>
          <div style={{ padding:"4px 10px 10px", borderTop:"1px solid var(--border-soft)" }}>
            {[
              { href:"/processes", label:"Browse ISO processes", sub:"Clause mappings across ISO 9001, 14001 and 45001" },
              { href:"/monitoring", label:"Monitoring tasks", sub:"Scheduled and overdue compliance checks" },
            ].map((l) => (
              <Link key={l.href} href={l.href} className="row-item" style={{ borderRadius:10 }}>
                <div>
                  <div style={{ fontSize:13, fontWeight:550, color:"var(--text)" }}>{l.label}</div>
                  <div style={{ fontSize:12, color:"var(--muted)", marginTop:2 }}>{l.sub}</div>
                </div>
                <ChevronRight size={15} color="#4a5163" />
              </Link>
            ))}
          </div>
        </div>
      </div>
    </AppShell>
  );
}
