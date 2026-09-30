from uuid import UUID

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..models.evidence import Evidence
from ..schemas.evidence import EvidenceCreate, EvidenceOut
from ..utils.security import get_current_user
from ..utils import storage

router = APIRouter(prefix="/evidence", tags=["evidence"])


@router.get("/", response_model=list[EvidenceOut])
async def list_evidence(
    audit_id: UUID | None = None,
    prompt_id: UUID | None = None,
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_user),
):
    q = select(Evidence)
    if audit_id:
        q = q.where(Evidence.audit_id == audit_id)
    if prompt_id:
        q = q.where(Evidence.audit_prompt_id == prompt_id)
    result = await db.execute(q)
    return result.scalars().all()


@router.post("/", response_model=EvidenceOut, status_code=201)
async def create_evidence(
    payload: EvidenceCreate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    obj = Evidence(**payload.model_dump(), uploaded_by=current_user.id)
    db.add(obj)
    await db.flush()
    await db.refresh(obj)
    return obj


@router.post("/upload", response_model=EvidenceOut, status_code=201)
async def upload_evidence_file(
    file: UploadFile = File(...),
    audit_id: UUID | None = None,
    audit_prompt_id: UUID | None = None,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Upload a file and create an Evidence record."""
    content = await file.read()
    uri = storage.upload_file(content, file.filename, file.content_type or "application/octet-stream")
    obj = Evidence(
        audit_id=audit_id,
        audit_prompt_id=audit_prompt_id,
        evidence_type="File",
        file_uri=uri,
        uploaded_by=current_user.id,
    )
    db.add(obj)
    await db.flush()
    await db.refresh(obj)
    return obj


@router.get("/{evidence_id}", response_model=EvidenceOut)
async def get_evidence(evidence_id: UUID, db: AsyncSession = Depends(get_db), _=Depends(get_current_user)):
    obj = await db.get(Evidence, evidence_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Evidence not found")
    return obj


@router.get("/{evidence_id}/download-url")
async def get_download_url(evidence_id: UUID, db: AsyncSession = Depends(get_db), _=Depends(get_current_user)):
    obj = await db.get(Evidence, evidence_id)
    if not obj or not obj.file_uri:
        raise HTTPException(status_code=404, detail="Evidence file not found")
    url = storage.generate_presigned_url(obj.file_uri)
    return {"url": url}
