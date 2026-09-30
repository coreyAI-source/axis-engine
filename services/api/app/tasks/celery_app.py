from celery import Celery
from celery.schedules import crontab

from ..config import settings

celery_app = Celery(
    "axis",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=["app.tasks.lag_monitor", "app.tasks.monitoring_scheduler"],
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
    beat_schedule={
        # Daily lag monitor at 07:00 UTC
        "lag-monitor-daily": {
            "task": "app.tasks.lag_monitor.run_lag_monitor",
            "schedule": crontab(hour=7, minute=0),
        },
        # Monitoring run generator — daily at 06:00 UTC
        "generate-monitoring-runs-daily": {
            "task": "app.tasks.monitoring_scheduler.generate_runs",
            "schedule": crontab(hour=6, minute=0),
        },
    },
)
