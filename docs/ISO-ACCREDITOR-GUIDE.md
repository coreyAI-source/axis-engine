# AXIS Hotel Audit Platform: ISO Accreditor Guide

**Version:** 1.0  
**Date:** October 2026  
**Standard:** GSTC Hotel Standard v4.01  
**Audience:** GSTC-accredited certification bodies (e.g., Control Union) and ISO accreditors

---

## Overview

AXIS is a purpose-built audit platform for hotel sustainability assessments using the **Global Sustainable Tourism Council (GSTC) Hotel Standard v4.01**. This guide explains how to use AXIS to conduct professional audits, manage teams, document findings, and generate certification-ready reports.

### Key Features

✅ **Official GSTC Criteria:** All 40 GSTC Hotel Standard v4.01 criteria pre-loaded  
✅ **Structured Evidence:** Upload and link documents, photos, and observations  
✅ **Findings & Actions:** Track corrective actions with independent verification  
✅ **Professional Reports:** Export audit reports in multiple formats  
✅ **Team Collaboration:** Multi-user workspaces with role-based access control  
✅ **Audit Trail:** Complete history of all assessments and changes  
✅ **Compliance Enforcement:** System enforces GSTC criteria usage and evidence requirements

---

## Getting Started

### 1. System Requirements

- **Browser:** Modern browser (Chrome, Firefox, Safari, Edge) with JavaScript enabled
- **Internet:** Stable connection (audits sync to server)
- **Node.js 22.6+:** Required on the API server only (not on client machines)
- **Database:** PostgreSQL 12+ (or compatible provider like Neon)

### 2. Login and Account Setup

1. Navigate to the AXIS platform login page (typically `https://your-domain/hospitality`)
2. Enter your email address and password
3. On first login, you'll see the **Hospitality** dashboard
4. Your organisation is pre-created; additional team members are added by administrators

### 3. Role-Based Access Control

| Role | Auditor | Reviewer | Admin | Can Assess | Can Verify | Can Manage Team |
|------|---------|----------|-------|-----------|-----------|-----------------|
| **Viewer** | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| **Process Owner** | ❌ | ❌ | ❌ | Own actions | ❌ | ❌ |
| **Auditor** | ✅ | ✅ | ❌ | ✅ | ❌ | ❌ |
| **Lead Auditor** | ✅ | ✅ | ❌ | ✅ | ✅ | ❌ |
| **Compliance Manager** | ✅ | ✅ | ❌ | ✅ | ✅ | ❌ |
| **Admin** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |

**Access Model:** Users access only audits within their organisation. Cross-organisation access requires explicit data sharing.

---

## Conducting an Audit

### Step 1: Create a New Audit

1. From the **Hospitality** dashboard, click **New hotel audit**
2. Fill in the audit details:
   - **Hotel Name:** The property being audited (e.g., "Bali Resort & Spa")
   - **Audit Title:** Short description of the engagement (e.g., "GSTC Certification Audit, Sep 2026")
   - **Scope Statement:** Define the boundaries (e.g., "Guest rooms, dining, and housekeeping areas; grounds excluded")
3. Click **Create**
4. The system automatically loads all 40 GSTC criteria
5. A notification appears: "Added GSTC Hotel Standard v4.01 criteria"

### Step 2: Review and Mark Criteria Applicability

1. Navigate to **Criteria** tab in the audit
2. For each criterion, determine if it applies to the hotel:
   - **Applicable:** Assess per normal workflow
   - **Not Applicable:** Record the reason (e.g., "No construction planned; A11/A12 excluded")
3. Criteria marked **Not applicable** with a documented reason are excluded from compliance scoring

**Example Not-Applicable Reason:**  
*"Property has no planned construction, renovations, or expansion. Criteria A11 and A12 do not apply during this audit period."*

### Step 3: Upload Evidence

1. Navigate to **Evidence** tab
2. Click **Add evidence**
3. Select file type:
   - **Documents:** PDF, Word, Excel, CSV, text
   - **Photos:** JPG, PNG (max 10 MB each)
   - **Records:** Any text file or structured data
4. Add description explaining:
   - What the evidence shows
   - Where it was collected (on-site, office records, interview)
   - Who provided it (manager, staff member, etc.)
5. Upload (max 10 MB per file)

**Evidence Quality Standards:**

