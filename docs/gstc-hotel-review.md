# GSTC hotel source review and decisions

Reviewed: **29 September 2026**. Status: **GSTC Hotel Standard v4.0 criteria imported; product decisions below still open**.

New hotel audits now load all 40 criteria of the GSTC Hotel Standard v4.0 with their 205 performance indicators and Annex guidelines, extracted verbatim from the official PDF into `packages/engine/src/gstc-hotel-v4-data.ts` (criterion and indicator counts verified per criterion against the source). Each criterion cites its section, clause ID and PDF page. Tarren confirmed the standard may be used for this purpose. Audits created before the import keep their eight fictional pilot criteria. The "Original examples" section below is historical.

## Source registry

| Source | Verified version/date | Purpose |
| --- | --- | --- |
| [GSTC Hotel Standard landing page](https://www.gstc.org/gstc-criteria/gstc-hotel-standard/) | Page checked 2026-09-29 | Authoritative starting point and current download link. |
| [GSTC Hotel Standard with Performance Indicators and SDGs (PDF)](https://www.gstc.org/wp-content/uploads/GSTC-Hotel-Standard.pdf) | **v4.0, December 30, 2025; 34 PDF pages** | Read the complete criteria, indicators and guidance before adoption. The extracted cover can render the footnote marker as `v.4.01`; the version is v4.0, also identified in [GSTC's version announcement](https://www.gstc.org/gstc-hotel-and-to-standard-now-available-japanese/). |
| [Hotel Standard Change Mapping V3 to V4 (PDF)](https://www.gstc.org/wp-content/uploads/GSTC-Hotel-Standard-Change-Mapping-V3-to-V4.pdf) | V3-to-V4 comparison; no separate issue date verified | Useful when existing checklists still reference the earlier industry standard. |
| [GSTC Standards overview](https://www.gstc.org/gstc-criteria/) | Page checked 2026-09-29 | Commercial-use statement and standard families. |
| [Certified Hotels Directory](https://www.gstc.org/certified-hotels-directory/) | Live directory; no frozen dataset adopted | Research candidate hotels by location and certification body. |
| [GSTC-accredited certification bodies](https://www.gstc.org/accreditation/gstc-accredited-certification-bodies/) | Page checked 2026-09-29 | Verify a body's current entity, scope, geography and accreditation dates. |
| [Control Union certification process](https://www.controlunion.com/service/certification/) | Page checked 2026-09-29 | General application, audit, corrective-action and certification-review process. |

The hotel document has 40 criteria across four sections: sustainability management (14), community and socioeconomic matters (9), cultural heritage (4), and environment (13). The last includes resource consumption, pollution and biodiversity. The hotel and tour-operator standards became separate documents in 2025. This is a high-level source review, not a claim that each indicator has been mapped into AXIS. [Official hotel standard](https://www.gstc.org/wp-content/uploads/GSTC-Hotel-Standard.pdf), [hotel overview](https://www.gstc.org/gstc-criteria/gstc-hotel-standard/).

## Original examples for discussion

These eight prompts are **AXIS draft examples**, not GSTC wording, indicator IDs, required evidence, or an exhaustive checklist. They illustrate a workflow your dad can review. No one should use their completion as proof of conformity to the full standard.

| Topic | Draft question | Example evidence to discuss |
| --- | --- | --- |
| Management | Who owns the hotel's improvement plan? | Named owner and current plan |
| Management | How did staff learn their responsibilities? | Briefing notes and attendance |
| Community | Which local suppliers were used this month? | Redacted purchase sample |
| Community | How can workers raise concerns? | Procedure and anonymised example |
| Culture | Who reviewed the guest cultural guide? | Review record and guide |
| Culture | How was permission for cultural material recorded? | Permission record |
| Environment | What explains this month's water change? | Meter log and investigation |
| Environment | Where did sampled waste loads go? | Collection records |

For each real requirement, record its source document, revision, exact location, assessment question, evidence expectations, applicability, reviewer and review date. Preserve the wording and version used by an existing assessment when later requirements change. A new or revised requirement should remain a draft until a competent reviewer approves it. Where evidence contains employee or guest data, choose a redacted sample for the pilot.

## Decisions for your dad

| Decision | Current pilot position | Required decision before real hotel use |
| --- | --- | --- |
| Scope | Fictional hotel assessment | Hotel type, facilities, boundaries, audit period and applicable local context |
| Standards | AXIS demonstration material | Approve the source edition and a complete reviewed criteria/indicator mapping |
| Applicability | A reason is required for exclusions | Define who can accept an exclusion and what supports it |
| Evidence | Files, observations and notes support assessments | Define acceptable samples, age, provenance and sufficiency for each requirement |
| Severity | Conforming, observation, minor and major | Define each category and approve examples; these are product choices |
| Critical requirements | Internal flags | Identify which requirements are critical and why |
| Scores | Provisional internal points and bands | Approve, replace or remove scores; do not present them as a GSTC rating |
| Deadlines | Engine defaults: major 14 days, minor 30 days | Approve the internal policy or cite the actual external deadline source |
| Verification | A different authenticated person checks implementation | Approve competence requirements and separation of duties |
| Reports | Internal assessment output | Approve audience, wording, sign-off and limitations |

The shared engine currently awards 1 / 0.75 / 0.4 / 0 points for conforming / observation / minor / major; requires 90% coverage for a rating; and uses thresholds of 85 and 70 for its two favourable bands. These values come from [the AXIS configuration](../packages/engine/src/config.ts), **not from GSTC**. A major finding or critical gap can prevent a favourable result even when the numeric score is high. Closing an action preserves the original assessment; it does not rewrite audit-time evidence. Confirm any pilot-specific override against its recorded configuration.

## Commercial use and claims

GSTC states that its standards are free for non-commercial use and that it reserves the right to assess and charge fees for commercial use. That statement does not establish AXIS's commercial permission, licence scope, pricing or logo rights. Record the proposed use (questions, copied text, translations, paid access and report exports), request clarification from GSTC, and retain its response before adopting the standard in a commercial service. No contact has been made or permission obtained in this task. [GSTC commercial-use statement](https://www.gstc.org/gstc-criteria/).

AXIS is an assessment and evidence-management tool. A platform report is not a certificate. GSTC accredits certification bodies; those bodies certify hotels. GSTC's list includes Control Union entities with different scopes and geographical coverage, so select the actual entity for a prospective Bali engagement and recheck its status before relying on it. [GSTC accredited bodies](https://www.gstc.org/accreditation/gstc-accredited-certification-bodies/).

Control Union describes certification as a process that includes an audit, corrective actions and a separate review that decides whether certification is awarded. Its general website does not define the detailed rules for this AXIS pilot. [Control Union process](https://www.controlunion.com/service/certification/).

The hotel directory is worldwide and updated quarterly. Filter by Indonesia and relevant Bali location terms; it is not a Bali-only register and absence may reflect a reporting delay. It is research material, not an instruction to import contact data or approach hotels. No hotel records have been imported. [GSTC directory](https://www.gstc.org/certified-hotels-directory/).

## Acceptance record to complete

- [ ] Dad/reviewer: __________________; date: __________________.
- [ ] Standard title, edition and permitted use confirmed.
- [ ] All applicable criteria and indicators mapped and checked against the source.
- [ ] Evidence, exclusions, severity, scoring and deadlines approved.
- [ ] Fictional pilot completed with a second person independently verifying an action.
- [ ] Report reviewed and approved for its intended internal audience.
- [ ] GSTC commercial-use response recorded before commercial adoption.

See [the hospitality pilot guide](hospitality-pilot.md) for the software walkthrough and deployment boundaries.
