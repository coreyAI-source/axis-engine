import enum
from datetime import datetime, date
from sqlalchemy import Boolean, Date, DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
import uuid

from .base import Base


class AuditType(str, enum.Enum):
    INTERNAL = "Internal"
    EXTERNAL = "External"
    SURVEILLANCE = "Surveillance"
    CERTIFICATION = "Certification"
    FOLLOW_UP = "FollowUp"


class AuditStage(str, enum.Enum):
    DOCUMENT_REVIEW = "DocumentReview"
    SITE_AUDIT = "SiteAudit"
    FOLLOW_UP = "FollowUp"


class AuditStatus(str, enum.Enum):
    PLANNED = "Planned"
    IN_PROGRESS = "InProgress"
    COMPLETED = "Completed"
    CANCELLED = "Cancelled"


class PromptType(str, enum.Enum):
    DOCUMENT_CHECK = "DocumentCheck"
    INTERVIEW = "Interview"
    OBSERVATION = "Observation"
    RECORD_REVIEW = "RecordReview"
    PHOTO_EVIDENCE = "PhotoEvidence"


class ResponseStatus(str, enum.Enum):
    PENDING = "Pending"
    C = "C"
    NC = "NC"
    OBS = "OBS"
    FUP = "FUP"
    TBA = "TBA"
    NA = "NA"


class Audit(Base):
    __tablename__ = "audits"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organisation_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("organisations.id"), nullable=False)
    site_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("sites.id"))
    audit_type: Mapped[str] = mapped_column(
        Enum("Internal", "External", "Surveillance", "Certification", "FollowUp", name="audit_type_enum", native_enum=False),
        nullable=False
    )
    audit_stage: Mapped[str] = mapped_column(
        Enum("DocumentReview", "SiteAudit", "FollowUp", name="audit_stage_enum", native_enum=False),
        nullable=False,
        default="DocumentReview"
    )
    status: Mapped[str] = mapped_column(
        Enum("Planned", "InProgress", "Completed", "Cancelled", name="audit_status_enum", native_enum=False),
        nullable=False,
        default="Planned"
    )
    auditee_name: Mapped[str | None] = mapped_column(String(255))
    audit_client: Mapped[str | None] = mapped_column(String(255))
    audit_body: Mapped[str | None] = mapped_column(String(255))
    lead_auditor_user_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    objective: Mapped[str | None] = mapped_column(Text)
    scope: Mapped[str | None] = mapped_column(Text)
    criteria_text: Mapped[str | None] = mapped_column(Text)
    start_date: Mapped[date | None] = mapped_column(Date)
    end_date: Mapped[date | None] = mapped_column(Date)
    duration_days: Mapped[int | None] = mapped_column(Integer)
    main_location: Mapped[str | None] = mapped_column(String(255))
    auditee_contact: Mapped[str | None] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    organisation: Mapped["Organisation"] = relationship("Organisation")
    site: Mapped["Site | None"] = relationship("Site")
    lead_auditor: Mapped["User | None"] = relationship("User")
    team_members: Mapped[list["AuditTeamMember"]] = relationship("AuditTeamMember", back_populates="audit")
    locations: Mapped[list["AuditLocation"]] = relationship("AuditLocation", back_populates="audit")
    audit_processes: Mapped[list["AuditProcess"]] = relationship("AuditProcess", back_populates="audit")
    prompts: Mapped[list["AuditPrompt"]] = relationship("AuditPrompt", back_populates="audit")
    findings: Mapped[list["Finding"]] = relationship("Finding", back_populates="audit")
    evidence: Mapped[list["Evidence"]] = relationship("Evidence", back_populates="audit")


class AuditTeamMember(Base):
    __tablename__ = "audit_team_members"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    audit_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("audits.id"), nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    role_in_audit: Mapped[str | None] = mapped_column(String(100))

    audit: Mapped["Audit"] = relationship("Audit", back_populates="team_members")
    user: Mapped["User"] = relationship("User")


class AuditLocation(Base):
    __tablename__ = "audit_locations"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    audit_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("audits.id"), nullable=False)
    site_name: Mapped[str] = mapped_column(String(255), nullable=False)
    is_main_location: Mapped[bool] = mapped_column(Boolean, default=False)
    confirmed_flag: Mapped[bool] = mapped_column(Boolean, default=False)

    audit: Mapped["Audit"] = relationship("Audit", back_populates="locations")


class AuditProcess(Base):
    __tablename__ = "audit_processes"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    audit_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("audits.id"), nullable=False)
    process_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("processes.id"), nullable=False)

    audit: Mapped["Audit"] = relationship("Audit", back_populates="audit_processes")
    process: Mapped["Process"] = relationship("Process")


class AuditPrompt(Base):
    __tablename__ = "audit_prompts"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    audit_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("audits.id"), nullable=False)
    process_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("processes.id"))
    clause_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("clauses.id"))
    prompt_text: Mapped[str] = mapped_column(Text, nullable=False)
    prompt_type: Mapped[str] = mapped_column(
        Enum("DocumentCheck", "Interview", "Observation", "RecordReview", "PhotoEvidence", name="prompt_type_enum", native_enum=False),
        nullable=False,
        default="DocumentCheck"
    )
    evidence_required: Mapped[bool] = mapped_column(Boolean, default=False)
    sequence_no: Mapped[int | None] = mapped_column(Integer)
    response_status: Mapped[str] = mapped_column(
        Enum("Pending", "C", "NC", "OBS", "FUP", "TBA", "NA", name="response_status_enum", native_enum=False),
        nullable=False,
        default="Pending"
    )
    comments: Mapped[str | None] = mapped_column(Text)
    responded_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    responded_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))

    audit: Mapped["Audit"] = relationship("Audit", back_populates="prompts")
    process: Mapped["Process | None"] = relationship("Process")
    clause: Mapped["Clause | None"] = relationship("Clause")
    responded_by_user: Mapped["User | None"] = relationship("User")
    evidence: Mapped[list["Evidence"]] = relationship("Evidence", back_populates="audit_prompt")
