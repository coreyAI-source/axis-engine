# AXIS Integrated Compliance Engine

Compliance platform prototype with a hotel-audit pilot: Next.js web interface, FastAPI backend, PostgreSQL/Neon persistence and a shared TypeScript rules engine. Mobile remains a separate scaffold.

## Start the hospitality pilot

Your existing setup uses **Neon**. Keep `services/api/.env`; no Docker or reseeding is needed for the new hotel module when your existing login works.

From this `axis-engine` folder, in the API terminal:

```powershell
cd services/api
.\.venv\Scripts\python.exe -m alembic upgrade head
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

In a second terminal, also starting from `axis-engine`:

```powershell
cd apps/web
npm run dev
```

Open **http://localhost:3000/hospitality** and sign in. Node.js 22.6+ must be available to the website and the API's rules bridge. The hotel module supports audits, criteria/review, assessments, private uploads, findings/actions, independent verification, team accounts and reports. Audit records, frozen scoring configuration and files are saved in Neon.

New hotel audits start with all **40 criteria of the GSTC Hotel Standard v4.0** (December 30, 2025), with their 205 performance indicators and the Annex guidelines, reproduced verbatim from the official PDF (`packages/engine/src/gstc-hotel-v4-data.ts`). Audits created earlier keep their original eight fictional demo criteria. The **Readiness report** tab builds the AXIS Sustainability Readiness Review (covering letter, gap analysis, phased action plan, registers) from the audit, with optional AI-drafted wording via OpenRouter, and downloads it as an editable Word document. Run `alembic upgrade head` once after updating, and set `OPENROUTER_API_KEY` in `services/api/.env` to enable AI drafting. See the [hotel pilot walkthrough](docs/hospitality-pilot.md) and [GSTC source/review notes](docs/gstc-hotel-review.md). Scoring bands, severity definitions, critical flags and deadlines are still AXIS settings awaiting your dad's approval; production hosting and backup/recovery setup remain outstanding.

## Current status and ZIP additions

The supplied `axis-engine.zip` is now included under [`packages/engine`](packages/engine). It adds ISO, offshore and hospitality audit rules: requirement review, evidence checks, assessment snapshots, findings, corrective actions, independent verification, monitoring flags, provisional hospitality scoring and Markdown reports. Its fictional demo audits run without a database or browser.

The engine can run standalone and now powers the **hospitality web workflow**, through a server-side Node bridge called by FastAPI. The older ISO web/mobile workflows have not been migrated to it. The ZIP's D1/R2/Vinext sketch has not replaced this project's architecture.

Also added: local Docker Compose infrastructure, example environment files, root test/demo commands and fixes with regression coverage for gaps found in the imported engine. See [integration notes](docs/engine-integration.md) for details and [the test guide](docs/testing.md) for full instructions.

### Test the new engine first

From this `axis-engine` folder, using Node.js 22.6 or later:

```powershell
npm test
npm run demo
npm run setup:engine
npm run typecheck
```

Tests and demos need only Node. The setup command installs the locked development dependencies for type-checking. Demo reports are written to `packages/engine/demo-output/`.

## Alternative local infrastructure and legacy modules

Use this setup only for a separate local database and storage stack. It is not required for the existing Neon-backed hotel pilot above. Do not replace a working `.env` just to follow these optional steps.

### 1. Start infrastructure

```bash
cd axis-engine/infra
docker compose up -d
```

### 2. Run the API

```bash
cd axis-engine/services/api
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Apply migrations
alembic upgrade head

# Seed reference data and demo org
python -m seed.run_seed

# Start API
uvicorn app.main:app --reload
```

API docs: http://localhost:8000/docs

### 3. Run background workers (optional for Phase 1)

```bash
# In separate terminals:
celery -A app.tasks.celery_app worker --loglevel=info
celery -A app.tasks.celery_app beat --loglevel=info
```

### 4. Start the web app

```bash
cd axis-engine/apps/web
npm install
npm run dev
```

Web app: http://localhost:3000

### 5. Mobile scaffold (unfinished)

The mobile app still needs its application setup, login and evidence/offline workflows before a full test. Its intended development command is:

```bash
cd axis-engine/apps/mobile
npm install
npx expo start
```

### 6. Run tests

```bash
cd axis-engine/services/api
pytest tests/ -v
```

---

## Environment Variables

Copy `.env.example` to `.env` in `services/api/` only if `.env` does not already exist. The values are for local development. For a step-by-step Windows setup, use [the test guide](docs/testing.md).

```
DATABASE_URL=postgresql+asyncpg://axis:axis@localhost:5432/axis_db
DATABASE_URL_SYNC=postgresql://axis:axis@localhost:5432/axis_db
SECRET_KEY=change-me-in-production
REDIS_URL=redis://localhost:6379/0
STORAGE_ENDPOINT=http://localhost:9000
STORAGE_ACCESS_KEY=minioadmin
STORAGE_SECRET_KEY=minioadmin
```

---

## Project Structure

```
axis-engine/
  packages/engine/       Shared TypeScript rules, tests and fictional demo reports
  services/api/          FastAPI backend
    app/
      models/            SQLAlchemy ORM models
      schemas/           Pydantic request/response schemas
      routers/           FastAPI route handlers (one per domain)
      services/          Business logic (monitoring, audit, reporting)
      tasks/             Celery tasks (lag monitor, scheduler)
      utils/             Security, scoring, storage
    alembic/             Database migrations
    seed/                Reference data and demo seed scripts
    tests/               pytest test suite
  apps/web/              Next.js admin UI
  apps/mobile/           React Native / Expo mobile audit app
  infra/                 Docker Compose
  docs/                  Architecture and lifecycle documentation
```

---

## Project Status

| Area | Status |
|------|--------|
| Shared rules engine | Tested rules plus a server bridge for the hotel pilot |
| Python API | Hotel lifecycle, evidence, reports, permissions and concurrency covered by integration tests; legacy modules need wider integration coverage |
| Hospitality web | Hotel audits, criteria/review, assessments, uploads, findings/actions, verification, team accounts and reports |
| Other web modules | Existing login/dashboard/process/monitoring pages; older ISO workflows remain separate |
| Mobile | Audit list/response scaffold; app setup, login, evidence capture and offline support unfinished |
| Infrastructure | Local Compose and sample configuration added; Docker execution not verified here |
| Production readiness | Hotel pilot has persistence, tenant/role checks and server rules. Real standard pack, business approval, hosting/backups, broader legacy security and notification delivery remain |

Keep the project available locally in OneDrive so source/dependency files do not stall during startup. See [testing notes](docs/testing.md) for verified checks and remaining browser/deployment checks.

---

## Demo Credentials

After running seed:
- Email: `admin@demo.local`
- Password: `changeme123`
