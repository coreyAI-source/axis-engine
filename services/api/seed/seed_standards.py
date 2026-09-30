"""
Seed ISO standards and clause data.

ISO 9001:2015 — Quality management systems
ISO 14001:2015 — Environmental management systems
ISO 45001:2018 — Occupational health and safety management systems

Source documents (axis-engine/ISO auditor/):
- 9001-14001-45001-comparison-table-20240412.pdf      (clause structure)
- 9001-14001-45001-mandatory-documented-information-list-20240412.pdf  (requires_* flags)
- ISO-9001-2015-checklist-20240412.xlsx               (evidence guidance)
- ISO-14001-2015-checklist-20240412.xlsx              (evidence guidance)
- ISO-45001-2018-checklist-20240412.xlsx              (evidence guidance)

Evidence guidance text derived from auditor checklists (Tarren Reitsema, ex-NOPSEMA).
requires_documented_information = clause requires maintaining a policy/procedure/plan/register
requires_retained_evidence = clause requires retaining records as proof of activities
"""
from sqlalchemy.orm import Session

from app.models.standard import Standard, Clause


STANDARDS = [
    {"code": "ISO9001", "title": "Quality management systems — Requirements", "version": "2015"},
    {"code": "ISO14001", "title": "Environmental management systems — Requirements with guidance for use", "version": "2015"},
    {"code": "ISO45001", "title": "Occupational health and safety management systems — Requirements with guidance for use", "version": "2018"},
]

# (clause_number, clause_title, parent, hls_section, req_doc_info, req_retained_evidence, evidence_guidance)

