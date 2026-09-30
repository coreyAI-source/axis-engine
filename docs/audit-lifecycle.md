# Audit Lifecycle

## Stages

```
Planned → InProgress → Completed
                     ↘ Cancelled
```

## Stage Types

```
DocumentReview → SiteAudit → FollowUp
```

## Step-by-Step

### 1. Create Audit (`POST /audits/`)
- Set `audit_type`, `audit_stage = DocumentReview`, `status = Planned`
- Assign lead auditor, team members, locations

### 2. Add Processes in Scope (`POST /audits/{id}/processes`)
- Link the processes to be audited

### 3. Generate Prompts (`POST /audit-prompts/generate?audit_id={id}`)
- System generates prompts from ProcessClauseMaps
- DocumentCheck prompts only generated for clauses with `requires_documented_information = True`

### 4. Document Review
- Work through prompts flagged for document review stage
- Respond to each prompt (C / NC / OBS / FUP / TBA / NA)
- NC → Finding auto-created → Action auto-created
- Generate Document Review Report (`GET /reports/audits/{id}/document-review`)

### 5. Audit Plan
- Generate formal plan (`GET /reports/audits/{id}/audit-plan`)

### 6. Audit Timetable
- Generate 30-min slot timetable (`GET /reports/audits/{id}/timetable`)

### 7. Site Audit
- Update `audit_stage = SiteAudit`
- Mobile auditors execute prompts
- Capture evidence (photos, documents, notes) against prompts
- Record responses

### 8. Findings Register
- Review all NC and OBS findings
- Auditor can upgrade MinorNC → MajorNC if severity warrants
- Generate findings register (`GET /reports/audits/{id}/findings-register`)

### 9. Audit Report
- Generate formal report (`GET /reports/audits/{id}/report`)
- Conditional logic auto-populates NC statements and verification method

### 10. Follow-up
- Actions assigned to process owners
- Daily lag monitor tracks activity
- At-risk and overdue notifications triggered
- Actions closed with verification evidence
- Follow-up audit can be created (`audit_type = FollowUp`, links back to original)

## Report Conditional Logic

| Condition | Output |
|---|---|
| No critical doc review findings | "No critical findings were identified during this document review." |
| Critical findings exist | Lists them with structured narrative |
| No major NC | "No major nonconformances were identified during this audit." |
| Major NC exists | "X major nonconformances identified... corrected within 90 days." |
| Verification by evidence | "Your actions will be verified by submitting appropriate evidence." |
| Follow-up audit required | "...at a follow-up audit within 90 days of this report." |
