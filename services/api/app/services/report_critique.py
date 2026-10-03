"""Report critique: cheap mechanical checks that catch embarrassing errors before issue.

Called after build_readiness. Returns a list of structured issues the reviewer must triage.
Severity:
  blocker  — must fix before issue (placeholders, missing actions on failed criteria)
  warning  — should fix (orphan references, unexplained statuses)
  note     — informational, often fine
"""
import json
import re

from fastapi import HTTPException

from . import openrouter


PLACEHOLDER_PATTERNS = [
    re.compile(r"\[Reviewer to complete\]"),
    re.compile(r"\[Date\]|\[date\]"),
    re.compile(r"\[Name\]|\[name\]"),
    re.compile(r"\[month\]|\[Month\]"),
    re.compile(r"\[Address\]"),
    re.compile(r"\[.+?\]"),  # catch-all for any remaining square-bracket placeholders
]
PLACEHOLDER_WHITELIST = {"[x]", "[ ]"}


def _collect_text(report):
    """All reviewer-facing strings from the built report, keyed by section for context."""
    sections = {}
    sections["cover"] = " · ".join(f"{k}: {v}" for k, v in report.get("cover", []))
    letter = report.get("letter") or {}
    sections["letter"] = " ".join([letter.get("salutation", ""), *letter.get("paragraphs", []), *letter.get("signoff", [])])
    summary = report.get("summary") or {}
    sections["summary"] = " ".join(filter(None, [summary.get("statement"), summary.get("readiness_statement"), summary.get("limitations")]))
    sections["pillars"] = " ".join(f"{p.get('headline','')} {p.get('in_place','')} {p.get('missing','')}" for p in summary.get("pillars", []))
    sections["gaps"] = " ".join(" ".join([row.get("evidence_seen", ""), row.get("gap", "")]) for p in report.get("gaps", []) for row in p.get("rows", []))
    plan = report.get("plan") or {}
    sections["plan"] = " ".join(a.get("action", "") for a in (plan.get("phase1") or []) + (plan.get("phase2") or []))
    signoff = report.get("signoff") or []
    sections["signoff"] = " · ".join(f"{k}: {v}" for k, v in signoff)
    return sections


def _find_placeholders(text):
    found = []
    for pattern in PLACEHOLDER_PATTERNS:
        for match in pattern.finditer(text):
            token = match.group(0)
            if token not in PLACEHOLDER_WHITELIST and token not in found:
                found.append(token)
    return found


