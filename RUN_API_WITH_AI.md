# Running the Full API with AI Integration

## Quick Start (5 minutes)

### Step 1: Start Database Services

```powershell
cd infra
docker compose up -d
```

Wait for all services to be healthy (check with `docker compose ps`):
```
STATUS: healthy
```

### Step 2: Create Test Audit Data

From project root:

```powershell
python setup_test_audit.py
```

This creates:
- Test organization and user
- Hotel audit with 7 assessed criteria
- 14 evidence files
- Readiness profile with hotel details

### Step 3: Start the API

```powershell
cd services\api
uvicorn app.main:app --reload --port 8000
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Started reloader process
```

API is now running at: http://localhost:8000

### Step 4: Get Auth Token

In a new PowerShell window:

```powershell
$body = @{
    username = "auditor@test.local"
    password = "TestPassword123!"
} | ConvertTo-Json

$response = Invoke-RestMethod -Uri "http://localhost:8000/auth/token" `
    -Method Post `
    -ContentType "application/json" `
    -Body $body

$token = $response.access_token
Write-Output "Token: $token"
```

Save the token for use in API calls.

### Step 5: Test Report Generation (Without AI)

```powershell
$headers = @{
    "Authorization" = "Bearer $token"
}

# Get the audit ID from setup output or query audits endpoint
$auditId = "paste-audit-id-here"

# Get readiness report
Invoke-RestMethod -Uri "http://localhost:8000/hospitality/audits/$auditId/readiness" `
    -Headers $headers | ConvertTo-Json -Depth 10 | Out-File "readiness_report.json"

Write-Output "Readiness report saved to readiness_report.json"
```

## AI Integration (OpenRouter API)

### Get OpenRouter API Key

1. Visit https://openrouter.ai
2. Sign up or log in
3. Go to API keys → Create key
4. Copy your API key

### Configure AI

