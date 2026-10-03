"""Document-ingestion preview.

Takes an uploaded file + the audit's criterion list, extracts text, asks the mechanical model
for a draft {description, kind, collectedVia, criteriaCodes}. Does not save anything —
the auditor reviews the draft, edits if needed, and then calls the existing upload endpoint
with the accepted values.
"""
import io
import json
import logging
import re

from fastapi import HTTPException

from . import openrouter

logger = logging.getLogger(__name__)

MAX_TEXT_CHARS = 20_000
VALID_KINDS = {"document", "record", "photo", "interview", "observation"}
VALID_VIA = {"on_site", "before_visit", "after_visit", "interview", "calculation"}

SYSTEM = """You draft a short metadata entry for a document a hotel sent to an AXIS sustainability reviewer, so the reviewer can accept it into the Evidence Register in one click.

Rules:
- Use ONLY the supplied text. Never invent dates, figures, laws or regulations. If the document is not clearly identifiable, say so in the description.
- "description" is one plain sentence (max 160 chars) naming the document type and what it shows.
- "kind" is one of: document, record, photo, interview, observation. Choose "record" for monthly logs/measurements/receipts; "document" for policies, procedures, certificates, contracts; "photo" only if the text is clearly a photo caption.
- "collectedVia" is one of: on_site, before_visit, after_visit, interview, calculation. Default to "before_visit" for documents sent to the reviewer; use "calculation" if the file is clearly a derived metric.
- "criteriaCodes" is a list of up to 4 GSTC-style criterion codes (e.g. "A1", "B9", "D6") that this document most likely supports. Pick only codes from the supplied list. If unsure, return an empty list.
- "confidence" is one of "high" | "medium" | "low".

Return exactly one JSON object with keys: description, kind, collectedVia, criteriaCodes, confidence. No prose outside the JSON."""


def extract_text(file_bytes: bytes, content_type: str) -> tuple[str, bool]:
    """Return (text, is_scanned). Scanned PDFs can't be text-extracted without OCR."""
    mime = (content_type or "").split(";")[0].lower().strip()
    if mime == "application/pdf":
        try:
            from pypdf import PdfReader
            reader = PdfReader(io.BytesIO(file_bytes))
            pages = [page.extract_text() or "" for page in reader.pages[:30]]
            text = "\n".join(pages).strip()
            # Heuristic: a PDF of mostly scanned pages produces very little text per page.
            is_scanned = bool(reader.pages) and len(text) < 200
            return text, is_scanned
        except Exception as exc:
            logger.warning("PDF extraction failed: %s", exc)
            raise HTTPException(422, "The PDF could not be read. Make sure the file is not password-protected.")
    if mime in {"text/plain", "text/csv"}:
        try:
            return file_bytes.decode("utf-8-sig", errors="replace").strip(), False
        except Exception:
            raise HTTPException(415, "The file is not valid UTF-8 text.")
    if mime.startswith("image/"):
        # Images can't be text-extracted here; the model will see only the filename.
        return "", True
    raise HTTPException(415, "Supported for metadata drafting: PDF, UTF-8 text, CSV. Image OCR is not enabled.")


def _parse(content: str, allowed_codes: set[str]) -> dict:
    data = openrouter.extract_json_object(content)
    description = str(data.get("description") or "").strip()[:400]
    if not description:
        raise ValueError("Missing description")
    kind = data.get("kind") if data.get("kind") in VALID_KINDS else "document"
    via = data.get("collectedVia") if data.get("collectedVia") in VALID_VIA else "before_visit"
    raw_codes = data.get("criteriaCodes") or []
    if not isinstance(raw_codes, list):
        raw_codes = []
    codes = []
    for code in raw_codes[:6]:
        if isinstance(code, str):
            cleaned = re.sub(r"\s+", "", code).upper()
            if cleaned in allowed_codes:
                codes.append(cleaned)
    confidence = data.get("confidence") if data.get("confidence") in {"high", "medium", "low"} else "medium"
    return {"description": description, "kind": kind, "collectedVia": via, "criteriaCodes": codes, "confidence": confidence}


async def draft_metadata(file_bytes: bytes, content_type: str, file_name: str, criteria: list[dict]) -> dict:
    """Return a draft metadata record. Does not persist anything."""
    text, is_scanned = extract_text(file_bytes, content_type)
    if is_scanned and not text:
        return {
            "description": f"{file_name} — content could not be read automatically (scanned or image).",
            "kind": "document", "collectedVia": "before_visit", "criteriaCodes": [], "confidence": "low",
            "scanned": True, "model": None,
        }
    truncated = text[:MAX_TEXT_CHARS]
    if len(text) > MAX_TEXT_CHARS:
        truncated += "\n[truncated]"
    allowed_codes = {c["code"] for c in criteria if c.get("code")}
    user = json.dumps({
        "fileName": file_name,
        "criteria": [{"code": c["code"], "title": c.get("title", "")} for c in criteria if c.get("code")],
        "excerpt": truncated,
    }, ensure_ascii=False)
    result = await openrouter.chat(
        system=SYSTEM,
        user=user,
        task="metadata",
        max_tokens=600,
        timeout=60.0,
        title="AXIS document ingestion",
    )
    try:
        parsed = _parse(result.content, allowed_codes)
    except (ValueError, TypeError):
        raise HTTPException(502, "The AI reply was not a valid metadata draft. Try again.")
    return {**parsed, "scanned": False, "model": result.model}
