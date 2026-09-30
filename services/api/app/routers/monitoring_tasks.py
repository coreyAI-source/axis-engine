from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..models.monitoring import MonitoringTask
from ..schemas.monitoring import MonitoringTaskCreate, MonitoringTaskUpdate, MonitoringTaskOut
from ..utils.security import get_current_user
from ..services.monitoring import generate_next_run, create_follow_up_task, generate_tasks_from_process

router = APIRouter(prefix="/monitoring-tasks", tags=["monitoring"])


@router.get("/", response_model=list[MonitoringTaskOut])
async def list_tasks(
    status: str | None = None,
    organisation_id: UUID | None = None,
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_user),
):
    q = select(MonitoringTask).where(MonitoringTask.active_flag == True)
    if status:
        q = q.where(MonitoringTask.status == status)
    if organisation_id:
        q = q.where(MonitoringTask.organisation_id == organisation_id)
    result = await db.execute(q)
    return result.scalars().all()


@router.post("/", response_model=MonitoringTaskOut, status_code=201)
async def create_task(payload: MonitoringTaskCreate, db: AsyncSession = Depends(get_db), _=Depends(get_current_user)):
    obj = MonitoringTask(**payload.model_dump())
    db.add(obj)
    await db.flush()
    await db.refresh(obj)
    return obj


@router.get("/{task_id}", response_model=MonitoringTaskOut)
async def get_task(task_id: UUID, db: AsyncSession = Depends(get_db), _=Depends(get_current_user)):
    obj = await db.get(MonitoringTask, task_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Monitoring task not found")
    return obj


@router.patch("/{task_id}", response_model=MonitoringTaskOut)
async def update_task(task_id: UUID, payload: MonitoringTaskUpdate, db: AsyncSession = Depends(get_db), _=Depends(get_current_user)):
    obj = await db.get(MonitoringTask, task_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Monitoring task not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(obj, field, value)
    await db.flush()
    await db.refresh(obj)
    return obj


@router.delete("/{task_id}", status_code=204)
async def suspend_task(task_id: UUID, db: AsyncSession = Depends(get_db), _=Depends(get_current_user)):
    obj = await db.get(MonitoringTask, task_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Monitoring task not found")
    obj.active_flag = False
    obj.status = "Suspended"
    await db.flush()


@router.post("/{task_id}/generate-run", status_code=201)
async def generate_run(task_id: UUID, db: AsyncSession = Depends(get_db), _=Depends(get_current_user)):
    """Manually trigger generation of the next monitoring run for a task."""
    obj = await db.get(MonitoringTask, task_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Monitoring task not found")
    run = await generate_next_run(obj, db)
    return {"run_id": str(run.id), "due_date": str(run.due_date)}


@router.post("/generate-from-process/{process_id}", status_code=201)
async def generate_from_process(
    process_id: UUID,
    organisation_id: UUID,
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_user),
):
    """
    Generate monitoring tasks for a process from its clause mappings.
    Frequency is set automatically from risk level using the risk-frequency rules.
    Skips tasks that already exist for a given process+clause combination.
    """
    from ..models.process import Process
    process = await db.get(Process, process_id)
    if not process:
        raise HTTPException(status_code=404, detail="Process not found")

    count = await generate_tasks_from_process(process_id, organisation_id, db)
    return {"tasks_created": count, "process_id": str(process_id)}
