"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import AppShell from "@/components/AppShell";
import { api } from "@/lib/api";

interface ClauseMapping {
  mapping_id: string;
  standard: string;
  clause_number: string;
  clause_title: string;
  hls_section: string;
  risk_level: string;
  requires_documented_information: boolean;
  requires_retained_evidence: boolean;
  evidence_guidance: string;
}

interface MonitoringTask {
  task_id: string;
  title: string;
  risk_level: string;
  frequency_code: string;
  status: string;
  next_due_date: string | null;
}

interface ComplianceSummary {
  process: { id: string; code: string; name: string; category: string; description: string };
  clause_mappings: ClauseMapping[];
  monitoring_tasks: MonitoringTask[];
  risk_profile: {
    counts_by_level: Record<string, number>;
    total_mappings: number;
    total_tasks: number;
    overdue_tasks: number;
    due_tasks: number;
    highest_risk: string;
  };
}

const riskBadgeClass: Record<string, string> = {
  Extreme: "badge badge-red",
  High:    "badge badge-orange",
  Medium:  "badge badge-yellow",
  Low:     "badge badge-green",
};

const riskDot: Record<string, string> = {
  Extreme: "#ef4444",
  High:    "#f97316",
  Medium:  "#eab308",
  Low:     "#22c55e",
};

const taskBadgeClass: Record<string, string> = {
  Scheduled: "badge badge-blue",
  Due:       "badge badge-yellow",
  Overdue:   "badge badge-red",
  Completed: "badge badge-green",
  Suspended: "badge badge-slate",
};

