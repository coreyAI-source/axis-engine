"use client";

import Link from "next/link";
import { useRouter, usePathname } from "next/navigation";

const links = [
  { href: "/dashboard", label: "Dashboard" },
  { href: "/processes", label: "Processes" },
  { href: "/monitoring", label: "Monitoring" },
];

export default function NavBar() {
  const router = useRouter();
  const pathname = usePathname();

  function logout() {
    localStorage.removeItem("axis_token");
    router.push("/login");
  }

  return (
    <nav className="bg-slate-900 text-white px-6 py-3 flex items-center gap-8">
      <Link href="/dashboard" className="font-bold text-lg tracking-tight mr-4">
        AXIS
      </Link>
      {links.map((l) => (
        <Link
          key={l.href}
          href={l.href}
          className={`text-sm font-medium transition-colors ${
            pathname.startsWith(l.href)
              ? "text-white"
              : "text-slate-400 hover:text-white"
          }`}
        >
          {l.label}
        </Link>
      ))}
      <button
        onClick={logout}
        className="ml-auto text-sm text-slate-400 hover:text-white transition-colors"
      >
        Sign out
      </button>
    </nav>
  );
}
