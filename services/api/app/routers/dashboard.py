from fastapi import APIRouter, Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..models.evidence import Action, Finding
from ..models.monitoring import MonitoringTask
from ..models.audit import Audit
from ..utils.security import get_current_user

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/summary")
async def dashboard_summary(db: AsyncSession = Depends(get_db), _=Depends(get_current_user)):
    # Overdue actions
    overdue_actions = await db.scalar(
        select(func.count()).select_from(Action).where(Action.status == "Overdue")
    )
    # At-risk actions
    at_risk_actions = await db.scalar(
        select(func.count()).select_from(Action).where(Action.lag_status == "AtRisk")
    )
    # Open actions
    open_actions = await db.scalar(
        select(func.count()).select_from(Action).where(Action.status.in_(["Open", "InProgress"]))
    )
    # Due monitoring tasks
    due_tasks = await db.scalar(
        select(func.count()).select_from(MonitoringTask).where(
            MonitoringTask.status.in_(["Due", "Overdue"]),
            MonitoringTask.active_flag == True,
        )
    )
    # Active audits
    active_audits = await db.scalar(
        select(func.count()).select_from(Audit).where(Audit.status == "InProgress")
    )
    # Findings by type
    findings_result = await db.execute(
        select(Finding.finding_type, func.count()).group_by(Finding.finding_type)
    )
    findings_by_type = {row[0]: row[1] for row in findings_result.all()}

    return {
        "overdue_actions": overdue_actions,
        "at_risk_actions": at_risk_actions,
        "open_actions": open_actions,
        "due_monitoring_tasks": due_tasks,
        "active_audits": active_audits,
        "findings_by_type": findings_by_type,
    }
