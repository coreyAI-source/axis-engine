import enum
from datetime import datetime, date
from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
import uuid

from .base import Base


class EvidenceType(str, enum.Enum):
    PHOTO = "Photo"
    DOCUMENT = "Document"
    NOTE = "Note"
    FILE = "File"


class FindingType(str, enum.Enum):
    MAJOR_NC = "MajorNC"
    MINOR_NC = "MinorNC"
    OBSERVATION = "Observation"
    POSITIVE = "Positive"
    CRITICAL_DOC_REVIEW = "CriticalDocumentReviewFinding"
    NON_CRITICAL_DOC_REVIEW = "NonCriticalDocumentReviewFinding"


class ActionStatus(str, enum.Enum):
    OPEN = "Open"
    IN_PROGRESS = "InProgress"
    PENDING_VERIFICATION = "PendingVerification"
    CLOSED = "Closed"
    OVERDUE = "Overdue"


class LagStatus(str, enum.Enum):
    ON_TRACK = "OnTrack"
    AT_RISK = "AtRisk"
    OVERDUE = "Overdue"


class NotificationType(str, enum.Enum):
    ASSIGNMENT = "Assignment"
    REMINDER = "Reminder"
    ESCALATION = "Escalation"
    VERIFICATION_REQUEST = "VerificationRequest"
    OVERDUE = "Overdue"


class Evidence(Base):
    __tablename__ = "evidence"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    audit_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("audits.id"))
    audit_prompt_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("audit_prompts.id"))
    monitoring_run_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("monitoring_runs.id"))
    process_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("processes.id"))
    clause_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("clauses.id"))
    evidence_type: Mapped[str] = mapped_column(
        Enum("Photo", "Document", "Note", "File", name="evidence_type_enum", native_enum=False),
        nullable=False
    )
    file_uri: Mapped[str | None] = mapped_column(Text)
    note_text: Mapped[str | None] = mapped_column(Text)
    uploaded_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    uploaded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    audit: Mapped["Audit | None"] = relationship("Audit", back_populates="evidence")
    audit_prompt: Mapped["AuditPrompt | None"] = relationship("AuditPrompt", back_populates="evidence")
    monitoring_run: Mapped["MonitoringRun | None"] = relationship("MonitoringRun")
    uploaded_by_user: Mapped["User | None"] = relationship("User")


class Finding(Base):
    __tablename__ = "findings"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    audit_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("audits.id"))
    process_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("processes.id"))
    clause_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("clauses.id"))
    finding_code: Mapped[str] = mapped_column(String(20), nullable=False)
    finding_type: Mapped[str] = mapped_column(
        Enum(
            "MajorNC", "MinorNC", "Observation", "Positive",
            "CriticalDocumentReviewFinding", "NonCriticalDocumentReviewFinding",
            name="finding_type_enum", native_enum=False
        ),
        nullable=False
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    requirement_text: Mapped[str | None] = mapped_column(Text)
    evidence_summary: Mapped[str | None] = mapped_column(Text)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    severity_score: Mapped[int | None] = mapped_column(Integer)
    created_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    audit: Mapped["Audit | None"] = relationship("Audit", back_populates="findings")
    process: Mapped["Process | None"] = relationship("Process")
    clause: Mapped["Clause | None"] = relationship("Clause")
    created_by_user: Mapped["User | None"] = relationship("User")
    actions: Mapped[list["Action"]] = relationship("Action", back_populates="finding")


class Action(Base):
    __tablename__ = "actions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    finding_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("findings.id"))
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    assigned_to_user_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    assigned_to_role_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("roles.id"))
    due_date: Mapped[date | None] = mapped_column(DateTime(timezone=True))
    status: Mapped[str] = mapped_column(
        Enum("Open", "InProgress", "PendingVerification", "Closed", "Overdue", name="action_status_enum", native_enum=False),
        nullable=False,
        default="Open"
    )
    escalation_level: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    lag_status: Mapped[str] = mapped_column(
        Enum("OnTrack", "AtRisk", "Overdue", name="lag_status_enum", native_enum=False),
        nullable=False,
        default="OnTrack"
    )
    last_activity_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    verification_required: Mapped[bool] = mapped_column(Boolean, default=True)
    verification_evidence: Mapped[str | None] = mapped_column(Text)
    closed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    finding: Mapped["Finding | None"] = relationship("Finding", back_populates="actions")
    assigned_to_user: Mapped["User | None"] = relationship("User", foreign_keys=[assigned_to_user_id], primaryjoin="Action.assigned_to_user_id == User.id")
    assigned_to_role: Mapped["Role | None"] = relationship("Role")
    comments: Mapped[list["ActionComment"]] = relationship("ActionComment", back_populates="action")
    notifications: Mapped[list["Notification"]] = relationship("Notification", back_populates="action")


class ActionComment(Base):
    __tablename__ = "action_comments"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    action_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("actions.id"), nullable=False)
    comment_text: Mapped[str] = mapped_column(Text, nullable=False)
    created_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    action: Mapped["Action"] = relationship("Action", back_populates="comments")
    created_by_user: Mapped["User | None"] = relationship("User")


class Notification(Base):
    __tablename__ = "notifications"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    action_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("actions.id"))
    audit_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("audits.id"))
    notification_type: Mapped[str] = mapped_column(
        Enum("Assignment", "Reminder", "Escalation", "VerificationRequest", "Overdue", name="notification_type_enum", native_enum=False),
        nullable=False
    )
    recipient_user_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    subject: Mapped[str | None] = mapped_column(String(255))
    body: Mapped[str | None] = mapped_column(Text)
    sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    action: Mapped["Action | None"] = relationship("Action", back_populates="notifications")
    recipient: Mapped["User | None"] = relationship("User")
