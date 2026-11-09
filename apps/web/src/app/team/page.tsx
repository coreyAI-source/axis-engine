"use client";

import { FormEvent, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import AppShell from "@/components/AppShell";
import { apiError, hospitality, httpStatus, initials, Member, roleLabels, roleSummaries } from "@/lib/hospitality";
import s from "../hospitality/hospitality.module.css";

const roleOrder = ["admin", "compliance_manager", "lead_auditor", "auditor", "process_owner", "viewer"];
const roleTone: Record<string, string> = { admin: "blue", compliance_manager: "green", lead_auditor: "amber" };

export default function TeamPage() {
  const router = useRouter();
  const [me, setMe] = useState<Member | null>(null);
  const [members, setMembers] = useState<Member[]>([]);
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  function fail(error: unknown) {
    if (httpStatus(error) === 401) { localStorage.removeItem("axis_token"); router.replace("/login"); return; }
    setError(apiError(error));
  }
  async function load() {
    setLoading(true); setError("");
    try {
      const [mine, team] = await Promise.all([hospitality.me(), hospitality.members()]);
      setMe(mine.data); setMembers(team.data);
    } catch (error) { fail(error); } finally { setLoading(false); }
  }
  useEffect(() => { if (!localStorage.getItem("axis_token")) router.replace("/login"); else void load(); /* eslint-disable-next-line react-hooks/exhaustive-deps */ }, []);

  async function addMember(event: FormEvent<HTMLFormElement>) {
    event.preventDefault(); const form = event.currentTarget; const values = new FormData(form);
    setBusy(true); setError(""); setMessage("");
    try {
      const response = await hospitality.addMember({ first_name: String(values.get("first")).trim(), last_name: String(values.get("last")).trim(), email: String(values.get("email")).trim(), password: String(values.get("password")), role_code: String(values.get("role")) });
      setMembers((previous) => [...previous, response.data]);
      form.reset();
      setMessage(`${response.data.name} has been added. They can sign in with the email and password you set.`);
    } catch (error) { fail(error); } finally { setBusy(false); }
  }

  const isAdmin = me?.role_code === "admin";

  return <div className={s.page}><AppShell>
    <header className={s.header}>
      <div>
        <p className={s.eyebrow}>Organisation</p>
        <h1 className={s.title}>Team</h1>
        <p className={s.subtitle}>The people who work on your assessments, and what each role is able to do.</p>
      </div>
    </header>

    {error && <div role="alert" className={s.error}>{error} <button className={s.secondary} onClick={() => void load()} disabled={loading}>Try again</button></div>}
    {message && <p role="status" className={s.success}>{message}</p>}

    <section className={s.card} aria-labelledby="roles-title">
      <div className={s.cardHead}>
        <div>
          <h2 id="roles-title">Roles</h2>
          <p className={s.muted} style={{ marginTop: 4 }}>Each person has one role. It decides what they can change.</p>
        </div>
      </div>
      <div className={s.roleGrid}>
        {roleOrder.map((code) => (
          <article key={code} className={s.roleCard} data-current={me?.role_code === code}>
            {me?.role_code === code && <span className={s.youTag}>Your role</span>}
            <h3>{roleLabels[code]}</h3>
            <p>{roleSummaries[code]}</p>
          </article>
        ))}
      </div>
    </section>

    <section className={s.card} aria-labelledby="members-title">
      <div className={s.cardHead}>
        <div>
          <h2 id="members-title">People</h2>
          <p className={s.muted} style={{ marginTop: 4 }}>{loading ? "Loading your team…" : `${members.length} ${members.length === 1 ? "person" : "people"} in your organisation`}</p>
        </div>
      </div>
      <div className={s.memberList}>
        {members.map((member) => (
          <div key={member.id} className={s.memberRow}>
            <span className={s.avatarSmall} aria-hidden="true">{initials(member.name)}</span>
            <div className={s.memberMeta}>
              <strong>{member.name}{member.id === me?.id ? " (you)" : ""}</strong>
              <span>{member.email}</span>
            </div>
            <span className={s.pill} data-tone={roleTone[member.role_code]}>{roleLabels[member.role_code] ?? member.role_code}</span>
          </div>
        ))}
      </div>
    </section>

    {isAdmin ? (
      <section className={s.card} aria-labelledby="add-title">
        <div className={s.cardHead}>
          <div>
            <h2 id="add-title">Add a team member</h2>
            <p className={s.muted} style={{ marginTop: 4 }}>Create an account with a role. Share the password with them securely.</p>
          </div>
        </div>
        <form onSubmit={addMember}>
          <fieldset disabled={busy} style={{ border: 0, minWidth: 0 }}>
            <div className={s.grid}>
              <label className={s.field}>First name<input name="first" required maxLength={100} /></label>
              <label className={s.field}>Last name<input name="last" required maxLength={100} /></label>
              <label className={s.field}>Email<input type="email" name="email" required autoComplete="off" /></label>
              <label className={s.field}>
                Password
                <input type="password" name="password" required minLength={12} maxLength={72} autoComplete="new-password" />
                <small>At least 12 characters.</small>
              </label>
            </div>
            <label className={s.field}>
              Role
              <select name="role" defaultValue="process_owner">
                {roleOrder.map((code) => <option key={code} value={code}>{roleLabels[code]}: {roleSummaries[code]}</option>)}
              </select>
            </label>
            <div className={s.toolbar}>
              <button className={s.button} type="submit">{busy ? "Adding…" : "Add team member"}</button>
            </div>
          </fieldset>
        </form>
      </section>
    ) : me && (
      <p className={s.small}>Only organisation admins can add people. Ask an admin if someone needs access.</p>
    )}
  </AppShell></div>;
}
