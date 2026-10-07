# GSTC Audit App - Manual Testing Guide

**Status**: ✅ All 56 automated tests pass  
**Test Coverage**: 100% of validators (7 functions, all edge cases)

---

## Pre-Testing Checklist

- [ ] Database migration applied: `alembic upgrade head`
- [ ] API server running: `uvicorn app.main:app --reload`
- [ ] Test suite passes: `pytest tests/test_audit_gstc_validation.py`
- [ ] All schemas loaded correctly (no import errors)

---

## Test Scenarios

### Scenario 1: Low Risk Hotel - Standard 1-Day Audit

**Setup**: Create a low-risk hotel audit in a clean country

**Test Steps**:
```bash
# 1. Create audit with LOW risk
curl -X POST http://localhost:8000/audits \
  -H "Content-Type: application/json" \
  -d '{
    "organisation_id": "UUID",
    "audit_type": "Initial",
    "country_code": "NZ",
    "country_corruption_index": 87,
    "risk_level": "LOW",
    "duration_days": 1,
    "has_negative_impacts": false
  }'

# 2. Note the audit_id from response

# 3. Validate GSTC compliance
curl -X POST http://localhost:8000/audits/{audit_id}/validate-gstc \
  -H "Authorization: Bearer {token}"
```

**Expected Results**:
- ✅ Audit created successfully
- ✅ `validate-gstc` returns `is_valid: true`
- ✅ No errors in validation response

---

### Scenario 2: High Risk Hotel - 2+ Day Audit Required

**Test Steps**:
```bash
# 1. Create high-risk hotel (corrupt country)
curl -X POST http://localhost:8000/audits \
  -H "Content-Type: application/json" \
  -d '{
    "organisation_id": "UUID",
    "audit_type": "Initial",
    "country_code": "XX",
    "country_corruption_index": 30,
    "risk_level": "HIGH",
    "duration_days": 2.5,
    "has_negative_impacts": true,
    "duration_justification": "Large multi-site resort with complex operations"
  }'

# 2. Validate
curl -X POST http://localhost:8000/audits/{audit_id}/validate-gstc
```

**Expected Results**:
- ✅ HIGH risk + 2.5 days accepted
- ✅ `is_valid: true`

**Test Negative Case** - Insufficient Duration:
```bash
# Same audit but with 1 day (invalid)
curl -X POST http://localhost:8000/audits \
  -H "Content-Type: application/json" \
  -d '{
    "organisation_id": "UUID",
    "audit_type": "Initial",
    "country_code": "XX",
    "country_corruption_index": 30,
    "risk_level": "HIGH",
    "duration_days": 1
  }'

curl -X POST http://localhost:8000/audits/{audit_id}/validate-gstc
```

**Expected Results**:
- ❌ Validation fails
- ✅ Error: "HIGH risk requires 2+ days"

---

### Scenario 3: Extremely Low Risk - 0.5 Day Audit

**Test Steps**:
```bash
# 1. Create extremely low risk hotel (all criteria met)
curl -X POST http://localhost:8000/audits \
  -H "Content-Type: application/json" \
  -d '{
    "organisation_id": "UUID",
    "audit_type": "Initial",
    "country_code": "NZ",
    "country_corruption_index": 87,
    "risk_level": "EXTREMELY_LOW",
    "duration_days": 0.5,
    "guest_room_count": 12,
    "staff_count": 8,
    "has_event_spaces": false,
    "has_function_spaces": false,
    "has_meeting_spaces": false,
    "is_local_ownership": true,
    "has_internet_access": true,
    "is_sensitive_area": false
  }'

# 2. Validate
curl -X POST http://localhost:8000/audits/{audit_id}/validate-gstc
```

**Expected Results**:
- ✅ All fields accepted
- ✅ `is_valid: true`
- ✅ Audit qualifies for extremely low risk

**Test Qualification Failure** - Too Many Rooms:
```bash
# Same audit but guest_room_count: 25 (fails < 20 requirement)
curl -X POST http://localhost:8000/audits/{audit_id}/validate-gstc
```

**Expected Results**:
- ❌ Validation fails
- ✅ Error: "Does not qualify for extremely low risk"
- ✅ Reason: "Guest rooms >= 20"

---

### Scenario 4: Sensitive Area - Auto-Classified as HIGH RISK

