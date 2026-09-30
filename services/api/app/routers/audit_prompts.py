from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..models.audit import AuditPrompt
from ..schemas.audit import AuditPromptCreate, AuditPromptUpdate, AuditPromptOut
from ..utils.security import get_current_user
from ..services.audit import handle_prompt_response

router = APIRouter(prefix="/audit-prompts", tags=["audit-prompts"])


@router.get("/", response_model=list[AuditPromptOut])
async def list_prompts(
    audit_id: UUID | None = None,
    response_status: str | None = None,
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_user),
):
    q = select(AuditPrompt)
    if audit_id:
        q = q.where(AuditPrompt.audit_id == audit_id)
    if response_status:
        q = q.where(AuditPrompt.response_status == response_status)
    result = await db.execute(q)
    return result.scalars().all()


@router.post("/", response_model=AuditPromptOut, status_code=201)
async def create_prompt(payload: AuditPromptCreate, db: AsyncSession = Depends(get_db), _=Depends(get_current_user)):
    obj = AuditPrompt(**payload.model_dump())
    db.add(obj)
    await db.flush()
    await db.refresh(obj)
    return obj


@router.get("/{prompt_id}", response_model=AuditPromptOut)
async def get_prompt(prompt_id: UUID, db: AsyncSession = Depends(get_db), _=Depends(get_current_user)):
    obj = await db.get(AuditPrompt, prompt_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Audit prompt not found")
    return obj


@router.patch("/{prompt_id}/respond", response_model=AuditPromptOut)
async def respond_to_prompt(
    prompt_id: UUID,
    payload: AuditPromptUpdate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Record a response against an audit prompt.
    NC status auto-creates a finding + action.
    OBS may create an optional action.
    FUP creates a follow-up item.
    TBA flags incomplete review.
    """
    obj = await db.get(AuditPrompt, prompt_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Audit prompt not found")

    obj.response_status = payload.response_status or obj.response_status
    obj.comments = payload.comments or obj.comments
    obj.responded_at = datetime.now(timezone.utc)
    obj.responded_by = current_user.id

    await handle_prompt_response(obj, current_user, db)

    await db.flush()
    await db.refresh(obj)
    return obj


@router.post("/generate", status_code=201)
async def generate_prompts_for_audit(
    audit_id: UUID,
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_user),
):
    """Generate audit prompts from process-clause mappings for this audit."""
    from ..services.audit import generate_audit_prompts
    count = await generate_audit_prompts(audit_id, db)
    return {"generated": count}
