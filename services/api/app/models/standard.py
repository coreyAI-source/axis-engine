import enum
from sqlalchemy import Boolean, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
import uuid

from .base import Base


class StandardCode(str, enum.Enum):
    ISO9001 = "ISO9001"
    ISO14001 = "ISO14001"
    ISO45001 = "ISO45001"


class HLSSection(str, enum.Enum):
    CONTEXT = "Context"
    LEADERSHIP = "Leadership"
    PLANNING = "Planning"
    SUPPORT = "Support"
    OPERATION = "Operation"
    PERFORMANCE_EVALUATION = "PerformanceEvaluation"
    IMPROVEMENT = "Improvement"


class Standard(Base):
    __tablename__ = "standards"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        unique=True
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    version: Mapped[str] = mapped_column(String(20), nullable=False)

    clauses: Mapped[list["Clause"]] = relationship("Clause", back_populates="standard")


class Clause(Base):
    __tablename__ = "clauses"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    standard_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("standards.id"), nullable=False)
    clause_number: Mapped[str] = mapped_column(String(20), nullable=False)
    clause_title: Mapped[str] = mapped_column(String(255), nullable=False)
    parent_clause_number: Mapped[str | None] = mapped_column(String(20))
    requirement_text: Mapped[str | None] = mapped_column(Text)
    hls_section: Mapped[str] = mapped_column(
        String(30),
        nullable=False
    )
    requires_documented_information: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    requires_retained_evidence: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    evidence_guidance: Mapped[str | None] = mapped_column(Text)
    active_flag: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    standard: Mapped["Standard"] = relationship("Standard", back_populates="clauses")
    process_maps: Mapped[list["ProcessClauseMap"]] = relationship("ProcessClauseMap", back_populates="clause")
