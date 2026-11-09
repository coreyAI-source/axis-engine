import type { Metadata } from "next";
import { JetBrains_Mono, Montserrat, Source_Sans_3 } from "next/font/google";
import "./globals.css";

// Brand type (Business Plan, Section 8): Montserrat for headings and the wordmark, Source Sans 3 for body copy.
const heading = Montserrat({ subsets: ["latin"], variable: "--font-heading", display: "swap", weight: ["600", "700", "800"] });
const body = Source_Sans_3({ subsets: ["latin"], variable: "--font-body", display: "swap", weight: ["400", "600", "700"] });
const mono = JetBrains_Mono({ subsets: ["latin"], variable: "--font-mono", display: "swap" });

export const metadata: Metadata = {
  title: "AXIS Environmental · Sustainable Hospitality",
  description: "Check your property against the GSTC Hotel Standard, keep evidence in one place and track the actions that prepare you for certification.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={`${heading.variable} ${body.variable} ${mono.variable}`}>
      <head>
        <style>{`
          /* AXIS Environmental palette (Business Plan, Section 8). Light-first for organisation users. */
          :root {
            color-scheme: light;
            --brand-navy: #12346E;
            --brand-ocean: #1F6FB2;
            --brand-teal: #17707D;
            --brand-lagoon: #1A9BB0;
            --brand-leaf: #7FB241;
            --brand-sand: #E9DFC9;
            --brand-stone: #F7F8F5;
            --navy-deep: #0C2452;
            --font-sans: var(--font-body), 'Source Sans 3', Calibri, Arial, sans-serif;
            --font-head: var(--font-heading), Montserrat, Arial, sans-serif;

            --bg: #F7F8F5;
            --surface: #FFFFFF;
            --surface-2: #F1F5F3;
            --surface-solid: #FFFFFF;
            --hover: rgba(18,52,110,0.045);
            --border: #E1E7E4;
            --border-soft: #ECF0EE;
            --border-strong: #C6D0CC;
            --text: #0F2747;
            --text-2: #334A66;
            --text-3: #5A6B82;
            --muted: #6B7A90;
            --faint: #A3AEBD;

            --accent: #1F6FB2;
            --accent-2: #17707D;
            --accent-soft: rgba(31,111,178,0.09);
            --accent-glow: rgba(31,111,178,0.30);
            --green: #6A9A2A;
            --green-text: #3E6B12;
            --green-soft: rgba(127,178,65,0.14);
            --green-line: rgba(127,178,65,0.40);
            --amber: #D08A10;
            --amber-text: #7D5300;
            --amber-soft: rgba(208,138,16,0.12);
            --amber-line: rgba(208,138,16,0.38);
            --red: #C23B30;
            --red-text: #A12A20;
            --red-soft: rgba(194,59,48,0.07);
            --red-line: rgba(194,59,48,0.30);
            --blue: #1F6FB2;
            --blue-text: #15578E;
            --violet: #5B5FA8;
            --orange: #C96A2B;
            --slate: #5A6B82;

            --radius: 16px;
            --radius-sm: 11px;
            --sidebar: 264px;
            --shadow: 0 1px 2px rgba(15,39,71,0.05), 0 6px 18px -10px rgba(15,39,71,0.16);
            --shadow-lg: 0 2px 6px rgba(15,39,71,0.06), 0 24px 48px -24px rgba(15,39,71,0.30);
          }
          *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
          html { font-size: 16px; -webkit-text-size-adjust: 100%; }
          body {
            font-family: var(--font-sans);
            font-size: 15px;
            line-height: 1.5;
            color: var(--text);
            background-color: var(--bg);
            background-image:
              radial-gradient(1100px 520px at 100% -8%, rgba(23,112,125,0.08), transparent 60%),
              radial-gradient(900px 520px at -6% 108%, rgba(31,111,178,0.06), transparent 60%);
            background-attachment: fixed;
            min-height: 100vh;
            -webkit-font-smoothing: antialiased;
            -moz-osx-font-smoothing: grayscale;
          }
          a { text-decoration: none; color: inherit; }
          button, input, textarea, select { font-family: inherit; }
          ::selection { background: rgba(31,111,178,0.22); color: var(--text); }
          ::-webkit-scrollbar { width: 10px; height: 10px; }
          ::-webkit-scrollbar-thumb { background: #CBD5D1; border-radius: 10px; border: 2px solid transparent; background-clip: padding-box; }
          ::-webkit-scrollbar-track { background: transparent; }
          :focus-visible { outline: 2px solid var(--brand-lagoon); outline-offset: 2px; border-radius: 6px; }
          .mono { font-family: var(--font-mono), ui-monospace, Consolas, monospace; }

          /* Brand lockup: the approved globe-and-wave mark on a Stone tile, with the name typeset beside it */
          .brand-mark {
            width: 42px; height: 42px; border-radius: 12px; background: var(--brand-stone); flex-shrink: 0;
            display: grid; place-items: center; overflow: hidden;
            box-shadow: 0 0 0 1px rgba(255,255,255,0.18) inset, 0 6px 18px -8px rgba(0,0,0,0.5);
          }
          .brand-mark img { display: block; width: 31px; height: auto; }
          .brand-lockup { display: flex; align-items: center; gap: 12px; min-width: 0; }
          .brand-word { font-family: var(--font-head); color: #fff; line-height: 1.05; white-space: nowrap; }
          .brand-word b { display: block; font-weight: 800; font-size: 17px; letter-spacing: 0.1em; }
          .brand-word span { display: block; font-weight: 600; font-size: 9.5px; letter-spacing: 0.32em; text-transform: uppercase; color: rgba(255,255,255,0.86); margin-top: 3px; }
          .brand-service { display: block; font-family: var(--font-sans); font-weight: 600; font-size: 10.5px; letter-spacing: 0.14em; text-transform: uppercase; color: var(--brand-sand); margin-top: 6px; }

          /* Sidebar: always-open navigation for organisation users */
          .sidebar {
            position: fixed; top: 0; left: 0; bottom: 0; z-index: 100;
            width: var(--sidebar);
            display: flex; flex-direction: column;
            background: linear-gradient(180deg, #164086 0%, #12346E 42%, #0C2452 100%);
            color: #E8EEF7;
            box-shadow: 1px 0 0 rgba(255,255,255,0.06), 16px 0 40px -28px rgba(12,36,82,0.7);
          }
          .sidebar::after {
            content: ""; position: absolute; inset: auto -40% -10% -40%; height: 60%; pointer-events: none;
            background: radial-gradient(closest-side, rgba(127,178,65,0.16), transparent);
          }
          .sidebar > * { position: relative; z-index: 1; }
          .sidebar-logo { padding: 26px 22px 22px; border-bottom: 1px solid rgba(255,255,255,0.09); }
          .sidebar-nav { flex: 1; padding: 14px 14px; display: flex; flex-direction: column; gap: 3px; overflow-y: auto; overflow-x: hidden; }
          .sidebar-section-label {
            font-size: 10.5px; font-weight: 700; color: rgba(255,255,255,0.46); text-transform: uppercase; letter-spacing: 0.14em;
            padding: 22px 12px 8px;
          }
          .nav-item {
            position: relative; display: flex; align-items: center; gap: 12px;
            height: 44px; width: 100%; padding: 0 12px; border-radius: 12px;
            color: rgba(255,255,255,0.74); font-size: 15px; font-weight: 600; white-space: nowrap;
            cursor: pointer; background: none; border: none; text-align: left;
            transition: color 150ms, background 150ms;
          }
          .nav-icon { width: 20px; display: grid; place-items: center; flex-shrink: 0; }
          .nav-item:hover { color: #fff; background: rgba(255,255,255,0.07); }
          .nav-item.active { color: #fff; background: rgba(255,255,255,0.13); box-shadow: inset 0 0 0 1px rgba(255,255,255,0.08); }
          .nav-item.active .nav-icon { color: var(--brand-leaf); }
          .nav-item.active::before { content: ""; position: absolute; left: -14px; top: 11px; bottom: 11px; width: 3px; border-radius: 0 3px 3px 0; background: var(--brand-leaf); }
          .nav-item.nav-small { font-size: 14px; font-weight: 500; color: rgba(255,255,255,0.62); height: 40px; }
          .sidebar-footer { padding: 14px; border-top: 1px solid rgba(255,255,255,0.09); display: flex; flex-direction: column; gap: 6px; }
          .user-card { display: flex; align-items: center; gap: 11px; padding: 10px; border-radius: 13px; background: rgba(255,255,255,0.06); min-width: 0; }
          .avatar {
            width: 36px; height: 36px; border-radius: 50%; flex-shrink: 0; display: grid; place-items: center;
            font-family: var(--font-head); font-size: 12.5px; font-weight: 700; color: #fff;
            background: linear-gradient(135deg, var(--brand-lagoon), var(--brand-ocean));
          }
          .user-meta { min-width: 0; display: flex; flex-direction: column; }
          .user-name { font-size: 14px; font-weight: 600; color: #fff; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
          .user-role { font-size: 12.5px; color: rgba(255,255,255,0.62); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
          .signout {
            display: flex; align-items: center; gap: 10px; height: 38px; padding: 0 12px; border-radius: 11px;
            border: 0; background: none; color: rgba(255,255,255,0.7); font-size: 14px; font-weight: 600; cursor: pointer; width: 100%;
          }
          .signout:hover { color: #fff; background: rgba(255,255,255,0.07); }

          /* Layout shell */
          .app-shell { min-height: 100vh; }
          .app-main { margin-left: var(--sidebar); min-height: 100vh; min-width: 0; }
          .page-content { padding: 40px clamp(20px, 4vw, 56px) 80px; max-width: 1240px; margin: 0 auto; }

          /* Headings */
          .page-heading { font-family: var(--font-head); font-size: 30px; font-weight: 700; letter-spacing: -0.02em; line-height: 1.18; color: var(--brand-navy); }
          .page-subheading { font-size: 15px; color: var(--text-3); margin-top: 8px; max-width: 680px; }
          .eyebrow { font-size: 11.5px; font-weight: 700; letter-spacing: 0.14em; text-transform: uppercase; color: var(--accent-2); margin-bottom: 8px; }

          /* Cards */
          .card { background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius); box-shadow: var(--shadow); }
          .card-header { padding: 20px 24px 16px; border-bottom: 1px solid var(--border-soft); display: flex; align-items: center; justify-content: space-between; gap: 12px; }
          .card-title { font-family: var(--font-head); font-size: 15.5px; font-weight: 700; color: var(--text); }
          .card-subtitle { font-size: 13.5px; color: var(--muted); margin-top: 3px; }

          /* Stat card */
          .stat-card {
            position: relative; overflow: hidden; height: 100%;
            background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius);
            padding: 20px 20px 18px; box-shadow: var(--shadow);
            transition: transform 180ms, border-color 180ms, box-shadow 180ms;
          }
          .stat-card::before { content: ""; position: absolute; inset: 0 0 auto 0; height: 3px; background: var(--tone, var(--accent)); opacity: 0.85; }
          .stat-card:hover { transform: translateY(-2px); border-color: var(--border-strong); box-shadow: var(--shadow-lg); }
          .stat-icon { width: 36px; height: 36px; border-radius: 11px; display: grid; place-items: center; margin-bottom: 16px; }
          .stat-number { font-family: var(--font-head); font-size: 30px; font-weight: 700; color: var(--text); letter-spacing: -0.03em; line-height: 1; font-variant-numeric: tabular-nums; }
          .stat-label { font-size: 14px; color: var(--text-2); margin-top: 8px; font-weight: 600; }
          .stat-hint { font-size: 12.5px; color: var(--muted); margin-top: 2px; }

          /* Hero: the one thing to do next */
          .hero {
            position: relative; overflow: hidden;
            display: flex; align-items: center; justify-content: space-between; gap: 24px; flex-wrap: wrap;
            padding: 30px 34px; border-radius: 20px; color: #fff;
            background: linear-gradient(125deg, #12346E 0%, #165A8C 58%, #17707D 100%);
            box-shadow: var(--shadow-lg);
          }
          .hero::after { content: ""; position: absolute; right: -60px; top: -90px; width: 320px; height: 320px; border-radius: 50%; background: radial-gradient(circle, rgba(127,178,65,0.35), transparent 65%); pointer-events: none; }
          .hero > * { position: relative; z-index: 1; }
          .hero-eyebrow { font-size: 11.5px; font-weight: 700; letter-spacing: 0.14em; text-transform: uppercase; color: var(--brand-sand); }
          .hero-title { font-family: var(--font-head); font-size: 24px; font-weight: 700; letter-spacing: -0.015em; color: #fff; margin: 8px 0 6px; line-height: 1.25; }
          .hero-text { font-size: 15px; color: rgba(255,255,255,0.82); max-width: 600px; }
          .hero-btn {
            display: inline-flex; align-items: center; gap: 9px; white-space: nowrap;
            padding: 13px 20px; border-radius: 13px; background: #fff; color: var(--brand-navy);
            font-size: 15px; font-weight: 700; box-shadow: 0 10px 24px -12px rgba(0,0,0,0.45);
            transition: transform 150ms, box-shadow 150ms;
          }
          .hero-btn:hover { transform: translateY(-1px); box-shadow: 0 14px 28px -12px rgba(0,0,0,0.5); }

          /* Two-column overview */
          .overview-grid { display: grid; grid-template-columns: minmax(0, 1.5fr) minmax(0, 1fr); gap: 20px; align-items: start; }
          .timeline { list-style: none; padding: 20px 24px 22px; display: flex; flex-direction: column; }
          .timeline li { position: relative; display: grid; grid-template-columns: 34px 1fr; gap: 14px; padding-bottom: 18px; }
          .timeline li:last-child { padding-bottom: 0; }
          .timeline li:not(:last-child)::after { content: ""; position: absolute; left: 16px; top: 36px; bottom: 2px; width: 2px; background: var(--border); border-radius: 2px; }
          .timeline-num { width: 34px; height: 34px; border-radius: 11px; display: grid; place-items: center; font-family: var(--font-head); font-size: 13px; font-weight: 700; color: var(--brand-navy); background: var(--accent-soft); border: 1px solid rgba(31,111,178,0.22); }
          .timeline strong { display: block; font-size: 15px; font-weight: 700; color: var(--text); margin-top: 4px; }
          .timeline p { font-size: 14px; color: var(--text-3); margin-top: 3px; }
          .timeline-note { margin: 0 24px 22px; padding: 14px 16px; border-radius: var(--radius-sm); background: var(--brand-stone); border: 1px solid var(--border-soft); font-size: 13.5px; color: var(--text-2); }

          /* Rows and list items */
          .row-item { display: flex; align-items: center; justify-content: space-between; gap: 14px; padding: 15px 24px; cursor: pointer; transition: background 140ms; border-bottom: 1px solid var(--border-soft); }
          .row-item:last-child { border-bottom: none; }
          .row-item:hover { background: var(--surface-2); }
          .hover-row { transition: background 120ms; }
          .hover-row:hover { background: var(--surface-2); }
          .dot { width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0; }

          /* Badges */
          .badge { display: inline-flex; align-items: center; gap: 6px; font-size: 12px; font-weight: 600; padding: 3px 10px; border-radius: 20px; border: 1px solid; white-space: nowrap; }
          .badge-red    { background: var(--red-soft);   color: var(--red-text);   border-color: var(--red-line); }
          .badge-orange { background: rgba(201,106,43,0.09); color: #97491A; border-color: rgba(201,106,43,0.28); }
          .badge-yellow { background: var(--amber-soft); color: var(--amber-text); border-color: var(--amber-line); }
          .badge-green  { background: var(--green-soft); color: var(--green-text); border-color: var(--green-line); }
          .badge-blue   { background: var(--accent-soft); color: var(--blue-text); border-color: rgba(31,111,178,0.26); }
          .badge-violet { background: rgba(91,95,168,0.10); color: #41448A; border-color: rgba(91,95,168,0.28); }
          .badge-slate  { background: #F1F4F6; color: var(--text-3); border-color: var(--border); }

          /* Buttons */
          .btn {
            display: inline-flex; align-items: center; justify-content: center; gap: 8px;
            font-size: 14px; font-weight: 600; padding: 10px 17px; border-radius: 12px;
            border: 1px solid transparent; cursor: pointer; white-space: nowrap;
            transition: background 150ms, border-color 150ms, box-shadow 150ms, transform 150ms, color 150ms;
          }
          .btn:active { transform: translateY(1px); }
          .btn-primary {
            color: #fff; background: var(--accent);
            box-shadow: 0 1px 0 rgba(255,255,255,0.18) inset, 0 8px 18px -10px rgba(31,111,178,0.75);
          }
          .btn-primary:hover { background: #195D98; }
          .btn-dark { color: #fff; background: var(--brand-navy); box-shadow: 0 6px 16px -10px rgba(18,52,110,0.8); }
          .btn-dark:hover { background: #0F2B5C; }
          .btn-ghost { background: #fff; color: var(--text-2); border-color: var(--border-strong); }
          .btn-ghost:hover { background: var(--surface-2); color: var(--text); border-color: #AEBBB6; }
          .btn:disabled { opacity: 0.5; cursor: not-allowed; }

          /* Inputs */
          .input {
            background: #fff; border: 1px solid var(--border-strong); border-radius: 11px;
            padding: 10px 13px; font-size: 14px; color: var(--text); outline: none;
            transition: border-color 150ms, box-shadow 150ms;
          }
          .input::placeholder { color: var(--faint); }
          .input:focus { border-color: var(--brand-ocean); box-shadow: 0 0 0 4px rgba(31,111,178,0.13); }

          /* Table */
          .table { width: 100%; border-collapse: collapse; }
          .table th { padding: 11px 16px; text-align: left; font-size: 11px; font-weight: 700; color: var(--muted); text-transform: uppercase; letter-spacing: 0.08em; background: var(--surface-2); border-bottom: 1px solid var(--border-soft); }
          .table td { padding: 13px 16px; border-bottom: 1px solid var(--border-soft); font-size: 14px; }
          .table tr:last-child td { border-bottom: none; }
          .table tr:hover td { background: var(--surface-2); }

          .spinner { border: 2.5px solid rgba(31,111,178,0.18); border-top-color: var(--accent); border-radius: 50%; animation: spin 0.7s linear infinite; }
          .spinner-white { border-color: rgba(255,255,255,0.35); border-top-color: #fff; }
          @keyframes spin { to { transform: rotate(360deg); } }
          @keyframes rise { from { opacity: 0; transform: translateY(6px); } to { opacity: 1; transform: none; } }
          .page-content > * { animation: rise 340ms cubic-bezier(.2,.7,.2,1) both; }

          .alert-error { background: var(--red-soft); border: 1px solid var(--red-line); border-radius: 12px; padding: 14px 16px; color: var(--red-text); font-size: 14px; }

          /* Grid helpers */
          .grid-5 { display: grid; grid-template-columns: repeat(auto-fit, minmax(170px, 1fr)); gap: 14px; }
          .grid-2 { display: grid; grid-template-columns: repeat(auto-fit, minmax(min(100%, 380px), 1fr)); gap: 20px; }
          .grid-sidebar { display: grid; grid-template-columns: minmax(0, 1fr) 340px; gap: 16px; align-items: start; }
          .grid-4 { display: grid; grid-template-columns: repeat(auto-fit, minmax(130px, 1fr)); gap: 12px; }
          @media (max-width: 1000px) { .grid-sidebar, .overview-grid { grid-template-columns: minmax(0, 1fr); } }

          /* Sign-in */
          .login-wrap { display: flex; min-height: 100vh; }
          .login-left {
            position: relative; overflow: hidden; color: #fff;
            width: min(48%, 580px); flex-shrink: 0;
            background:
              linear-gradient(160deg, rgba(12,36,82,0.86) 0%, rgba(18,52,110,0.93) 60%, rgba(23,112,125,0.94) 100%),
              url(/brand/axis-coastal-banner.jpg) center / cover no-repeat,
              var(--navy-deep);
            display: flex; flex-direction: column; justify-content: space-between; gap: 40px; padding: 48px 52px;
          }
          .login-left > * { position: relative; z-index: 1; }
          .login-headline { font-family: var(--font-head); font-size: 32px; font-weight: 700; line-height: 1.22; letter-spacing: -0.02em; color: #fff; }
          .login-lede { font-size: 16px; color: rgba(255,255,255,0.8); line-height: 1.6; margin-top: 16px; max-width: 440px; }
          .login-points { display: flex; flex-direction: column; gap: 18px; margin-top: 36px; }
          .login-point { display: flex; gap: 14px; }
          .login-point-icon { width: 30px; height: 30px; border-radius: 10px; flex-shrink: 0; display: grid; place-items: center; background: rgba(127,178,65,0.2); border: 1px solid rgba(127,178,65,0.5); color: var(--brand-leaf); }
          .login-point strong { display: block; font-size: 15px; font-weight: 700; color: #fff; }
          .login-point span { display: block; font-size: 14px; color: rgba(255,255,255,0.72); margin-top: 2px; line-height: 1.5; }
          .login-note { font-size: 13px; line-height: 1.55; color: rgba(255,255,255,0.7); padding-top: 18px; border-top: 1px solid rgba(255,255,255,0.14); }
          .login-right { flex: 1; display: flex; align-items: center; justify-content: center; padding: 48px 24px; background: var(--surface); }
          .login-form-box { width: 100%; max-width: 400px; }
          .login-mobile-brand { display: none; margin-bottom: 32px; }
          .login-label { display: block; font-size: 14px; font-weight: 600; color: var(--text-2); margin-bottom: 8px; }
          .login-input {
            width: 100%; padding: 12px 14px; background: #fff; border: 1px solid var(--border-strong);
            border-radius: 11px; font-size: 15px; color: var(--text); outline: none; transition: border-color 150ms, box-shadow 150ms;
          }
          .login-input:focus { border-color: var(--brand-ocean); box-shadow: 0 0 0 4px rgba(31,111,178,0.14); }
          .login-btn {
            width: 100%; padding: 13px; border-radius: 12px; border: none; cursor: pointer;
            font-size: 15px; font-weight: 700; color: #fff; background: var(--accent);
            box-shadow: 0 1px 0 rgba(255,255,255,0.18) inset, 0 12px 24px -14px rgba(31,111,178,0.9);
            display: flex; align-items: center; justify-content: center; gap: 8px; transition: background 150ms;
          }
          .login-btn:hover { background: #195D98; }
          .login-btn:disabled { opacity: 0.6; cursor: not-allowed; }
          .gradient-text { color: #fff; }

          /* Narrow screens: the sidebar becomes a bottom bar and the sign-in panel gets its own brand */
          @media (max-width: 900px) {
            .sidebar { top: auto; right: 0; width: auto; height: 68px; flex-direction: row; background: var(--brand-navy); box-shadow: 0 -10px 30px -18px rgba(12,36,82,0.7); }
            .sidebar::after { display: none; }
            .sidebar-logo, .sidebar-advisor, .user-card { display: none; }
            .sidebar-nav { flex-direction: row; flex: 1; justify-content: space-around; align-items: stretch; padding: 6px 8px; overflow: visible; }
            .nav-item { flex: 1; width: auto; height: auto; flex-direction: column; justify-content: center; gap: 4px; padding: 6px 2px; font-size: 11.5px; }
            .nav-item .nav-label { display: block; font-size: 11.5px; }
            .nav-item.active::before { display: none; }
            .nav-item.active { box-shadow: none; background: rgba(255,255,255,0.12); }
            .sidebar-footer { flex-direction: row; padding: 6px 8px; border-top: 0; }
            .signout { flex-direction: column; justify-content: center; gap: 4px; height: auto; font-size: 11.5px; width: 64px; padding: 6px 2px; }
            .app-main { margin-left: 0; padding-bottom: 92px; }
            .page-content { padding: 26px 16px 40px; }
            .page-heading { font-size: 25px; }
            .login-wrap { flex-direction: column; }
            .login-left { display: none; }
            .login-right { align-items: flex-start; padding: 40px 20px; }
            .login-mobile-brand { display: block; }
          }
          @media (prefers-reduced-motion: reduce) { *, *::before, *::after { animation: none !important; transition: none !important; } }
          @media print { body { background: #fff !important; } }
        `}</style>
      </head>
      <body>{children}</body>
    </html>
  );
}
