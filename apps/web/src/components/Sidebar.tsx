"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { Activity, ClipboardCheck, LayoutDashboard, LogOut, LucideIcon, Users, Workflow } from "lucide-react";
import { BrandLockup } from "./Brand";
import { canAudit, hospitality, initials, Member, roleLabels } from "@/lib/hospitality";

// Organisation pages first: what a property team uses day to day.
const primaryItems: { href: string; label: string; Icon: LucideIcon }[] = [
  { href: "/dashboard", label: "Overview", Icon: LayoutDashboard },
  { href: "/hospitality", label: "Assessments", Icon: ClipboardCheck },
  { href: "/team", label: "Team", Icon: Users },
];

// Practice tools used by AXIS advisers. Shown only to roles that run assessments.
const advisorItems: { href: string; label: string; Icon: LucideIcon }[] = [
  { href: "/processes", label: "ISO processes", Icon: Workflow },
  { href: "/monitoring", label: "Recurring checks", Icon: Activity },
];

export default function Sidebar() {
  const router = useRouter();
  const pathname = usePathname();
  const [me, setMe] = useState<Member | null>(null);

  useEffect(() => {
    if (!localStorage.getItem("axis_token")) return;
    hospitality.me().then((r) => setMe(r.data)).catch(() => setMe(null));
  }, []);

  const isActive = (href: string) => (href === "/dashboard" ? pathname === href : pathname === href || pathname.startsWith(`${href}/`));

  function signOut() {
    localStorage.removeItem("axis_token");
    router.push("/login");
  }

  const renderItem = ({ href, label, Icon }: { href: string; label: string; Icon: LucideIcon }, small = false) => {
    const active = isActive(href);
    return (
      <Link key={href} href={href} className={`nav-item${active ? " active" : ""}${small ? " nav-small" : ""}`} aria-current={active ? "page" : undefined}>
        <span className="nav-icon"><Icon size={19} strokeWidth={1.9} /></span>
        <span className="nav-label">{label}</span>
      </Link>
    );
  };

  return (
    <aside className="sidebar" aria-label="Main navigation">
      <div className="sidebar-logo">
        <BrandLockup />
      </div>

      <nav className="sidebar-nav">
        {primaryItems.map((item) => renderItem(item))}

        {canAudit(me) && (
          <div className="sidebar-advisor">
            <span className="sidebar-section-label">Advisor tools</span>
            {advisorItems.map((item) => renderItem(item, true))}
          </div>
        )}
      </nav>

      <div className="sidebar-footer">
        <div className="user-card">
          <span className="avatar" aria-hidden="true">{me ? initials(me.name) : ""}</span>
          <span className="user-meta">
            <span className="user-name">{me?.name ?? "Signed in"}</span>
            <span className="user-role">{me ? roleLabels[me.role_code] ?? me.role_code : " "}</span>
          </span>
        </div>
        <button type="button" onClick={signOut} className="signout">
          <LogOut size={17} strokeWidth={1.9} />
          <span>Sign out</span>
        </button>
      </div>
    </aside>
  );
}
