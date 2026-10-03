import hashlib
import re
import uuid
from datetime import datetime, timezone
from urllib.parse import quote

from fastapi import APIRouter, Depends, File, Form, HTTPException, Response, UploadFile
from pydantic import ValidationError
from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..models.hospitality import HospitalityAudit, HospitalityFile
from ..models.org import User
from ..schemas.hospitality import AuditCreate, Command, INPUT_MODELS, MemberCreate, ReadinessProfile, SuggestRequest
from ..services import ingest_ai, readiness_report as readiness, report_ai, report_critique, suggest_ai
from ..services.hospitality import actor_for, run_engine
from ..utils.security import get_current_user, hash_password

router = APIRouter(prefix="/hospitality", tags=["hospitality"])
WRITERS = {"admin", "compliance_manager", "lead_auditor", "auditor"}
READERS = WRITERS | {"process_owner", "viewer"}
REVIEWERS = {"admin", "compliance_manager", "lead_auditor"}
MAX_FILE_BYTES = 10 * 1024 * 1024


def require_role(user, allowed):
    if user.role_code not in allowed:
        raise HTTPException(403, "Your role does not allow this operation.")


def member_view(user):
    return {"id": str(user.id), "organisation_id": str(user.organisation_id), "name": actor_for(user)["name"], "email": user.email, "role_code": user.role_code}


@router.get("/me")
async def me(user=Depends(get_current_user)):
    require_role(user, READERS)
    return member_view(user)


