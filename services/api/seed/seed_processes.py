"""
Seed example processes per spec section 17.

These are generic IMS processes suitable for a construction/project-based organisation
with Quality, Environment, and OH&S management systems.
"""
from sqlalchemy.orm import Session

from app.models.process import Process


# (code, name, category, description)
EXAMPLE_PROCESSES = [
    # Management processes
    ("MGT-01", "Policy",                            "Management",
     "Establishes, reviews, and communicates the organisation's IMS policy across quality, environment, and OH&S."),
    ("MGT-02", "Objectives and targets",            "Management",
     "Sets, monitors, and reviews QEO&S objectives and targets at organisational and process levels."),
    ("MGT-03", "Process map",                       "Management",
     "Defines the organisation's process architecture and interactions across the IMS."),
    ("MGT-04", "Organisation structure",            "Management",
     "Defines roles, responsibilities, and authorities for the IMS."),
    ("MGT-05", "Legal and other requirements",      "Management",
     "Identifies, accesses, evaluates, and monitors applicable legal, regulatory, and other IMS requirements."),
    ("MGT-06", "Internal audit",                    "Management",
     "Plans, conducts, and reports internal audits of the IMS against applicable standards and requirements."),
    ("MGT-07", "Review and improvement",            "Management",
     "Conducts management reviews and drives continual improvement across the IMS."),
    # Support processes
    ("SUP-01", "Resources",                         "Support",
     "Determines, provides, and maintains resources required for the IMS including human resources and infrastructure."),
    ("SUP-02", "Internal communication",            "Support",
     "Manages internal communication on IMS matters including policy, objectives, hazards, and significant aspects."),
    ("SUP-03", "External communication",            "Support",
     "Manages external communication on environmental and OH&S matters with interested parties and regulators."),
    ("SUP-04", "Document control",                  "Support",
     "Creates, reviews, approves, distributes, and controls documents required by the IMS."),
    ("SUP-05", "Control of records",                "Support",
     "Identifies, stores, protects, retrieves, retains, and disposes of records required as evidence of IMS conformance."),
    ("SUP-06", "Competence and training",           "Support",
     "Determines competence requirements, provides training, and evaluates effectiveness of training."),
    # Environment and OH&S operational processes
    ("OPS-01", "Hazard identification and control",  "Operational",
     "Identifies workplace hazards, assesses risks, and implements and monitors controls using the hierarchy of controls."),
    ("OPS-02", "Environmental aspects and impacts",  "Operational",
     "Identifies, evaluates, and controls significant environmental aspects and impacts associated with activities."),
    ("OPS-03", "Emergency preparedness and response","Operational",
     "Establishes, tests, and maintains emergency response arrangements for potential emergency situations."),
    ("OPS-04", "Contractor and supplier management", "Operational",
     "Manages OH&S and environmental requirements for contractors, suppliers, and outsourced services."),
    ("OPS-05", "Control of nonconformances",         "Operational",
     "Identifies, investigates, classifies, and corrects nonconformances, incidents, and deviations from IMS requirements."),
    # Project processes
    ("PRJ-01", "Tender review and estimating",       "Project",
     "Reviews tender requirements, assesses OH&S and environmental risks, and prepares project-specific management plans."),
    ("PRJ-02", "Project resourcing",                 "Project",
     "Plans and allocates human, physical, and financial resources required for project delivery."),
    ("PRJ-03", "Executing the project",              "Project",
     "Delivers project activities in accordance with the project management plan, IMS requirements, and client specifications."),
    ("PRJ-04", "Handover",                           "Project",
     "Manages the systematic handover of completed works to the client including documentation, inspections, and sign-off."),
    ("PRJ-05", "Project review",                     "Project",
     "Conducts project close-out reviews to capture lessons learned and drive improvement in future project delivery."),
]


def seed_processes(db: Session, organisation_id) -> list[Process]:
    created = []
    for (code, name, category, description) in EXAMPLE_PROCESSES:
        existing = db.query(Process).filter_by(
            organisation_id=organisation_id, code=code
        ).first()
        if not existing:
            p = Process(
                organisation_id=organisation_id,
                code=code,
                name=name,
                category=category,
                description=description,
                active_flag=True,
            )
            db.add(p)
            created.append(p)
    db.flush()
    return created
