#!/usr/bin/env python3
"""Create a comprehensive professional GSTC-compliant audit."""

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
    """Create professional GSTC audit."""

    engine = create_async_engine(str(settings.database_url), echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as db:
        print("🔧 Setting up professional GSTC audit...\n")

        # Get organisation
        print("1️⃣ Getting organisation...")
        result = await db.execute(select(Organisation).limit(1))
        org = result.scalars().first()

        if not org:
            print("❌ No organisation found.")
            return

        print(f"   ✅ Using: {org.name}")

        # Verify GSTC Standard
        print("\n2️⃣ Verifying GSTC Hotel Standard v4.01...")
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
            auditee_name="Luxury Eco Resort & Spa",
            audit_client="Hospitality Group Ltd",
            audit_body="GSTC Accredited Auditor",
            objective="Initial GSTC certification audit for luxury eco-resort",
            scope="Assess compliance with GSTC Hotel Standard v4.01 across all four pillars",
            criteria_text="GSTC Hotel Standard v4.01 (40 criteria across 4 pillars)",

            # Dates
            start_date=today,
            end_date=today + timedelta(days=1),
            duration_days=1,
            main_location="Bali, Indonesia",
            auditee_contact="General Manager, Resort Operations",

            # GSTC Risk Assessment
            country_code="ID",
            country_corruption_index=38,
            risk_level="LOW",
            risk_assessment_date=today,
            risk_assessment_notes="Established luxury resort. Strong systems. No significant negative impacts.",
            has_negative_impacts=False,
            duration_justification="Standard 1-day audit appropriate for LOW risk resort",

            # GSTC Sensitive Areas
            is_sensitive_area=True,
            sensitive_area_reason="UNESCO World Heritage Site - Bali Cultural Landscape",
            sensitive_area_coordinates="-8.3695,115.2048",
            national_legislation_reference="Indonesian Law No. 26 of 2007",

            # Hotel Characteristics
            guest_room_count=120,
            staff_count=280,
            has_event_spaces=True,
            has_function_spaces=True,
            has_meeting_spaces=True,
            is_local_ownership=False,
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

        print("\n" + "="*60)
        print("✅ PROFESSIONAL GSTC AUDIT CREATED")
        print("="*60)
        print(f"\n🆔 Audit ID: {audit_id}")
        print(f"🏨 Property: {audit.auditee_name}")
        print(f"📍 Location: {audit.main_location}")
        print(f"⚠️  Sensitive Area: {audit.is_sensitive_area}")
        print(f"🎯 Risk Level: {audit.risk_level}")
        print(f"⏱️ Duration: {audit.duration_days} day(s)")
        print(f"📋 Prompts: {prompt_count}")

        print("\n📊 GSTC COVERAGE:")
        print("   Pillar A: 14 criteria")
        print("   Pillar B: 9 criteria")
        print("   Pillar C: 4 criteria")
        print("   Pillar D: 13 criteria")
        print("   Total: 40 criteria")

        print("\n✨ Report generation will include all GSTC v4.01 criteria\n")


if __name__ == "__main__":
    asyncio.run(main())
