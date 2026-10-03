"""Drafts a per-criterion assessment outcome + rationale from indicator-level notes.

The auditor reviews and edits the draft before it becomes the saved assessment.
Uses the shared openrouter helper (default premium model: anthropic/claude-sonnet-4.6).
"""
import json
import logging
import re

from fastapi import HTTPException

from . import openrouter

logger = logging.getLogger(__name__)

STATUSES = ["conforming", "observation", "minor", "major", "not_applicable"]

SYSTEM = """You draft one assessment outcome and rationale for a single hotel-audit criterion, based on the auditor's per-indicator notes and evidence descriptions. The auditor reviews and edits your draft before it is saved.

Rules:
- Use ONLY the facts supplied. Never invent evidence, figures, dates, names, laws or events. If an indicator has no notes, say it was not established.
- Refer to evidence by the descriptions provided; do not fabricate document titles or references. Interview evidence is staff-reported.
- Choose exactly one outcome from: conforming, observation, minor, major, not_applicable.
  * conforming: every indicator is met with corroborated evidence
  * observation: mostly met but with a low-risk gap worth flagging
  * minor: a single-indicator gap that does not undermine the criterion
  * major: a systemic gap, missing critical indicator, or absence of evidence for a critical criterion
  * not_applicable: the criterion does not apply to this property; the rationale must explain why
- The rationale must:
  * name each indicator by number (Indicator 1, Indicator 2, ...) and briefly say what the notes/evidence show
  * be plain, direct British/Australian English; short sentences; no marketing language
  * be at least 40 words if the outcome is not "not_applicable"
  * never state or imply the hotel is or will be certified; AXIS does not certify hotels
- Return exactly one JSON object with keys: "status" (one of the outcomes) and "rationale" (string). No other keys, no prose outside the JSON."""


def configured():
    return openrouter.configured()


def _parse(content):
    data = openrouter.extract_json_object(content)
    status = data.get("status")
    rationale = data.get("rationale")
    if status not in STATUSES or not isinstance(rationale, str) or not rationale.strip():
        raise ValueError("AI reply missing valid status or rationale")
    return {"status": status, "rationale": rationale.strip()}


def build_facts(requirement, assessment, evidence_by_id):
    """Shape a compact JSON payload for the model. Only fields the model needs."""
    indicators = requirement.get("indicators") or []
    guidance_map: dict[int, str] = {}
    guidance_notes: list[str] = []
    for entry in requirement.get("guidance") or []:
        match = re.match(r"^(\d+)\.\s+([\s\S]*)$", entry)
        if match:
            guidance_map[int(match.group(1))] = match.group(2).strip()
        else:
            guidance_notes.append(entry.strip())
    inputs_by_index = {int(item["index"]): item for item in (assessment.get("indicatorInputs") or [])}
    indicator_facts = []
    for position, text in enumerate(indicators):
        item = inputs_by_index.get(position) or {}
        linked = []
        for eid in item.get("evidenceIds") or []:
            record = evidence_by_id.get(eid)
            if record:
                linked.append({
                    "kind": record.get("kind"),
                    "description": record.get("description"),
                    "reference": record.get("reference") or "",
                    "fileName": (record.get("attachment") or {}).get("fileName"),
                })
        indicator_facts.append({
            "number": position + 1,
            "text": re.sub(r"\s*\(See Guidelines\)\s*$", "", text),
            "guideline": guidance_map.get(position + 1, ""),
            "notes": (item.get("notes") or "").strip(),
            "evidence": linked,
        })
    return {
        "criterion": {
            "clause": (requirement.get("source") or {}).get("clause"),
            "title": requirement.get("title"),
            "text": requirement.get("text"),
            "category": requirement.get("category"),
            "critical": bool(requirement.get("critical")),
            "auditPrompt": requirement.get("auditPrompt") or "",
        },
        "indicators": indicator_facts,
        "guidance_notes": guidance_notes,
        "current_outcome": assessment.get("status") or "unassessed",
        "current_rationale": assessment.get("rationale") or "",
    }


async def suggest_assessment(facts):
    result = await openrouter.chat(
        system=SYSTEM,
        user="Criterion facts (JSON):\n" + json.dumps(facts, ensure_ascii=False),
        task="suggestion",
        max_tokens=2000,
        timeout=90.0,
        title="AXIS assessment suggestion",
    )
    try:
        parsed = _parse(result.content)
    except (ValueError, TypeError):
        raise HTTPException(502, "The AI reply was not a valid assessment suggestion. Try again.")
    return {**parsed, "model": result.model}
