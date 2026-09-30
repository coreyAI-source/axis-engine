"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Check, ShieldCheck } from "lucide-react";
import { auth } from "@/lib/api";

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("admin@demo.local");
  const [password, setPassword] = useState("changeme123");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const res = await auth.login(email, password);
      localStorage.setItem("axis_token", res.data.access_token);
      router.push("/dashboard");
    } catch {
      setError("Invalid credentials. Ensure the API is running on port 8000.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="login-wrap">
      {/* Left panel */}
      <div className="login-left">
        <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
          <div className="sidebar-icon" style={{ width: 40, height: 40, borderRadius: 12 }}>
            <ShieldCheck size={20} color="#fff" strokeWidth={2.4} />
          </div>
          <div>
            <div style={{ fontSize: 18, fontWeight: 700, color: "var(--text)", letterSpacing: "0.04em" }}>AXIS</div>
            <div style={{ fontSize: 10, color: "var(--muted)", letterSpacing: "0.12em", textTransform: "uppercase" }}>Compliance engine</div>
          </div>
        </div>

        <div>
          <p className="gradient-text" style={{ fontSize: 30, fontWeight: 700, lineHeight: 1.2, letterSpacing: "-0.03em", marginBottom: 12 }}>
            From obligation to evidence — one integrated system.
          </p>
          <p style={{ fontSize: 14, color: "var(--text-3)", lineHeight: 1.6, marginBottom: 32, maxWidth: 380 }}>
            ISO management-system compliance and GSTC hotel sustainability audits, with evidence, findings and verified corrective actions in one place.
          </p>

          <div style={{ display: "flex", flexDirection: "column", gap: 16, marginBottom: 32 }}>
            {[
              { label: "GSTC hotel audits", desc: "All 40 criteria and performance indicators of the GSTC Hotel Standard v4.0." },
              { label: "Evidence-driven findings", desc: "Every outcome linked to documents, observations and interviews." },
              { label: "Independent verification", desc: "Corrective actions close only when a different person verifies them." },
            ].map((f) => (
              <div key={f.label} style={{ display: "flex", gap: 12 }}>
                <div style={{ width: 22, height: 22, borderRadius: 7, flexShrink: 0, marginTop: 1, background: "var(--accent-soft)", border: "1px solid rgba(125,155,255,0.3)", display: "grid", placeItems: "center" }}>
                  <Check size={12} color="var(--accent)" strokeWidth={3} />
                </div>
                <div>
                  <div style={{ fontSize: 13.5, fontWeight: 600, color: "var(--text)", marginBottom: 2 }}>{f.label}</div>
                  <div style={{ fontSize: 12.5, color: "var(--text-3)" }}>{f.desc}</div>
                </div>
              </div>
            ))}
          </div>

          <div style={{ display: "flex", gap: 6, flexWrap: "wrap" }}>
            {["GSTC Hotel v4.0", "ISO 9001:2015", "ISO 14001", "ISO 45001:2018"].map((s) => (
              <span key={s} className="badge badge-slate">{s}</span>
            ))}
          </div>
        </div>
      </div>

      {/* Right panel */}
      <div className="login-right">
        <div className="login-form-box">
          <div style={{ marginBottom: 28 }}>
            <h1 style={{ fontSize: 24, fontWeight: 700, color: "var(--text)", letterSpacing: "-0.02em", marginBottom: 6 }}>
              Welcome back
            </h1>
            <p style={{ fontSize: 13, color: "var(--text-3)" }}>Sign in to the compliance engine</p>
          </div>

          <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: 14 }}>
            <div>
              <label className="login-label">Email address</label>
              <input
                type="email" value={email} onChange={(e) => setEmail(e.target.value)}
                className="login-input" required
              />
            </div>
            <div>
              <label className="login-label">Password</label>
              <input
                type="password" value={password} onChange={(e) => setPassword(e.target.value)}
                className="login-input" required
              />
            </div>

            {error && (
              <div className="alert-error" style={{ padding: "10px 13px" }}>{error}</div>
            )}

            <button type="submit" disabled={loading} className="login-btn" style={{ marginTop: 6 }}>
              {loading
                ? <><div className="spinner spinner-white" style={{ width: 15, height: 15 }} /> Signing in…</>
                : "Sign in →"
              }
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
