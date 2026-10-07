#!/usr/bin/env python3
"""Create a high-quality demo audit for report generation testing."""

import asyncio
from datetime import date, timedelta
from uuid import uuid4

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select

from app.config import settings
from app.models.audit import Audit, AuditProcess
from app.models.org import Organisation
from app.models.process import Process
from app.services.audit import generate_audit_prompts
from app.services import gstc_standard


async def main():
    """Create professional GSTC audit with excellent data."""

    engine = create_async_engine(str(settings.database_url), echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as db:
        print("✨ Creating high-quality demo audit...\n")

        # Get organisation
        print("1️⃣ Getting organisation...")
        result = await db.execute(select(Organisation).limit(1))
        org = result.scalars().first()

        if not org:
            print("❌ No organisation found.")
            return

        print(f"   ✅ Using: {org.name}")

        # Verify GSTC Standard
        print("\n2️⃣ Verifying GSTC Hotel Standard v4.0...")
        gstc_meta = gstc_standard.get_standard_metadata()
        print(f"   ✅ Version: {gstc_meta['version']}")
        print(f"   ✅ Criteria: {gstc_meta['total_criteria']}")

        # Get processes
        print("\n3️⃣ Loading processes...")
        result = await db.execute(select(Process))
        processes = result.scalars().all()
        print(f"   ✅ Found {len(processes)} processes")

        # Create professional audit
        print("\n4️⃣ Creating professional GSTC audit...")

        today = date.today()
        audit = Audit(
            id=uuid4(),
            organisation_id=org.id,
            audit_type="Initial",
            audit_stage="DocumentReview",
            status="Planned",

            # Basic info
            auditee_name="Sustainable Wellness Retreat",
            audit_client="Eco Hospitality Partners",
            audit_body="GSTC Accredited Auditor",
            objective="Initial GSTC certification audit for luxury wellness resort",
            scope="Assess compliance with GSTC Hotel Standard v4.0 across all four pillars: Sustainable Management, Socioeconomic Benefits, Cultural Heritage, and Environmental Benefits",
            criteria_text="GSTC Hotel Standard v4.0 (40 criteria across 4 pillars: A, B, C, D)",

            # Dates
            start_date=today,
            end_date=today + timedelta(days=2),
            duration_days=2,
            main_location="Byron Bay, New South Wales, Australia",
            auditee_contact="General Manager, Sustainability Office",

            # GSTC Risk Assessment - Australia low risk
            country_code="AU",
            country_corruption_index=77,  # Australia Rule of Law Index: 0.79 (well above 0.60 threshold)
            risk_level="LOW",
            risk_assessment_date=today,
            risk_assessment_notes="Established luxury wellness resort with mature sustainability systems. Strong governance. Minimal environmental/social impact risks.",
            has_negative_impacts=False,
            duration_justification="2-day on-site audit appropriate for LOW risk resort with comprehensive systems",

            # GSTC Sensitive Areas
            is_sensitive_area=False,
            sensitive_area_reason=None,
            sensitive_area_coordinates=None,
            national_legislation_reference="Australian Environmental Protection and Biodiversity Conservation Act 1999",

            # Hotel Characteristics
            guest_room_count=45,
            staff_count=28,
            has_event_spaces=True,
            has_function_spaces=False,
            has_meeting_spaces=True,
            is_local_ownership=True,
            has_internet_access=True,

            # 3-Year Cycle
            certification_start_date=today,
            certification_expiry_date=today + timedelta(days=1095),
            last_on_site_audit_date=None,
            last_audit_date=None,
            audit_cycle_number=1,
        )

        db.add(audit)
        await db.flush()
        await db.refresh(audit)

        audit_id = audit.id
        print(f"   ✅ Created audit: {audit_id}")
        print(f"   📍 {audit.auditee_name}")
        print(f"   📍 {audit.main_location}")
        print(f"   ⏱️ {audit.duration_days} day(s)")

        # Add processes to audit
        print("\n5️⃣ Adding processes to audit...")
        added = 0
        for process in processes[:10]:
            ap = AuditProcess(
                id=uuid4(),
                audit_id=audit_id,
                process_id=process.id
            )
            db.add(ap)
            added += 1

        await db.flush()
        print(f"   ✅ Added {added} processes")

        # Generate prompts
        print("\n6️⃣ Generating audit prompts...")
        prompt_count = await generate_audit_prompts(audit_id, db)
        print(f"   ✅ Generated {prompt_count} prompts")

        # Commit
        print("\n7️⃣ Committing to database...")
        await db.commit()

        print("\n" + "="*70)
        print("✨ HIGH-QUALITY DEMO AUDIT CREATED")
        print("="*70)
        print(f"\n🆔 Audit ID: {audit_id}")
        print(f"🏨 Property: {audit.auditee_name}")
        print(f"📍 Location: {audit.main_location}")
        print(f"🌍 Country: Australia (LOW risk)")
        print(f"⚠️  Sensitive Area: No")
        print(f"🎯 Risk Level: {audit.risk_level}")
        print(f"⏱️  Duration: {audit.duration_days} day(s)")
        print(f"👥 Rooms: {audit.guest_room_count} | Staff: {audit.staff_count}")
        print(f"📋 Prompts: {prompt_count}")

        print("\n📊 GSTC v4.0 COVERAGE:")
        print("   Pillar A (Sustainable Management): 14 criteria")
        print("   Pillar B (Socioeconomic Benefits): 9 criteria")
        print("   Pillar C (Cultural Heritage): 4 criteria")
        print("   Pillar D (Environmental Benefits): 13 criteria")
        print("   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print("   Total: 40 criteria")

        print("\n✅ Audit is ready for:")
        print("   • Prompt response population")
        print("   • High-quality report generation testing")
        print("   • GSTC v5.0 compliance verification")
        print(f"\n   Use audit ID: {audit_id}")


if __name__ == "__main__":
    asyncio.run(main())