ISO9001_CLAUSES = [
    # Context
    ("4.1", "Understanding the organisation and its context", None, "Context", False, False,
     "Strategic risk register, business plans, quality risk assessments, management review inputs. Verify periodic review cycle exists and outputs link to QMS performance."),
    ("4.2", "Understanding the needs and expectations of interested parties", None, "Context", False, False,
     "Stakeholder register, contract requirement matrices, customer specifications. Check traceability from stakeholder requirements into QMS controls."),
    ("4.3", "Determining the scope of the quality management system", None, "Context", True, False,
     "QMS scope statement, process map, site/service coverage. Verify exclusions from scope are justified and documented."),
    ("4.4", "Quality management system and its processes", None, "Context", True, False,
     "Process maps, KPIs, RACI matrix, procedure suite. Process owners must be assigned and process performance must be measured, not just documented."),
    # Leadership
    ("5.1", "Leadership and commitment", None, "Leadership", False, False,
     "Board/executive minutes, quality performance dashboards, resource allocation decisions. QMS must be owned by top management, not delegated entirely to the Quality Manager."),
    ("5.1.1", "General", "5.1", "Leadership", False, False,
     "Evidence top management demonstrates leadership: policy sign-off, resource decisions linked to quality outcomes, active participation in management review."),
    ("5.1.2", "Customer focus", "5.1", "Leadership", False, False,
     "Customer satisfaction monitoring records, customer requirement review process, evidence of decisions made to enhance customer focus."),
    ("5.2", "Policy", None, "Leadership", True, False,
     "Quality policy document, induction records, staff interviews confirming awareness. Policy must commit to meeting requirements and continual improvement."),
    ("5.2.1", "Establishing the quality policy", "5.2", "Leadership", True, False,
     "Documented quality policy appropriate to the organisation's context and purpose. Must include commitment to satisfy applicable requirements and to continual improvement."),
    ("5.2.2", "Communicating the quality policy", "5.2", "Leadership", True, False,
     "Evidence policy is communicated and understood: induction records, toolbox talk records, staff interview responses, policy availability on notice boards or intranet."),
    ("5.3", "Organisational roles, responsibilities and authorities", None, "Leadership", False, False,
     "Position descriptions, delegation instruments, organisation chart. QMS accountabilities must be assigned and understood at all levels."),
    # Planning
    ("6.1", "Actions to address risks and opportunities", None, "Planning", False, False,
     "Risk register, improvement plans, corrective action records. Risks must be linked to product/service conformity and customer satisfaction outcomes, not generic business risk."),
    ("6.2", "Quality objectives and planning to achieve them", None, "Planning", True, False,
     "KPI dashboard, quality plan, action tracker. Objectives must be measurable, monitored, communicated and assigned. Failure mode: 'Improve quality' with no measurable target."),
    ("6.2.1", "Quality objectives", "6.2", "Planning", True, False,
     "Documented quality objectives consistent with policy. Must be measurable where practicable with assigned responsibility, timelines and review cycle."),
    ("6.2.2", "Planning actions to achieve quality objectives", "6.2", "Planning", False, False,
     "Action plans showing what will be done, resources required, responsible person, timelines and how results will be evaluated."),
    ("6.3", "Planning of changes", None, "Planning", False, False,
     "Management of change records, change impact assessments, communication and training records. QMS changes must be controlled before implementation."),
    # Support
    ("7.1", "Resources", None, "Support", False, False,
     "Resourcing plans, maintenance records, equipment registers. People, infrastructure, equipment and work environments must be adequate for QMS operation."),
    ("7.1.1", "General", "7.1", "Support", False, False,
     "Evidence of determination and provision of resources needed for QMS establishment, implementation, maintenance and continual improvement."),
    ("7.1.2", "People", "7.1", "Support", False, False,
     "Staffing plans, organisation charts. Persons necessary for effective QMS implementation and process operation must be determined and provided."),
    ("7.1.3", "Infrastructure", "7.1", "Support", False, False,
     "Asset registers, maintenance records, facilities management records. Infrastructure needed for conformity of products and services."),
    ("7.1.4", "Environment for the operation of processes", "7.1", "Support", False, False,
     "Work environment monitoring records, ergonomic assessments, temperature/cleanliness controls where relevant to product conformity."),
    ("7.1.5", "Monitoring and measuring resources", "7.1", "Support", False, True,
     "Calibration certificates, equipment register, out-of-tolerance reports. Measuring devices must be calibrated or verified at specified intervals."),
    ("7.1.5.1", "General", "7.1.5", "Support", True, True,
     "Equipment register with calibration status, calibration certificates, records of calibration/verification activities and results."),
    ("7.1.5.2", "Measurement traceability", "7.1.5", "Support", True, True,
     "Traceability records linking calibration to national or international measurement standards. Must include calibration basis and uncertainty statements where required."),
    ("7.1.6", "Organisational knowledge", "7.1", "Support", False, False,
     "Lessons learned registers, technical standards, knowledge transfer records. Critical business and process knowledge must be captured and maintained against loss."),
    ("7.2", "Competence", None, "Support", True, True,
     "Competency matrix, training records, assessment evidence. Competency requirements must be defined and verified for all roles affecting quality conformity."),
    ("7.3", "Awareness", None, "Support", False, False,
     "Interviews, toolbox talk records, induction records. Personnel must understand the quality policy, relevant objectives and consequences of nonconformance."),
    ("7.4", "Communication", None, "Support", False, False,
     "Communication plan, customer reporting records, meeting minutes. Internal and external QMS communications must be defined including what, when, with whom and how."),
    ("7.5", "Documented information", None, "Support", False, False,
     "Document register, revision history, controlled forms and templates. Documents must be controlled, current and accessible."),
    ("7.5.1", "General", "7.5", "Support", False, False,
     "Evidence QMS includes documented information required by ISO 9001 and determined by the organisation as necessary for effectiveness."),
    ("7.5.2", "Creating and updating", "7.5", "Support", False, False,
     "Document control procedure, revision history, approval records. Documented information must be appropriately identified, formatted, reviewed and approved before issue."),
    ("7.5.3", "Control of documented information", "7.5", "Support", False, False,
     "Document control system, access controls, version control logs. Documented information must be available where needed and protected from unintended alteration or loss. Failure mode: multiple uncontrolled versions in circulation."),
    # Operation
    ("8.1", "Operational planning and control", None, "Operation", True, False,
     "Quality plans, inspection/test plans, work instructions. Processes must be planned and controlled to meet product/service requirements."),
    ("8.2", "Requirements for products and services", None, "Operation", False, False,
     "Contract reviews, tender reviews, customer correspondence. Customer requirements must be reviewed and understood before acceptance."),
    ("8.2.1", "Customer communication", "8.2", "Operation", False, False,
     "Customer correspondence, complaints handling records, enquiry and order records, post-delivery feedback records, contingency action records."),
    ("8.2.2", "Determining the requirements for products and services", "8.2", "Operation", False, False,
     "Product/service specifications, applicable statutory and regulatory requirements register, documented customer-specific requirements."),
    ("8.2.3", "Review of the requirements for products and services", "8.2", "Operation", True, True,
     "Contract review records, tender review records. Changes to requirements must be controlled, documented and communicated to relevant persons."),
    ("8.2.4", "Changes to requirements for products and services", "8.2", "Operation", False, False,
     "Change notifications, updated contract documents, evidence of communication to affected personnel when requirements change."),
    ("8.3", "Design and development of products and services", None, "Operation", True, True,
     "Design plans, design review records, verification and validation records. Design must be controlled from inputs through outputs with approved changes."),
    ("8.3.1", "General", "8.3", "Operation", False, False,
     "Evidence design and development process is established, implemented and maintained appropriate to the nature and complexity of products/services."),
    ("8.3.2", "Design and development planning", "8.3", "Operation", True, False,
     "Design plans showing stages, review/verification/validation activities, responsibilities, timelines and interfaces between groups involved."),
    ("8.3.3", "Design and development inputs", "8.3", "Operation", True, False,
     "Design input records: functional and performance requirements, applicable statutory/regulatory requirements, previous design information, potential failure consequences."),
    ("8.3.4", "Design and development controls", "8.3", "Operation", True, False,
     "Design review records, verification records, validation records. Problems must be identified and resolved before progression."),
    ("8.3.5", "Design and development outputs", "8.3", "Operation", True, False,
     "Design output documents meeting input requirements, referencing applicable monitoring/measuring requirements and acceptance criteria."),
    ("8.3.6", "Design and development changes", "8.3", "Operation", True, True,
     "Design change records including review, verification, validation and authorisation. Impact on conformity of products/services must be assessed and recorded."),
    ("8.4", "Control of externally provided processes, products and services", None, "Operation", True, True,
     "Approved supplier list, supplier evaluations, purchase specifications. Suppliers must be selected, evaluated and monitored. Failure mode: supplier approval done once, then never reviewed again."),
    ("8.4.1", "General", "8.4", "Operation", True, True,
     "Supplier evaluation criteria, approved supplier register, records of evaluations and re-evaluations against defined criteria."),
    ("8.4.2", "Type and extent of control", "8.4", "Operation", False, False,
     "Evidence of controls applied to external providers commensurate with risk to product/service conformity and customer satisfaction."),
    ("8.4.3", "Information for external providers", "8.4", "Operation", False, False,
     "Purchase orders/specifications communicating requirements to external providers before provision. Must include applicable QMS requirements."),
    ("8.5", "Production and service provision", None, "Operation", True, True,
     "Work packs, batch records, inspection records, traceability logs. Controlled conditions must be defined and implemented."),
    ("8.5.1", "Control of production and service provision", "8.5", "Operation", True, True,
     "Work instructions, documented characteristics of products/services and results to be achieved. Monitoring and measuring activities records."),
    ("8.5.2", "Identification and traceability", "8.5", "Operation", False, True,
     "Batch records, traceability logs, product identification records. Outputs must be identified and conformity status maintained throughout production and service provision."),
    ("8.5.3", "Property belonging to customers or external providers", "8.5", "Operation", False, True,
     "Records of customer/external provider property received, verified for suitability and protected. Damage, loss or unsuitability must be reported to owner and retained on record."),
    ("8.5.4", "Preservation", "8.5", "Operation", False, False,
     "Preservation procedures, records of storage and handling conditions. Products must be preserved during internal processing and delivery to maintain conformity."),
    ("8.5.5", "Post-delivery activities", "8.5", "Operation", False, False,
     "Post-delivery service records, warranty claims, feedback records. Extent of post-delivery activities must reflect risk, customer expectations and applicable legal requirements."),
    ("8.5.6", "Control of changes", "8.5", "Operation", True, True,
     "Change records including review and authorisation. Production/service changes must be reviewed, authorised and controlled to maintain conformity."),
    ("8.6", "Release of products and services", None, "Operation", False, True,
     "Inspection/test records, release certificates, authorised sign-off records. Release must be authorised only after all acceptance criteria are met and authority is traceable."),
    ("8.7", "Control of nonconforming outputs", None, "Operation", True, True,
     "NCRs, concession approvals, rework records, segregation evidence. Nonconforming outputs must be identified, segregated, dispositioned and corrected before release."),
    # Performance Evaluation
    ("9.1", "Monitoring, measurement, analysis and evaluation", None, "PerformanceEvaluation", False, False,
     "KPI reports, customer feedback, complaints trend data. Quality metrics must be defined, monitored and analysed to evaluate QMS performance."),
    ("9.1.1", "General", "9.1", "PerformanceEvaluation", False, True,
     "Monitoring and measurement results records. Evidence of what is monitored, the methods used, when analysis occurs and when results are reported."),
    ("9.1.2", "Customer satisfaction", "9.1", "PerformanceEvaluation", False, True,
     "Customer satisfaction surveys, feedback records, complaints data and trend analysis. Must demonstrate systematic monitoring of customer perceptions of product/service conformity."),
    ("9.1.3", "Analysis and evaluation", "9.1", "PerformanceEvaluation", False, False,
     "Analysis outputs informing management review: conformity of products/services, customer satisfaction, QMS performance, risk effectiveness, supplier performance and improvement needs."),
    ("9.2", "Internal audit", None, "PerformanceEvaluation", True, True,
     "Audit schedule, audit reports, corrective action records. Audit program must be risk-based and auditors must be independent of audited activities. Failure mode: tick-box audits with no findings."),
    ("9.2.1", "General", "9.2", "PerformanceEvaluation", False, False,
     "Evidence audits are conducted at planned intervals to determine whether QMS conforms to requirements and is effectively implemented and maintained."),
    ("9.2.2", "Internal audit programme", "9.2", "PerformanceEvaluation", True, True,
     "Documented audit programme covering audit criteria, scope, frequency and methods. Audit results must be retained. Programme must account for importance of processes and previous audit results."),
    ("9.3", "Management review", None, "PerformanceEvaluation", False, True,
     "Review minutes, action logs, performance trend analysis. Management review must drive decisions, resourcing and improvement — not just be a reporting exercise."),
    ("9.3.1", "General", "9.3", "PerformanceEvaluation", False, False,
     "Evidence top management reviews QMS at planned intervals to ensure continuing suitability, adequacy, effectiveness and alignment with strategic direction."),
    ("9.3.2", "Management review inputs", "9.3", "PerformanceEvaluation", False, False,
     "Management review agenda/inputs covering: previous action status, external/internal issue changes, QMS performance data, nonconformities, audit results, customer satisfaction trends, improvement opportunities."),
    ("9.3.3", "Management review outputs", "9.3", "PerformanceEvaluation", True, True,
     "Documented management review decisions and actions on: improvement opportunities, QMS changes needed and resource requirements. Must be retained."),
    # Improvement
    ("10.1", "General", None, "Improvement", False, False,
     "Improvement register, lessons learned, customer feedback actions. Improvement opportunities must be systematically identified and actioned."),
    ("10.2", "Nonconformity and corrective action", None, "Improvement", True, True,
     "RCA records, CAPA register, effectiveness verification records. Root cause analysis must be robust and corrective actions verified for effectiveness before close-out."),
    ("10.3", "Continual improvement", None, "Improvement", False, False,
     "KPI trend data, defect and complaint reduction records, audit maturity trends. QMS performance must demonstrate measurable improvement over time."),
]

