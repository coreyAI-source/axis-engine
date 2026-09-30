"""Dashboard regressions, including PostgreSQL bindings for migrated text columns."""
import pytest
from sqlalchemy import Enum, select
from sqlalchemy.dialects.postgresql import asyncpg

from app.models.base import Base
from app.models.evidence import Action
from app.routers.dashboard import dashboard_summary


def test_status_queries_bind_as_text_on_postgresql():
    # Migration 0001 uses VARCHAR for these choices. Native enum casts produce
    # PostgreSQL error 42883 (varchar = enum), which SQLite cannot reproduce.
    dialect = asyncpg.dialect()
    checked = 0
    for table in Base.metadata.sorted_tables:
        for column in table.columns:
            if isinstance(column.type, Enum):
                query = select(column).where(column == column.type.enums[0])
                sql = str(query.compile(dialect=dialect))
                # An uncast parameter lets PostgreSQL infer VARCHAR as well.
                assert f"::{column.type.name}" not in sql, f"{table.name}.{column.name}: {sql}"
                checked += 1
    assert checked > 0


@pytest.mark.asyncio
async def test_dashboard_counts_actions_and_handles_empty_sections(db_session):
    db_session.add_all([
        Action(title="Overdue", status="Overdue", lag_status="Overdue"),
        Action(title="At risk", status="InProgress", lag_status="AtRisk"),
        Action(title="Open", status="Open", lag_status="OnTrack"),
        Action(title="Closed", status="Closed", lag_status="OnTrack"),
    ])
    await db_session.flush()

    summary = await dashboard_summary(db=db_session, _=None)

    assert summary == {
        "overdue_actions": 1,
        "at_risk_actions": 1,
        "open_actions": 2,
        "due_monitoring_tasks": 0,
        "active_audits": 0,
        "findings_by_type": {},
    }
