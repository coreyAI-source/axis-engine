import enum
from datetime import datetime, date
from sqlalchemy import Boolean, Date, DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
import uuid

from .base import Base


class RiskLevel(str, enum.Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    EXTREME = "Extreme"


class FrequencyCode(str, enum.Enum):
    ANNUAL = "Annual"
    BIANNUAL = "Biannual"
    QUARTERLY = "Quarterly"
    MONTHLY = "Monthly"


class ImportanceLevel(str, enum.Enum):
    LOW = "Low"
    MODERATE = "Moderate"
    HIGH = "High"
    CRITICAL = "Critical"


class MonitoringTaskStatus(str, enum.Enum):
    SCHEDULED = "Scheduled"
    DUE = "Due"
    COMPLETED = "Completed"
    OVERDUE = "Overdue"
    SUSPENDED = "Suspended"


class MonitoringRunStatus(str, enum.Enum):
    OPEN = "Open"
    COMPLETED = "Completed"
    OVERDUE = "Overdue"
    CANCELLED = "Cancelled"


class RiskFrequencyRule(Base):
    __tablename__ = "risk_frequency_rules"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    risk_level: Mapped[str] = mapped_column(
        Enum("Low", "Medium", "High", "Extreme", name="risk_level_enum", native_enum=False),
        nullable=False,
        unique=True
    )
    frequency_code: Mapped[str] = mapped_column(
        Enum("Annual", "Biannual", "Quarterly", "Monthly", name="frequency_code_enum", native_enum=False),
        nullable=False
    )
    interval_months: Mapped[int] = mapped_column(Integer, nullable=False)


class MonitoringMethod(Base):
    __tablename__ = "monitoring_methods"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)

    tasks: Mapped[list["MonitoringTask"]] = relationship("MonitoringTask", back_populates="method")


class MonitoringTask(Base):
    __tablename__ = "monitoring_tasks"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organisation_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("organisations.id"), nullable=False)
    site_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("sites.id"))
    process_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("processes.id"))
    clause_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("clauses.id"))
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    owner_user_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    owner_role_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("roles.id"))
    risk_level: Mapped[str] = mapped_column(
        Enum("Low", "Medium", "High", "Extreme", name="monitoring_risk_level_enum", native_enum=False),
        nullable=False,
        default="Medium"
    )
    importance_level: Mapped[str] = mapped_column(
        Enum("Low", "Moderate", "High", "Critical", name="importance_level_enum", native_enum=False),
        nullable=False,
        default="Moderate"
    )
    frequency_code: Mapped[str] = mapped_column(
        Enum("Annual", "Biannual", "Quarterly", "Monthly", name="monitoring_frequency_enum", native_enum=False),
        nullable=False
    )
    interval_months: Mapped[int] = mapped_column(Integer, nullable=False)
    method_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("monitoring_methods.id"))
    next_due_date: Mapped[date | None] = mapped_column(Date)
    last_completed_date: Mapped[date | None] = mapped_column(Date)
    status: Mapped[str] = mapped_column(
        Enum("Scheduled", "Due", "Completed", "Overdue", "Suspended", name="monitoring_task_status_enum", native_enum=False),
        nullable=False,
        default="Scheduled"
    )
    active_flag: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    organisation: Mapped["Organisation"] = relationship("Organisation")
    site: Mapped["Site | None"] = relationship("Site")
    process: Mapped["Process | None"] = relationship("Process", back_populates="monitoring_tasks")
    clause: Mapped["Clause | None"] = relationship("Clause")
    owner_user: Mapped["User | None"] = relationship("User")
    owner_role: Mapped["Role | None"] = relationship("Role")
    method: Mapped["MonitoringMethod | None"] = relationship("MonitoringMethod", back_populates="tasks")
    runs: Mapped[list["MonitoringRun"]] = relationship("MonitoringRun", back_populates="task")


class MonitoringRun(Base):
    __tablename__ = "monitoring_runs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    monitoring_task_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("monitoring_tasks.id"), nullable=False)
    run_date: Mapped[date] = mapped_column(Date, nullable=False)
    due_date: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[str] = mapped_column(
        Enum("Open", "Completed", "Overdue", "Cancelled", name="monitoring_run_status_enum", native_enum=False),
        nullable=False,
        default="Open"
    )
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    completed_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    summary_notes: Mapped[str | None] = mapped_column(Text)

    task: Mapped["MonitoringTask"] = relationship("MonitoringTask", back_populates="runs")
    completed_by_user: Mapped["User | None"] = relationship("User")