ISO14001_CLAUSES = [
    # Context
    ("4.1", "Understanding the organisation and its context", None, "Context", False, False,
     "SWOT/PESTLE outputs, risk registers with environmental linkage, board or management review inputs. Verify periodic review cycle exists. Failure mode: generic context statements with no operational linkage and no update cycle."),
    ("4.2", "Understanding the needs and expectations of interested parties", None, "Context", False, True,
     "Stakeholder register, mapping to compliance obligations, engagement records. Check traceability from stakeholder expectations into EMS controls. Failure mode: static stakeholder lists with no traceability to obligations."),
    ("4.3", "Determining the scope of the environmental management system", None, "Context", True, False,
     "EMS scope statement, org charts, asset registers. Boundaries must be justified — verify inclusions/exclusions align with actual operational control. Failure mode: excluding high-risk operations without justification."),
    ("4.4", "Environmental management system", None, "Context", False, False,
     "Process maps, procedures in use (not just stored), evidence EMS is integrated into business operations. Failure mode: shelfware EMS — documentation exists but system is not implemented."),
    # Leadership
    ("5.1", "Leadership and commitment", None, "Leadership", False, False,
     "Board minutes, resource allocation decisions, KPIs tied to environmental performance. Failure mode: delegation without oversight — EMS responsibilities handed off without accountability."),
    ("5.2", "Environmental policy", None, "Leadership", True, False,
     "Policy document, staff interviews confirming awareness. Policy must commit to protection of the environment, compliance with obligations and continual improvement. Failure mode: policy exists but no staff awareness."),
    ("5.3", "Organisational roles, responsibilities and authorities", None, "Leadership", False, False,
     "Position descriptions, RACI matrices, delegation instruments. Accountability must be assigned for key EMS elements. Failure mode: diffused accountability with no clear owner."),
    # Planning
    ("6.1", "Actions to address risks and opportunities", None, "Planning", False, False,
     "Risk registers, risk assessment methodology. Risks must be tied to EMS outcomes, not generic business risk."),
    ("6.1.1", "General", "6.1", "Planning", True, True,
     "Documented information on risks and opportunities considered for the EMS. Records of planning process and actions determined."),
    ("6.1.2", "Environmental aspects", "6.1", "Planning", True, True,
     "Aspect register, significance criteria, scoring methodology. Aspects must cover normal, abnormal and emergency conditions. Failure modes: qualitative non-defensible scoring; missing lifecycle stages."),
    ("6.1.3", "Compliance obligations", "6.1", "Planning", True, True,
     "Legal register, regulatory mapping (EP conditions, licences, permits). Must be complete, current and linked to operational controls. Failure mode: outdated register with no verification of compliance."),
    ("6.1.4", "Planning action", "6.1", "Planning", False, False,
     "Action plans, evidence actions are integrated into operational procedures and tracked to completion."),
    ("6.2", "Environmental objectives and planning to achieve them", None, "Planning", False, False,
     "KPI dashboards, environmental plans. Objectives must be measurable and aligned to significant risks and aspects."),
    ("6.2.1", "Environmental objectives", "6.2", "Planning", True, False,
     "Documented environmental objectives consistent with policy. Must be measurable where practicable with assigned responsibilities and timelines. Failure mode: vague objectives such as 'reduce impact' with no measurable target."),
    ("6.2.2", "Planning actions to achieve environmental objectives", "6.2", "Planning", False, False,
     "Action plans showing what will be done, resources required, responsible persons, timelines and how results will be evaluated."),
    # Support
    ("7.1", "Resources", None, "Support", False, False,
     "Budget allocation, staffing levels, equipment availability. Resources must be adequate to manage identified environmental risks."),
    ("7.2", "Competence", None, "Support", True, True,
     "Training records, competency matrices, certificates. Competency requirements must be defined and verified for all roles affecting EMS performance."),
    ("7.3", "Awareness", None, "Support", False, False,
     "Interviews, induction records. Personnel must understand environmental impacts of their work, the policy and consequences of not conforming."),
    ("7.4", "Communication", None, "Support", False, False,
     "Communication plans, incident reports, regulatory reporting records. Internal and external communication processes must be defined."),
    ("7.4.1", "General", "7.4", "Support", True, False,
     "Documented communication process defining what, when, with whom and how to communicate on EMS matters — both internal and external."),
    ("7.4.2", "Internal communication", "7.4", "Support", False, False,
     "Evidence of internal communication on EMS performance, significant aspects and changes relevant to the EMS."),
    ("7.4.3", "External communication", "7.4", "Support", False, False,
     "Evidence of external communication on significant environmental aspects as required by compliance obligations or as determined necessary."),
    ("7.5", "Documented information", None, "Support", False, False,
     "Version control logs, access controls. Documents must be controlled, current and protected. Failure mode: multiple uncontrolled versions in circulation."),
    ("7.5.1", "General", "7.5", "Support", False, False,
     "Evidence EMS includes documented information required by ISO 14001 and determined by the organisation as necessary for effectiveness."),
    ("7.5.2", "Creating and updating", "7.5", "Support", False, False,
     "Document control procedure, revision history, approval records. Documented information must be appropriately identified, formatted, reviewed and approved before issue."),
    ("7.5.3", "Control of documented information", "7.5", "Support", False, False,
     "Document control system, access controls, version control logs. Documented information must be available where needed, protected and controlled for distribution, access, retrieval, storage and disposition."),
    # Operation
    ("8.1", "Operational planning and control", None, "Operation", True, True,
     "SOPs, permit systems, contractor management systems. Controls must be linked to significant environmental aspects. Lifecycle perspective: procurement specs and design standards must consider upstream/downstream impacts. Failure mode: controls exist but are not tied to risk."),
    ("8.2", "Emergency preparedness and response", None, "Operation", True, True,
     "Emergency response plans, drill records, lessons learned. Environmental emergencies must be identified, planned for and regularly tested. Failure mode: no testing or lessons learned process."),
    # Performance Evaluation
    ("9.1", "Monitoring, measurement, analysis and evaluation", None, "PerformanceEvaluation", False, False,
     "Monitoring data, calibration records. KPIs must be defined, tracked and methods validated."),
    ("9.1.1", "General", "9.1", "PerformanceEvaluation", True, True,
     "Monitoring and measurement results, calibration/verification records where applicable. Must include what is monitored, methods, criteria and when analysis and reporting occurs."),
    ("9.1.2", "Evaluation of compliance", "9.1", "PerformanceEvaluation", True, True,
     "Compliance audit reports, compliance calendar results, regulatory correspondence. Compliance must be periodically evaluated with results retained."),
    ("9.2", "Internal audit", None, "PerformanceEvaluation", False, False,
     "Audit schedules, audit reports. Audit program must be structured and auditors must be independent. Failure mode: tick-box audits with no meaningful findings."),
    ("9.2.1", "General", "9.2", "PerformanceEvaluation", False, False,
     "Evidence audits are conducted at planned intervals to determine whether EMS conforms to requirements and is effectively implemented."),
    ("9.2.2", "Internal audit programme", "9.2", "PerformanceEvaluation", True, True,
     "Documented audit programme and retained audit results including findings and evidence of corrective actions taken."),
    ("9.3", "Management review", None, "PerformanceEvaluation", True, True,
     "Review minutes, action tracking records. Management review must drive decisions — not just be a reporting exercise. Failure mode: no strategic outcomes or resource decisions from review."),
    # Improvement
    ("10.1", "General", None, "Improvement", False, False,
     "Trend data, improvement register. Improvement must be demonstrable over time — not just stated as an intent."),
    ("10.2", "Nonconformity and corrective action", None, "Improvement", True, True,
     "Incident reports, corrective action logs, root cause analysis records, effectiveness verification. Failure mode: superficial fixes that address symptoms not causes."),
    ("10.3", "Continual improvement", None, "Improvement", False, False,
     "System update records, lessons learned integration. EMS must be evolving — check for evidence of improvements driven by audit, monitoring and review results."),
]

