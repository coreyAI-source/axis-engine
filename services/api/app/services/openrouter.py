"""Shared OpenRouter HTTP helper. Used by every AI task so model selection,
retry rules and error handling stay consistent."""
import json
import logging
import re
from dataclasses import dataclass

import httpx
from fastapi import HTTPException

from ..config import settings

logger = logging.getLogger(__name__)
URL = "https://openrouter.ai/api/v1/chat/completions"


def configured() -> bool:
    return bool(settings.openrouter_api_key.strip())


def model_for(task: str) -> str:
    """Pick the OpenRouter model slug for a named task.
    Tasks that produce reviewer-facing narrative (letter, gaps) use the premium model.
    Mechanical tasks (critique, metadata extraction) default to the cheaper model."""
    mechanical = {"critique", "metadata", "translate", "photo_tag"}
    return settings.openrouter_model_mechanical if task in mechanical else settings.openrouter_model


@dataclass
class ChatResult:
    content: str
    model: str


async def chat(system: str, user: str, task: str, *, temperature: float = 0.2, max_tokens: int = 4000, response_format_json: bool = True, timeout: float = 180.0, title: str = "AXIS") -> ChatResult:
    if not configured():
        raise HTTPException(503, "AI drafting is not configured. Add OPENROUTER_API_KEY to services/api/.env and restart the API.")
    model = model_for(task)
    body = {
        "model": model,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
    }
    if response_format_json:
        body["response_format"] = {"type": "json_object"}
    headers = {
        "Authorization": f"Bearer {settings.openrouter_api_key.strip()}",
        "HTTP-Referer": settings.openrouter_referer,
        "X-Title": title,
    }
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(URL, headers=headers, json=body)
            if response.status_code == 400 and response_format_json:
                body.pop("response_format", None)
                response = await client.post(URL, headers=headers, json=body)
    except httpx.HTTPError:
        raise HTTPException(502, "The AI provider could not be reached. Check the internet connection and try again.")
    if response.status_code != 200:
        logger.warning("OpenRouter %s task returned %s", task, response.status_code)
        detail = {
            401: "the API key was rejected",
            402: "the OpenRouter account has no credit",
            429: "the provider is rate-limiting requests",
        }.get(response.status_code, f"HTTP {response.status_code}")
        raise HTTPException(502, f"AI call failed: {detail}. No changes were saved.")
    try:
        payload = response.json()
        content = payload["choices"][0]["message"]["content"] or ""
        return ChatResult(content=content, model=payload.get("model") or model)
    except (ValueError, KeyError, IndexError, TypeError):
        raise HTTPException(502, "The AI provider returned a malformed response. Try again.")


def extract_json_object(content: str) -> dict:
    """Strip code fences and extract the first balanced JSON object from a model reply."""
    text = re.sub(r"^```(?:json)?|```$", "", (content or "").strip(), flags=re.MULTILINE).strip()
    start, end = text.find("{"), text.rfind("}")
    if start < 0 or end <= start:
        raise ValueError("No JSON object in response")
    return json.loads(text[start:end + 1])
