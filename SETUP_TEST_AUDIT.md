# Setting Up Test Audit Data

This guide helps you set up a single hotel audit with realistic test data for report generation testing.

## Prerequisites

You need Docker and Docker Compose running to set up the PostgreSQL database and other services.

### Step 1: Start Docker Services

Navigate to the `infra/` directory and start the services:

```bash
cd infra
docker compose up -d
```

This will start:
- **PostgreSQL** (port 5432): Database for audit data
- **Redis** (port 6379): Task queue backend
- **MinIO** (ports 9000, 9001): Object storage for evidence files

Verify services are ready (especially Postgres):
```bash
docker compose ps
```

Wait for all services to show "healthy" status.

### Step 2: Run the Test Audit Setup Script

Once the database is ready, run the setup script from the project root:

```bash
python setup_test_audit.py
```

This script will:
1. **Delete all existing audits** except the most recent one
2. **Populate that audit** with:
   - Realistic assessment data for 7 GSTC criteria (A1-A3, B1-B2, C1, D1)
   - Mixed assessment statuses (conforming, observation, minor, major)
   - Detailed rationales based on real hotel sustainability practices
   - 2 evidence items per criterion (14 evidence files total)
   - Generated PNG images as evidence attachments
   - Structured readiness report profile with:
     - Hotel details (name, location, contact)
     - Audit methodology and scope
     - Staff interviewed and areas inspected
     - Key figures (occupancy, environmental metrics)
     - Legal compliance status
     - Next steps

### Step 3: Access the Audit

Once setup completes successfully, the audit will be ready for:
- Report generation (`/audits/{audit_id}/report`)
- Readiness report generation (`/audits/{audit_id}/readiness`)
- Word document export

**Audit Details After Setup:**
- Title: "2026 GSTC Sustainability Audit"
- Site: "Bali Practice Hotel"
- Status: "reporting" (ready for report generation)
- Criteria Assessed: 7 out of 40 (A1-A3, B1-B2, C1, D1)
- Evidence Files: 14 PNG images with realistic labels

### Step 4: Test Report Generation

#### Via API

```bash
# Get JSON report
curl -H "Authorization: Bearer {token}" \
  http://localhost:8000/hospitality/audits/{audit_id}/report?format=json

# Get Markdown report
curl -H "Authorization: Bearer {token}" \
  http://localhost:8000/hospitality/audits/{audit_id}/report?format=markdown

# Get Readiness Report
curl -H "Authorization: Bearer {token}" \
  http://localhost:8000/hospitality/audits/{audit_id}/readiness
```

#### Via Web UI

1. Navigate to http://localhost:3000/hospitality
2. Sign in with test credentials:
   - Email: `auditor@test.local`
   - Password: `TestPassword123!`
3. Click on the "2026 GSTC Sustainability Audit" from the list
4. Click "Readiness Report" tab to view the readiness report
5. Use the "Generate Report" or "Export to Word" buttons

## Assessment Data Included

The setup includes realistic assessments for:

| Code | Criterion | Status | Evidence |
|------|-----------|--------|----------|
| A1 | Environmental and social policy | Conforming | 2 photos |
| A2 | Environmental management plan | Conforming | 2 documents |
| A3 | Monitoring and evaluation | Minor NC | 2 records |
| B1 | Water consumption | Conforming | 2 photos |
| B2 | Water sources | Observation | 2 documents |
| C1 | Waste reduction | Major NC | 2 records |
| D1 | Staff wellbeing | Conforming | 2 photos |

Each assessment includes:
- Detailed rationale (realistic hotel sustainability commentary)
- Linked evidence files (PNG images)
- Indicator-level notes
- Assessment timestamp and auditor name

## Troubleshooting

### Database Connection Refused
- Ensure Docker services are running: `docker compose ps`
- Check PostgreSQL logs: `docker compose logs db`
- Verify database is healthy (should show "healthy" status)

### Missing Evidence Files
- The setup script generates PNG evidence files automatically
- If images don't appear in reports, check MinIO is running and bucket exists:
  ```bash
  docker compose exec minio mc ls local/axis-evidence
  ```

### Token/Auth Issues
The test user created is:
- **Email**: auditor@test.local
- **Password**: TestPassword123!
- **Role**: lead_auditor (can assess and review criteria)
- **Organization**: "Test Organization"

### Reset Everything
To start fresh, delete all audit data and services:
```bash
# Stop and remove containers/volumes
docker compose down -v

# Remove the setup script's generated data
rm setup_test_audit.py  # or just run it again to reset

# Restart services and re-run setup
docker compose up -d
python setup_test_audit.py
```

## Configuration

The setup uses default values from `services/api/app/config.py`:
- Database: `postgresql://axis:axis@localhost:5432/axis_db`
- Storage: MinIO at `http://localhost:9000`
- Redis: `redis://localhost:6379/0`

To use different database credentials, update `services/api/app/config.py` before running the setup script.

---

**Ready for testing!** You now have a complete, realistic hotel audit with assessments, evidence, and readiness report data.
