# Quick Start - Run the Full API with AI

## In 3 Commands

### Command 1: Setup (One time)
```powershell
.\setup_and_run.ps1
```

This:
- Fixes dependencies
- Starts Docker (PostgreSQL, Redis, MinIO)
- Creates test audit data
- Shows you next steps

### Command 2: Start API (In first PowerShell window)
```powershell
cd services\api
uvicorn app.main:app --reload --port 8000
```

Wait for: `INFO: Uvicorn running on http://127.0.0.1:8000`

### Command 3: Get Token & Test (In second PowerShell window)
```powershell
. .\get_token.ps1
. .\test_api.ps1
```

This:
- Gets your auth token
- Tests all report endpoints
- Generates readiness_report.json, audit_report.json, audit_report.md
- Tests AI integration (if OpenRouter is configured)

## What You Get

After running those 3 commands:

✓ API running at http://localhost:8000
✓ Test audit with 7 criteria, mixed statuses, 14 evidence items
✓ Readiness report generated (full assessment)
✓ JSON audit export (structured data)
✓ Markdown report (email-safe)
✓ AI ready (if you add OpenRouter API key)

## View the Reports

**Open in VS Code:**
```
readiness_report.json
audit_report.json
audit_report.md
```

All reports are complete and ready to use.

## Enable AI Integration

Get a free API key from https://openrouter.ai

Create `.env` file in `services/api/`:
```
OPENROUTER_API_KEY=sk-or-v1-your-key-here
```

Restart the API and run tests again:
```powershell
# Stop uvicorn (Ctrl+C)
uvicorn app.main:app --reload --port 8000
. .\test_api.ps1
```

Now you'll also get `ai_narrative.json` with AI-generated content.

## Troubleshooting

### "Docker not found"
- Install Docker Desktop from https://www.docker.com/products/docker-desktop
- Then run `.\setup_and_run.ps1` again

### "Connection refused" on API startup
- Run: `docker compose ps` in `infra/` folder
- If services aren't running, restart: `docker compose up -d`
- Wait 30 seconds for database to be healthy

### "Auth token failed"
- Make sure database is healthy: `docker compose ps`
- Check test data was created: `python setup_test_audit.py`
- Then try: `. .\get_token.ps1`

### "AI endpoint not found"
- That's normal without OpenRouter setup
- All other endpoints work fine
- AI is optional

## Web UI (Optional)

After API is running:

```powershell
cd apps\web
npm install  # First time only
npm run dev
```

Visit: http://localhost:3000

Sign in:
- Email: auditor@test.local
- Password: TestPassword123!

## API Documentation

Once running, view interactive docs at:

http://localhost:8000/docs (Swagger UI)
http://localhost:8000/redoc (ReDoc)

## Test Files

- `setup_and_run.ps1` - One-click setup
- `get_token.ps1` - Get auth token
- `test_api.ps1` - Test all endpoints
- `test_audit_local.py` - Local test (no database)

## What's in the Test Audit

**Hotel:** Bali Practice Hotel
**Location:** Ubud, Bali, Indonesia
**Status:** Reporting (ready for final review)

**Criteria Assessed:**
- A1: Environmental policy - Conforming
- A2: Management plan - Conforming
- A3: Monitoring - Partly met
- B1: Water consumption - Conforming
- B2: Water sources - Met
- C1: Waste reduction - **NOT MET** (critical gap)
- D1: Staff wellbeing - Conforming

**Evidence:** 14 files (policies, photos, records, spreadsheets)

## What's Generated

1. **readiness_report.json**
   - Full readiness assessment
   - Hotel profile
   - Criteria details
   - Evidence register
   - Ready for Word conversion

2. **audit_report.json**
   - Structured audit data
   - All assessments
   - Evidence with metadata
   - API export format

3. **audit_report.md**
   - Plain-text markdown
   - Email/git safe
   - Human readable
   - Share easily

4. **ai_narrative.json** (if AI enabled)
   - Generated letter summary
   - Pillar-level narratives
   - Per-criterion analysis
   - Top gaps and strengths
   - Recommended actions

## Next Steps

- [ ] Run `.\setup_and_run.ps1`
- [ ] Start API with uvicorn
- [ ] Run `. .\get_token.ps1`
- [ ] Run `. .\test_api.ps1`
- [ ] Review generated reports
- [ ] (Optional) Add OpenRouter API key for AI
- [ ] (Optional) Test web UI with `npm run dev`
- [ ] (Optional) Convert JSON to Word with python-docx

---

**You're ready to test the full system in 5 minutes.**
