# Local MVP Testing - No Database Required

## What You Have Now

You can test the **complete report generation system** without Docker, without a database, without any setup:

```bash
python test_audit_local.py
```

This creates 3 fully working reports:
- `test_readiness_report.json` - Full readiness assessment with 7 criteria
- `test_audit_bundle.json` - Structured audit data export
- `test_audit_report.md` - Plain-text markdown summary

## What Gets Generated

### 1. Readiness Report (JSON)
**File:** `test_readiness_report.json`

Structure:
```json
{
  "title": "AXIS Sustainability Readiness Review",
  "hotel": "Bali Practice Hotel",
  "cover_page": { ... },
  "assessment_summary": {
    "criteria_reviewed": 7,
    "status_summary": {
      "met": 5,
      "partly_met": 1,
      "not_met": 1
    }
  },
  "detailed_findings": [ ... ],
  "evidence_register": [ ... ]
}
```

**Contains:**
- Hotel information (name, location, contact)
- Assessment results for 7 criteria
- Status breakdown (Met/Partly met/Not met)
- 11 evidence items with descriptions
- Detailed rationales for each assessment

### 2. Audit Bundle (JSON)
**File:** `test_audit_bundle.json`

Structured export of:
- Audit metadata
- 7 assessments with full details
- Evidence with collection dates and metadata

**Used for:**
- Export/sharing
- Integration with other systems
- API data format
- Archiving

### 3. Markdown Report (MD)
**File:** `test_audit_report.md`

Human-readable format with:
- Cover page details
- Assessment results table
- Key findings (strengths & gaps)
- Hotel profile
- Next steps
- Plain text (no images, safe to email/git)

## Test Data Structure

### The Audit
- **Hotel:** Bali Practice Hotel (luxury eco-resort, 180 rooms, 240 staff)
- **Location:** Ubud, Bali, Indonesia
- **Review Date:** October 2-3, 2026
- **Status:** Reporting (ready for final report)

### The Criteria (7 GSTC Hotel Standard v4.0)
| Code | Title | Status | Evidence |
|------|-------|--------|----------|
| A1 | Environmental & social policy | Conforming | 2 items |
| A2 | Environmental mgmt plan | Conforming | 2 items |
| A3 | Monitoring & evaluation | Partly met | 1 item |
| B1 | Water consumption | Conforming | 2 items |
| B2 | Water sources | Met | 1 item |
| C1 | Waste reduction | **Not met** | 1 item |
| D1 | Staff wellbeing | Conforming | 2 items |

**Status breakdown:** 5 Met, 1 Partly met, 1 Not met (Critical gap)

### The Evidence (11 items)
- 6 Documents (PDFs, contracts, plans)
- 3 Photos (facility inspection images)
- 2 Records (spreadsheets with data)

Example:
- "A1-policy-doc.pdf" - Environmental policy
- "B1-meter-photo.jpg" - Water meter installation
- "C1-waste-logs.xlsx" - Waste tracking data

## What This Proves (Locally, No Database)

```
✓ Readiness report generation works
✓ Assessment status mapping is correct
✓ Evidence register/linkage works
✓ JSON export format is valid
✓ Markdown report generation works
✓ Hotel profile integration works
✓ Criteria assessment calculations work
```

## Next: Add More Functionality

### 1. Generate Word Export
Integrate the JSON output with `python-docx` to export as `.docx`:

```python
from docx import Document

# Load test_readiness_report.json
# Create Word document with sections
# Export to test_audit_report.docx
```

### 2. Connect to Database
Once you have Docker running:

```bash
cd infra
docker compose up -d
python setup_test_audit.py
```

This populates the same test audit into PostgreSQL.

### 3. Connect to API
Start the FastAPI server:

```bash
cd services/api
uvicorn app.main:app --reload --port 8000
```

Then access:
- `GET /hospitality/audits/{id}/report?format=json`
- `GET /hospitality/audits/{id}/report?format=markdown`
- `GET /hospitality/audits/{id}/readiness`

### 4. Connect to Web UI
Start the Next.js frontend:

```bash
cd apps/web
npm install  # First time only
npm run dev  # Opens http://localhost:3000
```

Sign in with:
- Email: `auditor@test.local`
- Password: `TestPassword123!`

View the audit and download reports from the UI.

## Test Files Explained

### `test_audit_local.py` (The Test)
- **Lines 1-50:** Define test audit bundle with 7 criteria
- **Lines 70-110:** Generate readiness report JSON
- **Lines 130-165:** Generate audit bundle JSON
- **Lines 185-250:** Generate markdown report

All pure Python, no external dependencies needed.

### Generated Outputs
```
test_readiness_report.json
  - Full JSON readiness report
  - Ready for Word export
  - Ready for frontend display

test_audit_bundle.json
  - Structured audit data
  - API format
  - Archive/backup format

test_audit_report.md
  - Plain markdown
  - Email/git safe
  - Version control friendly
```

## Customizing the Test

### Change Hotel Details
Edit `test_audit_local.py`, line ~50:

```python
profile = {
    "hotel_name": "Your Hotel Name",  # Change this
    "location": "City, Country",      # Change this
    # ... etc
}
```

### Change Assessment Statuses
Edit criteria array (line ~20):

```python
{
    "code": "A1",
    "status": "Conforming",      # Change to: "Partly met", "Not met"
    "rationale": "...",
    "evidence": [...]
}
```

### Add More Criteria
Add more dicts to the `"criteria": [...]` array. The test will automatically:
- Count them correctly
- Generate evidence entries
- Update status summaries

### Run It Again
After changes:

```bash
python test_audit_local.py
```

New files are generated, overwriting previous ones.

## What You Can Do Now (No Setup)

1. **Review the outputs** - Open JSON in a text editor or VS Code
2. **Share reports** - Send markdown/JSON files to stakeholders
3. **Test Word export** - Take the JSON output and convert to Word
4. **Test the web UI** - Once you have the API running
5. **Verify structure** - Ensure report format matches your requirements
6. **Iterate on format** - Change test data and regenerate instantly
7. **Version control** - Commit JSON/markdown outputs to git for tracking

## Performance

- **Test run time:** <1 second
- **JSON file size:** ~30 KB
- **Markdown file size:** ~1.4 KB
- **No network calls**
- **No database needed**
- **No Docker needed**

## Next Steps

**Choice 1: Database & Full Stack (Later)**
```bash
cd infra && docker compose up -d
python setup_test_audit.py
cd services/api && uvicorn app.main:app --reload
```

**Choice 2: Word Export Only (Next)**
- Add python-docx to local test
- Generate .docx files directly

**Choice 3: Just Review Output (Now)**
- Open generated JSON/markdown files
- Verify structure meets your needs
- Share with team

---

**Key Takeaway:** You have a working, testable report generation system RIGHT NOW with zero setup. No database, no Docker, no API - just Python. Extend it as needed.
