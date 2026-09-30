# Prompt Generation Engine

## Overview

Audit prompts are generated from `AuditProcess + ProcessClauseMap + Clause` metadata.

## Generation Logic (`services/audit.py → generate_audit_prompts`)

1. Fetch all `AuditProcess` records for the audit
2. For each process, fetch `ProcessClauseMap` entries where `applicability != NotApplicable`
3. For each clause mapping, generate prompts by type:
   - `DocumentCheck` — only generated if `clause.requires_documented_information = True`
   - `Interview` — always generated
   - `Observation` — always generated
   - `RecordReview` — always generated
4. Set `evidence_required = True` if `requires_retained_evidence OR requires_documented_information`

## Prompt Emphasis

Prompts are structured to verify four things:

1. **Existence** — Is the document/process/control in place?
2. **Currency** — Is it current, reviewed, and approved?
3. **Implementation** — Is it being followed in practice?
4. **Effectiveness** — Is it achieving the intended outcome?

## Example Prompts

### ISO 14001 Clause 6.1.2 (Environmental Aspects)
- `DocumentCheck`: Verify that documented information of environmental aspects and associated impacts is established, maintained, and available where needed.
- `Interview`: Ask the process owner to explain how environmental aspects are identified and how significance is determined for this process.
- `RecordReview`: Review records retained as evidence of conformance with environmental aspects identification requirements.

### ISO 45001 Clause 6.1.2.1 (Hazard Identification)
- `DocumentCheck`: Verify that a documented hazard register is maintained and includes routine, non-routine activities, and emergency situations.
- `Interview`: Ask the process owner to explain how hazards are identified for activities in this process and how the hierarchy of controls is applied.
- `Observation`: Observe the work area and verify that identified controls are implemented as described in the documented information.

## Evidence Required Flag

When `evidence_required = True` on a prompt:
- Mobile UI shows "Evidence required" badge
- Prompt cannot be marked `C` without at least one attached evidence record (Phase 3 enforcement)
- Report auto-generates evidence guidance text from `clause.evidence_guidance`