| Evidence Type | Acceptable | Not Acceptable |
|---|---|---|
| **Document** | Policy with date/signature, training records, meeting minutes | Generic template with no specifics, undated |
| **Photo** | Facility/process with date, context visible | Out-of-focus, irrelevant background |
| **Interview Note** | Name, date, specific quotes or observations | Vague summaries, no attribut|ion |
| **Record** | Official register with entries, numbers, dates | Blank template, unverified data |

### Step 4: Assess Each Criterion

1. Navigate to **Assessments** tab
2. Select a criterion (e.g., A1 - Sustainability Management System)
3. Review the criterion statement and indicators
4. Gather relevant evidence from the **Evidence** tab
5. Choose an assessment status:

| Status | Meaning | Finding Type |
|--------|---------|---|
| **Conforming** | Meets all requirements with good evidence | None |
| **Observation** | Generally meets, minor improvements noted | Optional action |
| **Minor** | Does not fully meet; correctable action required | Mandatory minor finding |
| **Major** | Significant gap; serious corrective action required | Mandatory major finding |
| **Not Applicable** | Requirement does not apply to this property | Excluded (with reason) |

6. Enter **Rationale** (required):
   - Summarise the evidence reviewed
   - Explain the logic for the status
   - For non-conformances, describe the specific gap
   - Minimum 50 characters

Example rationale (Minor):  
*"Hotel has a written sustainability policy (seen, dated 2025) and annual review process. However, specific quantitative targets for water and waste reduction are missing. Corrective action required to add measurable KPIs."*

7. Select evidence supporting this assessment
8. Click **Save Assessment**

### Step 5: Track Findings and Corrective Actions

When you assess a criterion as **Minor** or **Major**, a **Finding** is automatically created.

#### For Each Finding:

1. Navigate to **Findings & Actions** tab
2. Select the finding and click **Create Action**
3. Complete the action form:
   - **Description:** What must be corrected (auto-populated from finding)
   - **Owner:** Assign to a specific team member (auditor or process owner)
   - **Due Date:** Based on severity (Minor=30 days, Major=90 days, or custom)
   - **Implementation Plan:** How the owner will address the gap

4. The action owner receives a notification
5. Owner updates progress:
   - **Start** when work begins
   - **Add evidence** of implementation (documents, photos)
   - **Submit for verification** when complete

#### Independent Verification (Critical Step)

1. A different person (not the owner, not the person who submitted) must verify:
   - Click **Verify effective** if evidence shows the corrective action worked
   - Click **Return for more work** if the action is incomplete or ineffective
   - Add notes explaining the verification decision

2. If verification fails, work returns to the owner with feedback
3. Once verified, click **Close action**
4. The finding is marked complete (but remains in the audit history)

**Important:** Independent verification ensures impartiality and is required for certification decisions.

---

## Reports and Certification Workflow

### Readiness Report (Internal Assessment)

The **Readiness Report** is an internal assessment document showing:
- Summary of audit findings by pillar
- Coverage and compliance status
- Gap analysis and phased action plan
- Route to GSTC certification

To generate:

1. Navigate to **Readiness report** tab
2. Click **Report details** and complete:
   - Cover letter (organisation, dates, scope)
   - People interviewed (names, roles)
   - Areas inspected (facilities visited)
   - Hotel profile (rooms, staff, certifications held)
   - Key figures (annual guest-nights, waste generation, water use)
   - Local legal requirements (environmental permits, labour laws)

3. Click **Generate AI draft** (optional, requires OpenRouter API key)
4. Review the draft and edit sections as needed
5. Click **Download Word** to export for final editing
6. Once reviewed, enter "Reviewed by" name to remove DRAFT watermark

**Report Output:**
- Format: Microsoft Word (.docx) editable
- Sections: Cover letter, findings summary, evidence registers, action plan
- Certification criteria map (shows which GSTC indicators are met/not met)
- Can be issued to the hotel or retained for internal records

### Completion Criteria (Before Issuing Final Report)

The audit cannot be marked complete until:

✅ Every applicable criterion has an assessment (Conforming / Observation / Minor / Major / Not Applicable)  
✅ Each non-applicable criterion has a documented reason  
✅ Every Minor and Major finding has an assigned action  
✅ Every action has an owner and due date  
✅ No actions remain unstarted past their due dates  