**Test Steps**:
```bash
# 1. Create audit in sensitive area
curl -X POST http://localhost:8000/audits \
  -H "Content-Type: application/json" \
  -d '{
    "organisation_id": "UUID",
    "audit_type": "Initial",
    "country_code": "TZ",
    "risk_level": "HIGH",
    "duration_days": 2,
    "is_sensitive_area": true,
    "sensitive_area_reason": "UNESCO World Heritage Site - Kilimanjaro",
    "sensitive_area_coordinates": "-3.0674,37.3556"
  }'

# 2. Validate
curl -X POST http://localhost:8000/audits/{audit_id}/validate-gstc
```

**Expected Results**:
- ✅ Sensitive area marked as HIGH RISK (mandatory)
- ✅ `is_valid: true`

**Test Violation** - Sensitive Area NOT HIGH RISK:
```bash
# Sensitive area with LOW risk (invalid)
curl -X POST http://localhost:8000/audits \
  -H "Content-Type: application/json" \
  -d '{
    "is_sensitive_area": true,
    "sensitive_area_reason": "IUCN Protected Area",
    "risk_level": "LOW"
  }'

curl -X POST http://localhost:8000/audits/{audit_id}/validate-gstc
```

**Expected Results**:
- ❌ Validation fails
- ✅ Error: "Sensitive area must be classified as HIGH RISK"

---

### Scenario 5: Remote Audit Section Coverage

**Test Steps**:
```bash
# 1. Create remote audit (LOW risk, allowed)
curl -X POST http://localhost:8000/audits \
  -H "Content-Type: application/json" \
  -d '{
    "organisation_id": "UUID",
    "audit_type": "Surveillance",
    "country_code": "AU",
    "risk_level": "LOW",
    "duration_days": 0.5,
    "audit_stage": "DocumentReview"
  }'

# 2. Add prompt with section coverage
# (Section coverage tracked in prompt generation)
```

**Expected Results**:
- ✅ Remote audit created (LOW risk allows remote)
- ✅ Can only audit sections: A, D1, D3

**Test Coverage Validation** (in prompt generation):
- ✅ Remote audit covers only A, D1, D3
- ❌ Remote audit cannot cover B or C (will fail validation)

**Test HIGH Risk Remote** (should fail):
```bash
curl -X POST http://localhost:8000/audits \
  -H "Content-Type: application/json" \
  -d '{
    "audit_type": "Surveillance",
    "risk_level": "HIGH",
    "duration_days": 1,
    "audit_stage": "DocumentReview"
  }'

curl -X POST http://localhost:8000/audits/{audit_id}/validate-gstc
```

**Expected Results**:
- ❌ Validation fails
- ✅ Error: "HIGH risk audits cannot be conducted remotely"

---

### Scenario 6: Surveillance Audit Timing

**Test Steps**:
```bash
# 1. Create initial audit (2023-01-01)
curl -X POST http://localhost:8000/audits \
  -H "Content-Type: application/json" \
  -d '{
    "organisation_id": "UUID",
    "audit_type": "Initial",
    "certification_start_date": "2023-01-01",
    "certification_expiry_date": "2026-01-01",
    "last_audit_date": "2023-01-01"
  }'

# 2. Create surveillance audit (2024-06-01 = 17 months later)
curl -X POST http://localhost:8000/audits \
  -H "Content-Type: application/json" \
  -d '{
    "organisation_id": "UUID",
    "audit_type": "Surveillance",
    "last_audit_date": "2023-01-01"
  }'

curl -X POST http://localhost:8000/audits/{audit_id}/validate-gstc
```

**Expected Results**:
- ❌ Validation fails (exceeds 12-month window)
- ✅ Error: "Last audit 17.0 months ago (must be <= 12)"

**Test Valid Surveillance** (11 months):
```bash
# Surveillance audit 11 months after initial
```

**Expected Results**:
- ✅ `is_valid: true`

---

### Scenario 7: Auditor Conclusions

**Test Steps**:
```bash
# 1. Create audit and generate prompts
curl -X POST http://localhost:8000/audits/{audit_id}/prompts/generate

# 2. Update prompt with response
curl -X PATCH http://localhost:8000/audits/{audit_id}/prompts/{prompt_id} \
  -H "Content-Type: application/json" \
  -d '{
    "response_status": "NC",
    "auditor_conclusion": "NotConform",
    "evidence_type": "Document",
    "evidence_reference": "Missing environmental policy v2.1",
    "basis_for_conclusion": "Policy dated 2021, not updated after 2023 changes"
  }'
```

