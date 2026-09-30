from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..models.evidence import Finding, Action
from ..schemas.evidence import FindingCreate, FindingUpdate, FindingOut, ActionOut
from ..utils.security import get_current_user
from ..services.audit import create_action_for_finding

router = APIRouter(prefix="/findings", tags=["findings"])


@router.get("/", response_model=list[FindingOut])
async def list_findings(
    audit_id: UUID | None = None,
    finding_type: str | None = None,
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_user),
):
    q = select(Finding)
    if audit_id:
        q = q.where(Finding.audit_id == audit_id)
    if finding_type:
        q = q.where(Finding.finding_type == finding_type)
    result = await db.execute(q)
    return result.scalars().all()


@router.post("/", response_model=FindingOut, status_code=201)
async def create_finding(
    payload: FindingCreate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    obj = Finding(**payload.model_dump(), created_by=current_user.id)
    db.add(obj)
    await db.flush()
    await db.refresh(obj)
    # Auto-create action for NC findings
    if obj.finding_type in ("MajorNC", "MinorNC", "CriticalDocumentReviewFinding"):
        await create_action_for_finding(obj, db)
    return obj


@router.get("/{finding_id}", response_model=FindingOut)
async def get_finding(finding_id: UUID, db: AsyncSession = Depends(get_db), _=Depends(get_current_user)):
    obj = await db.get(Finding, finding_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Finding not found")
    return obj


@router.patch("/{finding_id}", response_model=FindingOut)
async def update_finding(finding_id: UUID, payload: FindingUpdate, db: AsyncSession = Depends(get_db), _=Depends(get_current_user)):
    obj = await db.get(Finding, finding_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Finding not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(obj, field, value)
    await db.flush()
    await db.refresh(obj)
    return obj


@router.get("/{finding_id}/actions", response_model=list[ActionOut])
async def list_finding_actions(finding_id: UUID, db: AsyncSession = Depends(get_db), _=Depends(get_current_user)):
    result = await db.execute(select(Action).where(Action.finding_id == finding_id))
    return result.scalars().all()
