from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..database import get_db
from ..models.process import Process
from ..models.mapping import ProcessClauseMap
from ..models.monitoring import MonitoringTask
from ..models.standard import Clause
from ..models.standard import Standard
from ..schemas.process import ProcessCreate, ProcessUpdate, ProcessOut
from ..schemas.mapping import ProcessClauseMapOut
from ..utils.security import get_current_user
from ..utils.scoring import score_to_colour

router = APIRouter(prefix="/processes", tags=["processes"])


@router.get("/", response_model=list[ProcessOut])
async def list_processes(db: AsyncSession = Depends(get_db), _=Depends(get_current_user)):
    result = await db.execute(select(Process).where(Process.active_flag == True))
    return result.scalars().all()


@router.post("/", response_model=ProcessOut, status_code=201)
async def create_process(payload: ProcessCreate, db: AsyncSession = Depends(get_db), _=Depends(get_current_user)):
    obj = Process(**payload.model_dump())
    db.add(obj)
    await db.flush()
    await db.refresh(obj)
    return obj


@router.get("/{process_id}", response_model=ProcessOut)
async def get_process(process_id: UUID, db: AsyncSession = Depends(get_db), _=Depends(get_current_user)):
    obj = await db.get(Process, process_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Process not found")
    return obj


@router.patch("/{process_id}", response_model=ProcessOut)
async def update_process(process_id: UUID, payload: ProcessUpdate, db: AsyncSession = Depends(get_db), _=Depends(get_current_user)):
    obj = await db.get(Process, process_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Process not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(obj, field, value)
    await db.flush()
    await db.refresh(obj)
    return obj


@router.delete("/{process_id}", status_code=204)
async def delete_process(process_id: UUID, db: AsyncSession = Depends(get_db), _=Depends(get_current_user)):
    obj = await db.get(Process, process_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Process not found")
    obj.active_flag = False
    await db.flush()


@router.get("/{process_id}/clause-maps", response_model=list[ProcessClauseMapOut])
async def get_process_clause_maps(process_id: UUID, db: AsyncSession = Depends(get_db), _=Depends(get_current_user)):
    result = await db.execute(
        select(ProcessClauseMap).where(ProcessClauseMap.process_id == process_id)
    )
    return result.scalars().all()


@router.get("/{process_id}/compliance-summary")
async def get_compliance_summary(process_id: UUID, db: AsyncSession = Depends(get_db), _=Depends(get_current_user)):
    """
    Returns a full compliance picture for a process:
    - Process details
    - All clause mappings with clause info and standard
    - All monitoring tasks with status and next due date
    - Risk profile summary
    """
    process = await db.get(Process, process_id)
    if not process:
        raise HTTPException(status_code=404, detail="Process not found")

    # Clause mappings
    maps_result = await db.execute(
        select(ProcessClauseMap).where(ProcessClauseMap.process_id == process_id)
    )
    maps = maps_result.scalars().all()

    clause_summaries = []
    for m in maps:
        clause = await db.get(Clause, m.clause_id)
        if not clause:
            continue
        standard = await db.get(Standard, clause.standard_id)
        clause_summaries.append({
            "mapping_id": str(m.id),
            "applicability": m.applicability,
            "risk_level": m.risk_modifier,
            "standard": standard.code if standard else None,
            "clause_number": clause.clause_number,
            "clause_title": clause.clause_title,
            "hls_section": clause.hls_section,
            "requires_documented_information": clause.requires_documented_information,
            "requires_retained_evidence": clause.requires_retained_evidence,
            "evidence_guidance": clause.evidence_guidance,
        })

    # Monitoring tasks
    tasks_result = await db.execute(
        select(MonitoringTask).where(
            MonitoringTask.process_id == process_id,
            MonitoringTask.active_flag == True,
        )
    )
    tasks = tasks_result.scalars().all()

    task_summaries = []
    for t in tasks:
        task_summaries.append({
            "task_id": str(t.id),
            "title": t.title,
            "risk_level": t.risk_level,
            "importance_level": t.importance_level,
            "frequency_code": t.frequency_code,
            "status": t.status,
            "next_due_date": t.next_due_date.isoformat() if t.next_due_date else None,
            "last_completed_date": t.last_completed_date.isoformat() if t.last_completed_date else None,
        })

    # Risk profile
    risk_counts = {"Extreme": 0, "High": 0, "Medium": 0, "Low": 0}
    for m in maps:
        level = m.risk_modifier or "Medium"
        if level in risk_counts:
            risk_counts[level] += 1

    overdue_tasks = sum(1 for t in tasks if t.status == "Overdue")
    due_tasks = sum(1 for t in tasks if t.status in ("Due", "Overdue"))

    return {
        "process": {
            "id": str(process.id),
            "code": process.code,
            "name": process.name,
            "category": process.category,
            "description": process.description,
        },
        "clause_mappings": clause_summaries,
        "monitoring_tasks": task_summaries,
        "risk_profile": {
            "counts_by_level": risk_counts,
            "total_mappings": len(maps),
            "total_tasks": len(tasks),
            "overdue_tasks": overdue_tasks,
            "due_tasks": due_tasks,
            "highest_risk": next(
                (r for r in ["Extreme", "High", "Medium", "Low"] if risk_counts[r] > 0),
                "None"
            ),
        },
    }
