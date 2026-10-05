#!/usr/bin/env python3
"""Create a comprehensive, genuine hotel audit based on GSTC Hotel Standard v4.01"""

import asyncio
from uuid import uuid4
import sys
import json
from datetime import datetime, timedelta

sys.path.insert(0, r"C:\Users\reitsec2\OneDrive - FRSA\Desktop\Personal\AIreptondigital\claude-workspace-template\axis-engine\services\api")

from app.database import async_engine
from app.models.hospitality import HospitalityAudit
from app.models.org import User
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession


# Map of GSTC criteria with realistic indicators for a boutique hotel
AUDIT_CRITERIA = {
    # Pillar A: Sustainable Management
    "A1": {
        "title": "Sustainability Management System",
        "text": "The hotel operates under a documented sustainability management system proportional to its size and scope, ensuring that sustainability is managed in a systematic manner and continuous improvement is pursued.",
        "critical": True,
        "status": "conforming",
        "evidence": ["sustainability_policy", "mgmt_plan"],
        "notes": "Written sustainability policy with clear targets. Annual review process in place."
    },
    "A2": {
        "title": "Legal Compliance",
        "text": "The hotel complies with all relevant laws and regulations concerning social, cultural, and environmental matters.",
        "critical": True,
        "status": "conforming",
        "evidence": ["legal_register"],
        "notes": "Maintained register of all applicable local and national laws. Compliance verified during site visit."
    },
    "A3": {
        "title": "Guest and Staff Welfare",
        "text": "The hotel takes measures to support the well-being of guests and staff by identifying potential hazards and responding to any concerns.",
        "critical": False,
        "status": "observation",
        "evidence": ["health_safety_procedures", "staff_interview"],
        "notes": "Health and safety officer designated. Staff training program in place but documentation incomplete."
    },
    "A4": {
        "title": "Reporting and Communication",
        "text": "The hotel communicates its sustainability policy, actions, and performance to stakeholders, including guests, and seeks to engage their support.",
        "critical": False,
        "status": "minor",
        "evidence": ["annual_report"],
        "notes": "Annual sustainability report published but lacks detailed metrics."
    },
    "A5": {
        "title": "Accurate Promotion",
        "text": "The hotel markets and represents its sustainability performance accurately.",
        "critical": False,
        "status": "conforming",
        "evidence": ["website_marketing"],
        "notes": "Website claims verified against actual practices during audit."
    },
    "A7": {
        "title": "Staff Engagement",
        "text": "The hotel actively engages and involves staff in achieving sustainability goals.",
        "critical": False,
        "status": "minor",
        "evidence": ["staff_interview", "training_records"],
        "notes": "Ad-hoc sustainability meetings but no formal engagement structure."
    },

    # Pillar B: Socioeconomic Benefits
    "B1": {
        "title": "Community Support",
        "text": "The hotel demonstrates a commitment to supporting and strengthening the local economy and community.",
        "critical": False,
        "status": "observation",
        "evidence": ["community_programs", "local_sourcing"],
        "notes": "Community partnerships documented but limited formalization."
    },
    "B2": {
        "title": "Local Employment",
        "text": "The hotel provides employment opportunities and fair treatment to local workers.",
        "critical": False,
        "status": "conforming",
        "evidence": ["employment_records", "payroll"],
        "notes": "85% of staff are local hires. Fair wage practices verified."
    },
    "B5": {
        "title": "Access for All",
        "text": "The hotel ensures accessibility for people with disabilities.",
        "critical": False,
        "status": "major",
        "evidence": ["accessibility_audit", "staff_interview"],
        "notes": "Wheelchair ramps present but elevator access to upper floors limited."
    },
    "B6": {
        "title": "Code of Conduct",
        "text": "The hotel has adopted and implemented a code of conduct that prohibits harassment and discrimination.",
        "critical": True,
        "status": "minor",
        "evidence": ["code_of_conduct", "staff_interview"],
        "notes": "Code exists but staff training incomplete."
    },
    "B9": {
        "title": "Decent Work",
        "text": "The hotel ensures decent working conditions for all staff.",
        "critical": False,
        "status": "conforming",
        "evidence": ["employment_contracts", "working_conditions_obs"],
        "notes": "Contracts reviewed. Working conditions meet standards."
    },

    # Pillar C: Cultural Heritage
    "C1": {
        "title": "Cultural Interactions",
        "text": "The hotel educates guests and staff on local cultural norms and respects local culture.",
        "critical": False,
        "status": "observation",
        "evidence": ["orientation_materials", "staff_interview"],
        "notes": "Basic orientation provided but limited cultural education materials."
    },
    "C3": {
        "title": "Presenting Culture and Heritage",
        "text": "The hotel collaborates with local communities to present and safeguard cultural heritage.",
        "critical": False,
        "status": "minor",
        "evidence": ["cultural_programs", "community_interview"],
        "notes": "Local art exhibits in lobby but formal agreements with artisans missing."
    },

    # Pillar D: Environmental Benefits
    "D1": {
        "title": "Energy Conservation",
        "text": "The hotel measures, monitors and minimizes energy consumption.",
        "critical": False,
        "status": "observation",
        "evidence": ["energy_records", "monitoring_systems"],
        "notes": "Energy tracking in place. LED conversion 60% complete."
    },
    "D2": {
        "title": "Water Conservation",
        "text": "The hotel measures, monitors and minimizes water consumption.",
        "critical": False,
        "status": "minor",
        "evidence": ["water_records"],
        "notes": "Water monitoring system installed but leak detection program needed."
    },
    "D5": {
        "title": "Wastewater",
        "text": "The hotel ensures that all wastewater is treated and disposed of in an environmentally responsible manner.",
        "critical": False,
        "status": "conforming",
        "evidence": ["wastewater_permit", "treatment_records"],
        "notes": "On-site treatment system with regular monitoring."
    },
    "D6": {
        "title": "Solid Waste",
        "text": "The hotel minimizes waste generation and manages waste responsibly.",
        "critical": False,
        "status": "minor",
        "evidence": ["waste_records", "recycling_program"],
        "notes": "Recycling program in place. Composting program proposed."
    },
    "D7": {
        "title": "Harmful Substances",
        "text": "The hotel prevents pollution through the responsible use and storage of harmful substances.",
        "critical": False,
        "status": "observation",
        "evidence": ["chemical_inventory", "storage_obs"],
        "notes": "Chemical storage area complies with standards."
    },
    "D9": {
        "title": "Biodiversity Conservation",
        "text": "The hotel takes measures to preserve and enhance local biodiversity.",
        "critical": False,
        "status": "major",
        "evidence": ["grounds_obs", "landscaping_plan"],
        "notes": "Extensive manicured grounds with limited native plant species. Enhancement plan needed."
    },
}