If any criteria block completion, the system shows specific blockers preventing export.

### Audit Record (Final Report)

1. Navigate to **Audit record** tab
2. Review any reported blockers
3. Once all criteria assessed and actions assigned, click **Move to reporting**
4. Click **Complete audit**
5. The audit is locked for editing (historical record)
6. Export options:
   - **Download JSON:** Full audit data (for archiving)
   - **Download Markdown:** Formatted report for distribution
   - **Print / Save PDF:** Browser print to PDF

---

## Certification Pathway (GSTC Accreditation)

**Important:** AXIS generates an assessment. Certification is issued by GSTC-accredited certification bodies (e.g., Control Union).

### Typical Workflow

1. **Initial Assessment (This Platform)**
   - Use AXIS to complete the full audit
   - Generate the Readiness Report
   - Share findings with the hotel (optional)

2. **Corrective Action Period** (Weeks 1–12)
   - Hotel addresses Major findings
   - Verify corrective actions in AXIS
   - Update timelines as needed

3. **Final Inspection**
   - Conduct final site visit using AXIS
   - Verify all corrective actions implemented
   - Mark actions as closed

4. **Report to Certification Body**
   - Export final audit report
   - Attach supporting evidence
   - Submit to GSTC certification body (e.g., Control Union)

5. **Certification Review**
   - Certification body reviews your assessment
   - Issues GSTC certificate (if approved)
   - Hotel becomes GSTC-certified

**Note:** This platform does not issue certificates. It provides documented evidence for the certification body's decision.

---

## Team Management

### Adding Team Members (Admin Only)

1. Navigate to **Hospitality** → **Team accounts**
2. Click **Add member**
3. Enter:
   - **First Name** and **Last Name**
   - **Email address** (must be unique)
   - **Role:** Auditor, Lead Auditor, Compliance Manager, or Process Owner
   - **Password:** Min. 12 characters, mixed case and numbers recommended
4. Click **Create**
5. New user receives email with login details (if email notifications are configured)

### Resetting Passwords

- Users can reset their password using "Forgot password" link on login page
- Admins can issue temporary passwords via the team accounts page

### Removing Team Members

- Click the user in **Team accounts**
- Click **Deactivate**
- The user's account is disabled (audit history remains)

---

## Common Workflows

### Scenario 1: Split Audit (Different Lead and Verifier)

**Goal:** Ensure independent assessment and verification.

1. **Lead Auditor A** assesses all criteria and creates findings
2. **Lead Auditor B** (different person) verifies all actions
3. System enforces: Auditor A cannot verify their own actions
4. Final report signed by both leads

### Scenario 2: Multi-Site Assessment

**Goal:** Audit multiple hotel properties under one chain.

1. Create separate audit for each property
2. Use consistent team (same criteria interpretation)
3. Compare final reports across properties
4. System maintains separate audit trails per site

### Scenario 3: Re-Audit (Annual Renewal)

**Goal:** Update certification with new audit.

1. Create new audit (new audit ID, new audit date)
2. Review all criteria (not carried forward from previous audit)
3. Identify improvements since last audit
4. Track any previously-found gaps that remain open
5. Issue new report covering only this audit period

---

## API Integration (For Developers)

### GSTC Criteria Validation

```bash
# Validate criteria codes before submission
POST /reports/gstc-standard/validate-codes
{
  "codes": ["A1", "B2", "X1", "ZZ99"]
}

Response:
{
  "valid": ["A1", "B2"],
  "invalid": ["ZZ99"],
  "custom": ["X1"],
  "errors": ["ZZ99: 'ZZ99' is not a valid GSTC criterion..."]
}
```

### Get GSTC Standard Information

```bash
# Comprehensive standard info for audit setup
GET /reports/gstc-standard/info

Response:
{
  "metadata": {
    "version": "4.01",
    "source": "https://www.gstc.org/wp-content/uploads/GSTC-Hotel-Standard.pdf",
    "date": "2025-12-30",
    "total_criteria": 40
  },
  "criteria_by_pillar": {
    "A": 14,  // Sustainable Management
    "B": 9,   // Social/Economic Benefits
    "C": 4,   // Cultural Heritage
    "D": 13   // Environmental Benefits
  },
  ...
}
```

### Get All GSTC Criteria