**Expected Results**:
- ✅ NotConform conclusion recorded
- ✅ Finding auto-created
- ✅ Action assigned for remediation

**Test Conclusion Mapping**:
- NC → NotConform (auto-assigned)
- C → Conform (auto-assigned)
- OBS → Conform (enhancement, not NC)
- NA → NotAssessed (not applicable)

---

## Database Migration Verification

**Test Steps**:
```sql
-- Connect to PostgreSQL
psql -U postgres -d audit_app

-- Verify new columns exist
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'audits' 
ORDER BY ordinal_position
LIMIT 30;

-- Should show: country_code, country_corruption_index, risk_level, etc.

-- Verify enum types
SELECT * FROM pg_type WHERE typname LIKE '%risk%level%';
```

**Expected Results**:
- ✅ 22 new columns in audits table
- ✅ Enum types created: risk_level_enum, auditor_conclusion_enum
- ✅ All columns nullable (except defaults)

---

## API Schema Verification

**Test Steps**:
```bash
# 1. Check OpenAPI schema
curl http://localhost:8000/openapi.json | grep -A 20 "AuditCreate"

# 2. Verify new fields appear
```

**Expected Results**:
- ✅ country_code in schema
- ✅ risk_level in schema
- ✅ guest_room_count in schema
- ✅ All 22 fields present

---

## Performance Testing (Optional)

**Test Steps**:
```bash
# 1. Time validation endpoint with comprehensive audit
time curl -X POST http://localhost:8000/audits/{audit_id}/validate-gstc

# 2. Measure validator execution
```

**Expected Results**:
- ✅ Response < 500ms (local)
- ✅ All 7 validators execute in parallel or sequential without blocking

---

## Regression Testing

**Test Steps**:
```bash
# 1. Verify existing audit operations still work
curl -X GET http://localhost:8000/audits
curl -X GET http://localhost:8000/audits/{old_audit_id}
curl -X PATCH http://localhost:8000/audits/{old_audit_id} \
  -d '{"status": "InProgress"}'

# 2. Verify prompt generation still works
curl -X POST http://localhost:8000/audits/{audit_id}/prompts/generate

# 3. Verify finding/action creation still works
```

**Expected Results**:
- ✅ All existing endpoints work
- ✅ No breaking changes
- ✅ Backward compatible

---

## Test Summary

| Scenario | Test Cases | Expected | Actual | Status |
|----------|-----------|----------|--------|--------|
| Low Risk | 2 | ✅ Pass | | TBD |
| High Risk | 3 | ✅ Pass | | TBD |
| Extremely Low Risk | 3 | ✅ Pass | | TBD |
| Sensitive Area | 2 | ✅ Pass | | TBD |
| Remote Audit | 2 | ✅ Pass | | TBD |
| Surveillance Timing | 2 | ✅ Pass | | TBD |
| Auditor Conclusions | 4 | ✅ Pass | | TBD |
| Database | 2 | ✅ Pass | | TBD |
| API Schema | 1 | ✅ Pass | | TBD |
| Regression | 3 | ✅ Pass | | TBD |

---

## Sign-Off Criteria

- [x] All 56 automated tests pass
- [ ] Manual test scenarios 1-7 pass
- [ ] Database migration verified
- [ ] API schema verified
- [ ] Regression testing complete
- [ ] Performance acceptable
- [ ] Documentation complete

**Ready for Production**: Once all manual tests pass

---

## Troubleshooting

### Migration Failed
```bash
# Rollback migration
alembic downgrade -1

# Check migration status
alembic current

# Re-run migration
alembic upgrade head
```

### Validation Endpoint 404
- Verify router import added: `from ..services.audit_validator import validate_audit_against_gstc`
- Verify endpoint added to routers/audits.py
- Restart API server

### Tests Fail
```bash
# Run with verbose output
pytest tests/test_audit_gstc_validation.py -vv

# Run single test
pytest tests/test_audit_gstc_validation.py::TestRiskLevelValidation::test_valid_high_risk -vv
```

### Schema Errors
- Verify all new fields match model definitions
- Check for typos in field names
- Run: `python -c "from app.schemas.audit import AuditCreate; print(AuditCreate.model_fields.keys())"`

