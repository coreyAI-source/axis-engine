import enum
from datetime import datetime
from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
import uuid

from .base import Base


class ProcessCategory(str, enum.Enum):
    MANAGEMENT = "Management"
    OPERATIONAL = "Operational"
    SUPPORT = "Support"
    PROJECT = "Project"
    CORPORATE = "Corporate"


class Process(Base):
    __tablename__ = "processes"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organisation_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("organisations.id"), nullable=False)
    code: Mapped[str] = mapped_column(String(50), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    category: Mapped[str] = mapped_column(
        Enum("Management", "Operational", "Support", "Project", "Corporate", name="process_category", native_enum=False),
        nullable=False
    )
    description: Mapped[str | None] = mapped_column(Text)
    owner_role_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("roles.id"))
    site_scope: Mapped[str | None] = mapped_column(String(255))
    active_flag: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    organisation: Mapped["Organisation"] = relationship("Organisation", back_populates="processes")
    owner_role: Mapped["Role | None"] = relationship("Role")
    clause_maps: Mapped[list["ProcessClauseMap"]] = relationship("ProcessClauseMap", back_populates="process")
    monitoring_tasks: Mapped[list["MonitoringTask"]] = relationship("MonitoringTask", back_populates="process")
