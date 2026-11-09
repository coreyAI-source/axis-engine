"use client";

import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";
import { ArrowRight, Check } from "lucide-react";
import { auth } from "@/lib/api";
import { BrandLockup } from "@/components/Brand";

const points = [
  { title: "A clear readiness picture", text: "Every GSTC criterion scored, with the reasons behind each score." },
  { title: "Evidence in one place", text: "Documents, photos and interview notes linked to the criterion they support." },
  { title: "Actions with owners", text: "Each gap has an owner and a due date, and closes only once a second person has confirmed it." },
];

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const res = await auth.login(email, password);
      localStorage.setItem("axis_token", res.data.access_token);
      router.push("/dashboard");
    } catch (err) {
      // No response means the API could not be reached. Otherwise the status code says what happened.
      const status = (err as { response?: { status?: number } }).response?.status;
      if (status === undefined) setError("AXIS can't be reached right now. Check your connection, then try again.");
      else if (status === 401) setError("Email or password is not correct.");
      else if (status === 403) setError("This account is inactive. Ask your organisation admin to reactivate it.");
      else if (status === 429) setError("Too many sign-in attempts. Wait a few minutes, then try again.");
      else if (status === 422 || status === 400) setError("Enter a valid email address and password.");
      else if (status >= 500) setError(`AXIS ran into a problem (HTTP ${status}). Try again shortly.`);
      else setError(`Sign-in failed (HTTP ${status}). Try again.`);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="login-wrap">
      <aside className="login-left">
        <BrandLockup />

        <div>
          <h1 className="login-headline">Know where your property stands, and what to do next.</h1>
          <p className="login-lede">
            Check your property against the GSTC Hotel Standard, keep the evidence in one place and track the actions that prepare you for certification.
          </p>
          <div className="login-points">
            {points.map((point) => (
              <div key={point.title} className="login-point">
                <span className="login-point-icon" aria-hidden="true"><Check size={15} strokeWidth={2.6} /></span>
                <div>
                  <strong>{point.title}</strong>
                  <span>{point.text}</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        <p className="login-note">
          AXIS prepares your property for certification. Only GSTC-accredited certification bodies can certify it.
        </p>
      </aside>

      <main className="login-right">
        <div className="login-form-box">
          <div className="login-mobile-brand"><BrandLockup /></div>

          <div style={{ marginBottom: 30 }}>
            <h2 style={{ fontFamily: "var(--font-head)", fontSize: 26, fontWeight: 700, color: "var(--brand-navy)", letterSpacing: "-0.02em", marginBottom: 8 }}>
              Sign in
            </h2>
            <p style={{ fontSize: 15, color: "var(--text-3)" }}>Use the email and password for your AXIS account.</p>
          </div>

          <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: 18 }}>
            <div>
              <label className="login-label" htmlFor="login-email">Email address</label>
              <input
                id="login-email" type="email" autoComplete="email" value={email}
                onChange={(e) => setEmail(e.target.value)} className="login-input" required
              />
            </div>
            <div>
              <label className="login-label" htmlFor="login-password">Password</label>
              <input
                id="login-password" type="password" autoComplete="current-password" value={password}
                onChange={(e) => setPassword(e.target.value)} className="login-input" required
              />
            </div>

            {error && <div role="alert" className="alert-error">{error}</div>}

            <button type="submit" disabled={loading} className="login-btn" style={{ marginTop: 4 }}>
              {loading
                ? <><div className="spinner spinner-white" style={{ width: 16, height: 16 }} /> Signing in…</>
                : <>Sign in <ArrowRight size={17} /></>
              }
            </button>
          </form>
        </div>
      </main>
    </div>
  );
}