async def create_genuine_audit():
    """Create a comprehensive, realistic hotel audit."""
    async with AsyncSession(async_engine) as session:
        # Get or create a user
        user_result = await session.execute(select(User).limit(1))
        user = user_result.scalar()
        if not user:
            print("❌ No users found in database")
            return

        user_id = user.id
        org_id = user.organisation_id
        user_name = f"{user.first_name} {user.last_name}"

        print(f"Using user: {user_name}\n")

        # Delete any existing test audit
        await session.execute(text("""
            DELETE FROM hospitality_files
            WHERE audit_id IN (
                SELECT id FROM hospitality_audits
                WHERE title LIKE '%Genuine%' OR title LIKE '%Riverside%'
            )
        """))
        await session.execute(text("""
            DELETE FROM hospitality_audits
            WHERE title LIKE '%Genuine%' OR title LIKE '%Riverside%'
        """))
        await session.commit()

        # Create the comprehensive audit
        print("✨ Creating genuine, comprehensive hotel audit...\n")
        audit_id = uuid4()
        audit_date = datetime(2026, 10, 5)

        # Build requirements, evidence, assessments, findings
        requirements = []
        assessments = []
        evidence_list = []
        findings = []
        actions = []

        evidence_id = 0
        evidence_map = {}

        # Create evidence items
        evidence_types = {
            "sustainability_policy": ("document", "before_visit", "Sustainability Policy 2025-2026"),
            "mgmt_plan": ("document", "before_visit", "Sustainability Management Plan"),
            "legal_register": ("document", "on_site", "Register of Applicable Laws and Regulations"),
            "health_safety_procedures": ("document", "on_site", "Health & Safety Procedures Manual"),
            "staff_interview": ("interview", "on_site", "Interview with General Manager - Sustainability"),
            "annual_report": ("document", "before_visit", "2025 Annual Sustainability Report"),
            "website_marketing": ("observation", "on_site", "Hotel website sustainability claims review"),
            "training_records": ("record", "on_site", "Staff Training Records 2025"),
            "community_programs": ("document", "before_visit", "Community Engagement Programs"),
            "local_sourcing": ("document", "on_site", "Supplier Documentation - Local Sources"),
            "employment_records": ("record", "on_site", "Employment Records and Staff Profile"),
            "payroll": ("record", "on_site", "Payroll Records Sample"),
            "accessibility_audit": ("record", "on_site", "Accessibility Assessment Report"),
            "code_of_conduct": ("document", "before_visit", "Staff Code of Conduct"),
            "working_conditions_obs": ("observation", "on_site", "Observation of Staff Working Areas"),
            "orientation_materials": ("document", "on_site", "Guest Orientation Materials"),
            "cultural_programs": ("document", "on_site", "Cultural Programs and Exhibits"),
            "community_interview": ("interview", "on_site", "Interview with Local Community Representative"),
            "energy_records": ("record", "on_site", "Energy Consumption Records 2025"),
            "monitoring_systems": ("observation", "on_site", "Energy Monitoring Systems Review"),
            "water_records": ("record", "on_site", "Water Consumption Records 2025"),
            "wastewater_permit": ("document", "on_site", "Wastewater Treatment Permit"),
            "treatment_records": ("record", "on_site", "Wastewater Treatment Monitoring Records"),
            "waste_records": ("record", "on_site", "Waste Management Records 2025"),
            "recycling_program": ("observation", "on_site", "Recycling Program Review"),
            "chemical_inventory": ("record", "on_site", "Chemical Inventory and Safety Data Sheets"),
            "storage_obs": ("observation", "on_site", "Chemical Storage Area Inspection"),
            "grounds_obs": ("observation", "on_site", "Grounds and Landscaping Inspection"),
            "landscaping_plan": ("document", "on_site", "Landscaping and Biodiversity Plan"),
        }

        # Create evidence
        for evidence_key, (kind, via, title) in evidence_types.items():
            evidence_id += 1
            ev_id = str(uuid4())
            evidence_map[evidence_key] = ev_id

            evidence_list.append({
                "id": ev_id,
                "kind": kind,
                "collectedAt": (audit_date + timedelta(days=1 if via == "before_visit" else 2)).isoformat() + "Z",
                "collectedVia": via,
                "description": title,
                "reference": f"{title} - {evidence_id:02d}"
            })

        # Create requirements and assessments
        for criterion_code, criterion_info in sorted(AUDIT_CRITERIA.items()):
            req_id = str(uuid4())

            # Get evidence IDs for this criterion
            evidence_ids = [evidence_map[ev_key] for ev_key in criterion_info["evidence"] if ev_key in evidence_map]

            # Requirement
            requirements.append({
                "id": req_id,
                "title": criterion_info["title"],
                "text": criterion_info["text"],
                "critical": criterion_info["critical"],
                "indicators": [f"Indicator {i+1}" for i in range(3)],
                "source": {
                    "clause": criterion_code,
                    "title": criterion_info["title"]
                }
            })

            # Assessment
            status_map = {
                "conforming": "conforming",
                "observation": "observation",
                "minor": "minor",
                "major": "major"
            }

            indicator_inputs = []
            for i, ev_key in enumerate(criterion_info["evidence"]):
                if ev_key in evidence_map:
                    indicator_inputs.append({
                        "index": i,
                        "notes": criterion_info["notes"],
                        "evidenceIds": [evidence_map[ev_key]]
                    })

            assessment = {
                "requirementId": req_id,
                "status": status_map.get(criterion_info["status"], "unassessed"),
                "rationale": criterion_info["notes"],
                "evidenceIds": evidence_ids,
                "indicatorInputs": indicator_inputs if indicator_inputs else []
            }
            assessments.append(assessment)

            # Findings for non-conforming criteria
            if criterion_info["status"] in ["minor", "major"]:
                finding_id = str(uuid4())
                severity = "major" if criterion_info["status"] == "major" else "minor"

                gap_statement = {
                    "minor": f"Partial implementation of {criterion_code}: {criterion_info['title']}",
                    "major": f"Significant gap in {criterion_code}: {criterion_info['title']}"
                }[criterion_info["status"]]

                findings.append({
                    "id": finding_id,
                    "requirementId": req_id,
                    "status": "open",
                    "severity": severity,
                    "title": gap_statement,
                    "statement": criterion_info["notes"],
                    "evidence_summary": "See evidence linked to this criterion"
                })

                # Create action for this finding
                action_titles = {
                    "A3": "Complete staff health and safety training documentation",
                    "A4": "Enhance annual report with detailed sustainability metrics",
                    "A7": "Establish formal sustainability engagement framework",
                    "B1": "Formalize community partnership agreements",
                    "B5": "Assess and improve disability access provisions",
                    "B6": "Complete staff training on code of conduct",
                    "C3": "Establish formal agreements with local artisans",
                    "D1": "Complete LED lighting retrofit program",
                    "D2": "Implement water leak detection and management program",
                    "D6": "Launch composting program for organic waste",
                    "D9": "Develop and implement native plant landscaping plan"
                }

                action_due = audit_date + timedelta(days=60 if criterion_info["status"] == "major" else 90)

                actions.append({
                    "id": str(uuid4()),
                    "findingId": finding_id,
                    "description": action_titles.get(criterion_code, criterion_info["notes"]),
                    "owner": {"name": "General Manager", "role": "Hotel Management"},
                    "dueDate": action_due.strftime("%Y-%m-%d"),
                    "status": "open"
                })

        # Build the complete bundle
        requirement_ids = [req["id"] for req in requirements]

        bundle = {
            "audit": {
                "id": str(audit_id),
                "title": "Riverside Boutique Hotel - GSTC Readiness Review",
                "siteName": "Riverside Boutique Hotel",
                "status": "completed",
                "auditDate": audit_date.strftime("%Y-%m-%d"),
                "leadAuditor": {
                    "name": user_name,
                    "role": "Lead Auditor"
                },
                "reviewType": "One-day on-site readiness review",
                "requirementIds": requirement_ids,
            },
            "template": {
                "id": "gstc-hotel-v4.01",
                "title": "GSTC Hotel Standard",
                "version": "v4.01",
                "disclaimer": "This is a sample-based readiness review, not a certification audit."
            },
            "evidence": evidence_list,
            "requirements": requirements,
            "assessments": assessments,
            "findings": findings,
            "actions": actions
        }

        # Create the audit in database
        new_audit = HospitalityAudit(
            id=audit_id,
            organisation_id=org_id,
            created_by=user_id,
            title="Riverside Boutique Hotel - GSTC Readiness Review",
            site_name="Riverside Boutique Hotel",
            status="completed",
            bundle=bundle,
            version=1,
            report_profile={
                "hotel_name": "Riverside Boutique Hotel",
                "location": "Mendocino County, California, USA",
                "hotel_contact_name": "Sarah Mitchell",
                "hotel_contact_role": "General Manager",
                "review_date": audit_date.strftime("%Y-%m-%d"),
                "reviewer": user_name,
                "reviewer_contact": "contact@axisauditing.com",
                "report_reference": f"GSTC-RBTA-2026-{audit_id.hex[:8].upper()}",
                "report_date": datetime.now().strftime("%Y-%m-%d"),
                "hotel_type": "Boutique Hotel",
                "rooms": "32",
                "staff": "18 full-time, 4 part-time",
                "facilities": "Restaurant, bar, spa, fitness center, conference facilities",
                "occupancy": "72% annual average",
                "existing_certifications": "ISO 14001 (Environmental Management)",
                "people_interviewed": "Sarah Mitchell (GM) | James Chen (Environmental Manager) | Maria Garcia (Staff Representative)",
                "areas_inspected": "Front desk, restaurant, kitchen, spa, guest rooms, maintenance area, grounds, staff areas",
                "areas_not_inspected": "Not applicable - full walkthrough completed",
            },
            report_draft=None,
        )
        session.add(new_audit)
        await session.commit()

        # Print summary
        print("✅ Comprehensive, Genuine Audit Created!\n")
        print(f"   Hotel: Riverside Boutique Hotel")
        print(f"   Location: Mendocino County, California")
        print(f"   Rooms: 32 | Staff: 18 FT, 4 PT")
        print(f"   Audit ID: {audit_id}")
        print(f"   Audit Date: {audit_date.strftime('%Y-%m-%d')}\n")

        print(f"   Coverage:")
        print(f"   • Requirements: {len(requirements)} GSTC criteria")
        print(f"   • Evidence: {len(evidence_list)} items")
        print(f"   • Assessments: {len(assessments)} criteria assessed")
        print(f"   • Findings: {len(findings)} gaps identified")
        print(f"   • Actions: {len(actions)} recommended actions\n")

        # Count by status
        statuses = {}
        for assessment in assessments:
            status = assessment["status"]
            statuses[status] = statuses.get(status, 0) + 1

        print(f"   Assessment Summary:")
        for status in ["conforming", "observation", "minor", "major"]:
            count = statuses.get(status, 0)
            if count > 0:
                print(f"   • {status.capitalize()}: {count}")

        print(f"\n📝 Ready to generate readiness report!")
        print(f"   POST /hospitality/audits/{audit_id}/readiness/generate")


if __name__ == "__main__":
    asyncio.run(create_genuine_audit())
