# Genuine GSTC Audit Guide

## Overview

The `create_genuine_audit.py` script creates a **comprehensive, realistic hotel audit** based on the official GSTC Hotel Standard v4.01. The resulting audit and readiness report will look and function like a real GSTC readiness assessment.

## What Makes It Genuine

### 1. Real Hotel Profile
- **Hotel**: Riverside Boutique Hotel (fictional but realistic)
- **Location**: Mendocino County, California
- **Size**: 32 rooms, 22 staff
- **Certifications**: ISO 14001 Environmental Management
- **Facilities**: Restaurant, bar, spa, fitness center, conference facilities

### 2. Comprehensive Criteria Coverage
- **19 GSTC criteria** assessed across all four pillars
- Mix of **met, partly met, and not met** criteria
- Realistic gaps for a mid-sized boutique hotel

Pillar A (Sustainable Management):
- A1: Sustainability Management System (✓ Met)
- A2: Legal Compliance (✓ Met)
- A3: Guest & Staff Welfare (⚠ Partly Met)
- A4: Reporting & Communication (⚠ Partly Met)
- A5: Accurate Promotion (✓ Met)
- A7: Staff Engagement (⚠ Partly Met)

Pillar B (Socioeconomic Benefits):
- B1: Community Support (⚠ Partly Met)
- B2: Local Employment (✓ Met)
- B5: Access for All (✗ Not Met)
- B6: Code of Conduct (⚠ Partly Met)
- B9: Decent Work (✓ Met)

Pillar C (Cultural Heritage):
- C1: Cultural Interactions (⚠ Partly Met)
- C3: Presenting Culture & Heritage (⚠ Partly Met)

Pillar D (Environmental Benefits):
- D1: Energy Conservation (⚠ Partly Met)
- D2: Water Conservation (⚠ Partly Met)
- D5: Wastewater (✓ Met)
- D6: Solid Waste (⚠ Partly Met)
- D7: Harmful Substances (⚠ Partly Met)
- D9: Biodiversity Conservation (✗ Not Met)

### 3. Realistic Evidence
- **27 evidence items** of different types:
  - Documents (policies, plans, permits, records)
  - Interviews (General Manager, staff, community)
  - Observations (facilities, practices, storage)
  - Records (employment, energy, water, waste)

Each evidence item has:
- Realistic title
- Appropriate collection method (before visit, on-site, interview)
- Collection date and time
- Links to relevant criteria

### 4. Realistic Assessments
Each criterion has:
- Status (conforming, observation, minor, major)
- Linked evidence
- Auditor notes explaining the finding
- Indicator-level documentation

### 5. Actionable Findings & Gaps
**Criteria with gaps:**
- A3: Incomplete health & safety documentation
- A4: Missing detailed sustainability metrics
- A7: No formal staff engagement structure
- B1: Community partnerships not formalized
- B5: Limited wheelchair access
- B6: Code of conduct training incomplete
- C3: No formal agreements with artisans
- D1: LED retrofit 60% complete
- D2: Leak detection system needed
- D6: Composting program proposed
- D9: Limited native plantings

Each gap includes:
- Clear description of what's needed
- Suggested action
- Realistic due date (60-90 days)
- Assigned to General Manager

## How to Use

### Step 1: Create the Genuine Audit

Run the script:
```bash
cd C:\Users\reitsec2\OneDrive\ -\ FRSA\Desktop\Personal\AIreptondigital\claude-workspace-template\axis-engine
python create_genuine_audit.py
```

**Output:**
```
Using user: Corey Reitsema

✨ Creating genuine, comprehensive hotel audit...

✅ Comprehensive, Genuine Audit Created!

   Hotel: Riverside Boutique Hotel
   Location: Mendocino County, California
   Rooms: 32 | Staff: 18 FT, 4 PT
   Audit ID: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
   Audit Date: 2026-10-05

   Coverage:
   • Requirements: 19 GSTC criteria
   • Evidence: 27 items
   • Assessments: 19 criteria assessed
   • Findings: 8 gaps identified
   • Actions: 8 recommended actions

   Assessment Summary:
   • Conforming: 6
   • Observation: 7
   • Minor: 5
   • Major: 2

📝 Ready to generate readiness report!
   POST /hospitality/audits/{audit_id}/readiness/generate
```

