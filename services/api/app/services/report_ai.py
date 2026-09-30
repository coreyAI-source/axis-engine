"""Drafts readiness-report narrative through OpenRouter. Output is validated by readiness_report.clean_narrative."""
import json
import logging
import re

import httpx
from fastapi import HTTPException

from ..config import settings

logger = logging.getLogger(__name__)
URL = "https://openrouter.ai/api/v1/chat/completions"

SYSTEM = """You draft the narrative sections of an AXIS Sustainability Readiness Review: a one-day, sample-based review of what a hotel must address to achieve GSTC certification. A qualified reviewer edits and approves your draft before it is issued.

Rules (all mandatory):
- Use ONLY the facts supplied. Never invent evidence, figures, percentages, dates, names, laws, permits, regulations or events. If something is unknown, say it was not established.
- Refer to evidence by the IDs supplied (e.g. D01, I02, O03). Evidence of type Interview is staff-reported, not verified.
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
Include a "criteria" entry for every criterion whose status is Partly met, Not met or Not evidenced, or whose priority is Improvement. Every such criterion must appear in at least one action; related criteria may share an action. Give 2-5 strengths and up to 5 top gaps, Critical first. Omit a pillar key if it has no criteria."""


def configured():
    return bool(settings.openrouter_api_key.strip())


def _parse(content):
    text = re.sub(r"^```(?:json)?|```$", "", (content or "").strip(), flags=re.MULTILINE).strip()
    start, end = text.find("{"), text.rfind("}")
    if start < 0 or end <= start:
        raise ValueError("No JSON object in response")
    return json.loads(text[start:end + 1])


async def draft_narrative(facts):
    if not configured():
        raise HTTPException(503, "AI drafting is not configured. Add OPENROUTER_API_KEY to services/api/.env and restart the API.")
    body = {
        "model": settings.openrouter_model,
        "temperature": 0.2,
        "max_tokens": 12000,
        "response_format": {"type": "json_object"},
        "messages": [
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": "Audit facts (JSON):\n" + json.dumps(facts, ensure_ascii=False)},
        ],
    }
    headers = {"Authorization": f"Bearer {settings.openrouter_api_key.strip()}", "HTTP-Referer": settings.openrouter_referer, "X-Title": "AXIS readiness report"}
    try:
        async with httpx.AsyncClient(timeout=180) as client:
            response = await client.post(URL, headers=headers, json=body)
            if response.status_code == 400:
                # Some models reject response_format; the prompt already demands JSON.
                body.pop("response_format")
                response = await client.post(URL, headers=headers, json=body)
    except httpx.HTTPError:
        raise HTTPException(502, "The AI provider could not be reached. Check the internet connection and try again.")
    if response.status_code != 200:
        logger.warning("OpenRouter returned %s", response.status_code)
        detail = {401: "the API key was rejected", 402: "the OpenRouter account has no credit", 429: "the provider is rate-limiting requests"}.get(response.status_code, f"HTTP {response.status_code}")
        raise HTTPException(502, f"AI drafting failed: {detail}. No report changes were saved.")
    try:
        payload = response.json()
        content = payload["choices"][0]["message"]["content"]
        return _parse(content), payload.get("model") or settings.openrouter_model
    except (ValueError, KeyError, IndexError, TypeError):
        raise HTTPException(502, "The AI response was not valid report JSON. Try again, or choose a different OPENROUTER_MODEL.")
