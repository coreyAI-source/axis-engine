# AXIS-Engine: GSTC Hotel Standard Integration

## Completion Status: ✅ DONE

The system now uses the **official GSTC Hotel Standard v4.01** as the authoritative source for all criteria in audits and readiness reports.

### What Was Done

#### 1. **Official Standard Data Extraction** ✅
- Downloaded GSTC Hotel Standard PDF: https://www.gstc.org/wp-content/uploads/GSTC-Hotel-Standard.pdf
- Parsed and extracted all 40 criteria with full text and indicators
- Created structured JSON file: `services/api/app/data/gstc-hotel-standard-v4.01.json`
- File size: 42.5 KB with complete criterion statements and indicator lists

#### 2. **New Module: `gstc_standard.py`** ✅
Created comprehensive criteria management module at `services/api/app/services/gstc_standard.py`

**Features:**
- Load official GSTC criteria from JSON
- Get individual criteria by code (A1, B2, etc.)
- Get criteria by pillar (all A criteria, all B criteria, etc.)
- Validate criterion codes
- Get metadata about the standard (version, source, date)

**Key Functions:**
```python
gstc_standard.get_all_criteria()           # All 40 criteria
gstc_standard.get_criterion("A1")          # Specific criterion
gstc_standard.get_pillar_criteria("B")     # Pillar B1–B9
gstc_standard.validate_criteria_codes([...]) # Validate codes
gstc_standard.get_standard_metadata()      # Version, source, etc.
```

#### 3. **Updated Report Generation** ✅
Modified `services/api/app/services/report_ai.py`:
- System prompt now explicitly references GSTC Hotel Standard v4.01
- Lists valid criterion codes (A1–A14, B1–B9, C1–C4, D1–D13)
- AI model instructed to use ONLY official criteria
- Prevents hallucinated or outdated criteria in reports

#### 4. **Criteria Validation** ✅
Updated `services/api/app/services/readiness_report.py`:
- Added `_validate_criteria_code()` function
- Validates all criterion codes against official standard
- Converts invalid codes to custom codes (X1, X2, etc.)
- Ensures report criteria align with GSTC standard

#### 5. **API Endpoints** ✅
Added new endpoints to `services/api/app/routers/reports.py`:

```
GET /reports/gstc-standard/metadata
  → Returns: version, source URL, date, total criteria

GET /reports/gstc-standard/criteria
  → Returns: All 40 GSTC criteria with full text

GET /reports/gstc-standard/pillar/{pillar_code}
  → Returns: Criteria for pillar A, B, C, or D
```

#### 6. **Documentation** ✅
- `GSTC_INTEGRATION.md` — Complete technical documentation
- `GSTC_QUICK_START.md` — Quick reference for developers
- This file — Implementation summary

---

## The 40 Official Criteria

### Pillar A: Demonstrate Effective Sustainable Management (14 criteria)
**A1–A14:** Management systems, legal compliance, staff welfare, reporting, procurement, etc.

### Pillar B: Maximize Social and Economic Benefits (9 criteria)
**B1–B9:** Community support, local employment, working conditions, equity, etc.

### Pillar C: Maximize Cultural Heritage Benefits (4 criteria)
**C1–C4:** Cultural interactions, heritage protection, artifact management, etc.

### Pillar D: Maximize Environmental Benefits (13 criteria)
**D1–D13:** Energy, water, emissions, waste, pollution, biodiversity, wildlife, etc.

---

## How It Works Now

### Before
```
Audit Template (possibly outdated)
    ↓
Manually maintained criteria list
    ↓
Report generation (criteria not validated)
    ↓
Risk: Criteria could be outdated or incorrect
```

### After
```
Official GSTC PDF
    ↓
Extracted & Stored: gstc-hotel-standard-v4.01.json
    ↓
Loaded by: gstc_standard.py module
    ↓
Used by: Report generation, API, AI prompts, validation
    ↓
Benefit: Single source of truth, automatic validation
```

---

## Integration Points

### Audit Templates
Requirements should map to official criteria:
```json
{
  "id": "req-123",
  "source": {
    "clause": "A1"  // Valid: A1–A14, B1–B9, C1–C4, D1–D13
  }
}
```