### Step 2: Generate the Readiness Report

The audit is now ready for report generation. Use the audit ID from above:

```bash
curl -X POST http://localhost:8000/hospitality/audits/{audit_id}/readiness/generate \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{"draft": true}'
```

Or via the UI:
1. Navigate to the audit
2. Click "Generate Readiness Report"
3. Select AI-assisted narrative
4. The report will include all 19 criteria with realistic assessments

### Step 3: Review the Report

The generated report will include:

**Front Matter:**
- Professional cover page with hotel details
- Covering letter from auditor
- Important notices about the readiness review

**Content Sections:**
1. **Summary** — Overall readiness, pillar breakdown
2. **Scope & Method** — Review type, evidence collected
3. **Gap Analysis** — Each criterion with evidence and gaps
4. **Local Legal Requirements** — Area-specific compliance
5. **Action Plan** — Critical gaps (Phase 1) and supporting documentation (Phase 2)
6. **Route to Certification** — Steps to GSTC certification

**Evidence Appendices:**
- Evidence register with all documents/interviews
- Observation log with site observations
- Criterion coverage matrix

## Key Features

### Realistic Assessment Mix
- **Conforming (6)**: Criteria where the hotel exceeds standards
- **Observation (7)**: Areas of good practice with minor notes
- **Minor (5)**: Gaps requiring attention
- **Major (2)**: Critical gaps preventing certification

This distribution is realistic for a boutique hotel with good intent but incomplete implementation.

### Critical vs. Important Gaps
- **Critical**: Prevent certification (B5, D9)
- **Important**: Likely to be raised at audit (A4, A7, B6, D2, D9)
- **Improvement**: Good practice recommendations (A4, D1, D6)

### Actionable Recommendations
Each gap has:
- Clear statement of what's needed
- Evidence the auditor will expect
- Realistic timeline
- Assigned responsibility

## Report Quality Indicators

✅ **Legitimate Audit**
- Uses official GSTC criteria from PDF
- Covers all pillar areas
- Realistic hotel profile
- Diverse evidence types
- Professional assessment mix
- Clear action plan with timelines

✅ **Genuine Evidence**
- Different evidence types (documents, interviews, observations)
- Realistic titles and descriptions
- Proper collection dates and methods
- Linked to appropriate criteria

✅ **Professional Report**
- AI-drafted narrative based on audit data
- References actual evidence
- Grounded in real findings
- Actionable recommendations
- Complies with GSTC review standards

## Customization

To modify the audit for a different hotel:

Edit the top of `create_genuine_audit.py`:

```python
# Modify these sections:
new_audit = HospitalityAudit(
    ...
    title="Your Hotel Name - GSTC Readiness Review",
    site_name="Your Hotel Name",
    ...
    report_profile={
        "hotel_name": "Your Hotel Name",
        "location": "Your Location",
        "hotel_contact_name": "Contact Name",
        ...
    },
)
```

## Troubleshooting

**Error: "No users found in database"**
- Ensure you've created a user in the system first
- Run the API to initialize the database

**Error: Module not found**
- Ensure you're running from the axis-engine directory
- Check that services/api/app is on the Python path

**Audit created but not visible**
- Check database connection
- Verify audit ID is correct
- Refresh the audit list in UI

## What Comes Next

1. ✅ Genuine audit created with realistic data
2. ✅ Ready for readiness report generation
3. ✅ Report will reference official GSTC criteria
4. ✅ Professional, legitimate-looking output

The readiness report generated from this audit will:
- Look and function like a real GSTC readiness review
- Reference the official GSTC v4.01 standard
- Include all audit evidence and findings
- Provide actionable gap closure plan
- Be suitable for presentation to hotel stakeholders

## Files

- `create_genuine_audit.py` — Script to create comprehensive audit
- `GENUINE_AUDIT_GUIDE.md` — This guide
- `GSTC_INTEGRATION.md` — Information on GSTC criteria integration

## Support

For questions:
- See `GSTC_INTEGRATION.md` for criteria details
- See `GSTC_QUICK_START.md` for API examples
- Review audit schema in `services/api/app/models/hospitality.py`