```bash
GET /reports/gstc-standard/criteria

Response:
{
  "criteria": {
    "A1": {
      "code": "A1",
      "title": "Sustainability Management System",
      "statement": "The hotel operates under a documented...",
      "indicators": [...]
    },
    ...
  }
}
```

---

## Security & Compliance

### Data Protection

- **Encryption in Transit:** All API communication uses HTTPS (TLS 1.2+)
- **Encryption at Rest:** Database and file storage encrypted
- **Authentication:** Time-limited session tokens (default 24 hours)
- **Access Control:** Users see only audits within their organisation

### Audit Trail & Compliance

Every audit action is logged:
- Who made the change (authenticated user)
- What changed (assessment, finding, action)
- When it changed (server timestamp)
- Previous version (for rollback if needed)

This enables:
- Compliance with auditor certification requirements
- Investigation of disputed findings
- Regulatory reporting (if required)

### File Storage & Retention

- Uploaded evidence stored securely (encrypted)
- File integrity verified (SHA256 hash)
- Retention policy: Define based on regulatory requirements
- Deletion: Only admins can delete audits (creates archive record)

### Multi-Tenancy

- Organisations are isolated at the database level
- Users from Organisation A cannot view Organisation B's audits
- Admins manage only users within their organisation

---

## Troubleshooting

| Issue | Cause | Solution |
|-------|-------|----------|
| Cannot log in | Account inactive or email typo | Check email spelling; contact admin to reactivate |
| Audit won't save | Version conflict (another user edited) | Reload audit, reapply your changes |
| Cannot verify action | You are the owner or submitter | Have a different eligible person verify |
| File upload fails | File too large or unsupported format | Check file is <10 MB and is PDF/JPG/PNG/TXT/CSV |
| Missing GSTC criteria | Using old audit template | Create new audit; system loads GSTC v4.01 automatically |
| Report generation fails | OpenRouter API key missing or expired | Set OPENROUTER_API_KEY in server config; restart API |

---

## System Deployment (IT/DevOps)

### Production Deployment Checklist

Before deploying AXIS for real audits:

- [ ] **Database:** PostgreSQL backup policy defined and tested
- [ ] **Secrets:** Strong `SECRET_KEY` generated; stored in secrets manager (not .env)
- [ ] **CORS:** Configure allowed domain origins
- [ ] **HTTPS:** SSL/TLS certificate installed; redirects HTTP → HTTPS
- [ ] **Monitoring:** Error tracking and uptime monitoring configured
- [ ] **Backups:** Automated daily backups with restore procedure tested
- [ ] **Node.js:** Verified running Node 22.6+ on API host
- [ ] **Auth:** LDAP/SSO integration (if required)
- [ ] **Email:** SMTP configured for notifications (optional)

### Container Deployment (Docker)

```bash
# Build container
docker build -f infra/Dockerfile.api -t axis-api .

# Run container
docker run -e DATABASE_URL=postgresql://... \
           -e SECRET_KEY=strong-random-key \
           -e CORS_ORIGINS='["https://yourdomain.com"]' \
           -p 8000:8000 \
           axis-api
```

### Environment Variables (Production)

```
DATABASE_URL=postgresql://user:pass@host:5432/axis_db
SECRET_KEY=<strong random 32+ char key>
CORS_ORIGINS=["https://domain.com"]
OPENROUTER_API_KEY=sk-or-...
AUTO_CREATE_TABLES=false
```

---

## Support and Updates

### Getting Help

- **Platform Questions:** Contact your IT administrator or system vendor
- **GSTC Standard Questions:** Visit https://www.gstc.org/
- **Certification Pathways:** Contact your certification body (e.g., Control Union)

### Software Updates

- The platform automatically receives patches for security issues
- Major feature updates may require audit template adjustments
- GSTC standard updates (if any) are deployed automatically

---

## References

- [GSTC Hotel Standard v4.01](https://www.gstc.org/gstc-criteria/gstc-hotel-standard/)
- [GSTC Certified Hotels Directory](https://www.gstc.org/certified-hotels-directory/)
- [GSTC-Accredited Certification Bodies](https://www.gstc.org/accreditation/gstc-accredited-certification-bodies/)
- [Control Union Certification Services](https://www.controlunion.com/service/certification/)

---

**Document Version:** 1.0  
**Last Updated:** October 2026  
**Next Review:** October 2027
