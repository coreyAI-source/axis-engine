from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..models.evidence import Action, ActionComment
from ..schemas.evidence import ActionCreate, ActionUpdate, ActionOut, ActionCommentCreate, ActionCommentOut
from ..utils.security import get_current_user

router = APIRouter(prefix="/actions", tags=["actions"])


@router.get("/", response_model=list[ActionOut])
async def list_actions(
    status: str | None = None,
    lag_status: str | None = None,
    assigned_to_user_id: UUID | None = None,
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_user),
):
    q = select(Action)
    if status:
        q = q.where(Action.status == status)
    if lag_status:
        q = q.where(Action.lag_status == lag_status)
    if assigned_to_user_id:
        q = q.where(Action.assigned_to_user_id == assigned_to_user_id)
    result = await db.execute(q)
    return result.scalars().all()


@router.post("/", response_model=ActionOut, status_code=201)
async def create_action(payload: ActionCreate, db: AsyncSession = Depends(get_db), _=Depends(get_current_user)):
    obj = Action(**payload.model_dump())
    db.add(obj)
    await db.flush()
    await db.refresh(obj)
    return obj


@router.get("/overdue", response_model=list[ActionOut])
async def list_overdue(db: AsyncSession = Depends(get_db), _=Depends(get_current_user)):
    result = await db.execute(select(Action).where(Action.status == "Overdue"))
    return result.scalars().all()


@router.get("/at-risk", response_model=list[ActionOut])
async def list_at_risk(db: AsyncSession = Depends(get_db), _=Depends(get_current_user)):
    result = await db.execute(select(Action).where(Action.lag_status == "AtRisk"))
    return result.scalars().all()


@router.get("/{action_id}", response_model=ActionOut)
async def get_action(action_id: UUID, db: AsyncSession = Depends(get_db), _=Depends(get_current_user)):
    obj = await db.get(Action, action_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Action not found")
    return obj


@router.patch("/{action_id}", response_model=ActionOut)
async def update_action(
    action_id: UUID,
    payload: ActionUpdate,
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_user),
):
    obj = await db.get(Action, action_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Action not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(obj, field, value)
    obj.last_activity_at = datetime.now(timezone.utc)
    if payload.status == "Closed":
        obj.closed_at = datetime.now(timezone.utc)
    await db.flush()
    await db.refresh(obj)
    return obj


@router.post("/{action_id}/comments", response_model=ActionCommentOut, status_code=201)
async def add_comment(
    action_id: UUID,
    payload: ActionCommentCreate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    obj = await db.get(Action, action_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Action not found")
    comment = ActionComment(action_id=action_id, comment_text=payload.comment_text, created_by=current_user.id)
    db.add(comment)
    obj.last_activity_at = datetime.now(timezone.utc)
    await db.flush()
    await db.refresh(comment)
    return comment


@router.get("/{action_id}/comments", response_model=list[ActionCommentOut])
async def list_comments(action_id: UUID, db: AsyncSession = Depends(get_db), _=Depends(get_current_user)):
    result = await db.execute(select(ActionComment).where(ActionComment.action_id == action_id))
    return result.scalars().all()
