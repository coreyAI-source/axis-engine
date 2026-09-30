"""Run the shared engine on the server. The browser never supplies identity or state."""
import asyncio
import json
import logging
import os
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from fastapi import HTTPException

logger = logging.getLogger(__name__)
ENGINE_SCRIPT = Path(__file__).resolve().parents[4] / "packages" / "engine" / "src" / "server.ts"
ENGINE_SLOTS = asyncio.Semaphore(4)


def actor_for(user):
    return {"name": f"{user.first_name} {user.last_name}".strip(), "userId": str(user.id), "authenticated": True}


def _run(payload):
    node = shutil.which("node")
    if not node or not ENGINE_SCRIPT.is_file():
        raise HTTPException(503, "Hotel rules engine is unavailable. Install Node.js 22.6+ and include packages/engine in the API deployment.")
    # Do not give the engine database credentials or the API signing secret.
    child_env = {k: v for k, v in os.environ.items() if k.upper() in {"PATH", "SYSTEMROOT", "WINDIR", "TEMP", "TMP"}}
    try:
        result = subprocess.run(
            [node, "--experimental-strip-types", "--no-warnings", str(ENGINE_SCRIPT)],
            input=json.dumps(payload), capture_output=True, text=True, encoding="utf-8",
            timeout=20, env=child_env, cwd=ENGINE_SCRIPT.parents[3],
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
        )
        parsed = json.loads(result.stdout)
        if result.returncode != 0 or not isinstance(parsed, dict) or "ok" not in parsed:
            raise ValueError("Invalid engine response")
    except (OSError, ValueError, subprocess.TimeoutExpired):
        logger.error("Hospitality rules process failed (details withheld from client)")
        raise HTTPException(503, "The hotel rules engine could not finish this request. No audit changes were saved.")
    if not parsed["ok"]:
        raise HTTPException(422, parsed.get("violations", [{"code": "ENGINE_ERROR", "message": "The audit could not be updated."}]))
    return parsed


async def run_engine(operation, user, bundle=None, input=None):
    payload = {"operation": operation, "actor": actor_for(user), "now": datetime.now(timezone.utc).isoformat(), "input": input or {}}
    if bundle is not None:
        payload["bundle"] = bundle
    # A thread also works under Windows uvicorn's reload event loop.
    async with ENGINE_SLOTS:
        return await asyncio.to_thread(_run, payload)
