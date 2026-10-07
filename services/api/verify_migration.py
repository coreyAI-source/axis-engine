#!/usr/bin/env python3
"""Verify GSTC migration was applied successfully."""

from sqlalchemy import inspect, create_engine
from app.config import settings

engine = create_engine(str(settings.database_url))
inspector = inspect(engine)

# Get audit table columns
columns = inspector.get_columns('audits')
print(f'✅ Total audit table columns: {len(columns)}')
print()

# Check for new GSTC columns
gstc_columns_to_check = [
    'country_code', 'country_corruption_index', 'risk_level',
    'guest_room_count', 'staff_count', 'is_sensitive_area',
    'sensitive_area_reason', 'certification_start_date',
    'last_audit_date', 'audit_cycle_number'
]

found_columns = {c['name']: c for c in columns}

print('GSTC Columns Verification:')
found = 0
for col_name in gstc_columns_to_check:
    if col_name in found_columns:
        col = found_columns[col_name]
        print(f'  ✅ {col_name:35} {col["type"]}')
        found += 1
    else:
        print(f'  ❌ {col_name:35} MISSING')

print()
print(f'Result: {found}/{len(gstc_columns_to_check)} GSTC columns found')
print()

# Check AuditPrompt table
prompts = inspector.get_columns('audit_prompts')
prompt_gstc = [c for c in prompts if c['name'] in [
    'auditor_conclusion', 'evidence_type', 'evidence_reference',
    'basis_for_conclusion', 'observation_notes', 'follow_up_notes'
]]

print('AuditPrompt Columns:')
for col in prompt_gstc:
    print(f'  ✅ {col["name"]:35} {col["type"]}')

print()
print('✅ Migration verification complete!')
