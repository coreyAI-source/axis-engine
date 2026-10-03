# Hotel Audit Report Generation - Setup & Testing Guide

## Overview

This guide helps you test the hotel audit report generation system with realistic test data. The system supports:
- **Readiness Reports** - Detailed sustainability assessment reviews in Word and JSON formats
- **JSON Reports** - Structured audit data export
- **Markdown Reports** - Plain-text audit summary export

## Quick Start

### 1. Start the Database & Services

```bash
cd infra
docker compose up -d
```

Wait for services to become healthy (check with `docker compose ps`). You should see:
- ✓ db (PostgreSQL)
- ✓ redis 
- ✓ minio (Object storage)

### 2. Install Dependencies

From the project root:

```bash
pip install -r services/api/requirements.txt
```

### 3. Create Test Data

```bash
python setup_test_audit.py
```

This creates:
- ✓ Test organization and user account
- ✓ Single hotel audit (or resets existing ones)
- ✓ 7 assessed criteria with mixed statuses
- ✓ 14 evidence files (PNG images)
- ✓ Comprehensive readiness profile
- ✓ Realistic assessment rationales

**Output Example:**
```
✓ Test audit setup complete!
   Audit ID: [uuid]
   Title: 2026 GSTC Sustainability Audit
   Site: Bali Practice Hotel
   Status: reporting
   Evidence files added: 14
   Criteria assessed: 7

Test user credentials:
   Email: auditor@test.local
   Password: TestPassword123!
   Role: lead_auditor

Report generation endpoints ready:
   GET /hospitality/audits/{audit_id}/report?format=json
   GET /hospitality/audits/{audit_id}/report?format=markdown
   GET /hospitality/audits/{audit_id}/readiness
```

### 4. Start the API Server

```bash
cd services/api
uvicorn app.main:app --reload --port 8000
```

### 5. Start the Web Frontend (optional)

In a new terminal:

```bash
cd apps/web
npm install  # First time only
npm run dev  # Runs on http://localhost:3000
```

## Testing Report Generation

### Method A: API Endpoints

#### Get JSON Report
```bash
curl -H "Authorization: Bearer {token}" \
  http://localhost:8000/hospitality/audits/{audit_id}/report?format=json | jq '.'
```

#### Get Markdown Report
```bash
curl -H "Authorization: Bearer {token}" \
  http://localhost:8000/hospitality/audits/{audit_id}/report?format=markdown
```

#### Get Readiness Report (JSON)
```bash
curl -H "Authorization: Bearer {token}" \
  http://localhost:8000/hospitality/audits/{audit_id}/readiness | jq '.'
```

### Method B: Web UI

1. Navigate to http://localhost:3000/hospitality
2. Sign in:
   - Email: `auditor@test.local`
   - Password: `TestPassword123!`
3. Click on "2026 GSTC Sustainability Audit"
4. Click "Readiness Report" tab
5. View the full assessment with:
   - Hotel profile information
   - Assessment statuses and rationales
   - Evidence register
   - Action plan (if any)
   - AI-generated narrative (if configured)

### Method C: Get Auth Token

First, get a token to use with API calls:

```bash
curl -X POST http://localhost:8000/auth/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=auditor@test.local&password=TestPassword123!"
```