Edit `.env` file in `services/api/` (create if doesn't exist):

```env
OPENROUTER_API_KEY=sk-or-v1-your-actual-key-here
OPENROUTER_MODEL=openai/gpt-4-turbo
OPENROUTER_REFERER=http://localhost:3000
```

Or edit `services/api/app/config.py` directly:

```python
class Settings(BaseSettings):
    openrouter_api_key: str = "sk-or-v1-your-key"
    openrouter_model: str = "openai/gpt-4-turbo"
```

### Restart API with AI Enabled

```powershell
# Stop the running uvicorn (Ctrl+C)
# Then restart:
uvicorn app.main:app --reload --port 8000
```

## Test Report Generation (With AI)

### Generate AI Narrative for Report

The API will now call OpenRouter to generate:
- Letter summary (personalized intro)
- Readiness statement (hotel's readiness level)
- Pillar-level narratives (A, B, C, D findings)
- Per-criterion analysis
- Top gaps and strengths
- Recommended actions

### Endpoint: Generate AI Report

```powershell
# Request AI-generated narrative
$auditId = "your-audit-id"
$payload = @{} | ConvertTo-Json

$response = Invoke-RestMethod -Uri "http://localhost:8000/hospitality/audits/$auditId/readiness/generate-ai" `
    -Method Post `
    -Headers $headers `
    -ContentType "application/json" `
    -Body $payload

$response | ConvertTo-Json -Depth 10 | Out-File "ai_narrative.json"
```

### What AI Generates

The AI output includes:

```json
{
  "letter_summary": "Dear Ketut, Thank you for hosting...",
  "readiness_statement": "Bali Practice Hotel is at a developing stage...",
  "pillars": {
    "A": {
      "headline": "Governance: Strong foundations with room for improvement",
      "in_place": "Clear policies and management structures",
      "missing": "Automated monitoring systems"
    },
    "B": { ... },
    "C": { ... },
    "D": { ... }
  },
  "criteria": {
    "A1": {
      "evidence_seen": "Policy document signed by GM, published on website",
      "gap": ""
    },
    "A3": {
      "evidence_seen": "Monthly energy and water reports",
      "gap": "Implement automated meter reading to capture all metrics"
    },
    "C1": {
      "evidence_seen": "Waste segregation system in place",
      "gap": "Establish formal 20% waste reduction target within 12 months"
    }
  },
  "strengths": [
    {"text": "Strong environmental policy signed by leadership", "evidence": "documented"},
    {"text": "Comprehensive water consumption tracking", "evidence": "documented"}
  ],
  "top_gaps": [
    {"criterion": "C1", "text": "No formal waste reduction targets despite 45% landfill rate"},
    {"criterion": "A3", "text": "Incomplete environmental monitoring for non-utility metrics"}
  ],
  "actions": [
    {
      "criteria": ["C1"],
      "action": "Establish 20% waste reduction target and implement composting",
      "owner": "Sustainability Manager",
      "evidence": "Quarterly waste reports and process documentation"
    }
  ]
}
```

## Full API Endpoints

### Authentication
```
POST /auth/token
  username: auditor@test.local
  password: TestPassword123!
  Returns: access_token
```

### Audits
```
GET /hospitality/audits
  Returns: List of all audits

GET /hospitality/audits/{audit_id}
  Returns: Full audit detail with assessments and evidence

POST /hospitality/audits
  Payload: {title, site_name, scope_statement}
  Returns: New audit
```

### Reports
```
GET /hospitality/audits/{audit_id}/report?format=json
  Returns: Structured audit data

GET /hospitality/audits/{audit_id}/report?format=markdown
  Returns: Plain-text markdown report

GET /hospitality/audits/{audit_id}/readiness
  Returns: Full readiness assessment with profile and evidence register

POST /hospitality/audits/{audit_id}/readiness/generate-ai
  Returns: AI-generated narrative (requires OPENROUTER_API_KEY)
```

### Assessment Commands
```
POST /hospitality/audits/{audit_id}/commands
  Payload: {
    expected_version: 2,
    operation: "assess",
    input: {
      requirementId: "uuid",
      status: "conforming|observation|minor|major",
      rationale: "Assessment explanation",
      evidenceIds: ["uuid1", "uuid2"]
    }
  }
  Returns: Updated audit with assessment
```

### Evidence Upload
```
POST /hospitality/audits/{audit_id}/files
  Multipart form:
    file: (binary)
    description: "Evidence description"
    expected_version: 2
  Returns: Updated audit with new evidence
```

## Testing Workflow

### 1. View Test Audit
```powershell
$auditId = "from-setup-output"
$headers = @{ "Authorization" = "Bearer $token" }

$audit = Invoke-RestMethod -Uri "http://localhost:8000/hospitality/audits/$auditId" `
    -Headers $headers

$audit | ConvertTo-Json -Depth 20 | Out-File "audit_detail.json"
```

### 2. Generate Reports (No AI)
```powershell
# JSON report
Invoke-RestMethod -Uri "http://localhost:8000/hospitality/audits/$auditId/report?format=json" `
    -Headers $headers | ConvertTo-Json -Depth 10 | Out-File "report.json"

# Markdown report
Invoke-RestMethod -Uri "http://localhost:8000/hospitality/audits/$auditId/report?format=markdown" `
    -Headers $headers | Out-File "report.md"

# Readiness report
Invoke-RestMethod -Uri "http://localhost:8000/hospitality/audits/$auditId/readiness" `
    -Headers $headers | ConvertTo-Json -Depth 20 | Out-File "readiness.json"
```

### 3. Generate with AI Narrative
```powershell
# First, generate AI narrative
Invoke-RestMethod -Uri "http://localhost:8000/hospitality/audits/$auditId/readiness/generate-ai" `
    -Method Post `
    -Headers $headers `
    -ContentType "application/json" `
    -Body '{}'

# Then fetch readiness with AI content
Invoke-RestMethod -Uri "http://localhost:8000/hospitality/audits/$auditId/readiness" `
    -Headers $headers | ConvertTo-Json -Depth 30 | Out-File "readiness_with_ai.json"
```

### 4. View in Browser (Optional)

Start the web frontend:
```powershell
cd apps\web
npm install  # First time only
npm run dev
```

Then visit: http://localhost:3000

Sign in with:
- Email: auditor@test.local
- Password: TestPassword123!

## Troubleshooting

### API Won't Start
```
ImportError: cannot import name '_lenient_issubclass'
```
**Fix:**
```powershell
pip install --upgrade pydantic pydantic-settings
```

### Database Connection Refused
**Fix:**
```powershell
cd infra
docker compose ps  # Check status
docker compose logs db  # View logs
docker compose restart db  # Restart if needed
```

### AI API Not Working
```
Error: openrouter_api_key not set
```
**Fix:**
1. Get key from https://openrouter.ai
2. Set in .env or config.py
3. Restart API
4. Verify with: `echo $env:OPENROUTER_API_KEY`

### Auth Token Expired
Just get a new one:
```powershell
# Repeat the token request
$response = Invoke-RestMethod -Uri "http://localhost:8000/auth/token" ...
$token = $response.access_token
```

## What You Can Test

✓ Report generation (JSON, Markdown, Readiness)
✓ Assessment CRUD operations
✓ Evidence upload and tracking
✓ AI-generated narrative (with API key)
✓ Status transitions (in_progress → reporting)
✓ Profile management (hotel details, reviewer info)
✓ Readiness level calculation
✓ Evidence register generation
✓ Critical gap identification

## Next: Word Export

Once reports are working, add Word export:

```python
from docx import Document
from docx.shared import Inches, Pt

# Load readiness report JSON
# Create Word document with sections
# Export to .docx
```

## Summary

**You now have:**
1. ✓ Full API running
2. ✓ Test audit with realistic data
3. ✓ All report formats (JSON, Markdown, Readiness)
4. ✓ AI integration ready (with OpenRouter API key)
5. ✓ Web UI accessible (optional)

**To test AI:**
1. Get OpenRouter key from https://openrouter.ai
2. Set OPENROUTER_API_KEY in .env
3. Restart API
4. Call `/readiness/generate-ai` endpoint
5. View AI-generated narrative in output

---

Run the setup, start the API, and you're testing the full system with AI integration.
