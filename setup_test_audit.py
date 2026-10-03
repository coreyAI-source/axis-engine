#!/usr/bin/env python3
"""
Setup script to populate a single test hotel audit with realistic data.
Deletes all other audits and fills the remaining one with assessment data, evidence, and notes.
"""

import asyncio
import json
import uuid
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Optional
import sys

# PIL for generating test images
try:
    from PIL import Image, ImageDraw
except ImportError:
    print("Installing Pillow for image generation...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "Pillow", "-q"])
    from PIL import Image, ImageDraw

# Database imports
from sqlalchemy import select, delete, desc
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

# Models
sys.path.insert(0, str(Path(__file__).parent / "services" / "api"))

from app.models.hospitality import HospitalityAudit, HospitalityFile
from app.models.org import User, Organisation
from app.config import settings

# Generate test images
def create_test_image(width: int = 800, height: int = 600, label: str = "Evidence") -> bytes:
    """Create a realistic-looking test image."""
    img = Image.new('RGB', (width, height), color=(245, 245, 245))
    draw = ImageDraw.Draw(img)

    # Draw a border
    draw.rectangle([(10, 10), (width-10, height-10)], outline='#333', width=3)

    # Add label text
    draw.text((50, 50), label, fill='#333')
    draw.text((50, 100), f"Test Evidence - {datetime.now().strftime('%Y-%m-%d %H:%M')}", fill='#666')

    # Add some mock content
    y_pos = 150
    for i in range(5):
        draw.line([(50, y_pos + i*30), (width-50, y_pos + i*30)], fill='#ddd', width=1)

    # Save to bytes
    from io import BytesIO
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    return buffer.getvalue()


# GSTC Hotel Standard v4.0 criteria data (simplified)
GSTC_CRITERIA = {
    "A1": {
        "title": "Environmental and social policy",
        "text": "The organisation has an environmental and social policy that aims to be a global leader in sustainable tourism.",
        "category": "Governance",
        "indicators": [
            "Written policies are in place and signed by senior management",
            "Policy covers environmental and social sustainability",
            "Policy is publicly available"
        ]
    },
    "A2": {
        "title": "Environmental management plan",
        "text": "The organisation has an environmental management plan in place.",
        "category": "Governance",
        "indicators": [
            "Written plan exists and is dated",
            "Plan covers all main environmental impacts",
            "Plan is reviewed annually"
        ]
    },
    "A3": {
        "title": "Monitoring and evaluation",
        "text": "The organisation monitors and evaluates its environmental performance.",
        "category": "Governance",
        "indicators": [
            "Baseline environmental data is collected",
            "Regular monitoring data is available",
            "Performance targets are set and tracked"
        ]
    },
    "B1": {
        "title": "Water consumption",
        "text": "The organisation measures and manages water consumption.",
        "category": "Environmental",
        "indicators": [
            "Total water consumption is measured",
            "Water consumption per guest is tracked",
            "Water conservation measures are in place"
        ]
    },
    "B2": {
        "title": "Water sources",
        "text": "Water is sourced responsibly.",
        "category": "Environmental",
        "indicators": [
            "Water source information is documented",
            "Impact on local water resources is assessed",
            "Water is not sourced from sensitive areas"
        ]
    },
    "C1": {
        "title": "Waste reduction",
        "text": "The organisation has a waste reduction programme.",
        "category": "Environmental",
        "indicators": [
            "Waste reduction targets are set",
            "Waste is monitored and measured",
            "Recycling programme is implemented"
        ]
    },
    "D1": {
        "title": "Staff wellbeing",
        "text": "The organisation ensures staff wellbeing and safety.",
        "category": "Social",
        "indicators": [
            "Staff training programme is in place",
            "Working conditions meet legal standards",
            "Staff satisfaction is monitored"
        ]
    },
}

# Assessment outcomes for realistic variety
ASSESSMENT_DATA = {
    "A1": {"status": "conforming", "rationale": "Strong written policy in place, signed by General Manager. Policy covers environmental conservation, cultural preservation, and community engagement. Publicly available on hotel website."},
    "A2": {"status": "conforming", "rationale": "Comprehensive environmental management plan updated annually. Covers water, energy, waste, biodiversity, and community impacts. Implementation tracked quarterly."},
    "A3": {"status": "minor", "rationale": "Environmental monitoring system in place but data collection is incomplete for some metrics. Monthly data available for energy and water. Recommend implementing automated meter reading."},
    "B1": {"status": "conforming", "rationale": "Water meters installed on main building. Consumption tracked monthly and reviewed quarterly. 2025 consumption: 312 m³/guest/year (target: 280 m³)."},
    "B2": {"status": "observation", "rationale": "Water sourced from municipal supply. No risk of overexploitation. Local water authority confirms sustainable supply. Recommend documenting water quality assessments annually."},
    "C1": {"status": "major", "rationale": "Basic waste segregation in place but no formal waste reduction targets. Currently 45% of waste to landfill. Recommend establishing 20% reduction target within 12 months."},
    "D1": {"status": "conforming", "rationale": "Mandatory staff training programme covering sustainability, cultural sensitivity, and safety. Annual training completion rate: 96%. Staff satisfaction survey average rating: 4.2/5."},
}

async def setup_test_audit():
    """Main setup function."""
    engine = create_async_engine(settings.database_url, echo=False)
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        try:
            # Get or create test organization and user
            org = await session.scalar(
                select(Organisation).where(Organisation.name == "Test Organization").limit(1)
            )

            if not org:
                print("Creating test organization...")
                org = Organisation(
                    id=uuid.uuid4(),
                    name="Test Organization",
                    industry="Hospitality",
                    country="United States"
                )
                session.add(org)
                await session.flush()

            # Get or create test user
            user = await session.scalar(
                select(User).where(
                    User.organisation_id == org.id,
                    User.email == "auditor@test.local"
                ).limit(1)
            )

            if not user:
                print("Creating test user...")
                from app.utils.security import hash_password
                user = User(
                    id=uuid.uuid4(),
                    organisation_id=org.id,
                    first_name="Test",
                    last_name="Auditor",
                    email="auditor@test.local",
                    hashed_password=hash_password("TestPassword123!"),
                    role_code="lead_auditor",
                    active_flag=True
                )
                session.add(user)
                await session.flush()

            # Delete all audits except one
            all_audits = await session.scalars(
                select(HospitalityAudit)
                .where(HospitalityAudit.organisation_id == org.id)
                .order_by(desc(HospitalityAudit.created_at))
            )

            all_audits_list = all_audits.all()

            if len(all_audits_list) > 1:
                print(f"Deleting {len(all_audits_list) - 1} existing audits...")
                for audit in all_audits_list[1:]:
                    # Delete associated files
                    await session.execute(
                        delete(HospitalityFile).where(HospitalityFile.audit_id == audit.id)
                    )
                    # Delete the audit
                    await session.delete(audit)
                await session.flush()
                audit_to_update = all_audits_list[0]
            elif len(all_audits_list) == 1:
                audit_to_update = all_audits_list[0]
            else:
                print("No audits found. Creating new test audit...")
                # Create a new audit if none exist
                from app.services.hospitality import run_engine
                result = await run_engine(
                    "create",
                    {"name": "Test Auditor", "userId": str(user.id), "authenticated": True},
                    input={
                        "title": "2026 GSTC Sustainability Audit",
                        "siteName": "Bali Practice Hotel",
                        "scopeStatement": "Full hotel audit covering all 40 GSTC criteria. Includes main building (180 rooms), spa facilities, restaurant and bar operations, and 2-hectare grounds."
                    }
                )

                if not result["ok"]:
                    print(f"Error creating audit: {result['violations']}")
                    return

                bundle = result["value"]
                audit_to_update = HospitalityAudit(
                    id=uuid.UUID(bundle["audit"]["id"]),
                    organisation_id=org.id,
                    created_by=user.id,
                    title=bundle["audit"]["title"],
                    site_name=bundle["audit"]["siteName"],
                    status=bundle["audit"]["status"],
                    version=1,
                    bundle=bundle
                )
                session.add(audit_to_update)
                await session.flush()

            print(f"\nUpdating audit: {audit_to_update.title} at {audit_to_update.site_name}")

            # Load the current bundle
            bundle = audit_to_update.bundle

            # Add realistic readiness profile
            print("Adding readiness profile...")
            readiness_profile = {
                "hotel_name": "Bali Practice Hotel",
                "location": "Ubud, Bali, Indonesia",
                "hotel_contact_name": "Ketut Wijaya",
                "hotel_contact_role": "General Manager",
                "purpose": "GSTC Certification Readiness Assessment",
                "standard_edition": "GSTC Hotel Standard v4.0",
                "standard_used": "GSTC Hotel Standard v4.0 - Global Criteria",
                "review_date": "2026-10-02",
                "reviewer": "Test Auditor",
                "reviewer_contact": "auditor@test.local",
                "report_reference": "BAL-2026-Q4-001",
                "report_date": "2026-10-03",
                "confidentiality": "This assessment is confidential and intended for the hotel management team only.",
                "staff_present": "General Manager, Sustainability Manager, Engineering Manager, Housekeeping Supervisor",
                "review_type": "Full facility assessment",
                "duration": "2 days on-site (October 1-2, 2026)",
                "method": "Documentation review, on-site inspection, staff interviews, facility tours",
                "hotel_type": "Luxury eco-resort",
                "rooms": "180 guest rooms + 12 suites",
                "staff": "240 full-time staff + 80 seasonal workers",
                "facilities": "Spa (1500 m²), restaurant (250 seats), bar, conference center (800 m²), 2 pools, wellness center",
                "occupancy": "Current: 72% average annual occupancy",
                "water_sources": "Municipal supply (main) + rainwater harvesting system (secondary)",
                "wastewater": "Municipal treatment plant + on-site greywater recycling (40% of garden irrigation)",
                "existing_certifications": "Green Building Council certification (2020), ISO 14001 (2023)",
                "people_interviewed": "Ketut Wijaya (GM), Putu Sari (Sustainability Manager), Wayan Agus (Engineering), Santi (Housekeeping), 8 frontline staff",
                "areas_inspected": "All guest rooms, common areas, kitchen, spa, laundry, waste management area, water treatment facility, energy systems",
                "areas_not_inspected": "None - full facility access granted",
                "plan_changes": "Building plans reviewed for past 3 years. No major construction planned for 2026.",
                "key_figures": "Annual electricity: 450,000 kWh (32 kWh/m²). Annual water: 312 m³/guest. Waste per guest: 2.1 kg/day. Staff turnover: 18% annually.",
                "legal_items": "All licenses current: Hotel operation permit, environmental compliance certificate, building permits for spa renovation (2023). No violations in past 5 years.",
                "prepared_by": "Test Auditor",
                "reviewed_by": "Test Auditor",
                "issued_to": "Ketut Wijaya, General Manager",
                "next_step": "Preliminary findings review meeting scheduled for October 10, 2026. Full report delivery by October 30, 2026."
            }

            audit_to_update.report_profile = readiness_profile

            # Add evidence and assessments
            print("Adding evidence and assessments...")

            now = datetime.now(timezone.utc)
            evidence_counter = 0

            for criterion_code, assessment_data in ASSESSMENT_DATA.items():
                if criterion_code not in GSTC_CRITERIA:
                    continue

                criteria = GSTC_CRITERIA[criterion_code]

                # Find or create requirement
                requirement = next(
                    (r for r in bundle.get("requirements", [])
                     if (r.get("source", {}).get("clause") or "").upper() == criterion_code),
                    None
                )

                if not requirement:
                    continue

                # Add evidence (create 2-3 pieces per criterion)
                evidence_ids = []

                for ev_idx in range(2):
                    evidence_id = str(uuid.uuid4())
                    evidence_counter += 1

                    # Create test image
                    image_data = create_test_image(
                        label=f"{criterion_code} - Evidence {ev_idx + 1}: {['Document', 'Photos', 'Inspection notes'][ev_idx % 3]}"
                    )

                    # Add to evidence list
                    evidence_entry = {
                        "id": evidence_id,
                        "auditId": str(audit_to_update.id),
                        "kind": ["document", "photo", "photo"][ev_idx % 3],
                        "description": [
                            f"Policy documentation and implementation checklist for {criteria['title'].lower()}",
                            f"On-site photograph showing implementation of {criterion_code} requirements",
                            f"Interview notes and staff training records related to {criterion_code}"
                        ][ev_idx % 3],
                        "reference": [
                            f"File: {criterion_code}_policy_2026.pdf",
                            f"Photo taken: {(now - timedelta(days=5 + ev_idx)).strftime('%Y-%m-%d')}",
                            f"Interview date: {(now - timedelta(days=3)).strftime('%Y-%m-%d')}"
                        ][ev_idx % 3],
                        "attachment": {
                            "key": f"hospitality/{audit_to_update.id}/{evidence_id}",
                            "fileName": f"{criterion_code}_evidence_{ev_idx + 1}.png",
                            "contentType": "image/png",
                            "sizeBytes": len(image_data),
                            "sha256": "0" * 64  # Placeholder
                        },
                        "collectedBy": {"name": "Test Auditor", "userId": str(user.id), "authenticated": True},
                        "collectedAt": (now - timedelta(days=5 - ev_idx)).isoformat(),
                        "collectedVia": ["on_site", "on_site", "interview"][ev_idx % 3]
                    }

                    if "evidence" not in bundle:
                        bundle["evidence"] = []
                    bundle["evidence"].append(evidence_entry)
                    evidence_ids.append(evidence_id)

                    # Save file to database
                    file_record = HospitalityFile(
                        id=uuid.UUID(evidence_id),
                        audit_id=audit_to_update.id,
                        evidence_id=evidence_id,
                        file_name=f"{criterion_code}_evidence_{ev_idx + 1}.png",
                        content_type="image/png",
                        sha256="0" * 64,
                        content=image_data
                    )
                    session.add(file_record)

                # Add assessment
                assessment_id = str(uuid.uuid4())
                assessment = {
                    "id": assessment_id,
                    "auditId": str(audit_to_update.id),
                    "requirementId": requirement["id"],
                    "status": assessment_data["status"],
                    "rationale": assessment_data["rationale"],
                    "evidenceIds": evidence_ids,
                    "snapshot": {
                        "requirementId": requirement["id"],
                        "requirementVersion": requirement.get("version", 1),
                        "text": requirement.get("text", ""),
                        "source": requirement.get("source", {}),
                        "auditPrompt": requirement.get("auditPrompt", ""),
                        "category": requirement.get("category", ""),
                        "critical": requirement.get("critical", False),
                        "weight": requirement.get("weight", 1)
                    },
                    "assessedBy": {"name": "Test Auditor", "userId": str(user.id), "authenticated": True},
                    "assessedAt": (now - timedelta(days=2)).isoformat(),
                    "indicatorInputs": [
                        {
                            "index": idx,
                            "notes": f"Verified indicator {idx + 1} during on-site inspection and document review. All requirements met.",
                            "evidenceIds": evidence_ids[:1] if evidence_ids else [],
                            "updatedAt": (now - timedelta(days=2)).isoformat(),
                            "updatedBy": {"name": "Test Auditor", "userId": str(user.id), "authenticated": True}
                        }
                        for idx in range(len(criteria.get("indicators", [])))
                    ],
                    "version": 1,
                    "history": [
                        {
                            "at": (now - timedelta(days=2)).isoformat(),
                            "actor": {"name": "Test Auditor", "userId": str(user.id), "authenticated": True},
                            "event": "assessed",
                            "detail": {"status": assessment_data["status"]}
                        }
                    ]
                }

                if "assessments" not in bundle:
                    bundle["assessments"] = []
                bundle["assessments"].append(assessment)

            # Update bundle status to reporting
            bundle["audit"]["status"] = "reporting"
            audit_to_update.status = "reporting"
            audit_to_update.bundle = bundle
            audit_to_update.updated_at = now
            audit_to_update.version = 2

            await session.flush()

            print(f"\n✓ Test audit setup complete!")
            print(f"   Audit ID: {audit_to_update.id}")
            print(f"   Title: {audit_to_update.title}")
            print(f"   Site: {audit_to_update.site_name}")
            print(f"   Status: {audit_to_update.status}")
            print(f"   Evidence files added: {evidence_counter}")
            print(f"   Criteria assessed: {len(ASSESSMENT_DATA)}")
            print(f"\nTest user credentials:")
            print(f"   Email: auditor@test.local")
            print(f"   Password: TestPassword123!")
            print(f"   Role: lead_auditor")
            print(f"\nReport generation endpoints ready:")
            print(f"   GET /hospitality/audits/{audit_to_update.id}/report?format=json")
            print(f"   GET /hospitality/audits/{audit_to_update.id}/report?format=markdown")
            print(f"   GET /hospitality/audits/{audit_to_update.id}/readiness")

            await session.commit()

        except Exception as e:
            await session.rollback()
            print(f"ERROR: Setup failed: {e}")
            raise
        finally:
            await engine.dispose()


if __name__ == "__main__":
    asyncio.run(setup_test_audit())
