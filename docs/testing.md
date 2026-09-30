# Testing AXIS

## Hospitality pilot checks (29 September 2026)

The engine suite now includes the server bridge and fictional hotel template: **48 tests passed**, with TypeScript validation passing. Ten additional API integration scenarios exercise the real Node bridge and real signed user sessions against an isolated in-memory SQLite database. They cover the full hotel lifecycle, authenticated independent verification, persisted reloads, file-byte roundtrips, tenant boundaries, role checks, forged input rejection and stale saves/uploads.

Migration `0002` adds the hotel tables and has been applied to the configured Neon database. No existing records were reset. The latest run instructions and hands-on demo checklist are in [the hospitality pilot guide](hospitality-pilot.md). Historical results below describe the earlier ZIP import and dashboard fix.

## Dashboard fix verified on 29 September 2026

The configured database was Neon. Login, dashboard summary, process listing and monitoring-task listing returned HTTP 200 after correcting the ORM choice fields to use text storage, matching migration 0001. Previously, PostgreSQL rejected comparisons between the migrated VARCHAR columns and native enum parameters, causing a dashboard HTTP 500 that the web page incorrectly labelled as a connection failure.

All 17 API tests passed, including dashboard counts and PostgreSQL query-binding regressions. No database reset or reseeding was needed. If the API is started without `--reload`, restart it after updating these models. The read-only `services/api/scripts/check_dashboard.py` diagnostic can check the dashboard queries using the configured database without changing records.

## Verified during this update

On 28 September 2026, with Node 22.20.0 and TypeScript 5.9.3:

- `npm test` from the project root: **41 passed, 0 failed** (including all three demo audit cycles and 10 new regression tests).
- `npm run typecheck` from the project root: **passed**.
- All three fictional Markdown reports regenerated successfully.

API tests, the web build/browser flow, Docker services and mobile were **not verified**. Existing OneDrive files could not all be read, Docker was unavailable, and the Python runtime was blocked in the sandbox.

## 1. New engine: no database needed

Open a terminal in the `axis-engine` folder. Node.js 22.6+ is required (22.20 was available during import).

```powershell
node --version
npm test
npm run demo
npm run setup:engine
npm run typecheck
```

Expected: the Node test runner reports zero failures. The demo runs complete ISO, offshore and hospitality audit cycles and writes:

- `packages/engine/demo-output/iso-report.md`
- `packages/engine/demo-output/offshore-report.md`
- `packages/engine/demo-output/hospitality-report.md`

Open these reports and check source references, evidence descriptions, corrective action owners/deadlines and verification. The hospitality example must remain non-favourable despite action closure because it records a major finding at audit time. Demo attachments are fictional references, not actual PDFs.

The first two commands do not install dependencies or need the internet. `setup:engine` installs the locked development dependencies; `typecheck` then checks both source and tests. These checks exercise the **new library**, not the existing Python API or browser UI.

## 2. Existing API and website

Before this part, ensure OneDrive has finished syncing the project: in File Explorer choose **Always keep on this device** for `axis-engine`. Some existing source and dependency files timed out as cloud placeholders during the import. Install/start Docker Desktop, Python and Node if missing. Docker was not available in the testing environment.

In PowerShell from `axis-engine`:

```powershell
docker compose -f infra/compose.yaml config
docker compose -f infra/compose.yaml up -d
docker compose -f infra/compose.yaml ps -a
```

Database and Redis should become healthy, MinIO should stay running and `minio-init` should exit with code 0 after creating the private `axis-evidence` bucket. MinIO's local console is http://localhost:9001 (local demo credentials are in the Compose file).

Set up the API:

```powershell
cd services/api
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
if (-not (Test-Path .env)) { Copy-Item .env.example .env }
.\.venv\Scripts\python.exe -m pytest tests -v
.\.venv\Scripts\python.exe -m alembic upgrade head
.\.venv\Scripts\python.exe -m seed.run_seed
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

Use a local development database for migrations and seed data. If `.env` already exists, check that it targets the local Compose services before those commands; do not overwrite a working configuration. Existing tests use an in-memory SQLite fixture and cover scoring and scheduling, rather than a full API audit lifecycle.

API docs: http://localhost:8000/docs. In a **second terminal**, from `axis-engine`:

```powershell
cd apps/web
npm ci
npm run build
npm run dev
```

Open http://localhost:3000 and sign in using the seeded demo account:

- Email: `admin@demo.local`
- Password: `changeme123`

Check login, dashboard, process list/details and monitoring. Check browser and API terminal errors. Audit, finding/action and report UI flows are not complete; the shared TypeScript engine is not yet connected to these pages. The web package's Playwright command has no implemented test suite in the current project.

## 3. Mobile and background jobs

Mobile remains a scaffold, so it is not yet a complete test target. `apps/mobile/.env.example` documents the API address setting; a physical phone needs the computer's reachable LAN address rather than `localhost`.

The API contains Celery worker/scheduler code, but parts of follow-up/lag handling and actual email delivery are unfinished. Do not treat the presence of those tasks as verified notifications. Full API/browser, Docker, mobile and worker integration checks remain to be completed on a machine with the prerequisites and all source files available locally.