ISO45001_CLAUSES = [
    # Context
    ("4.1", "Understanding the organisation and its context", None, "Context", False, False,
     "WHS risk profile, legal/regulatory context scan, workforce and operational risk analysis. Internal/external issues must be linked to OH&S management outcomes."),
    ("4.2", "Understanding the needs and expectations of workers and other interested parties", None, "Context", False, True,
     "Worker consultation records, contractor interface records, stakeholder register. Worker needs must be explicitly identified — not just management assumptions about what workers need."),
    ("4.3", "Determining the scope of the OH&S management system", None, "Context", True, False,
     "Scope statement, site/activity register, contractor boundary analysis. Scope must cover all controlled activities, locations and workers including contractors."),
    ("4.4", "OH&S management system", None, "Context", False, False,
     "Process maps, procedures, records showing implementation. Must be an implemented system, not just a WHS manual on a shelf."),
    # Leadership
    ("5.1", "Leadership and commitment", None, "Leadership", False, False,
     "Executive minutes, resourcing decisions, site leadership walk records. Top management must demonstrate accountability for OH&S performance. Failure mode: safety outsourced to HSE team while leadership does the safety moment theatre and goes home."),
    ("5.2", "OH&S policy", None, "Leadership", True, False,
     "Policy document, induction records, worker interviews. Policy must commit to safe working conditions, legal compliance, worker consultation and continual improvement."),
    ("5.3", "Organisational roles, responsibilities and authorities", None, "Leadership", True, False,
     "Position descriptions, delegations, RACI matrix. OH&S responsibilities must be assigned at all levels of the organisation."),
    ("5.4", "Consultation and participation of workers", None, "Leadership", True, True,
     "HSR/committee minutes, toolbox talk records, consultation records, worker interview evidence. Workers must be genuinely consulted in hazard identification, risk controls, incident investigation and change management. Failure mode: consultation after the decision has already been made."),
    # Planning
    ("6.1", "Actions to address risks and opportunities", None, "Planning", False, False,
     "Hazard register, risk assessments, legal register, action plans. Risks must cover routine, non-routine, emergency, human factors, contractor and change scenarios."),
    ("6.1.1", "General", "6.1", "Planning", True, True,
     "Documented OH&S risks, opportunities and other risks to the OH&S management system. Records of planning process and actions determined."),
    ("6.1.2", "Hazard identification and assessment of risks and opportunities", "6.1", "Planning", True, True,
     "Hazard register, JHAs/JSAs/SWMS, HAZID records, incident trend analysis, risk assessments, critical control registers. Hierarchy of controls must be demonstrably applied."),
    ("6.1.2.1", "Hazard identification", "6.1.2", "Planning", True, True,
     "Hazard register covering routine and non-routine activities, past incidents, emergency situations, human factors, contractor activities and changes. Must be systematic, not reactive."),
    ("6.1.2.2", "Assessment of OH&S risks and other risks to the OH&S management system", "6.1.2", "Planning", True, True,
     "Risk assessments using defined criteria, bowties, critical control registers, verification records. Failure modes: PPE used as the default control; administrative controls pretending to be engineering controls."),
    ("6.1.2.3", "Assessment of OH&S opportunities and other opportunities", "6.1.2", "Planning", False, False,
     "Evidence of consideration of OH&S improvement opportunities — better work organisation, elimination opportunities, new technology — when planning actions."),
    ("6.1.3", "Determination of legal requirements and other requirements", "6.1", "Planning", True, True,
     "Legal register, compliance calendar, licence and permit obligations. Must be complete, current and kept up to date as legislation changes."),
    ("6.1.4", "Planning action", "6.1", "Planning", False, False,
     "WHS plans, action registers, risk treatment plans. Actions must be integrated into operational controls and tracked to completion."),
    ("6.2", "OH&S objectives and planning to achieve them", None, "Planning", False, False,
     "WHS objectives, KPI dashboard, action plans. Objectives must be measurable and risk-based. Failure mode: sole reliance on LTIFR as the only indicator."),
    ("6.2.1", "OH&S objectives", "6.2", "Planning", True, False,
     "Documented OH&S objectives consistent with policy. Must be measurable where practicable and include both lead and lag indicators."),
    ("6.2.2", "Planning to achieve OH&S objectives", "6.2", "Planning", True, False,
     "Action plans showing what will be done, resources, responsible persons, timelines and how results will be evaluated. Must be maintained as documented information."),
    # Support
    ("7.1", "Resources", None, "Support", False, False,
     "WHS budget, staffing model, equipment availability records. Adequate people, funds, equipment and systems must be provided for OH&S management."),
    ("7.2", "Competence", None, "Support", True, True,
     "Competency matrix, licences/tickets, verification of competency (VOC) records. Competence requirements must be defined for safety-critical roles and verified — not assumed."),
    ("7.3", "Awareness", None, "Support", False, False,
     "Worker interviews, induction records, toolbox talk records. Workers must understand hazards, controls, the OH&S policy, incident reporting obligations and stop-work rights."),
    ("7.4", "Communication", None, "Support", True, False,
     "Communication matrix, safety alerts, shift handovers, contractor communications. OH&S communications must be planned, timely and two-way."),
    ("7.4.1", "General", "7.4", "Support", True, False,
     "Documented communication processes defining what, when, with whom and how to communicate on OH&S matters — internal and external."),
    ("7.4.2", "Internal communication", "7.4", "Support", False, False,
     "Safety alerts, toolbox records, shift handover records. Evidence of timely internal communication on OH&S performance, hazards and changes."),
    ("7.4.3", "External communication", "7.4", "Support", False, False,
     "Contractor communications, regulator correspondence, emergency service notifications. External OH&S communication as required by legal obligations or stakeholder needs."),
    ("7.5", "Documented information", None, "Support", False, False,
     "Controlled procedures, revision history, incident records, training records. WHS documents must be controlled and records retained."),
    ("7.5.1", "General", "7.5", "Support", False, False,
     "Evidence OH&S management system includes documented information required by ISO 45001 and determined by the organisation as necessary for effectiveness."),
    ("7.5.2", "Creating and updating", "7.5", "Support", False, False,
     "Document control procedure, revision history, approval records. Documented information must be appropriately identified, formatted, reviewed and approved before issue."),
    ("7.5.3", "Control of documented information", "7.5", "Support", False, False,
     "Document control system, access controls, version control logs. Documented information must be available where needed, protected and controlled. Failure mode: multiple uncontrolled versions in circulation."),
    # Operation
    ("8.1", "Operational planning and control", None, "Operation", True, True,
     "SWMS/JSA, PTW records, critical control checks, maintenance records. Operational controls must be implemented for identified risks, maintained and verified as effective."),
    ("8.1.1", "General", "8.1", "Operation", True, False,
     "Documented processes to control OH&S risks. Must include processes for eliminating hazards and implementing hierarchy of controls. Retain records to the extent necessary."),
    ("8.1.2", "Eliminating hazards and reducing OH&S risks", "8.1", "Operation", False, False,
     "Design reviews, engineering control records, substitution decisions, risk treatment evidence. Hierarchy of controls must actually be applied — elimination first, PPE last."),
    ("8.1.3", "Management of change", "8.1", "Operation", True, True,
     "MOC records, pre-start reviews, updated risk assessments. Changes must be assessed for OH&S impact before implementation — not after."),
    ("8.1.4", "Procurement", "8.1", "Operation", True, False,
     "Procurement specs, supplier prequalification records, equipment safety reviews. WHS requirements must be embedded in procurement decisions."),
    ("8.1.4.1", "General", "8.1.4", "Operation", True, False,
     "Documented procurement processes ensuring products and services conform to OH&S requirements before purchase or engagement."),
    ("8.1.4.2", "Contractors", "8.1.4", "Operation", True, True,
     "Contractor evaluations, induction records, site observations, interface agreements. Contractors must be selected, inducted, supervised and monitored — not just inducted once."),
    ("8.1.4.3", "Outsourcing", "8.1.4", "Operation", False, False,
     "Contract clauses incorporating OH&S requirements, performance reports, audit records. Outsourced functions affecting OH&S must be controlled."),
    ("8.2", "Emergency preparedness and response", None, "Operation", True, True,
     "Emergency response plans, drill records, lessons learned, equipment inspections. Foreseeable emergencies must be identified, planned for and regularly tested."),
    # Performance Evaluation
    ("9.1", "Monitoring, measurement, analysis and evaluation of performance", None, "PerformanceEvaluation", False, False,
     "Inspection records, critical control verification records, health surveillance, exposure monitoring, KPI trends. Controls must be verified as effective — not merely assumed."),
    ("9.1.1", "General", "9.1", "PerformanceEvaluation", True, True,
     "Monitoring and measurement results, calibration records where applicable. Must cover both proactive (inspections, critical control checks) and reactive (incidents, nonconformities) indicators."),
    ("9.1.2", "Evaluation of compliance", "9.1", "PerformanceEvaluation", True, True,
     "Compliance audits, legal register reviews, regulator correspondence. Legal compliance must be periodically and systematically evaluated — not just assumed."),
    ("9.2", "Internal audit", None, "PerformanceEvaluation", True, True,
     "Audit plan, audit reports, corrective actions. Audit program must be risk-based and auditors must be independent of areas audited."),
    ("9.2.1", "General", "9.2", "PerformanceEvaluation", False, False,
     "Evidence audits are conducted at planned intervals to determine whether OH&S management system conforms to requirements and is effectively implemented."),
    ("9.2.2", "Internal audit programme", "9.2", "PerformanceEvaluation", True, True,
     "Documented audit programme and retained audit results. Programme must account for risk, importance of processes and results of previous audits."),
    ("9.3", "Management review", None, "PerformanceEvaluation", True, True,
     "Review minutes, actions assigned, resourcing decisions, strategic OH&S changes. Leadership must review performance and make decisions — not just receive a report."),
    # Improvement
    ("10.1", "General", None, "Improvement", False, False,
     "Improvement register, safety observations, audit findings. Improvement opportunities must be identified from incidents, audits, worker input and monitoring results."),
    ("10.2", "Incident, nonconformity and corrective action", None, "Improvement", True, True,
     "Incident reports, ICAM/TapRooT/5-Why records, CAPA register, effectiveness reviews. Root cause must go beyond worker behaviour — system defects must be identified. Failure mode: blaming worker behaviour while leaving system defects untouched."),
    ("10.3", "Continual improvement", None, "Improvement", True, True,
     "Trend data, reduction in repeat incidents, stronger controls over time, improved consultation outcomes. OH&S performance must demonstrate measurable improvement — not just stability."),
]


