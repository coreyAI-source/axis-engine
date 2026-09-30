# AXIS Architecture

## Overview

AXIS is a process-based, risk-based, evidence-driven compliance engine for ISO 9001, ISO 14001, and ISO 45001.

## Core Design Principles

- **Process-centric**: The top-level object is `Process`. Clauses are mapped to processes. Everything flows from the process.
- **Single engine, multi-standard**: ISO 9001, 14001, and 45001 share one architecture. The HLS structure is modelled explicitly.
- **Evidence-driven**: Every compliance decision must be linked to required evidence. The prompt engine flags evidence requirements from clause metadata.
- **Actionable outputs**: Every nonconformance produces a Finding → Action → Owner → Due Date → Verification chain.
- **Report-first**: Formal audit artefacts are auto-populated from structured data.

## HLS Sections

All three standards share the High Level Structure:

| Section | Clauses |
|---------|---------|
| Context | 4.x |
| Leadership | 5.x |
| Planning | 6.x |
| Support | 7.x |
| Operation | 8.x |
| PerformanceEvaluation | 9.x |
| Improvement | 10.x |

## Data Flow

```
Organisation → Sites → Processes
                            ↓
                    ProcessClauseMap (maps processes to ISO clauses)
                            ↓
              MonitoringTask (risk-driven frequency, method, owner)
                            ↓
              MonitoringRun (individual execution record)
                            ↓
              Audit → AuditProcess → AuditPrompt (generated from process-clause maps)
                            ↓
              AuditPrompt Response (C / NC / OBS / FUP / TBA / NA)
                            ↓
              Finding → Action → Notification → Close/Verify
                            ↓
              Reports (DocumentReview, AuditPlan, AuditReport, FindingsRegister)
```

## Severity Scoring

```
severity_score = status_weight × importance_weight

Status:     Excellent=1, Good=2, OK=3, Poor=4
Importance: Low=1, Moderate=2, High=3, Critical=4

Range: 1 (best) to 16 (worst)
Colour: ≤2=green, ≤6=yellow, ≤9=orange, ≥10=red
```

## Audit Response Rules

| Code | Meaning | Consequence |
|------|---------|-------------|
| C | Compliant | No action |
| NC | Nonconformant | Mandatory finding + action |
| OBS | Observation | Optional action |
| FUP | Follow-up required | Follow-up item created |
| TBA | To be advised | Flagged incomplete |
| NA | Not applicable | No action |

## Action Due Dates (default)

| Finding Type | Days |
|---|---|
| MajorNC | 90 |
| MinorNC | 30 |
| Observation | 60 |
| CriticalDocumentReviewFinding | 90 |
| NonCriticalDocumentReviewFinding | 30 |

## Lag Monitoring Rules

- No activity in 7 days → `AtRisk`
- Past due date → `Overdue`
- Notification sent to assignee on status change to AtRisk or Overdue
- Celery beat runs daily at 07:00 UTC
