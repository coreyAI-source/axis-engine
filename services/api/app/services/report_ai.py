"""Drafts readiness-report narrative through OpenRouter. Output is validated by readiness_report.clean_narrative."""
import json
import logging
from pathlib import Path

from fastapi import HTTPException

from . import openrouter

logger = logging.getLogger(__name__)

SYSTEM = """You draft the narrative sections of an AXIS Sustainability Readiness Review: a one-day, sample-based review of what a hotel must address to achieve GSTC certification. A qualified reviewer edits and approves your draft before it is issued.

Rules (all mandatory):
- Use ONLY the facts supplied. Never invent evidence, figures, percentages, dates, names, laws, permits, regulations or events. If something is unknown, say it was not established.
- Refer to evidence by the IDs supplied (e.g. D01, I02, O03). Evidence of type Interview is staff-reported, not verified.
- When a criterion has an "indicator_notes" list, treat each entry as the auditor's record for that indicator. The "evidence_seen" entry must summarise what those indicator notes show by indicator number, naming the evidence IDs linked to each indicator. Do not restate the notes verbatim.
- Keep each criterion's status and priority exactly as supplied. Do not assign scores, percentages or a pass/fail.
- Write each gap as a concrete deliverable that must exist on the day of a certification audit ("A written policy that…", "Monthly records of…"), not advice ("consider improving…").
- Never call gaps "nonconformities". Never state or imply the hotel is, or will be, certified. AXIS does not certify hotels.
- Only mention a law or local rule if it appears in the supplied legal items; otherwise refer to "applicable laws and permits" generally.
- Action owners are hotel roles (e.g. General Manager, Chief Engineer, HR Manager), not personal names.
- Plain, polite, direct British/Australian English. Short sentences. No marketing language.

Return one JSON object with exactly these keys:
{
  "letter_summary": "3-5 sentences for the covering letter: genuine strengths, the main gaps, and whether they are typical and closable. No numbers that are not in the facts.",
  "readiness_statement": "1-2 sentences on overall readiness and what kind of work remains (documentation, measurement, practice). Do not repeat the criterion counts.",
  "limitations": "2-4 sentences: what this one-day review could not establish, based on not-sampled criteria, areas not inspected and interview-only evidence.",
  "pillars": {"A": {"headline": "under 15 words", "in_place": "one sentence", "missing": "one sentence"}, "B": {...}, "C": {...}, "D": {...}},
  "strengths": [{"text": "one sentence citing evidence IDs", "evidence": "observed|documented|staff-reported|unverified"}],
  "top_gaps": [{"criterion": "A1", "text": "imperative deliverable, under 25 words"}],
  "criteria": {"<code>": {"evidence_seen": "under 25 words, starting with the evidence IDs", "gap": "the deliverable(s) that must exist on audit day"}},
  "actions": [{"criteria": ["A1"], "action": "imperative action", "owner": "hotel role", "evidence": "what the certification auditor will want to see"}]
}
Include a "criteria" entry for every criterion whose status is Partly met, Not met or Not evidenced, or whose priority is Improvement. Every such criterion must appear in at least one action; related criteria may share an action. Give 2-5 strengths and up to 5 top gaps, Critical first. Omit a pillar key if it has no criteria.

""" + (Path(__file__).with_name("report_style_examples.txt")).read_text(encoding="utf-8")


def _copied_example(narrative):
    return "rumah padi" in json.dumps(narrative, ensure_ascii=False).lower()


def configured():
    return openrouter.configured()


async def draft_narrative(facts):
    result = await openrouter.chat(
        system=SYSTEM,
        user="Audit facts (JSON):\n" + json.dumps(facts, ensure_ascii=False),
        task="narrative",
        max_tokens=12000,
        timeout=180.0,
        title="AXIS readiness report",
    )
    try:
        narrative = openrouter.extract_json_object(result.content)
    except (ValueError, TypeError):
        raise HTTPException(502, "The AI response was not valid report JSON. Try again, or choose a different OPENROUTER_MODEL.")
    if _copied_example(narrative):
        raise HTTPException(502, "The AI copied the template's fictional example instead of this audit. Nothing was saved; try again.")
    return narrative, result.model