def mechanical_critique(report):
    """Run cheap deterministic checks against the built readiness report."""
    issues = []
    sections = _collect_text(report)

    # 1. Placeholders anywhere in reviewer-facing text.
    for section, text in sections.items():
        for token in _find_placeholders(text):
            issues.append({
                "severity": "blocker",
                "code": "PLACEHOLDER_LEFT",
                "section": section,
                "message": f"Placeholder {token!r} is still in the {section} section. Replace it before issuing.",
            })

    # 2. Criteria that need work but appear in no action in section 7.
    pillars = (report.get("summary") or {}).get("pillars") or report.get("gaps") or []
    needs_codes = []
    for p in pillars:
        for row in p.get("rows") or []:
            if row.get("status") in {"Partly met", "Not met", "Not evidenced"}:
                needs_codes.append(row.get("code"))
    plan_codes = set()
    for a in (report.get("plan") or {}).get("phase1", []) + (report.get("plan") or {}).get("phase2", []):
        plan_codes.update(a.get("criteria") or [])
    for code in needs_codes:
        if code and code not in plan_codes:
            issues.append({
                "severity": "blocker",
                "code": "CRITERION_WITHOUT_ACTION",
                "section": "plan",
                "message": f"{code} needs work but is not covered by any action in section 7.",
            })

    # 3. Action references a criterion that isn't in the coverage register.
    coverage_codes = {c.get("code") for c in report.get("coverage") or []}
    for a in (report.get("plan") or {}).get("phase1", []) + (report.get("plan") or {}).get("phase2", []):
        for code in a.get("criteria") or []:
            if code not in coverage_codes:
                issues.append({
                    "severity": "warning",
                    "code": "ACTION_UNKNOWN_CRITERION",
                    "section": "plan",
                    "message": f"Action {a.get('number')} cites {code}, which is not in the criterion coverage register.",
                })

    # 4. Legal items referenced in gaps but absent from section 6.
    legal_rows = report.get("legal") or []
    legal_text = " ".join(cell for row in legal_rows for cell in row).lower()
    gap_text = sections["gaps"].lower()
    for law_term in ("groundwater permit", "wastewater", "waste separation", "bpjs", "single-use plastic"):
        if law_term in gap_text and law_term not in legal_text and not any(law_term in cell.lower() for row in legal_rows for cell in row):
            issues.append({
                "severity": "warning",
                "code": "LAW_NOT_IN_REGISTER",
                "section": "legal",
                "message": f"Section 5 gaps mention “{law_term}” but it is not in the section 6 legal register.",
            })

    # 5. Pillar has narrative but no criteria.
    for p in pillars:
        if (p.get("headline") or p.get("in_place") or p.get("missing")) and not p.get("rows"):
            issues.append({
                "severity": "note",
                "code": "PILLAR_EMPTY_NARRATIVE",
                "section": f"pillar_{p.get('code')}",
                "message": f"Pillar {p.get('code')} has narrative text but no criterion rows. Either add rows or clear the headline.",
            })

    # 6. Critical gaps missing from the first phase of the action plan.
    phase1_codes = set()
    for a in (report.get("plan") or {}).get("phase1", []):
        phase1_codes.update(a.get("criteria") or [])
    critical_codes = []
    for p in pillars:
        for row in p.get("rows") or []:
            if row.get("priority") == "Critical":
                critical_codes.append(row.get("code"))
    for code in critical_codes:
        if code and code not in phase1_codes:
            issues.append({
                "severity": "warning",
                "code": "CRITICAL_IN_PHASE_2",
                "section": "plan",
                "message": f"{code} is marked Critical but appears in Months 4–6 rather than Months 1–3.",
            })

    # 7. Top gaps that don't resolve to a known criterion code.
    for gap in (report.get("summary") or {}).get("top_gaps") or []:
        code = gap.get("criterion")
        if code and code not in coverage_codes:
            issues.append({
                "severity": "warning",
                "code": "TOP_GAP_UNKNOWN_CRITERION",
                "section": "summary",
                "message": f"Top gap cites {code}, which is not in the criterion coverage register.",
            })

    return issues


AI_SYSTEM = """You review an AXIS Sustainability Readiness Review for internal contradictions and factual conflicts.

Rules:
- Only report issues that are visible in the supplied report text. Do not invent problems.
- Only flag contradictions, factual conflicts and claims that contradict stated evidence. Ignore style and grammar.
- Return at most 8 issues. Return an empty list if the report is coherent.
- Each issue cites one short quote from the report so the reviewer can find it.

Return JSON exactly:
{"issues": [{"severity": "warning|note", "section": "letter|summary|gaps|plan|legal|other", "message": "one-sentence problem description", "quote": "<= 25 words from the report that shows the issue"}]}"""


async def ai_contradiction_pass(report):
    """Optional second pass that uses the mechanical model to catch internal contradictions."""
    if not openrouter.configured():
        return []
    sections = _collect_text(report)
    # Keep the payload compact — only the reviewer-facing text, not the full bundle.
    payload = {k: v[:4000] for k, v in sections.items() if v}
    result = await openrouter.chat(
        system=AI_SYSTEM,
        user="Report sections (JSON):\n" + json.dumps(payload, ensure_ascii=False),
        task="critique",
        max_tokens=1200,
        timeout=60.0,
        title="AXIS report critique",
    )
    try:
        data = openrouter.extract_json_object(result.content)
    except (ValueError, TypeError):
        raise HTTPException(502, "The AI critique reply was not valid JSON. Try again.")
    issues = []
    for item in (data.get("issues") or [])[:8]:
        if not isinstance(item, dict):
            continue
        severity = item.get("severity") if item.get("severity") in {"warning", "note"} else "note"
        message = str(item.get("message") or "").strip()[:400]
        if not message:
            continue
        issues.append({
            "severity": severity,
            "code": "AI_CONTRADICTION",
            "section": str(item.get("section") or "other")[:40],
            "message": message,
            "quote": str(item.get("quote") or "").strip()[:300] or None,
        })
    return issues


async def critique(report, include_ai=False):
    issues = mechanical_critique(report)
    if include_ai:
        issues = issues + await ai_contradiction_pass(report)
    counts = {"blocker": 0, "warning": 0, "note": 0}
    for issue in issues:
        counts[issue.get("severity", "note")] = counts.get(issue.get("severity", "note"), 0) + 1
    return {"ready_to_issue": counts["blocker"] == 0, "counts": counts, "issues": issues}
