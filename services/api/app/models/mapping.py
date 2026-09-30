import enum
from datetime import datetime
from sqlalchemy import DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
import uuid

from .base import Base


class Applicability(str, enum.Enum):
    FULL = "Full"
    PARTIAL = "Partial"
    NOT_APPLICABLE = "NotApplicable"


class MappingType(str, enum.Enum):
    EQUIVALENT = "Equivalent"
    RELATED = "Related"
    SUPPORTING = "Supporting"


class ProcessClauseMap(Base):
    __tablename__ = "process_clause_maps"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    process_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("processes.id"), nullable=False)
    clause_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("clauses.id"), nullable=False)
    applicability: Mapped[str] = mapped_column(
        Enum("Full", "Partial", "NotApplicable", name="applicability_type", native_enum=False),
        nullable=False,
        default="Full"
    )
    rationale: Mapped[str | None] = mapped_column(Text)
    risk_modifier: Mapped[str | None] = mapped_column(String(20))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    process: Mapped["Process"] = relationship("Process", back_populates="clause_maps")
    clause: Mapped["Clause"] = relationship("Clause", back_populates="process_maps")


class ControlMapping(Base):
    __tablename__ = "control_mappings"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    process_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("processes.id"), nullable=False)
    source_standard_code: Mapped[str] = mapped_column(String(20), nullable=False)
    source_clause_number: Mapped[str] = mapped_column(String(20), nullable=False)
    target_standard_code: Mapped[str] = mapped_column(String(20), nullable=False)
    target_clause_number: Mapped[str] = mapped_column(String(20), nullable=False)
    mapping_type: Mapped[str] = mapped_column(
        Enum("Equivalent", "Related", "Supporting", name="mapping_type_enum", native_enum=False),
        nullable=False
    )
    notes: Mapped[str | None] = mapped_column(Text)

    process: Mapped["Process"] = relationship("Process")
