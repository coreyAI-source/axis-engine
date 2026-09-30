"use client";

import { useEffect, useState } from "react";
import AppShell from "@/components/AppShell";
import { monitoring } from "@/lib/api";

interface MonitoringTask {
  id: string;
  title: string;
  risk_level: string;
  frequency_code: string;
  status: string;
  next_due_date: string | null;
}

const statusBadgeClass: Record<string, string> = {
  Overdue:   "badge badge-red",
  Due:       "badge badge-yellow",
  Scheduled: "badge badge-blue",
  Completed: "badge badge-green",
  Suspended: "badge badge-slate",
};

const statusDot: Record<string, string> = {
  Overdue:   "#ef4444",
  Due:       "#eab308",
  Scheduled: "#3b82f6",
  Completed: "#22c55e",
  Suspended: "#94a3b8",
};

const riskDot: Record<string, string> = {
  Extreme: "#ef4444",
  High:    "#f97316",
  Medium:  "#eab308",
  Low:     "#22c55e",
};

export default function MonitoringPage() {
  const [tasks, setTasks] = useState<MonitoringTask[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState("all");

  useEffect(() => {
    monitoring.tasks().then((r) => setTasks(r.data)).catch(console.error).finally(() => setLoading(false));
  }, []);

  const counts = tasks.reduce<Record<string, number>>((acc, t) => {
    acc[t.status] = (acc[t.status] || 0) + 1;
    return acc;
  }, {});

  const filtered = filter === "all" ? tasks : tasks.filter((t) => t.status === filter);

  const filterOptions = [
    { key:"all",       label:"All",       count:tasks.length,          dot:"var(--muted)" },
    { key:"Overdue",   label:"Overdue",   count:counts.Overdue   || 0, dot:"#ef4444" },
    { key:"Due",       label:"Due",       count:counts.Due       || 0, dot:"#eab308" },
    { key:"Scheduled", label:"Scheduled", count:counts.Scheduled || 0, dot:"#3b82f6" },
    { key:"Completed", label:"Completed", count:counts.Completed || 0, dot:"#22c55e" },
  ];

  return (
    <AppShell>
      {/* Header */}
      <div style={{ marginBottom:24 }}>
        <div className="eyebrow">ISO 9001 · 14001 · 45001</div>
        <div className="page-heading">Monitoring</div>
        <div className="page-subheading">Scheduled compliance checks across all processes</div>
      </div>

      {/* Filter tabs */}
      <div style={{ display:"flex", gap:6, marginBottom:18, flexWrap:"wrap" }}>
        {filterOptions.map((f) => {
          const active = filter === f.key;
          return (
            <button
              key={f.key}
              onClick={() => setFilter(f.key)}
              className={active ? "btn btn-dark" : "btn btn-ghost"}
              style={{ padding:"5px 12px", fontSize:12 }}
            >
              <div className="dot" style={{ width:6, height:6, background: active ? "rgba(255,255,255,0.45)" : f.dot }} />
              {f.label}
              <span style={{
                fontSize:10, fontWeight:700, padding:"1px 6px", borderRadius:10,
                background: active ? "rgba(255,255,255,0.15)" : "var(--surface-2)",
                color: active ? "#fff" : "var(--text-3)",
              }}>{f.count}</span>
            </button>
          );
        })}
      </div>

      {loading ? (
        <div style={{ display:"flex", justifyContent:"center", padding:"80px 0" }}>
          <div className="spinner" style={{ width:24, height:24 }} />
        </div>
      ) : (
        <div className="card" style={{ overflowX:"auto" }}><div style={{ minWidth:640 }}>
          {/* Table header */}
          <div style={{
            display:"grid", gridTemplateColumns:"1fr 100px 110px 120px 130px",
            padding:"10px 18px", borderBottom:"1px solid var(--border-soft)", background:"var(--surface)",
          }}>
            {["Task", "Risk", "Frequency", "Status", "Next Due"].map((h) => (
              <div key={h} style={{ fontSize:10, fontWeight:700, color:"var(--muted)", textTransform:"uppercase", letterSpacing:"0.06em" }}>{h}</div>
            ))}
          </div>

          {/* Rows */}
          {filtered.map((t, i) => (
            <div
              key={t.id}
              style={{
                display:"grid", gridTemplateColumns:"1fr 100px 110px 120px 130px",
                padding:"12px 18px",
                borderTop: i > 0 ? "1px solid var(--border-soft)" : "none",
                alignItems:"center",
                transition:"background 120ms",
              }}
              onMouseEnter={(e) => (e.currentTarget as HTMLElement).style.background = "var(--hover)"}
              onMouseLeave={(e) => (e.currentTarget as HTMLElement).style.background = "transparent"}
            >
              <div style={{ fontSize:13, fontWeight:500, color:"var(--text)", paddingRight:16, overflow:"hidden", textOverflow:"ellipsis", whiteSpace:"nowrap" }}>
                {t.title}
              </div>
              <div style={{ display:"flex", alignItems:"center", gap:6 }}>
                <div className="dot" style={{ width:7, height:7, background: riskDot[t.risk_level] || "var(--muted)" }} />
                <span style={{ fontSize:12, color:"var(--text-2)" }}>{t.risk_level}</span>
              </div>
              <span style={{ fontSize:12, color:"var(--text-3)" }}>{t.frequency_code}</span>
              <div>
                <span className={statusBadgeClass[t.status] || "badge badge-slate"} style={{ gap:5 }}>
                  <div className="dot" style={{ width:5, height:5, background: statusDot[t.status] || "var(--muted)" }} />
                  {t.status}
                </span>
              </div>
              <span style={{ fontSize:12, color:"var(--muted)" }}>{t.next_due_date ?? "—"}</span>
            </div>
          ))}

          {filtered.length === 0 && (
            <div style={{ padding:"60px 18px", textAlign:"center", fontSize:13, color:"var(--muted)" }}>
              No tasks matching this filter
            </div>
          )}
        </div></div>
      )}
    </AppShell>
  );
}
