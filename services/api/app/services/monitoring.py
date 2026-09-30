"""
Monitoring engine service layer.

Core functions:
- generate_next_run: create a MonitoringRun from an active task
- calculate_next_due_date: advance next_due_date by interval_months
- generate_recurring_monitoring_runs: batch generator for all due tasks
- create_follow_up_task: create a new task from a finding
"""
from datetime import date, datetime, timezone
from dateutil.relativedelta import relativedelta
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.monitoring import MonitoringTask, MonitoringRun, RiskFrequencyRule
from ..models.mapping import ProcessClauseMap
from ..models.standard import Clause
from ..models.evidence import Finding


def calculate_next_due_date(from_date: date, interval_months: int) -> date:
    return from_date + relativedelta(months=interval_months)


async def generate_next_run(task: MonitoringTask, db: AsyncSession) -> MonitoringRun:
    today = date.today()
    due = task.next_due_date or today
    run = MonitoringRun(
        monitoring_task_id=task.id,
        run_date=today,
        due_date=due,
        status="Open",
    )
    db.add(run)
    # Advance next_due_date
    task.next_due_date = calculate_next_due_date(due, task.interval_months)
    await db.flush()
    await db.refresh(run)
    return run


async def generate_recurring_monitoring_runs(db: AsyncSession) -> int:
    """
    Called by Celery scheduler.
    Creates runs for all active tasks whose next_due_date <= today.
    Returns number of runs created.
    """
    today = date.today()
    result = await db.execute(
        select(MonitoringTask).where(
            MonitoringTask.active_flag == True,
            MonitoringTask.status.in_(["Scheduled", "Due", "Overdue"]),
            MonitoringTask.next_due_date <= today,
        )
    )
    tasks = result.scalars().all()
    count = 0
    for task in tasks:
        await generate_next_run(task, db)
        count += 1
    await db.commit()
    return count


async def mark_overdue_tasks(db: AsyncSession) -> int:
    """Mark tasks overdue if next_due_date < today and still Scheduled/Due."""
    today = date.today()
    result = await db.execute(
        select(MonitoringTask).where(
            MonitoringTask.active_flag == True,
            MonitoringTask.status.in_(["Scheduled", "Due"]),
            MonitoringTask.next_due_date < today,
        )
    )
    tasks = result.scalars().all()
    for task in tasks:
        task.status = "Overdue"
    await db.commit()
    return len(tasks)


async def generate_tasks_from_process(
    process_id,
    organisation_id,
    db: AsyncSession,
    method_id=None,
) -> int:
    """
    Generate MonitoringTask records for a process from its clause mappings.

    For each ProcessClauseMap:
    - Derives risk level from risk_modifier on the map
    - Looks up the matching RiskFrequencyRule
    - Creates a MonitoringTask if one doesn't already exist for that process+clause
    - Sets next_due_date to today + interval_months

    Returns count of tasks created.
    """
    today = date.today()

    # Load all active mappings for this process
    maps_result = await db.execute(
        select(ProcessClauseMap).where(
            ProcessClauseMap.process_id == process_id,
            ProcessClauseMap.applicability.in_(["Full", "Partial"]),
        )
    )
    maps = maps_result.scalars().all()

    # Load all frequency rules into a dict for quick lookup
    rules_result = await db.execute(select(RiskFrequencyRule))
    rules = {r.risk_level: r for r in rules_result.scalars().all()}

    created = 0

    for pcm in maps:
        # Skip if task already exists for this process+clause
        existing_result = await db.execute(
            select(MonitoringTask).where(
                MonitoringTask.process_id == process_id,
                MonitoringTask.clause_id == pcm.clause_id,
                MonitoringTask.active_flag == True,
            )
        )
        if existing_result.scalar_one_or_none():
            continue

        # Determine risk level — use map's risk_modifier, default Medium
        risk_level = pcm.risk_modifier or "Medium"
        rule = rules.get(risk_level) or rules.get("Medium")

        # Load clause for title
        clause = await db.get(Clause, pcm.clause_id)
        if not clause:
            continue

        task = MonitoringTask(
            organisation_id=organisation_id,
            process_id=process_id,
            clause_id=pcm.clause_id,
            title=f"Monitor: {clause.clause_number} {clause.clause_title}",
            description=pcm.rationale,
            risk_level=risk_level,
            importance_level=_risk_to_importance(risk_level),
            frequency_code=rule.frequency_code,
            interval_months=rule.interval_months,
            method_id=method_id,
            next_due_date=calculate_next_due_date(today, rule.interval_months),
            status="Scheduled",
            active_flag=True,
        )
        db.add(task)
        created += 1

    await db.flush()
    return created


def _risk_to_importance(risk_level: str) -> str:
    return {
        "Extreme": "Critical",
        "High": "High",
        "Medium": "Moderate",
        "Low": "Low",
    }.get(risk_level, "Moderate")


async def create_follow_up_task(
    finding: Finding,
    interval_months: int,
    db: AsyncSession,
    organisation_id=None,
) -> MonitoringTask:
    """Create a follow-up monitoring task from a finding."""
    due = calculate_next_due_date(date.today(), interval_months)
    task = MonitoringTask(
        organisation_id=organisation_id or finding.audit.organisation_id if finding.audit else None,
        process_id=finding.process_id,
        clause_id=finding.clause_id,
        title=f"Follow-up: {finding.title}",
        description=f"Follow-up monitoring task generated from finding {finding.finding_code}.",
        risk_level="High",
        importance_level="High",
        frequency_code="Annual",
        interval_months=12,
        next_due_date=due,
        status="Scheduled",
        active_flag=True,
    )
    db.add(task)
    await db.flush()
    await db.refresh(task)
    return task