def seed_standards(db: Session) -> dict:
    """Seed standards and clauses. Returns {code: Standard} map."""
    standards_map = {}

    for s_data in STANDARDS:
        existing = db.query(Standard).filter_by(code=s_data["code"]).first()
        if not existing:
            std = Standard(**s_data)
            db.add(std)
            db.flush()
            standards_map[s_data["code"]] = std
        else:
            standards_map[s_data["code"]] = existing

    clause_datasets = {
        "ISO9001": ISO9001_CLAUSES,
        "ISO14001": ISO14001_CLAUSES,
        "ISO45001": ISO45001_CLAUSES,
    }

    for std_code, clauses in clause_datasets.items():
        std = standards_map[std_code]
        for (number, title, parent, hls, req_doc, req_ret, guidance) in clauses:
            existing = db.query(Clause).filter_by(standard_id=std.id, clause_number=number).first()
            if existing:
                # Update evidence guidance and flags from real source data
                existing.clause_title = title
                existing.parent_clause_number = parent
                existing.hls_section = hls
                existing.requires_documented_information = req_doc
                existing.requires_retained_evidence = req_ret
                existing.evidence_guidance = guidance
            else:
                clause = Clause(
                    standard_id=std.id,
                    clause_number=number,
                    clause_title=title,
                    parent_clause_number=parent,
                    hls_section=hls,
                    requires_documented_information=req_doc,
                    requires_retained_evidence=req_ret,
                    evidence_guidance=guidance,
                    active_flag=True,
                )
                db.add(clause)

    db.flush()
    return standards_map
