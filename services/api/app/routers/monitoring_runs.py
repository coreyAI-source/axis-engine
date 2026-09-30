from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..models.monitoring import MonitoringRun
from ..schemas.monitoring import MonitoringRunCreate, MonitoringRunUpdate, MonitoringRunOut
from ..utils.security import get_current_user

router = APIRouter(prefix="/monitoring-runs", tags=["monitoring"])


@router.get("/", response_model=list[MonitoringRunOut])
async def list_runs(
    task_id: UUID | None = None,
    status: str | None = None,
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_user),
):
    q = select(MonitoringRun)
    if task_id:
        q = q.where(MonitoringRun.monitoring_task_id == task_id)
    if status:
        q = q.where(MonitoringRun.status == status)
    result = await db.execute(q)
    return result.scalars().all()


@router.post("/", response_model=MonitoringRunOut, status_code=201)
async def create_run(payload: MonitoringRunCreate, db: AsyncSession = Depends(get_db), _=Depends(get_current_user)):
    obj = MonitoringRun(**payload.model_dump())
    db.add(obj)
    await db.flush()
    await db.refresh(obj)
    return obj


@router.get("/{run_id}", response_model=MonitoringRunOut)
async def get_run(run_id: UUID, db: AsyncSession = Depends(get_db), _=Depends(get_current_user)):
    obj = await db.get(MonitoringRun, run_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Monitoring run not found")
    return obj


@router.patch("/{run_id}", response_model=MonitoringRunOut)
async def update_run(run_id: UUID, payload: MonitoringRunUpdate, db: AsyncSession = Depends(get_db), current_user=Depends(get_current_user)):
    from datetime import datetime, timezone
    obj = await db.get(MonitoringRun, run_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Monitoring run not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(obj, field, value)
    if payload.status == "Completed":
        obj.completed_at = datetime.now(timezone.utc)
        obj.completed_by = current_user.id
    await db.flush()
    await db.refresh(obj)
    return obj
