"""
Process-clause mapping seed data.

Maps each of the 21 example processes to their relevant ISO clauses
across ISO 9001, ISO 14001, and ISO 45001.

Each entry is:
  (process_code, standard_code, clause_number, applicability, risk_level, rationale)

Risk levels drive monitoring frequency:
  Extreme -> Monthly
  High    -> Quarterly
  Medium  -> Biannual
  Low     -> Annual
"""
from sqlalchemy.orm import Session

from app.models.process import Process
from app.models.standard import Standard, Clause
from app.models.mapping import ProcessClauseMap


MAPPINGS = [

    # -----------------------------------------------------------------------
    # MGT-01 Policy
    # -----------------------------------------------------------------------
    ("MGT-01", "ISO9001",  "5.2",   "Full", "Low",    "Quality policy must be established, maintained and communicated."),
    ("MGT-01", "ISO9001",  "5.1.1", "Full", "Low",    "Top management demonstrates commitment through policy."),
    ("MGT-01", "ISO14001", "5.2",   "Full", "Low",    "Environmental policy must be documented, maintained, and available."),
    ("MGT-01", "ISO14001", "5.1",   "Full", "Low",    "Leadership and commitment demonstrated through policy establishment."),
    ("MGT-01", "ISO45001", "5.2",   "Full", "Low",    "OH&S policy must be documented, communicated, and available to workers."),
    ("MGT-01", "ISO45001", "5.1",   "Full", "Low",    "Top management commitment demonstrated through OH&S policy."),

    # -----------------------------------------------------------------------
    # MGT-02 Objectives and targets
    # -----------------------------------------------------------------------
    ("MGT-02", "ISO9001",  "6.2",   "Full", "Medium", "Quality objectives must be established, measurable, monitored and updated."),
    ("MGT-02", "ISO14001", "6.2.1", "Full", "Medium", "Environmental objectives must be documented and consistent with policy."),
    ("MGT-02", "ISO14001", "6.2.2", "Full", "Medium", "Plans to achieve environmental objectives must include actions, resources, timelines."),
    ("MGT-02", "ISO45001", "6.2",   "Full", "Medium", "OH&S objectives must be measurable, monitored and communicated."),
    ("MGT-02", "ISO9001",  "9.3",   "Partial", "Medium", "Management review must assess whether objectives have been achieved."),
    ("MGT-02", "ISO14001", "9.3",   "Partial", "Medium", "Management review must include assessment of environmental objective performance."),
    ("MGT-02", "ISO45001", "9.3",   "Partial", "Medium", "Management review must include OH&S objective performance."),

    # -----------------------------------------------------------------------
    # MGT-03 Process map
    # -----------------------------------------------------------------------
    ("MGT-03", "ISO9001",  "4.4",   "Full", "Low",    "QMS must determine processes, their interactions, inputs and outputs."),
    ("MGT-03", "ISO9001",  "4.3",   "Full", "Low",    "Scope of QMS must be documented and boundary of processes defined."),
    ("MGT-03", "ISO14001", "4.4",   "Full", "Low",    "EMS must establish and maintain processes needed for the system."),
    ("MGT-03", "ISO45001", "4.4",   "Full", "Low",    "OH&S MS must include processes needed, their interactions."),

    # -----------------------------------------------------------------------
    # MGT-04 Organisation structure
    # -----------------------------------------------------------------------
    ("MGT-04", "ISO9001",  "5.3",   "Full", "Low",    "Roles, responsibilities and authorities must be assigned and communicated."),
    ("MGT-04", "ISO14001", "5.3",   "Full", "Low",    "Environmental roles, responsibilities and authorities must be documented."),
    ("MGT-04", "ISO45001", "5.3",   "Full", "Low",    "OH&S roles, responsibilities and authorities at all levels."),
    ("MGT-04", "ISO45001", "5.4",   "Full", "Medium", "Workers must be consulted and participate in OH&S management."),

    # -----------------------------------------------------------------------
    # MGT-05 Legal and other requirements
    # -----------------------------------------------------------------------
    ("MGT-05", "ISO14001", "6.1.3", "Full", "High",   "Compliance obligations must be identified, accessed, and kept current."),
    ("MGT-05", "ISO14001", "9.1.2", "Full", "High",   "Compliance with legal obligations must be evaluated at planned intervals."),
    ("MGT-05", "ISO45001", "6.1.3", "Full", "High",   "Legal and other OH&S requirements must be determined and kept current."),
    ("MGT-05", "ISO45001", "9.1.2", "Full", "High",   "Compliance with legal requirements must be evaluated periodically."),
    ("MGT-05", "ISO9001",  "4.2",   "Partial", "Medium", "Legal and regulatory requirements are part of interested party needs."),

    # -----------------------------------------------------------------------
    # MGT-06 Internal audit
    # -----------------------------------------------------------------------
    ("MGT-06", "ISO9001",  "9.2",   "Full", "High",   "Internal audit programme must be established and implemented."),
    ("MGT-06", "ISO14001", "9.2",   "Full", "High",   "EMS internal audit programme must be documented and records retained."),
    ("MGT-06", "ISO14001", "9.2.2", "Full", "High",   "Audit programme must consider environmental importance and previous results."),
    ("MGT-06", "ISO45001", "9.2",   "Full", "High",   "OH&S internal audit programme must cover all system elements."),

    # -----------------------------------------------------------------------
    # MGT-07 Review and improvement
    # -----------------------------------------------------------------------
    ("MGT-07", "ISO9001",  "9.3",   "Full", "Medium", "Management review inputs and outputs must be documented."),
    ("MGT-07", "ISO14001", "9.3",   "Full", "Medium", "Management review must assess EMS suitability, adequacy, and effectiveness."),
    ("MGT-07", "ISO45001", "9.3",   "Full", "Medium", "Management review must cover all required inputs including worker participation."),
    ("MGT-07", "ISO9001",  "10.3",  "Full", "Low",    "Continual improvement of QMS suitability, adequacy and effectiveness."),
    ("MGT-07", "ISO14001", "10.3",  "Full", "Low",    "Organisation must continually improve EMS to enhance environmental performance."),
    ("MGT-07", "ISO45001", "10.3",  "Full", "Low",    "Continual improvement of OH&S performance must be demonstrated."),

    # -----------------------------------------------------------------------
    # SUP-01 Resources
    # -----------------------------------------------------------------------
    ("SUP-01", "ISO9001",  "7.1",   "Full", "Medium", "Resources for QMS must be determined, provided and maintained."),
    ("SUP-01", "ISO14001", "7.1",   "Full", "Medium", "Resources needed for EMS must be determined and provided."),
    ("SUP-01", "ISO45001", "7.1",   "Full", "Medium", "Resources for OH&S MS must be determined and provided."),

    # -----------------------------------------------------------------------
    # SUP-02 Internal communication
    # -----------------------------------------------------------------------
    ("SUP-02", "ISO9001",  "7.4",   "Full", "Low",    "Internal communication on QMS matters must be defined."),
    ("SUP-02", "ISO14001", "7.4.2", "Full", "Low",    "Internal communication on environmental matters must be established."),
    ("SUP-02", "ISO45001", "7.4.1", "Full", "Medium", "Communication processes for OH&S must include what, when, with whom and how."),
    ("SUP-02", "ISO45001", "5.4",   "Partial", "Medium", "Internal communication supports worker participation and consultation."),

    # -----------------------------------------------------------------------
    # SUP-03 External communication
    # -----------------------------------------------------------------------
    ("SUP-03", "ISO9001",  "7.4",   "Full", "Low",    "External communication needs must be determined."),
    ("SUP-03", "ISO9001",  "8.2.1", "Full", "Medium", "Customer communication must cover information, orders, feedback and complaints."),
    ("SUP-03", "ISO14001", "7.4.3", "Full", "Medium", "External communication on significant environmental aspects as required by obligations."),
    ("SUP-03", "ISO45001", "7.4.1", "Partial", "Low", "External communication on OH&S matters with contractors and authorities."),

    # -----------------------------------------------------------------------
    # SUP-04 Document control
    # -----------------------------------------------------------------------
    ("SUP-04", "ISO9001",  "7.5",   "Full", "Medium", "Documented information required by QMS must be controlled."),
    ("SUP-04", "ISO9001",  "7.5.3", "Full", "Medium", "Documents must be available, protected and controlled for distribution and access."),
    ("SUP-04", "ISO14001", "7.5",   "Full", "Medium", "EMS documented information must be controlled and available where needed."),
    ("SUP-04", "ISO14001", "7.5.3", "Full", "Medium", "Control includes storage, preservation, retrieval, retention and disposal."),
    ("SUP-04", "ISO45001", "7.5",   "Full", "Medium", "OH&S documented information must be controlled and available."),

    # -----------------------------------------------------------------------
    # SUP-05 Control of records
    # -----------------------------------------------------------------------
    ("SUP-05", "ISO9001",  "7.5",   "Full", "Medium", "Records as retained documented information must be identified and controlled."),
    ("SUP-05", "ISO9001",  "7.5.2", "Full", "Low",    "Records must be appropriately identified, formatted and approved."),
    ("SUP-05", "ISO9001",  "7.5.3", "Full", "Medium", "Records must be retrievable and protected from loss of integrity."),
    ("SUP-05", "ISO14001", "7.5.3", "Full", "Medium", "Environmental records must be retained and available as evidence of conformance."),
    ("SUP-05", "ISO45001", "7.5",   "Full", "Medium", "OH&S records must be retained and protected."),

    # -----------------------------------------------------------------------
    # SUP-06 Competence and training
    # -----------------------------------------------------------------------
    ("SUP-06", "ISO9001",  "7.2",   "Full", "Medium", "Competence of persons doing work affecting QMS must be determined and maintained."),
    ("SUP-06", "ISO9001",  "7.3",   "Full", "Low",    "Persons must be aware of quality policy, objectives and their contribution."),
    ("SUP-06", "ISO14001", "7.2",   "Full", "Medium", "Competence for EMS work must be determined, training provided, records retained."),
    ("SUP-06", "ISO14001", "7.3",   "Full", "Low",    "Environmental awareness including significant aspects and compliance obligations."),
    ("SUP-06", "ISO45001", "7.2",   "Full", "High",   "OH&S competence is critical — workers must be competent for hazardous activities."),
    ("SUP-06", "ISO45001", "7.3",   "Full", "Medium", "Workers must be aware of OH&S policy, hazards, risks and emergency procedures."),

    # -----------------------------------------------------------------------
    # OPS-01 Hazard identification and control
    # -----------------------------------------------------------------------
    ("OPS-01", "ISO45001", "6.1.2",   "Full", "Extreme", "Hazard identification must be systematic, proactive and cover all activities."),
    ("OPS-01", "ISO45001", "6.1.2.1", "Full", "Extreme", "Hazard register must include routine/non-routine activities and emergency situations."),
    ("OPS-01", "ISO45001", "6.1.2.2", "Full", "High",    "Risk assessment must use defined criteria and produce documented results."),
    ("OPS-01", "ISO45001", "8.1.1",   "Full", "High",    "Operational controls must implement hierarchy of controls for identified risks."),
    ("OPS-01", "ISO45001", "8.1.2",   "Full", "High",    "Hierarchy of controls must be applied — elimination preferred over PPE."),
    ("OPS-01", "ISO45001", "8.1.3",   "Full", "High",    "Management of change must assess OH&S implications before changes proceed."),

    # -----------------------------------------------------------------------
    # OPS-02 Environmental aspects and impacts
    # -----------------------------------------------------------------------
    ("OPS-02", "ISO14001", "6.1.2",   "Full", "High",    "Environmental aspects must be identified for all activities, products and services."),
    ("OPS-02", "ISO14001", "6.1.4",   "Full", "Medium",  "Actions to address significant aspects must be planned and integrated."),
    ("OPS-02", "ISO14001", "8.1",     "Full", "High",    "Operational controls must be established for significant environmental aspects."),
    ("OPS-02", "ISO14001", "9.1.1",   "Partial", "High", "Monitoring must measure environmental performance against significant aspects."),

    # -----------------------------------------------------------------------
    # OPS-03 Emergency preparedness and response
    # -----------------------------------------------------------------------
    ("OPS-03", "ISO14001", "8.2",     "Full", "Extreme", "Emergency preparedness plans must be established, tested and maintained."),
    ("OPS-03", "ISO45001", "8.2",     "Full", "Extreme", "OH&S emergency response arrangements must cover all credible emergency scenarios."),
    ("OPS-03", "ISO9001",  "8.5.1",   "Partial", "Medium", "Contingency arrangements for production continuity during emergencies."),

    # -----------------------------------------------------------------------
    # OPS-04 Contractor and supplier management
    # -----------------------------------------------------------------------
    ("OPS-04", "ISO9001",  "8.4",     "Full", "High",    "External providers must be evaluated, selected and their performance monitored."),
    ("OPS-04", "ISO9001",  "8.4.1",   "Full", "High",    "Criteria for evaluation and records of evaluations must be documented."),
    ("OPS-04", "ISO9001",  "8.4.2",   "Full", "Medium",  "Controls applied to external providers must be commensurate with risk."),
    ("OPS-04", "ISO9001",  "8.4.3",   "Full", "Medium",  "Requirements communicated to external providers before commencement."),
    ("OPS-04", "ISO45001", "8.1.4.2", "Full", "High",    "Contractor OH&S requirements must be defined and compliance verified on-site."),
    ("OPS-04", "ISO45001", "8.1.4.3", "Full", "Medium",  "Outsourced functions affecting OH&S must be controlled."),
    ("OPS-04", "ISO14001", "8.1",     "Partial", "Medium", "Environmental requirements must flow down to contractors and suppliers."),

    # -----------------------------------------------------------------------
    # OPS-05 Control of nonconformances
    # -----------------------------------------------------------------------
    ("OPS-05", "ISO9001",  "8.7",     "Full", "High",    "Nonconforming outputs must be identified, controlled and dispositioned."),
    ("OPS-05", "ISO9001",  "10.2",    "Full", "High",    "Nonconformities must be investigated, root cause identified and corrected."),
    ("OPS-05", "ISO14001", "10.2",    "Full", "High",    "Environmental nonconformities must be investigated and corrective action taken."),
    ("OPS-05", "ISO45001", "10.2",    "Full", "High",    "Incidents and nonconformities must be reported, investigated and corrected."),
    ("OPS-05", "ISO9001",  "10.1",    "Partial", "Low",  "Nonconformance control contributes to continual improvement."),

    # -----------------------------------------------------------------------
    # PRJ-01 Tender review and estimating
    # -----------------------------------------------------------------------
    ("PRJ-01", "ISO9001",  "8.2.2",   "Full", "Medium",  "Requirements for products and services must be determined before tendering."),
    ("PRJ-01", "ISO9001",  "8.2.3",   "Full", "Medium",  "Requirements must be reviewed before commitment — records retained."),
    ("PRJ-01", "ISO45001", "6.1.2.1", "Partial", "High", "Hazards for proposed project activities must be identified at tender stage."),
    ("PRJ-01", "ISO14001", "6.1.2",   "Partial", "Medium", "Significant environmental aspects for proposed project scope identified early."),

    # -----------------------------------------------------------------------
    # PRJ-02 Project resourcing
    # -----------------------------------------------------------------------
    ("PRJ-02", "ISO9001",  "7.1",     "Full", "Medium",  "Human, infrastructure and environment resources must be planned for each project."),
    ("PRJ-02", "ISO45001", "7.1",     "Full", "Medium",  "OH&S resources including competent supervisors must be allocated per project."),
    ("PRJ-02", "ISO9001",  "8.5.1",   "Partial", "Medium", "Production planning must identify resource requirements before work commences."),

    # -----------------------------------------------------------------------
    # PRJ-03 Executing the project
    # -----------------------------------------------------------------------
    ("PRJ-03", "ISO9001",  "8.5",     "Full", "High",    "Production and service provision must be carried out under controlled conditions."),
    ("PRJ-03", "ISO9001",  "8.5.1",   "Full", "High",    "Controlled conditions include documented information defining results to be achieved."),
    ("PRJ-03", "ISO45001", "8.1",     "Full", "High",    "Operational controls for OH&S risks must be implemented during project execution."),
    ("PRJ-03", "ISO45001", "8.1.3",   "Full", "High",    "Changes during project execution must be assessed for OH&S implications."),
    ("PRJ-03", "ISO14001", "8.1",     "Full", "High",    "Environmental operational controls must be maintained throughout project delivery."),

    # -----------------------------------------------------------------------
    # PRJ-04 Handover
    # -----------------------------------------------------------------------
    ("PRJ-04", "ISO9001",  "8.6",     "Full", "High",    "Products and services must not be released until all requirements verified."),
    ("PRJ-04", "ISO9001",  "8.5.2",   "Full", "Medium",  "Traceability records must be maintained and available at handover."),

    # -----------------------------------------------------------------------
    # PRJ-05 Project review
    # -----------------------------------------------------------------------
    ("PRJ-05", "ISO9001",  "9.1.3",   "Full", "Medium",  "Analysis and evaluation of project results informs process improvement."),
    ("PRJ-05", "ISO9001",  "10.3",    "Full", "Low",     "Project reviews must identify improvement opportunities for future projects."),
    ("PRJ-05", "ISO14001", "10.3",    "Partial", "Low",  "Environmental performance lessons learned feed into continual improvement."),
    ("PRJ-05", "ISO45001", "10.3",    "Partial", "Low",  "OH&S lessons learned from projects must feed into system improvement."),
]


