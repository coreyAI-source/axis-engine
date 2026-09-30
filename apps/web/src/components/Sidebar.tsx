"use client";

import Link from "next/link";
import { useRouter, usePathname } from "next/navigation";
import { Activity, Hotel, LayoutDashboard, LogOut, ShieldCheck, Workflow } from "lucide-react";

const navItems = [
  { href: "/dashboard", label: "Dashboard", Icon: LayoutDashboard },
  { href: "/hospitality", label: "Hotel audits", Icon: Hotel },
  { href: "/processes", label: "ISO processes", Icon: Workflow },
  { href: "/monitoring", label: "Monitoring", Icon: Activity },
];

export default function Sidebar() {
  const router = useRouter();
  const pathname = usePathname();

  return (
    <aside className="sidebar" aria-label="Main navigation">
      <div className="sidebar-logo">
        <div className="sidebar-icon-wrap"><div className="sidebar-icon"><ShieldCheck size={18} color="#fff" strokeWidth={2.4} /></div></div>
        <div className="sidebar-brand-text">
          <div className="sidebar-brand">AXIS</div>
          <div className="sidebar-tagline">Compliance engine</div>
        </div>
      </div>

      <nav className="sidebar-nav">
        <span className="sidebar-section-label">Workspace</span>
        {navItems.map(({ href, label, Icon }) => {
          const active = pathname === href || (href !== "/dashboard" && pathname.startsWith(href));
          return (
            <Link key={href} href={href} className={`nav-item${active ? " active" : ""}`} title={label} aria-current={active ? "page" : undefined}>
              <span className="nav-icon"><Icon size={19} strokeWidth={1.9} /></span>
              <span className="nav-label">{label}</span>
            </Link>
          );
        })}
      </nav>

      <div className="sidebar-footer">
        <button
          onClick={() => { localStorage.removeItem("axis_token"); router.push("/login"); }}
          className="nav-item"
          title="Sign out"
        >
          <span className="nav-icon"><LogOut size={18} strokeWidth={1.9} /></span>
          <span className="nav-label">Sign out</span>
        </button>
      </div>
    </aside>
  );
}
