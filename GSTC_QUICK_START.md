# GSTC Integration - Quick Start

## What Changed

The system now uses **official GSTC Hotel Standard v4.01 criteria** as the authoritative source. All audits, templates, and reports reference the true GSTC standard, not a possibly-outdated copy.

## How to Use

### 1. In Audit Templates

Ensure requirements map to official GSTC criteria:
```json
{
  "id": "req-123",
  "title": "Sustainability Management",
  "source": {
    "clause": "A1"  // Must be A1-A14, B1-B9, C1-C4, or D1-D13
  }
}
```

### 2. In Code

```python
from services.api.app.services import gstc_standard

# Get a criterion
a1 = gstc_standard.get_criterion("A1")
print(a1["statement"])  # Full criterion text
print(a1["indicators"])  # List of indicators

# Get all criteria for a pillar
b_criteria = gstc_standard.get_pillar_criteria("B")

# Validate codes
valid, invalid = gstc_standard.validate_criteria_codes(["A1", "ZZ99"])
# Returns: (['A1'], ['ZZ99'])
```

### 3. Via API

```bash
# Get standard metadata
curl http://localhost:8000/reports/gstc-standard/metadata

# Get all criteria
curl http://localhost:8000/reports/gstc-standard/criteria

# Get criteria for pillar B (Socioeconomic)
curl http://localhost:8000/reports/gstc-standard/pillar/B
```

### 4. In Reports

The AI-generated reports now:
- Only reference official GSTC criteria
- Validate all criterion codes before use
- Link back to the official standard

## The 40 Official Criteria

### Pillar A: Sustainable Management (A1–A14)
- A1: Sustainability Management System
- A2: Legal Compliance
- A3: Guest and Staff Welfare
- A4: Reporting and Communication
- A5: Accurate Promotion
- A6: Information Sharing and Guidance
- A7: Staff Engagement
- A8: Guest Experience
- A9: Collaboration with Stakeholders
- A10: Land, Water, and Property Rights
- A11: Site Selection, Planning, and Development
- A12: Buildings, Construction, and Infrastructure
- A13: Procurement
- A14: Food and Beverages

### Pillar B: Socioeconomic Benefits (B1–B9)
- B1: Community Support
- B2: Local Employment
- B3: Local Entrepreneur Support
- B4: Community Services and Facilities
- B5: Access for All
- B6: Code of Conduct
- B7: Exploitation, Harassment, and Abuse
- B8: Employment Inclusion and Equality
- B9: Decent Work

### Pillar C: Cultural Heritage (C1–C4)
- C1: Cultural Interactions
- C2: Protecting Cultural Heritage
- C3: Presenting Culture and Heritage
- C4: Artifacts

### Pillar D: Environmental Benefits (D1–D13)
- D1: Energy Conservation
- D2: Water Conservation
- D3: Greenhouse Gas Emissions
- D4: Transportation
- D5: Wastewater
- D6: Solid Waste
- D7: Harmful Substances
- D8: Minimize Pollution
- D9: Biodiversity Conservation
- D10: Invasive Species
- D11: Interactions with Animals
- D12: Animal Welfare
- D13: Wildlife Harvesting and Trade

## Custom Criteria

Need audit-specific requirements not in GSTC? Use custom codes:
```json
{
  "id": "req-custom",
  "source": {
    "clause": "X1"  // Custom requirement
  }
}
```

These are allowed and won't cause validation errors. They appear in reports as additional requirements.

## Source Files

- **Data**: `services/api/app/data/gstc-hotel-standard-v4.01.json`
- **Module**: `services/api/app/services/gstc_standard.py`
- **Documentation**: `GSTC_INTEGRATION.md`

## Next Steps

1. ✅ Integration complete
2. Run tests to verify audit templates still work
3. Test report generation with new validation
4. Update any templates with invalid criterion codes

## Support

For questions about the GSTC standard itself, see:
- https://www.gstc.org/
- https://www.gstc.org/wp-content/uploads/GSTC-Hotel-Standard.pdf
