"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import AppShell from "@/components/AppShell";
import { processes } from "@/lib/api";

interface Process {
  id: string;
  code: string;
  name: string;
  category: string;
  description: string;
}

const catColor: Record<string, string> = {
  Management: "#8b5cf6",
  Core:       "#3b82f6",
  Support:    "#22c55e",
  Project:    "#f97316",
};

const catBadgeClass: Record<string, string> = {
  Management: "badge badge-violet",
  Core:       "badge badge-blue",
  Support:    "badge badge-green",
  Project:    "badge badge-orange",
};

export default function ProcessesPage() {
  const [data, setData] = useState<Process[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");

  useEffect(() => {
    processes.list().then((r) => setData(r.data)).catch(console.error).finally(() => setLoading(false));
  }, []);

  const filtered = data.filter((p) =>
    !search || p.name.toLowerCase().includes(search.toLowerCase()) || p.code.toLowerCase().includes(search.toLowerCase())
  );

  const grouped = filtered.reduce<Record<string, Process[]>>((acc, p) => {
    acc[p.category] = acc[p.category] || [];
    acc[p.category].push(p);
    return acc;
  }, {});

  return (
    <AppShell>
      {/* Header */}
      <div style={{ display:"flex", alignItems:"flex-end", justifyContent:"space-between", flexWrap:"wrap", gap:16, marginBottom:28 }}>
        <div>
          <div className="eyebrow">ISO 9001 · 14001 · 45001</div>
          <div className="page-heading">Processes</div>
          <div className="page-subheading">{data.length} processes mapped to ISO standards</div>
        </div>
        <input
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Search processes…"
          className="input"
          style={{ width:260, maxWidth:"100%" }}
        />
      </div>

      {loading ? (
        <div style={{ display:"flex", justifyContent:"center", padding:"80px 0" }}>
          <div className="spinner" style={{ width:24, height:24 }} />
        </div>
      ) : (
        <div style={{ display:"flex", flexDirection:"column", gap:24 }}>
          {Object.entries(grouped).map(([category, items]) => (
            <div key={category}>
              {/* Section label */}
              <div style={{ display:"flex", alignItems:"center", gap:8, marginBottom:10 }}>
                <div className="dot" style={{ background: catColor[category] || "var(--muted)" }} />
                <span style={{ fontSize:11, fontWeight:700, color:"var(--text-3)", letterSpacing:"0.06em", textTransform:"uppercase" }}>
                  {category}
                </span>
                <span style={{ fontSize:11, color:"var(--faint)" }}>({items.length})</span>
              </div>

              {/* Process list */}
              <div className="card" style={{ overflow:"hidden" }}>
                {items.map((p, i) => (
                  <Link key={p.id} href={`/processes/${p.id}`}>
                    <div
                      className="row-item"
                      style={{ borderTop: i > 0 ? "1px solid var(--border-soft)" : "none", borderBottom:"none" }}
                    >
                      <div style={{ display:"flex", alignItems:"center", gap:16, minWidth:0, flex:1 }}>
                        <span style={{ fontSize:11, fontFamily:"monospace", color:"var(--muted)", width:52, flexShrink:0 }}>
                          {p.code}
                        </span>
                        <div style={{ minWidth:0 }}>
                          <div style={{ fontSize:14, fontWeight:500, color:"var(--text)" }}>{p.name}</div>
                          {p.description && (
                            <div style={{ fontSize:12, color:"var(--muted)", overflow:"hidden", textOverflow:"ellipsis", whiteSpace:"nowrap", maxWidth:480 }}>
                              {p.description}
                            </div>
                          )}
                        </div>
                      </div>
                      <div style={{ display:"flex", alignItems:"center", gap:10, flexShrink:0, marginLeft:16 }}>
                        <span className={catBadgeClass[p.category] || "badge badge-slate"}>{category}</span>
                        <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="#4a5163" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                          <polyline points="9 18 15 12 9 6"/>
                        </svg>
                      </div>
                    </div>
                  </Link>
                ))}
              </div>
            </div>
          ))}

          {Object.keys(grouped).length === 0 && (
            <div style={{ textAlign:"center", padding:"60px 0", fontSize:13, color:"var(--muted)" }}>
              No processes match &ldquo;{search}&rdquo;
            </div>
          )}
        </div>
      )}
    </AppShell>
  );
}