export default function ProcessDetailPage() {
  const { id } = useParams<{ id: string }>();
  const [summary, setSummary] = useState<ComplianceSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeStandard, setActiveStandard] = useState<string | null>(null);
  const [expandedClause, setExpandedClause] = useState<string | null>(null);
  const [aiQuestions, setAiQuestions] = useState("");
  const [aiLoading, setAiLoading] = useState(false);

  useEffect(() => {
    api.get(`/processes/${id}/compliance-summary`)
      .then((res) => {
        setSummary(res.data);
        const stds = [...new Set(res.data.clause_mappings.map((m: ClauseMapping) => m.standard))];
        if (stds.length) setActiveStandard(stds[0] as string);
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [id]);

  async function generateAuditQuestions() {
    if (!summary) return;
    setAiLoading(true);
    setAiQuestions("");
    try {
      const clauses = summary.clause_mappings
        .filter((m) => !activeStandard || m.standard === activeStandard)
        .slice(0, 8);
      const res = await fetch("/api/audit-questions", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ process: summary.process, clause_mappings: clauses }),
      });
      const data = await res.json();
      setAiQuestions(data.questions || data.error || "No response.");
    } catch {
      setAiQuestions("Failed — check OPENROUTER_API_KEY in .env.local");
    } finally {
      setAiLoading(false);
    }
  }

  if (loading) return (
    <AppShell>
      <div style={{ display:"flex", alignItems:"center", justifyContent:"center", height:"60vh" }}>
        <div className="spinner" style={{ width:24, height:24 }} />
      </div>
    </AppShell>
  );

  if (!summary) return (
    <AppShell>
      <div style={{ padding:32, color:"var(--red)", fontSize:13 }}>Process not found.</div>
    </AppShell>
  );

  const { process, clause_mappings, monitoring_tasks, risk_profile } = summary;
  const standards = [...new Set(clause_mappings.map((m) => m.standard))];
  const visibleClauses = activeStandard ? clause_mappings.filter((m) => m.standard === activeStandard) : clause_mappings;

  return (
    <AppShell>
      {/* Breadcrumb */}
      <div style={{ display:"flex", alignItems:"center", gap:6, marginBottom:20, fontSize:12, color:"var(--muted)" }}>
        <Link href="/processes" style={{ color:"var(--muted)" }}
          onMouseEnter={(e) => (e.currentTarget as HTMLElement).style.color = "var(--text-2)"}
          onMouseLeave={(e) => (e.currentTarget as HTMLElement).style.color = "var(--muted)"}
        >Processes</Link>
        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <polyline points="9 18 15 12 9 6"/>
        </svg>
        <span style={{ color:"var(--text-2)", fontWeight:500 }}>{process.name}</span>
      </div>

      {/* Process header card */}
      <div className="card" style={{ marginBottom:20 }}>
        <div style={{ padding:"22px 24px 18px" }}>
          <div style={{ display:"flex", alignItems:"flex-start", justifyContent:"space-between", gap:16 }}>
            <div style={{ flex:1, minWidth:0 }}>
              <div style={{ display:"flex", alignItems:"center", gap:8, marginBottom:6 }}>
                <span style={{ fontSize:11, fontFamily:"monospace", color:"var(--muted)", background:"var(--surface-2)", padding:"2px 7px", borderRadius:4 }}>{process.code}</span>
                <span style={{ color:"var(--faint)", fontSize:11 }}>·</span>
                <span style={{ fontSize:11, color:"var(--muted)" }}>{process.category}</span>
              </div>
              <h1 style={{ fontSize:20, fontWeight:700, color:"var(--text)", letterSpacing:"-0.02em", marginBottom: process.description ? 6 : 0 }}>
                {process.name}
              </h1>
              {process.description && (
                <p style={{ fontSize:13, color:"var(--text-3)", lineHeight:1.6, maxWidth:600 }}>{process.description}</p>
              )}
            </div>
            {riskBadgeClass[risk_profile.highest_risk] && (
              <span className={riskBadgeClass[risk_profile.highest_risk]} style={{ flexShrink:0, padding:"5px 12px" }}>
                {risk_profile.highest_risk} risk
              </span>
            )}
          </div>

          {/* Risk breakdown */}
          <div className="grid-4" style={{ marginTop:20 }}>
            {Object.entries(risk_profile.counts_by_level).map(([level, count]) => (
              <div key={level} style={{ background:"var(--surface)", border:"1px solid var(--border-soft)", borderRadius:10, padding:"12px 14px" }}>
                <div style={{ display:"flex", alignItems:"center", gap:6, marginBottom:8 }}>
                  <div className="dot" style={{ width:6, height:6, background: riskDot[level] || "var(--muted)" }} />
                  <span style={{ fontSize:11, fontWeight:600, color:"var(--text-3)", textTransform:"uppercase", letterSpacing:"0.04em" }}>{level}</span>
                </div>
                <span style={{ fontSize:22, fontWeight:700, color:"var(--text)", letterSpacing:"-0.02em" }}>{count}</span>
                <span style={{ fontSize:11, color:"var(--muted)", marginLeft:4 }}>clauses</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Main 2-col grid */}
      <div className="grid-sidebar">

        {/* Left: clause mappings */}
        <div>
          <div style={{ display:"flex", alignItems:"center", justifyContent:"space-between", marginBottom:10 }}>
            <div className="card-title">
              Clause Mappings <span style={{ color:"var(--muted)", fontWeight:400 }}>({risk_profile.total_mappings})</span>
            </div>
            <div style={{ display:"flex", gap:4 }}>
              {standards.map((s) => (
                <button
                  key={s}
                  onClick={() => setActiveStandard(s)}
                  className={activeStandard === s ? "btn btn-dark" : "btn btn-ghost"}
                  style={{ padding:"4px 10px", fontSize:11 }}
                >
                  {s}
                </button>
              ))}
            </div>
          </div>

          <div className="card" style={{ overflow:"hidden" }}>
            {visibleClauses.map((m, i) => (
              <div key={m.mapping_id} style={{ borderTop: i > 0 ? "1px solid var(--border-soft)" : "none" }}>
                <div
                  style={{ padding:"13px 18px", cursor:"pointer", transition:"background 120ms" }}
                  onClick={() => setExpandedClause(expandedClause === m.mapping_id ? null : m.mapping_id)}
                  onMouseEnter={(e) => (e.currentTarget as HTMLElement).style.background = "var(--hover)"}
                  onMouseLeave={(e) => { if (expandedClause !== m.mapping_id) (e.currentTarget as HTMLElement).style.background = "transparent"; }}
                >
                  <div style={{ display:"flex", alignItems:"center", justifyContent:"space-between", gap:12 }}>
                    <div style={{ display:"flex", alignItems:"center", gap:12, minWidth:0, flex:1 }}>
                      <span style={{ fontSize:11, fontFamily:"monospace", color:"var(--muted)", width:40, flexShrink:0 }}>{m.clause_number}</span>
                      <span style={{ fontSize:13, color:"var(--text)", fontWeight:500 }}>{m.clause_title}</span>
                      <div style={{ display:"flex", gap:4, flexShrink:0 }}>
                        {m.requires_documented_information && (
                          <span className="badge badge-blue" style={{ fontSize:10, padding:"2px 6px", borderRadius:4 }}>Doc</span>
                        )}
                        {m.requires_retained_evidence && (
                          <span className="badge badge-violet" style={{ fontSize:10, padding:"2px 6px", borderRadius:4 }}>Rec</span>
                        )}
                      </div>
                    </div>
                    <div style={{ display:"flex", alignItems:"center", gap:8, flexShrink:0 }}>
                      {riskBadgeClass[m.risk_level] && (
                        <span className={riskBadgeClass[m.risk_level]} style={{ padding:"3px 8px" }}>{m.risk_level}</span>
                      )}
                      <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="#4a5163" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"
                        style={{ transform: expandedClause === m.mapping_id ? "rotate(180deg)" : "none", transition:"transform 150ms ease", flexShrink:0 }}>
                        <polyline points="6 9 12 15 18 9"/>
                      </svg>
                    </div>
                  </div>
                </div>
                {expandedClause === m.mapping_id && (
                  <div style={{ padding:"0 18px 14px 70px", background:"var(--surface)", borderTop:"1px solid var(--border-soft)" }}>
                    <div style={{ paddingTop:12 }}>
                      <div style={{ fontSize:10, fontWeight:700, color:"var(--muted)", textTransform:"uppercase", letterSpacing:"0.06em", marginBottom:6 }}>
                        Auditor Evidence Guidance
                      </div>
                      <p style={{ fontSize:13, color:"var(--text-2)", lineHeight:1.65 }}>{m.evidence_guidance}</p>
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Right column */}
        <div style={{ display:"flex", flexDirection:"column", gap:14 }}>

          {/* AI audit questions */}
          <div className="card" style={{ overflow:"hidden" }}>
            <div className="card-header">
              <div>
                <div style={{ display:"flex", alignItems:"center", gap:7, marginBottom:2 }}>
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#3b82f6" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>
                  </svg>
                  <span className="card-title">AI Audit Questions</span>
                </div>
                <div className="card-subtitle">
                  Targeted questions from {activeStandard || "all"} clause requirements
                </div>
              </div>
            </div>
            <div style={{ padding:14 }}>
              <button
                onClick={generateAuditQuestions}
                disabled={aiLoading}
                className="btn btn-dark"
                style={{ width:"100%", justifyContent:"center" }}
              >
                {aiLoading
                  ? <><div className="spinner" style={{ width:14, height:14 }} /> Generating…</>
                  : <>
                      <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                        <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>
                      </svg>
                      Generate Audit Questions
                    </>
                }
              </button>
              {aiQuestions && (
                <div style={{
                  marginTop:12, padding:"12px 14px",
                  background:"var(--surface)", borderRadius:8, border:"1px solid var(--border-soft)",
                  fontSize:12, color:"var(--text-2)", lineHeight:1.7,
                  whiteSpace:"pre-wrap", maxHeight:360, overflowY:"auto",
                }}>
                  {aiQuestions}
                </div>
              )}
            </div>
          </div>

          {/* Monitoring tasks */}
          <div className="card" style={{ overflow:"hidden" }}>
            <div className="card-header">
              <span className="card-title">
                Monitoring Tasks <span style={{ color:"var(--muted)", fontWeight:400 }}>({risk_profile.total_tasks})</span>
              </span>
            </div>
            {monitoring_tasks.length === 0 ? (
              <div style={{ padding:"28px 18px", textAlign:"center" }}>
                <div style={{ fontSize:13, color:"var(--muted)" }}>No tasks yet</div>
                <div style={{ fontSize:11, color:"var(--faint)", marginTop:3 }}>Generate from the API endpoint</div>
              </div>
            ) : (
              <div>
                {monitoring_tasks.slice(0, 10).map((t, i) => (
                  <div key={t.task_id} style={{ padding:"11px 18px", borderTop: i > 0 ? "1px solid var(--border-soft)" : "none" }}>
                    <div style={{ display:"flex", justifyContent:"space-between", gap:8, marginBottom:3 }}>
                      <span style={{ fontSize:12, color:"var(--text-2)", lineHeight:1.4, flex:1, minWidth:0, overflow:"hidden", textOverflow:"ellipsis", whiteSpace:"nowrap" }}>
                        {t.title.replace("Monitor: ", "")}
                      </span>
                      <span className={taskBadgeClass[t.status] || "badge badge-slate"} style={{ flexShrink:0, fontSize:10, padding:"2px 7px" }}>
                        {t.status}
                      </span>
                    </div>
                    <div style={{ display:"flex", gap:8, fontSize:11, color:"var(--muted)" }}>
                      <span>{t.frequency_code}</span>
                      {t.next_due_date && <><span>·</span><span>{t.next_due_date}</span></>}
                    </div>
                  </div>
                ))}
                {monitoring_tasks.length > 10 && (
                  <div style={{ padding:"10px 18px", fontSize:11, color:"var(--muted)", textAlign:"center", borderTop:"1px solid var(--border-soft)" }}>
                    +{monitoring_tasks.length - 10} more tasks
                  </div>
                )}
              </div>
            )}
          </div>

        </div>
      </div>
    </AppShell>
  );
}
