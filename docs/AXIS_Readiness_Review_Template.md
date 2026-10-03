# AXIS Sustainability Readiness Review template

The approved report template is in [`templates/`](templates/):

- [AXIS_Readiness_Review_Template.pdf](templates/AXIS_Readiness_Review_Template.pdf) — 17-page worked example for the fictional "Rumah Padi Resort, Ubud"
- [AXIS_Readiness_Review_Template.docx](templates/AXIS_Readiness_Review_Template.docx) — the editable original

The **Readiness report** tab reproduces this layout: cover details, covering letter, important notice, summary of results, scope and method, hotel profile and key figures, gap analysis, local legal requirements, certification action plan, route to certification, and Appendices A–C (evidence register, observation and photo log, criterion coverage register), then sign-off.

## How the app uses it

- **Layout and Word styling.** `services/api/app/services/readiness_report.py` builds the same sections. The Word export uses the template's Calibri text, dark green (`#1F4E3D`) headings and green header rows with white text.
- **AI wording.** `services/api/app/services/report_style_examples.txt` holds the template's example wording (letter summary, pillar summaries, strengths, gap wording, actions). It is appended to the AI instructions in `report_ai.py` as a style guide only. If the AI copies the fictional hotel name into a real report, the draft is rejected and nothing is saved.
- **Never from AI.** Statuses, counts, priorities, evidence IDs and the coverage register are computed from the audit. See the status table in [hospitality-pilot.md](hospitality-pilot.md#readiness-report-ai-assisted).

## When the template changes

1. Replace the files in `templates/`.
2. Update the section builders in `readiness_report.py` if sections were added, removed or renamed.
3. Update `report_style_examples.txt` if the example wording changed.
4. Run `pytest tests/test_readiness.py` from `services/api`.

## Differences from the template, for review

- **Standard edition.** The template cites v4.01 and GSTC's April 2026 minimum performance requirements. AXIS's criteria data is v4.0 (30 December 2025). The edition is editable per report in Report details.
- **Measurement IDs.** The template uses M01… for figures AXIS calculates. AXIS has no measurement evidence type yet; key figures are typed into Report details instead.
- **Facts not copied in.** Template statements the app can't verify (v3.0 certificates valid until 30 December 2028, the May 2026 Bali waste directive, minimum performance requirements) are not printed automatically. Add them through the legal items and "Standard used" fields once confirmed.