### Report Generation
- AI uses official criteria when drafting narratives
- Report validation ensures only official criteria are referenced
- Custom criteria (X1, X2) allowed for audit-specific items

### API Access
Developers and tools can fetch official criteria:
```bash
curl http://localhost:8000/reports/gstc-standard/criteria
```

---

## Testing & Validation

**All files verified:**
```
✓ gstc_standard.py          (3.5 KB)  - Module loads & functions
✓ report_ai.py              (5.6 KB)  - Updated system prompt
✓ readiness_report.py       (45.8 KB) - Criteria validation added
✓ reports.py                (2.4 KB)  - New API endpoints
✓ gstc-hotel-standard-v4.01.json (42.5 KB) - All 40 criteria loaded
```

**Python syntax validated:** ✅ All files compile without errors

**Data verification:** ✅ All 40 criteria present and accessible

---

## Usage Examples

### Python: Get a Criterion
```python
from services.api.app.services import gstc_standard

a1 = gstc_standard.get_criterion("A1")
print(a1["title"])           # "Sustainability Management System"
print(a1["statement"])       # Full criterion text
print(len(a1["indicators"])) # 8 indicators
```

### Python: Validate Codes
```python
valid, invalid = gstc_standard.validate_criteria_codes(["A1", "B2", "ZZ"])
# valid:   ['A1', 'B2']
# invalid: ['ZZ']
```

### API: Get All Criteria
```bash
curl -H "Authorization: Bearer {token}" \
  http://localhost:8000/reports/gstc-standard/criteria | jq .
```

### API: Get Pillar
```bash
curl -H "Authorization: Bearer {token}" \
  http://localhost:8000/reports/gstc-standard/pillar/A | jq .
```

---

## Maintenance & Updates

### When GSTC Releases a New Version

1. Download new PDF from https://www.gstc.org/
2. Run extraction script (regenerate JSON)
3. Replace `gstc-hotel-standard-v4.01.json`
4. Optionally update module version constants
5. Test that all criterion codes still validate

### Version Tracking

Current version in system:
- **GSTC Hotel Standard v4.01**
- **Extracted:** 2025-12-30
- **Total Criteria:** 40
- **Source:** https://www.gstc.org/wp-content/uploads/GSTC-Hotel-Standard.pdf

---

## Files Modified/Created

### Created
- `services/api/app/services/gstc_standard.py` — New module
- `services/api/app/data/gstc-hotel-standard-v4.01.json` — Standard data
- `GSTC_INTEGRATION.md` — Technical documentation
- `GSTC_QUICK_START.md` — Quick reference
- `README_GSTC_SETUP.md` — This file

### Modified
- `services/api/app/services/report_ai.py` — Import gstc_standard, updated prompt
- `services/api/app/services/readiness_report.py` — Import gstc_standard, validation function
- `services/api/app/routers/reports.py` — New API endpoints

---

## Benefits

✅ **Official Source** — Uses the true GSTC standard, not a copy  
✅ **Current** — Can be updated when GSTC releases new versions  
✅ **Validated** — All criteria codes automatically validated  
✅ **Consistent** — Single source of truth across all audits  
✅ **Accessible** — API endpoints provide public access  
✅ **Trustworthy** — Reports backed by official criteria  

---

## Next Steps

1. **Test** — Run existing audit/report tests to ensure compatibility
2. **Verify** — Check that audit templates work with new validation
3. **Monitor** — Watch for GSTC standard updates
4. **Document** — Update internal docs if templates change

---

## References

- **GSTC Organization**: https://www.gstc.org/
- **Standard PDF**: https://www.gstc.org/wp-content/uploads/GSTC-Hotel-Standard.pdf
- **Certification Bodies**: https://www.gstc.org/get-certified/about-certification
- **Technical Docs**: See `GSTC_INTEGRATION.md`
- **Quick Start**: See `GSTC_QUICK_START.md`

---

**Integration completed on: 2026-10-05**  
**Status: Ready for testing and deployment** ✅