@router.get("/members")
async def members(db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    require_role(user, READERS)
    result = await db.execute(select(User).where(User.organisation_id == user.organisation_id, User.active_flag.is_(True)).order_by(User.first_name, User.last_name))
    return [member_view(u) for u in result.scalars()]


@router.post("/members", status_code=201)
async def create_member(payload: MemberCreate, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    require_role(user, {"admin"})
    if len(payload.password.encode("utf-8")) > 72:
        raise HTTPException(422, "Password must fit within 72 UTF-8 bytes.")
    record = User(organisation_id=user.organisation_id, first_name=payload.first_name, last_name=payload.last_name,
                  email=str(payload.email).lower(), role_code=payload.role_code, active_flag=True,
                  hashed_password=hash_password(payload.password))
    db.add(record)
    try:
        await db.flush()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(409, "That email address is unavailable.")
    return member_view(record)


async def get_audit(audit_id, db, user):
    require_role(user, READERS)
    row = await db.scalar(select(HospitalityAudit).where(HospitalityAudit.id == audit_id, HospitalityAudit.organisation_id == user.organisation_id))
    if row is None:
        raise HTTPException(404, "Hotel audit not found.")
    return row


def summary(row):
    return {"id": str(row.id), "title": row.title, "site_name": row.site_name, "status": row.status, "version": row.version, "updated_at": row.updated_at.isoformat()}


async def detail(row, user, warnings=None):
    report = await run_engine("report", user, row.bundle)
    return {**summary(row), "bundle": row.bundle, "report": report["value"]["report"], "warnings": warnings or []}


def check_version(row, expected):
    if row.version != expected:
        raise HTTPException(409, "This audit changed in another session. Reload it before saving again.")


async def save_bundle(row, expected, bundle, db, user):
    result = await db.execute(update(HospitalityAudit).where(
        HospitalityAudit.id == row.id, HospitalityAudit.organisation_id == user.organisation_id,
        HospitalityAudit.version == expected,
    ).values(bundle=bundle, version=expected + 1, status=bundle["audit"]["status"],
             title=bundle["audit"]["title"], site_name=bundle["audit"]["siteName"],
             updated_at=datetime.now(timezone.utc)).execution_options(synchronize_session=False))
    if result.rowcount != 1:
        raise HTTPException(409, "This audit changed in another session. Reload it before saving again.")
    await db.refresh(row)


@router.get("/audits")
async def list_audits(db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    require_role(user, READERS)
    result = await db.execute(select(HospitalityAudit).where(HospitalityAudit.organisation_id == user.organisation_id).order_by(HospitalityAudit.updated_at.desc()))
    return [summary(row) for row in result.scalars()]


@router.post("/audits", status_code=201)
async def create_audit(payload: AuditCreate, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    require_role(user, WRITERS)
    result = await run_engine("create", user, input={"title": payload.title, "siteName": payload.site_name, "scopeStatement": payload.scope_statement})
    bundle = result["value"]
    row = HospitalityAudit(id=uuid.UUID(bundle["audit"]["id"]), organisation_id=user.organisation_id, created_by=user.id,
                           title=bundle["audit"]["title"], site_name=bundle["audit"]["siteName"],
                           status=bundle["audit"]["status"], version=1, bundle=bundle)
    db.add(row)
    await db.flush()
    return await detail(row, user, result.get("warnings"))


@router.get("/audits/{audit_id}")
async def read_audit(audit_id: uuid.UUID, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    return await detail(await get_audit(audit_id, db, user), user)


@router.post("/audits/{audit_id}/commands")
async def command(audit_id: uuid.UUID, payload: Command, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    row = await get_audit(audit_id, db, user)
    try:
        data = INPUT_MODELS[payload.operation].model_validate(payload.input).model_dump(mode="json", exclude_none=True)
    except ValidationError as exc:
        raise HTTPException(422, [{"code": "INVALID_INPUT", "message": error["msg"], "field": ".".join(map(str, error["loc"]))} for error in exc.errors(include_input=False)])
    if payload.operation in {"action.progress", "action.submit"} and user.role_code == "process_owner":
        action = next((a for a in row.bundle["actions"] if a["id"] == data["actionId"]), None)
        if not action or action["owner"].get("userId") != str(user.id):
            raise HTTPException(403, "You can update only actions assigned to you.")
    elif payload.operation == "evidence":
        require_role(user, WRITERS | {"process_owner"})
    elif payload.operation == "requirement.review":
        require_role(user, REVIEWERS)
    else:
        require_role(user, WRITERS)
    check_version(row, payload.expected_version)
    if payload.operation == "action.create":
        owner = await db.scalar(select(User).where(User.id == uuid.UUID(data.pop("ownerUserId")), User.organisation_id == user.organisation_id, User.active_flag.is_(True)))
        if owner is None or owner.role_code not in WRITERS | {"process_owner"}:
            raise HTTPException(422, "Choose an active action owner from this organisation with permission to implement actions.")
        data["owner"] = actor_for(owner)
    result = await run_engine(payload.operation, user, row.bundle, data)
    await save_bundle(row, payload.expected_version, result["value"], db, user)
    return await detail(row, user, result.get("warnings"))


@router.post("/audits/{audit_id}/files", status_code=201)
async def upload_file(audit_id: uuid.UUID, file: UploadFile = File(...), expected_version: int = Form(..., ge=1),
                      description: str = Form(..., min_length=1, max_length=4000),
                      collected_via: str = Form("", max_length=20),
                      db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    row = await get_audit(audit_id, db, user)
    require_role(user, WRITERS | {"process_owner"})
    check_version(row, expected_version)
    content = await file.read(MAX_FILE_BYTES + 1)
    if not content:
        raise HTTPException(422, "The file is empty.")
    if len(content) > MAX_FILE_BYTES:
        raise HTTPException(413, "Evidence files must be 10 MB or smaller.")
    mime = (file.content_type or "").split(";")[0].lower()
    signatures = {"application/pdf": b"%PDF-", "image/png": b"\x89PNG\r\n\x1a\n", "image/jpeg": b"\xff\xd8\xff"}
    if mime in signatures:
        if not content.startswith(signatures[mime]):
            raise HTTPException(415, "The file content does not match its declared type.")
    elif mime in {"text/plain", "text/csv"}:
        try:
            decoded = content.decode("utf-8-sig")
            if "\x00" in decoded:
                raise ValueError()
        except (ValueError, UnicodeDecodeError):
            raise HTTPException(415, "Text evidence must be UTF-8 text.")
    else:
        raise HTTPException(415, "Supported evidence: PDF, JPEG, PNG, UTF-8 text and CSV.")
    name = re.sub(r"[\x00-\x1f\x7f/\\]", "_", file.filename or "evidence")[:255]
    file_id = uuid.uuid4()
    digest = hashlib.sha256(content).hexdigest()
    key = f"hospitality/{audit_id}/{file_id}"
    valid_via = {"on_site", "before_visit", "after_visit", "interview", "calculation"}
    via = collected_via.strip() if collected_via.strip() in valid_via else ""
    result = await run_engine("evidence", user, row.bundle, {
        "kind": "photo" if mime.startswith("image/") else "document", "description": description.strip(),
        "attachment": {"key": key, "fileName": name, "contentType": mime, "sizeBytes": len(content), "sha256": digest},
        **({"collectedVia": via} if via else {}),
    })
    bundle = result["value"]
    evidence = next(e for e in bundle["evidence"] if e.get("attachment", {}).get("key") == key)
    # The attachment and aggregate version update commit together, or neither does.
    await save_bundle(row, expected_version, bundle, db, user)
    db.add(HospitalityFile(id=file_id, audit_id=audit_id, evidence_id=evidence["id"], file_name=name,
                           content_type=mime, sha256=digest, content=content))
    await db.flush()
    return await detail(row, user, result.get("warnings"))


@router.post("/audits/{audit_id}/evidence/draft-metadata")
async def draft_evidence_metadata(audit_id: uuid.UUID, file: UploadFile = File(...), db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    row = await get_audit(audit_id, db, user)
    require_role(user, WRITERS | {"process_owner"})
    content = await file.read(MAX_FILE_BYTES + 1)
    if not content:
        raise HTTPException(422, "The file is empty.")
    if len(content) > MAX_FILE_BYTES:
        raise HTTPException(413, "Files must be 10 MB or smaller for metadata drafting.")
    criteria = []
    for requirement in row.bundle.get("requirements", []):
        clause = (requirement.get("source") or {}).get("clause") or ""
        if re.match(r"^[A-D]\d+$", clause):
            criteria.append({"code": clause, "title": requirement.get("title") or requirement.get("text", "")[:120]})
    mime = (file.content_type or "").split(";")[0].lower()
    draft = await ingest_ai.draft_metadata(content, mime, (file.filename or "file")[:255], criteria)
    return draft


@router.get("/audits/{audit_id}/files/{evidence_id}")
async def download_file(audit_id: uuid.UUID, evidence_id: uuid.UUID, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    await get_audit(audit_id, db, user)
    file = await db.scalar(select(HospitalityFile).where(HospitalityFile.audit_id == audit_id, HospitalityFile.evidence_id == str(evidence_id)))
    if file is None:
        raise HTTPException(404, "Evidence file not found.")
    return Response(content=file.content, media_type=file.content_type, headers={
        "Content-Disposition": "attachment; filename*=UTF-8''" + quote(file.file_name, safe=""),
        "X-Content-Type-Options": "nosniff", "Cache-Control": "private, no-store",
    })


@router.post("/audits/{audit_id}/assessments/suggest")
async def suggest_assessment(audit_id: uuid.UUID, payload: SuggestRequest, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    row = await get_audit(audit_id, db, user)
    require_role(user, WRITERS)
    check_version(row, payload.expected_version)
    requirement_id = str(payload.requirementId)
    requirement = next((r for r in row.bundle["requirements"] if r["id"] == requirement_id), None)
    if requirement is None or requirement.get("reviewStatus") != "approved":
        raise HTTPException(404, "Approved requirement not found in this audit.")
    if requirement_id not in row.bundle["audit"]["requirementIds"]:
        raise HTTPException(422, "Requirement is not in this audit's scope.")
    bundle = row.bundle
    warnings = []
    if payload.indicatorInputs:
        step = await run_engine("assessment.indicators", user, bundle, {
            "requirementId": requirement_id,
            "indicatorInputs": [item.model_dump(mode="json") for item in payload.indicatorInputs],
        })
        bundle = step["value"]
        warnings.extend(step.get("warnings") or [])
    assessment = next((a for a in bundle["assessments"] if a["requirementId"] == requirement_id), None)
    if assessment is None:
        raise HTTPException(404, "Assessment not found for this requirement.")
    updated_requirement = next(r for r in bundle["requirements"] if r["id"] == requirement_id)
    evidence_by_id = {e["id"]: e for e in bundle["evidence"]}
    facts = suggest_ai.build_facts(updated_requirement, assessment, evidence_by_id)
    suggestion = await suggest_ai.suggest_assessment(facts)
    result = await run_engine("assessment.suggestion", user, bundle, {
        "requirementId": requirement_id,
        "status": suggestion["status"],
        "rationale": suggestion["rationale"],
        "model": suggestion["model"],
    })
    warnings.extend(result.get("warnings") or [])
    await save_bundle(row, payload.expected_version, result["value"], db, user)
    return await detail(row, user, warnings)


@router.get("/audits/{audit_id}/report")
async def get_report(audit_id: uuid.UUID, format: str = "json", db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    row = await get_audit(audit_id, db, user)
    result = await run_engine("report", user, row.bundle)
    if format == "markdown":
        return Response(result["value"]["markdown"], media_type="text/markdown; charset=utf-8", headers={
            "Content-Disposition": f'attachment; filename="hotel-audit-{audit_id}.md"', "Cache-Control": "private, no-store",
        })
    if format != "json":
        raise HTTPException(422, "Report format must be json or markdown.")
    return result["value"]["report"]


def readiness_view(row):
    return {
        "report": readiness.build_readiness(row.bundle, row.report_profile, row.report_draft, row.version),
        "saved_profile": row.report_profile or {},
        "ai_configured": report_ai.configured(),
    }


@router.get("/audits/{audit_id}/readiness")
async def get_readiness(audit_id: uuid.UUID, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    return readiness_view(await get_audit(audit_id, db, user))


@router.put("/audits/{audit_id}/readiness/profile")
async def save_readiness_profile(audit_id: uuid.UUID, payload: ReadinessProfile, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    row = await get_audit(audit_id, db, user)
    require_role(user, WRITERS)
    row.report_profile = {k: v for k, v in payload.model_dump().items() if v}
    await db.flush()
    return readiness_view(row)


@router.post("/audits/{audit_id}/readiness/generate")
async def generate_readiness(audit_id: uuid.UUID, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    row = await get_audit(audit_id, db, user)
    require_role(user, WRITERS)
    profile = readiness.merge_profile(row.bundle, row.report_profile)
    narrative, model = await report_ai.draft_narrative(readiness.ai_facts(row.bundle, profile))
    row.report_draft = {"narrative": narrative, "model": model, "generated_at": readiness.now_iso(),
                        "generated_by": actor_for(user)["name"], "audit_version": row.version}
    # A regenerated narrative has not been reviewed yet.
    if row.report_profile and row.report_profile.get("reviewed_by"):
        row.report_profile = {k: v for k, v in row.report_profile.items() if k != "reviewed_by"}
    await db.flush()
    return readiness_view(row)


@router.get("/audits/{audit_id}/readiness/critique")
async def critique_readiness(audit_id: uuid.UUID, include_ai: bool = False, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    row = await get_audit(audit_id, db, user)
    report = readiness.build_readiness(row.bundle, row.report_profile, row.report_draft, row.version)
    return await report_critique.critique(report, include_ai=include_ai and report_ai.configured())


@router.get("/audits/{audit_id}/readiness/export")
async def export_readiness(audit_id: uuid.UUID, format: str = "docx", db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    row = await get_audit(audit_id, db, user)
    report = readiness.build_readiness(row.bundle, row.report_profile, row.report_draft, row.version)
    name = f"AXIS-readiness-review-{readiness.slug(report['hotel'])}"
    if format == "docx":
        return Response(readiness.render_docx(report), media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                        headers={"Content-Disposition": f'attachment; filename="{name}.docx"', "Cache-Control": "private, no-store"})
    if format == "markdown":
        return Response(readiness.render_markdown(report), media_type="text/markdown; charset=utf-8",
                        headers={"Content-Disposition": f'attachment; filename="{name}.md"', "Cache-Control": "private, no-store"})
    raise HTTPException(422, "Export format must be docx or markdown.")
