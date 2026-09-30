"""Celery task: generate recurring monitoring runs and mark overdue tasks."""
from .celery_app import celery_app
from ..database import SyncSessionLocal
from ..models.monitoring import MonitoringTask, MonitoringRun
from ..services.monitoring import calculate_next_due_date
from datetime import date
from sqlalchemy import select


@celery_app.task(name="app.tasks.monitoring_scheduler.generate_runs")
def generate_runs():
    with SyncSessionLocal() as db:
        today = date.today()

        # Mark overdue
        overdue_result = db.execute(
            select(MonitoringTask).where(
                MonitoringTask.active_flag == True,
                MonitoringTask.status.in_(["Scheduled", "Due"]),
                MonitoringTask.next_due_date < today,
            )
        )
        overdue_tasks = overdue_result.scalars().all()
        for task in overdue_tasks:
            task.status = "Overdue"

        # Generate runs for tasks due today or past due
        due_result = db.execute(
            select(MonitoringTask).where(
                MonitoringTask.active_flag == True,
                MonitoringTask.status.in_(["Scheduled", "Due", "Overdue"]),
                MonitoringTask.next_due_date <= today,
            )
        )
        due_tasks = due_result.scalars().all()
        created = 0
        for task in due_tasks:
            run = MonitoringRun(
                monitoring_task_id=task.id,
                run_date=today,
                due_date=task.next_due_date or today,
                status="Open",
            )
            db.add(run)
            task.next_due_date = calculate_next_due_date(task.next_due_date or today, task.interval_months)
            created += 1

        db.commit()
        return {"runs_created": created, "tasks_marked_overdue": len(overdue_tasks)}