def seed_process_clause_maps(db: Session, organisation_id) -> int:
    """
    Seed process-clause mappings for the demo organisation.
    Returns count of mappings created.
    """
    created = 0

    for (proc_code, std_code, clause_num, applicability, risk_level, rationale) in MAPPINGS:
        # Look up process
        process = db.query(Process).filter_by(
            organisation_id=organisation_id, code=proc_code
        ).first()
        if not process:
            print(f"  SKIP: process {proc_code} not found")
            continue

        # Look up standard
        standard = db.query(Standard).filter_by(code=std_code).first()
        if not standard:
            print(f"  SKIP: standard {std_code} not found")
            continue

        # Look up clause
        clause = db.query(Clause).filter_by(
            standard_id=standard.id, clause_number=clause_num
        ).first()
        if not clause:
            print(f"  SKIP: clause {std_code} {clause_num} not found")
            continue

        # Skip if already exists
        existing = db.query(ProcessClauseMap).filter_by(
            process_id=process.id, clause_id=clause.id
        ).first()
        if existing:
            continue

        mapping = ProcessClauseMap(
            process_id=process.id,
            clause_id=clause.id,
            applicability=applicability,
            rationale=rationale,
            risk_modifier=risk_level,
        )
        db.add(mapping)
        created += 1

    db.flush()
    return created
