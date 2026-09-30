import type { Metadata } from "next";
import { Inter, JetBrains_Mono } from "next/font/google";
import "./globals.css";

const sans = Inter({ subsets: ["latin"], variable: "--font-sans", display: "swap" });
const mono = JetBrains_Mono({ subsets: ["latin"], variable: "--font-mono", display: "swap" });

export const metadata: Metadata = {
  title: "AXIS — Compliance Engine",
  description: "Integrated compliance: ISO 9001 / 14001 / 45001 and GSTC hotel sustainability audits",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={`${sans.variable} ${mono.variable}`}>
      <head>
        <style>{`
          :root {
            color-scheme: dark;
            --bg: #06080d;
            --surface: rgba(255,255,255,0.032);
            --surface-2: rgba(255,255,255,0.055);
            --surface-solid: #0e121b;
            --hover: rgba(255,255,255,0.045);
            --border: rgba(255,255,255,0.08);
            --border-soft: rgba(255,255,255,0.05);
            --border-strong: rgba(255,255,255,0.15);
            --text: #eef1f8;
            --text-2: #c4cad8;
            --text-3: #8e96a8;
            --muted: #6c7489;
            --faint: #454c5e;
            --accent: #7d9bff;
            --accent-2: #5fe3cf;
            --accent-soft: rgba(125,155,255,0.12);
            --accent-glow: rgba(125,155,255,0.38);
            --green: #4ade9c;  --green-soft: rgba(74,222,156,0.11);  --green-line: rgba(74,222,156,0.28);
            --amber: #fcc545;  --amber-soft: rgba(252,197,69,0.11);  --amber-line: rgba(252,197,69,0.28);
            --red: #fb7c7c;    --red-soft: rgba(251,124,124,0.11);   --red-line: rgba(251,124,124,0.3);
            --blue: #6fb1ff;   --violet: #b29bff;  --orange: #ff9f5a;  --slate: #9aa6bb;
            --radius: 14px;
            --rail: 68px;
            --rail-open: 236px;
            --shadow: 0 1px 0 rgba(255,255,255,0.04) inset, 0 12px 32px -14px rgba(0,0,0,0.7);
          }
          *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
          html { font-size: 16px; }
          body {
            font-family: var(--font-sans), -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Arial, sans-serif;
            color: var(--text);
            background:
              radial-gradient(1100px 620px at 12% -12%, rgba(125,155,255,0.11), transparent 62%),
              radial-gradient(900px 520px at 105% 6%, rgba(95,227,207,0.07), transparent 60%),
              radial-gradient(800px 600px at 50% 120%, rgba(178,155,255,0.05), transparent 60%),
              var(--bg);
            background-attachment: fixed;
            min-height: 100vh;
            -webkit-font-smoothing: antialiased;
            -moz-osx-font-smoothing: grayscale;
            line-height: 1.5;
            font-feature-settings: "cv11", "ss01";
          }
          a { text-decoration: none; color: inherit; }
          button, input, textarea, select { font-family: inherit; }
          ::selection { background: rgba(125,155,255,0.35); color: #fff; }
          ::-webkit-scrollbar { width: 10px; height: 10px; }
          ::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.08); border-radius: 10px; border: 2px solid transparent; background-clip: padding-box; }
          ::-webkit-scrollbar-thumb:hover { background: rgba(255,255,255,0.16); background-clip: padding-box; border: 2px solid transparent; }
          ::-webkit-scrollbar-track { background: transparent; }
          :focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; border-radius: 6px; }
          .mono { font-family: var(--font-mono), ui-monospace, Consolas, monospace; }

          /* Sidebar: icon rail that expands over the content on hover or keyboard focus */
          .sidebar {
            position: fixed; top: 0; left: 0; bottom: 0; z-index: 100;
            width: var(--rail);
            display: flex; flex-direction: column;
            background: rgba(9,11,17,0.86);
            backdrop-filter: blur(18px) saturate(140%);
            -webkit-backdrop-filter: blur(18px) saturate(140%);
            border-right: 1px solid var(--border);
            overflow: hidden;
            transition: width 200ms cubic-bezier(.2,.7,.2,1), box-shadow 200ms;
          }
          .sidebar:hover, .sidebar:focus-within {
            width: var(--rail-open);
            box-shadow: 24px 0 60px -20px rgba(0,0,0,0.85), 1px 0 0 rgba(125,155,255,0.12);
            transition-delay: 60ms;
          }
          .sidebar-logo { display: flex; align-items: center; height: 72px; padding: 0 10px; border-bottom: 1px solid var(--border-soft); white-space: nowrap; }
          .sidebar-icon-wrap { width: 48px; display: grid; place-items: center; flex-shrink: 0; }
          .sidebar-icon {
            width: 36px; height: 36px; border-radius: 11px;
            background: linear-gradient(140deg, #9db3ff 0%, #6a7dff 55%, #5fe3cf 130%);
            display: grid; place-items: center;
            box-shadow: 0 0 0 1px rgba(255,255,255,0.12) inset, 0 6px 22px -4px var(--accent-glow);
          }
          .sidebar-brand { font-size: 15px; font-weight: 700; letter-spacing: 0.04em; color: var(--text); }
          .sidebar-tagline { font-size: 10px; color: var(--muted); text-transform: uppercase; letter-spacing: 0.12em; margin-top: 1px; }
          .sidebar-nav { flex: 1; padding: 14px 10px; display: flex; flex-direction: column; gap: 4px; overflow-y: auto; overflow-x: hidden; }
          .sidebar-section-label {
            font-size: 10px; font-weight: 700; color: var(--faint); text-transform: uppercase; letter-spacing: 0.12em;
            padding: 4px 0 8px 14px; white-space: nowrap;
          }
          .nav-item {
            position: relative;
            display: flex; align-items: center; height: 44px; width: 100%;
            border-radius: 11px; color: var(--text-3);
            font-size: 13.5px; font-weight: 500; white-space: nowrap;
            cursor: pointer; background: none; border: none; text-align: left;
            transition: color 140ms, background 140ms;
          }
          .nav-icon { width: 48px; display: grid; place-items: center; flex-shrink: 0; }
          .nav-item svg { transition: color 140ms, filter 140ms; }
          .nav-item:hover { color: var(--text); background: var(--hover); }
          .nav-item.active { color: var(--text); background: linear-gradient(90deg, rgba(125,155,255,0.16), rgba(125,155,255,0.04)); box-shadow: 0 0 0 1px rgba(125,155,255,0.18) inset; }
          .nav-item.active svg { color: var(--accent); filter: drop-shadow(0 0 8px rgba(125,155,255,0.6)); }
          .nav-item.active::before { content: ""; position: absolute; left: -10px; top: 11px; bottom: 11px; width: 3px; border-radius: 0 3px 3px 0; background: var(--accent); box-shadow: 0 0 12px var(--accent); }
          .nav-label, .sidebar-brand-text, .sidebar-section-label { opacity: 0; transform: translateX(-4px); transition: opacity 140ms, transform 160ms; }
          .sidebar:hover .nav-label, .sidebar:focus-within .nav-label,
          .sidebar:hover .sidebar-brand-text, .sidebar:focus-within .sidebar-brand-text,
          .sidebar:hover .sidebar-section-label, .sidebar:focus-within .sidebar-section-label { opacity: 1; transform: none; transition-delay: 90ms; }
          .sidebar-footer { padding: 10px; border-top: 1px solid var(--border-soft); }

          /* Layout shell */
          .app-shell { min-height: 100vh; }
          .app-main { margin-left: var(--rail); min-height: 100vh; min-width: 0; }
          .page-content { padding: 32px clamp(16px, 3.2vw, 44px) 64px; max-width: 1280px; margin: 0 auto; }

          /* Headings */
          .page-heading {
            font-size: 28px; font-weight: 700; letter-spacing: -0.03em; line-height: 1.15;
            background: linear-gradient(180deg, #ffffff 30%, #b9c3dc 100%);
            -webkit-background-clip: text; background-clip: text; color: transparent;
          }
          .page-subheading { font-size: 14px; color: var(--text-3); margin-top: 6px; }
          .eyebrow { font-size: 11px; font-weight: 700; letter-spacing: 0.14em; text-transform: uppercase; color: var(--accent); margin-bottom: 8px; }

          /* Cards */
          .card {
            background: linear-gradient(180deg, rgba(255,255,255,0.045), rgba(255,255,255,0.018));
            border: 1px solid var(--border);
            border-radius: var(--radius);
            box-shadow: var(--shadow);
          }
          .card-header { padding: 16px 20px; border-bottom: 1px solid var(--border-soft); display: flex; align-items: center; justify-content: space-between; gap: 12px; }
          .card-title { font-size: 14px; font-weight: 600; color: var(--text); }
          .card-subtitle { font-size: 12px; color: var(--muted); margin-top: 2px; }

          /* Stat card */
          .stat-card {
            position: relative; overflow: hidden; height: 100%;
            background: linear-gradient(180deg, rgba(255,255,255,0.05), rgba(255,255,255,0.015));
            border: 1px solid var(--border); border-radius: var(--radius);
            padding: 18px 18px 16px; box-shadow: var(--shadow);
            transition: transform 160ms, border-color 160ms, box-shadow 160ms;
          }
          .stat-card::before { content: ""; position: absolute; inset: 0 0 auto 0; height: 1px; background: linear-gradient(90deg, transparent, var(--tone, var(--accent)), transparent); opacity: 0.7; }
          .stat-card:hover { transform: translateY(-2px); border-color: var(--border-strong); box-shadow: var(--shadow), 0 18px 40px -22px var(--tone, var(--accent)); }
          .stat-icon { width: 34px; height: 34px; border-radius: 10px; display: grid; place-items: center; margin-bottom: 14px; }
          .stat-number { font-size: 30px; font-weight: 700; color: var(--text); letter-spacing: -0.035em; line-height: 1; font-variant-numeric: tabular-nums; }
          .stat-label { font-size: 12px; color: var(--text-3); margin-top: 6px; font-weight: 500; }

          /* Badges */
          .badge { display: inline-flex; align-items: center; gap: 5px; font-size: 11px; font-weight: 600; padding: 3px 9px; border-radius: 20px; border: 1px solid; white-space: nowrap; }
          .badge-red    { background: var(--red-soft);   color: #ffb1b1; border-color: var(--red-line); }
          .badge-orange { background: rgba(255,159,90,0.11); color: #ffc497; border-color: rgba(255,159,90,0.3); }
          .badge-yellow { background: var(--amber-soft); color: #ffe08a; border-color: var(--amber-line); }
          .badge-green  { background: var(--green-soft); color: #9af0c4; border-color: var(--green-line); }
          .badge-blue   { background: rgba(111,177,255,0.11); color: #b3d4ff; border-color: rgba(111,177,255,0.3); }
          .badge-violet { background: rgba(178,155,255,0.12); color: #d3c6ff; border-color: rgba(178,155,255,0.3); }
          .badge-slate  { background: rgba(154,166,187,0.1); color: #c7cfdc; border-color: rgba(154,166,187,0.25); }

          /* Buttons */
          .btn {
            display: inline-flex; align-items: center; justify-content: center; gap: 7px;
            font-size: 13px; font-weight: 600; padding: 9px 16px; border-radius: 10px;
            border: 1px solid transparent; cursor: pointer; white-space: nowrap;
            transition: background 140ms, border-color 140ms, box-shadow 140ms, transform 140ms, color 140ms;
          }
          .btn:active { transform: translateY(1px); }
          .btn-primary, .btn-dark {
            color: #fff;
            background: linear-gradient(135deg, #8ea8ff, #6576ff);
            box-shadow: 0 1px 0 rgba(255,255,255,0.25) inset, 0 8px 22px -10px var(--accent-glow);
          }
          .btn-primary:hover, .btn-dark:hover { box-shadow: 0 1px 0 rgba(255,255,255,0.25) inset, 0 10px 28px -8px var(--accent-glow); filter: brightness(1.06); }
          .btn-ghost { background: var(--surface); color: var(--text-2); border-color: var(--border); }
          .btn-ghost:hover { background: var(--surface-2); color: var(--text); border-color: var(--border-strong); }
          .btn:disabled { opacity: 0.5; cursor: not-allowed; }

          /* Input */
          .input {
            background: rgba(255,255,255,0.035); border: 1px solid var(--border); border-radius: 10px;
            padding: 9px 12px; font-size: 13px; color: var(--text); outline: none;
            transition: border-color 150ms, box-shadow 150ms, background 150ms;
          }
          .input::placeholder { color: var(--muted); }
          .input:focus { border-color: rgba(125,155,255,0.6); box-shadow: 0 0 0 4px rgba(125,155,255,0.12); background: rgba(255,255,255,0.05); }

          /* Table */
          .table { width: 100%; border-collapse: collapse; }
          .table th { padding: 10px 16px; text-align: left; font-size: 10px; font-weight: 700; color: var(--muted); text-transform: uppercase; letter-spacing: 0.08em; background: rgba(255,255,255,0.02); border-bottom: 1px solid var(--border-soft); }
          .table td { padding: 12px 16px; border-bottom: 1px solid var(--border-soft); font-size: 13px; }
          .table tr:last-child td { border-bottom: none; }
          .table tr:hover td { background: var(--hover); }

          /* Row list */
          .row-item { display: flex; align-items: center; justify-content: space-between; padding: 14px 18px; cursor: pointer; transition: background 120ms; border-bottom: 1px solid var(--border-soft); }
          .row-item:last-child { border-bottom: none; }
          .row-item:hover { background: var(--hover); }
          .hover-row { transition: background 120ms; }
          .hover-row:hover { background: var(--hover); }

          .dot { width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0; }

          @keyframes spin { to { transform: rotate(360deg); } }
          .spinner { border: 2.5px solid rgba(125,155,255,0.18); border-top-color: var(--accent); border-radius: 50%; animation: spin 0.7s linear infinite; }
          .spinner-white { border-color: rgba(255,255,255,0.3); border-top-color: #fff; }
          @keyframes rise { from { opacity: 0; transform: translateY(6px); } to { opacity: 1; transform: none; } }
          .page-content > * { animation: rise 320ms cubic-bezier(.2,.7,.2,1) both; }

          .alert-error { background: var(--red-soft); border: 1px solid var(--red-line); border-radius: 12px; padding: 14px 16px; color: #ffc0c0; font-size: 13px; }

          /* Grid helpers */
          .grid-5 { display: grid; grid-template-columns: repeat(auto-fit, minmax(170px, 1fr)); gap: 14px; }
          .grid-2 { display: grid; grid-template-columns: repeat(auto-fit, minmax(min(100%, 380px), 1fr)); gap: 16px; }
          .grid-sidebar { display: grid; grid-template-columns: minmax(0, 1fr) 340px; gap: 16px; align-items: start; }
          .grid-4 { display: grid; grid-template-columns: repeat(auto-fit, minmax(130px, 1fr)); gap: 10px; }
          @media (max-width: 1100px) { .grid-sidebar { grid-template-columns: minmax(0, 1fr); } }

          /* Login */
          .login-wrap { display: flex; min-height: 100vh; }
          .login-left {
            position: relative; overflow: hidden;
            width: min(46%, 520px); flex-shrink: 0;
            background: linear-gradient(160deg, rgba(20,24,38,0.9), rgba(8,10,16,0.95));
            border-right: 1px solid var(--border);
            display: flex; flex-direction: column; justify-content: space-between; padding: 44px;
          }
          .login-left::before { content: ""; position: absolute; width: 520px; height: 520px; left: -160px; bottom: -200px; border-radius: 50%; background: radial-gradient(circle, rgba(125,155,255,0.22), transparent 65%); pointer-events: none; }
          .login-left::after { content: ""; position: absolute; width: 380px; height: 380px; right: -140px; top: -120px; border-radius: 50%; background: radial-gradient(circle, rgba(95,227,207,0.14), transparent 65%); pointer-events: none; }
          .login-left > * { position: relative; z-index: 1; }
          .login-right { flex: 1; display: flex; align-items: center; justify-content: center; padding: 40px 20px; }
          .login-form-box {
            width: 100%; max-width: 380px; padding: 32px;
            background: linear-gradient(180deg, rgba(255,255,255,0.05), rgba(255,255,255,0.02));
            border: 1px solid var(--border); border-radius: 20px; box-shadow: var(--shadow), 0 30px 80px -40px rgba(125,155,255,0.35);
          }
          .login-label { display: block; font-size: 12.5px; font-weight: 500; color: var(--text-2); margin-bottom: 7px; }
          .login-input {
            width: 100%; padding: 11px 14px; background: rgba(255,255,255,0.04); border: 1px solid var(--border);
            border-radius: 10px; font-size: 14px; color: var(--text); outline: none; transition: border-color 150ms, box-shadow 150ms;
          }
          .login-input:focus { border-color: rgba(125,155,255,0.65); box-shadow: 0 0 0 4px rgba(125,155,255,0.12); }
          .login-btn {
            width: 100%; padding: 12px; border-radius: 10px; border: none; cursor: pointer;
            font-size: 14px; font-weight: 600; color: #fff;
            background: linear-gradient(135deg, #8ea8ff, #6576ff);
            box-shadow: 0 1px 0 rgba(255,255,255,0.25) inset, 0 10px 30px -10px var(--accent-glow);
            display: flex; align-items: center; justify-content: center; gap: 8px; transition: filter 150ms;
          }
          .login-btn:hover { filter: brightness(1.08); }
          .login-btn:disabled { opacity: 0.6; cursor: not-allowed; }
          .gradient-text { background: linear-gradient(100deg, #ffffff, #b8c7ff 45%, #7ff0de); -webkit-background-clip: text; background-clip: text; color: transparent; }

          /* Narrow screens: icon rail becomes a bottom bar */
          @media (max-width: 640px) {
            .sidebar, .sidebar:hover, .sidebar:focus-within { top: auto; right: 0; width: auto; height: 62px; flex-direction: row; border-right: 0; border-top: 1px solid var(--border); box-shadow: none; }
            .sidebar-logo, .sidebar-section-label, .nav-label { display: none; }
            .sidebar-nav { flex-direction: row; justify-content: space-around; padding: 8px; }
            .sidebar-footer { border-top: 0; padding: 8px; }
            .nav-item { width: 48px; height: 46px; justify-content: center; }
            .nav-item.active::before { left: 12px; right: 12px; top: auto; bottom: -8px; width: auto; height: 3px; border-radius: 3px 3px 0 0; }
            .app-main { margin-left: 0; padding-bottom: 70px; }
            .login-left { display: none; }
          }
          @media print { body { background: #fff !important; } }
          @media (prefers-reduced-motion: reduce) { *, *::before, *::after { animation: none !important; transition: none !important; } }
        `}</style>
      </head>
      <body>{children}</body>
    </html>
  );
}