Response:
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer"
}
```

Then use the token in subsequent requests:
```bash
export TOKEN="<access_token from above>"
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/hospitality/audits/{audit_id}/readiness | jq '.'
```

## Test Data Structure

### Hotel Profile
- **Name**: Bali Practice Hotel
- **Location**: Ubud, Bali, Indonesia
- **Type**: Luxury eco-resort
- **Rooms**: 180 guest rooms + 12 suites
- **Staff**: 240 full-time + 80 seasonal
- **Certifications**: Green Building Council (2020), ISO 14001 (2023)

### Assessment Data

| Code | Title | Status | Evidence | Rationale |
|------|-------|--------|----------|-----------|
| A1 | Environmental & social policy | Conforming | Policy doc, meeting notes | Strong policy signed by GM, covers conservation & community |
| A2 | Environmental mgmt plan | Conforming | Plan document, review records | Comprehensive plan reviewed quarterly |
| A3 | Monitoring & evaluation | Minor | Baseline data, monthly reports | Good but incomplete data collection, recommend automation |
| B1 | Water consumption | Conforming | Meter readings, usage logs | Meters installed, 312 m³/guest/year (target: 280) |
| B2 | Water sources | Observation | Municipal docs, risk assessment | Municipal supply, sustainable, recommend annual QA |
| C1 | Waste reduction | Major | Waste logs, segregation records | Basic segregation only, 45% to landfill, needs reduction targets |
| D1 | Staff wellbeing | Conforming | Training records, survey results | Annual training 96% completion, satisfaction 4.2/5 |

### Evidence Types
- **Photo (P01-P07)**: On-site photographs of systems and facilities
- **Document (D01-D07)**: Policies, permits, compliance certificates
- **Record (R01-R07)**: Operational data, training records, inspection logs

All evidence is automatically assigned:
- Collection date (past 5-7 days)
- Auditor name: "Test Auditor"
- Collection method: "on_site", "interview", or "document review"

## Report Generation Features

### Readiness Report Output

The readiness report includes:

1. **Cover Page**
   - Hotel name, location, contact
   - Review date and reviewer
   - Report reference number
   - Confidentiality statement

2. **Executive Letter**
   - Personalized salutation
   - Summary of findings
   - Key gaps and priorities
   - Next steps

3. **Assessment Summary**
   - Overall readiness statement
   - Criteria breakdown by pillar (A, B, C, D)
   - Status counts (Met, Partly met, Not met, etc.)
   - Readiness level per pillar

4. **Detailed Findings**
   - Each criterion reviewed with status
   - Auditor rationale
   - Linked evidence with IDs
   - Indicators and notes

5. **Action Plan**
   - Priority-ordered closure items
   - Timeline (months 1-3, 4-6)
   - Responsible parties
   - Evidence requirements

6. **Evidence Register** (Appendix A)
   - Complete list of evidence items
   - Evidence ID, type, description
   - Linked criteria
   - Collection method and date

7. **Methodology & Definitions**
   - Assessment status meanings
   - Priority definitions
   - Evidence type descriptions
   - How assessments are derived

8. **Certification Guide** (Appendix B)
   - What GSTC certification is
   - Steps to certification
   - Choosing a certification body
   - Questions to ask
   - Recommended schemes

### JSON Report Structure

```json
{
  "audit": {
    "id": "uuid",
    "title": "2026 GSTC Sustainability Audit",
    "siteName": "Bali Practice Hotel",
    "status": "reporting",
    "version": 2
  },
  "assessments": [
    {
      "requirementId": "uuid",
      "status": "conforming|observation|minor|major|unassessed|not_applicable",
      "rationale": "Human-readable assessment explanation",
      "evidenceIds": ["uuid1", "uuid2"],
      "assessedBy": { "name": "Test Auditor", "userId": "..." },
      "assessedAt": "ISO timestamp",
      "indicatorInputs": [
        {
          "index": 0,
          "notes": "Indicator-specific assessment notes",
          "evidenceIds": ["uuid"]
        }
      ]
    }
  ],
  "evidence": [
    {
      "id": "uuid",
      "kind": "photo|document|record|interview|observation",
      "description": "Evidence description",
      "collectedAt": "ISO timestamp",
      "collectedVia": "on_site|before_visit|after_visit|interview|calculation",
      "attachment": {
        "key": "s3-key",
        "fileName": "evidence.png",
        "contentType": "image/png"
      }
    }
  ]
}
```

### Markdown Report Format

Plain-text summary with:
- Hotel and reviewer details
- Criteria assessment table
- Evidence references
- Assessment rationales
- Action items (if any)

Perfect for:
- Email sharing
- Version control/Git tracking
- Plaintext archiving
- Integration with other tools

## Customizing Test Data

### Change Hotel Details

Edit `setup_test_audit.py`, `readiness_profile` dict:

```python
readiness_profile = {
    "hotel_name": "Your Hotel Name",
    "location": "City, Country",
    "hotel_contact_name": "Contact Name",
    # ... etc
}
```

### Change Assessment Statuses

Modify `ASSESSMENT_DATA` dict:

```python
"A1": {
    "status": "minor",  # Changed from "conforming"
    "rationale": "Your custom rationale text",
}
```

### Add More Evidence

In the loop adding evidence, increase the range:

```python
for ev_idx in range(3):  # was 2, now 3 per criterion
```

### Change Criteria Assessed

Edit the `GSTC_CRITERIA` and `ASSESSMENT_DATA` dicts to include/exclude criteria.

## Troubleshooting

### "Connection refused" on setup
- Verify Docker services are running: `docker compose ps` in `infra/` directory
- Check PostgreSQL logs: `docker compose logs db`
- Ensure port 5432 is not in use by another service

### "Evidence files not loading in report"
- Verify MinIO is running: `docker compose logs minio`
- Check bucket exists: `docker compose exec minio mc ls local/axis-evidence`
- Verify file content-type is correct (should be `image/png`)

### "Assessment data missing"
- Check the audit status is "reporting": query DB or use API
- Verify requirements exist in the audit scope
- Check that assessment.requirementId matches a requirement in the bundle

### Reset Everything

```bash
# Stop services and delete data
cd infra
docker compose down -v

# Reinstall Python dependencies (fresh)
pip install --force-reinstall -r services/api/requirements.txt

# Restart and re-setup
docker compose up -d
sleep 5  # Wait for DB to be ready
python setup_test_audit.py
```

### Authentication Issues

If sign-in fails with test credentials:

1. Verify the user exists:
   ```bash
   docker compose exec db psql -U axis -d axis_db -c \
     "SELECT email, role_code FROM users WHERE email='auditor@test.local';"
   ```

2. Reset the test user:
   ```bash
   docker compose exec db psql -U axis -d axis_db -c \
     "DELETE FROM users WHERE email='auditor@test.local';"
   ```
   Then run `python setup_test_audit.py` again.

## Performance Notes

- Initial setup: 2-5 seconds (depends on image generation)
- Report generation: <1 second for JSON/Markdown, ~5 seconds for Word export
- Evidence image size: ~50KB per PNG (14 images = ~700KB total)
- Database size: ~10MB after setup

## Security Notes

⚠️ **Test credentials and data are for development only:**
- Default password `TestPassword123!` is in plaintext in this guide
- MinIO credentials are `minioadmin/minioadmin`
- Database password is `axis`
- Never use these in production

For production:
- Use strong, unique passwords
- Enable password hashing verification
- Restrict database network access
- Use environment-specific secrets management
- Enable audit logging

## Next Steps

Once testing is complete:

1. **Review the readiness report** to understand the output format
2. **Test with your own data** by modifying the setup script
3. **Generate multiple assessment statuses** to see different report outputs
4. **Add more evidence** to test large evidence registers
5. **Test Word export** if WordExporter is configured
6. **Verify AI narrative** if OpenRouter API is configured

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review logs: `docker compose logs [service-name]`
3. Check database state: `docker compose exec db psql -U axis -d axis_db`
4. Review API errors: Check uvicorn console output
5. Review frontend errors: Check browser console (F12)

---

**Ready to test!** Your audit is set up with realistic data and all report endpoints are ready.
