# GSTC Hotel Standard Integration

## Overview

The system now uses the **official GSTC Hotel Standard v4.01** criteria as the authoritative source for all audits and reports.

- **Source**: https://www.gstc.org/wp-content/uploads/GSTC-Hotel-Standard.pdf
- **Version**: 4.01
- **Total Criteria**: 40
- **Structure**: 4 pillars (A, B, C, D) with 14, 9, 4, and 13 criteria respectively

### Four Pillars

| Pillar | Code | Name | Criteria |
|--------|------|------|----------|
| A | A1–A14 | Demonstrate Effective Sustainable Management | 14 |
| B | B1–B9 | Maximize Social and Economic Benefits | 9 |
| C | C1–C4 | Maximize Benefits to Cultural Heritage | 4 |
| D | D1–D13 | Maximize Environmental Benefits | 13 |

## Key Changes

### 1. Authoritative Criteria Source

The system now loads criteria from the official GSTC standard file:
```
services/api/app/data/gstc-hotel-standard-v4.01.json
```

This JSON file contains:
- Full criterion text and statement
- Indicators for each criterion
- Metadata (version, source URL, date)

### 2. New Module: `gstc_standard.py`

Located at: `services/api/app/services/gstc_standard.py`

**Key Functions:**

```python
# Get all criteria
gstc_standard.get_all_criteria()  # Returns dict of all 40 criteria

# Get a specific criterion
gstc_standard.get_criterion("A1")  # Returns A1 criterion data

# Get all criteria for a pillar
gstc_standard.get_pillar_criteria("B")  # Returns B1–B9

# Validate criteria codes
valid, invalid = gstc_standard.validate_criteria_codes(["A1", "B2", "X99"])

# Get standard metadata
gstc_standard.get_standard_metadata()  # Returns version, source, date, total
```

### 3. Criteria Validation

All criteria codes used in audits are now validated against the official GSTC standard:
- Valid codes: A1–A14, B1–B9, C1–C4, D1–D13
- Custom codes allowed: X1, X2, etc. (for audit-specific requirements)
- Invalid codes are automatically converted to custom codes (X1, X2, etc.)

### 4. API Endpoints

New endpoints provide access to the official GSTC criteria:

#### Get Standard Metadata
```
GET /reports/gstc-standard/metadata
```
Returns version, source URL, date, and total criteria count.

#### Get All Criteria
```
GET /reports/gstc-standard/criteria
```
Returns all 40 GSTC criteria with full text and indicators.

#### Get Pillar Criteria
```
GET /reports/gstc-standard/pillar/{pillar_code}
```
Returns all criteria for a pillar (A, B, C, or D).

**Example:**
```bash
curl http://localhost:8000/reports/gstc-standard/pillar/A
```

### 5. Report Generation

#### AI Prompts

The AI report generation system (`report_ai.py`) now:
- References the official GSTC v4.01 criteria in the system prompt
- Explicitly lists valid criterion codes (A1–A14, B1–B9, C1–C4, D1–D13)
- Requires that all criteria mentioned in reports come from the official standard
- Rejects AI-generated criteria that don't exist in the standard

#### Report Validation

Reports are validated to ensure:
- Only official GSTC criteria are referenced
- Criteria statements match the official standard
- Evidence is linked to correct criteria

## Implementation Details

### Criteria Structure

Each criterion in the JSON has:
```json
{
  "code": "A1",
  "title": "Sustainability Management System",
  "statement": "The hotel operates under a documented sustainability management system...",
  "indicators": [
    {
      "number": 1,
      "text": "The hotel has a written sustainability policy..."
    },
    ...
  ]
}
```

### Data Flow

```
GSTC PDF (official source)
    ↓
Extracted to: gstc-hotel-standard-v4.01.json
    ↓
Loaded by: gstc_standard.py
    ↓
Used by:
  - Audit templates (map requirements to official criteria)
  - Report generation (validate criteria usage)
  - API endpoints (provide criteria access)
  - AI prompts (ensure correct criteria)
```

## Database Integration

Existing audit templates map their requirements to GSTC criteria via:
- `requirement.source.clause` field (e.g., "A1", "B2")
- Validated against the official standard on load
- Invalid codes converted to custom codes (X1, X2)

## Maintenance

### Updating the Standard

If GSTC publishes a new version:

1. Download the new PDF from https://www.gstc.org/
2. Update the extraction script (currently in `/tmp/extract_full_criteria.py`)
3. Regenerate the JSON file:
   ```bash
   python extract_full_criteria.py
   ```
4. Replace `services/api/app/data/gstc-hotel-standard-v4.01.json`
5. Update the version in `gstc_standard.py` if needed

### Audit Template Alignment

When creating or updating audit templates:
1. Ensure all requirements map to valid GSTC criteria
2. Use codes from the official standard (A1–A14, B1–B9, C1–C4, D1–D13)
3. Include criterion statements and indicators from `gstc_standard.py`

## Testing

To verify the integration is working:

```python
from services.api.app.services import gstc_standard

# Load the standard
criteria = gstc_standard.get_all_criteria()
print(f"Loaded {len(criteria)} criteria")

# Check a specific criterion
a1 = gstc_standard.get_criterion("A1")
print(f"A1: {a1['title']}")

# Validate codes
valid, invalid = gstc_standard.validate_criteria_codes(["A1", "ZZ99"])
print(f"Valid: {valid}, Invalid: {invalid}")
```

## Benefits

✅ **Accuracy**: All criteria come from the official GSTC source  
✅ **Currency**: Can be updated when GSTC releases new versions  
✅ **Consistency**: Single source of truth for all audits  
✅ **Traceability**: All report criteria link back to official standard  
✅ **Validation**: Invalid criteria are automatically caught  
✅ **Transparency**: API endpoints provide public access to criteria  

## References

- GSTC Hotel Standard: https://www.gstc.org/
- Standard PDF: https://www.gstc.org/wp-content/uploads/GSTC-Hotel-Standard.pdf
- Certification bodies: https://www.gstc.org/get-certified/about-certification
