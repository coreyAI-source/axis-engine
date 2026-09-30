"""initial schema

Revision ID: 0001
Revises:
Create Date: 2026-04-26
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # organisations
    op.create_table(
        "organisations",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("legal_name", sa.String(255)),
        sa.Column("active_flag", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    # roles
    op.create_table(
        "roles",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("code", sa.String(50), nullable=False, unique=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text()),
    )

    # sites
    op.create_table(
        "sites",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("organisation_id", UUID(as_uuid=True), sa.ForeignKey("organisations.id"), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text()),
        sa.Column("active_flag", sa.Boolean(), nullable=False, server_default="true"),
    )

    # users
    op.create_table(
        "users",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("organisation_id", UUID(as_uuid=True), sa.ForeignKey("organisations.id"), nullable=False),
        sa.Column("first_name", sa.String(100), nullable=False),
        sa.Column("last_name", sa.String(100), nullable=False),
        sa.Column("email", sa.String(255), nullable=False, unique=True),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column("role_id", UUID(as_uuid=True), sa.ForeignKey("roles.id")),
        sa.Column("role_code", sa.String(50)),
        sa.Column("active_flag", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    # processes
    op.create_table(
        "processes",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("organisation_id", UUID(as_uuid=True), sa.ForeignKey("organisations.id"), nullable=False),
        sa.Column("code", sa.String(50), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("category", sa.String(20), nullable=False),
        sa.Column("description", sa.Text()),
        sa.Column("owner_role_id", UUID(as_uuid=True), sa.ForeignKey("roles.id")),
        sa.Column("site_scope", sa.String(255)),
        sa.Column("active_flag", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    # standards
    op.create_table(
        "standards",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("code", sa.String(20), nullable=False, unique=True),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("version", sa.String(20), nullable=False),
    )

    # clauses
    op.create_table(
        "clauses",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("standard_id", UUID(as_uuid=True), sa.ForeignKey("standards.id"), nullable=False),
        sa.Column("clause_number", sa.String(20), nullable=False),
        sa.Column("clause_title", sa.String(255), nullable=False),
        sa.Column("parent_clause_number", sa.String(20)),
        sa.Column("requirement_text", sa.Text()),
        sa.Column("hls_section", sa.String(30), nullable=False),
        sa.Column("requires_documented_information", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("requires_retained_evidence", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("evidence_guidance", sa.Text()),
        sa.Column("active_flag", sa.Boolean(), nullable=False, server_default="true"),
    )

    # process_clause_maps
    op.create_table(
        "process_clause_maps",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("process_id", UUID(as_uuid=True), sa.ForeignKey("processes.id"), nullable=False),
        sa.Column("clause_id", UUID(as_uuid=True), sa.ForeignKey("clauses.id"), nullable=False),
        sa.Column("applicability", sa.String(20), nullable=False, server_default="Full"),
        sa.Column("rationale", sa.Text()),
        sa.Column("risk_modifier", sa.String(20)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    # control_mappings
    op.create_table(
        "control_mappings",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("process_id", UUID(as_uuid=True), sa.ForeignKey("processes.id"), nullable=False),
        sa.Column("source_standard_code", sa.String(20), nullable=False),
        sa.Column("source_clause_number", sa.String(20), nullable=False),
        sa.Column("target_standard_code", sa.String(20), nullable=False),
        sa.Column("target_clause_number", sa.String(20), nullable=False),
        sa.Column("mapping_type", sa.String(20), nullable=False),
        sa.Column("notes", sa.Text()),
    )

    # risk_frequency_rules
    op.create_table(
        "risk_frequency_rules",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("risk_level", sa.String(20), nullable=False, unique=True),
        sa.Column("frequency_code", sa.String(20), nullable=False),
        sa.Column("interval_months", sa.Integer(), nullable=False),
    )

    # monitoring_methods
    op.create_table(
        "monitoring_methods",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("code", sa.String(50), nullable=False, unique=True),
        sa.Column("name", sa.String(255), nullable=False),
    )

    # monitoring_tasks
    op.create_table(
        "monitoring_tasks",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("organisation_id", UUID(as_uuid=True), sa.ForeignKey("organisations.id"), nullable=False),
        sa.Column("site_id", UUID(as_uuid=True), sa.ForeignKey("sites.id")),
        sa.Column("process_id", UUID(as_uuid=True), sa.ForeignKey("processes.id")),
        sa.Column("clause_id", UUID(as_uuid=True), sa.ForeignKey("clauses.id")),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("description", sa.Text()),
        sa.Column("owner_user_id", UUID(as_uuid=True), sa.ForeignKey("users.id")),
        sa.Column("owner_role_id", UUID(as_uuid=True), sa.ForeignKey("roles.id")),
        sa.Column("risk_level", sa.String(20), nullable=False, server_default="Medium"),
        sa.Column("importance_level", sa.String(20), nullable=False, server_default="Moderate"),
        sa.Column("frequency_code", sa.String(20), nullable=False),
        sa.Column("interval_months", sa.Integer(), nullable=False),
        sa.Column("method_id", UUID(as_uuid=True), sa.ForeignKey("monitoring_methods.id")),
        sa.Column("next_due_date", sa.Date()),
        sa.Column("last_completed_date", sa.Date()),
        sa.Column("status", sa.String(20), nullable=False, server_default="Scheduled"),
        sa.Column("active_flag", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    # monitoring_runs
    op.create_table(
        "monitoring_runs",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("monitoring_task_id", UUID(as_uuid=True), sa.ForeignKey("monitoring_tasks.id"), nullable=False),
        sa.Column("run_date", sa.Date(), nullable=False),
        sa.Column("due_date", sa.Date(), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="Open"),
        sa.Column("completed_at", sa.DateTime(timezone=True)),
        sa.Column("completed_by", UUID(as_uuid=True), sa.ForeignKey("users.id")),
        sa.Column("summary_notes", sa.Text()),
    )

    # audits
    op.create_table(
        "audits",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("organisation_id", UUID(as_uuid=True), sa.ForeignKey("organisations.id"), nullable=False),
        sa.Column("site_id", UUID(as_uuid=True), sa.ForeignKey("sites.id")),
        sa.Column("audit_type", sa.String(20), nullable=False),
        sa.Column("audit_stage", sa.String(20), nullable=False, server_default="DocumentReview"),
        sa.Column("status", sa.String(20), nullable=False, server_default="Planned"),
        sa.Column("auditee_name", sa.String(255)),
        sa.Column("audit_client", sa.String(255)),
        sa.Column("audit_body", sa.String(255)),
        sa.Column("lead_auditor_user_id", UUID(as_uuid=True), sa.ForeignKey("users.id")),
        sa.Column("objective", sa.Text()),
        sa.Column("scope", sa.Text()),
        sa.Column("criteria_text", sa.Text()),
        sa.Column("start_date", sa.Date()),
        sa.Column("end_date", sa.Date()),
        sa.Column("duration_days", sa.Integer()),
        sa.Column("main_location", sa.String(255)),
        sa.Column("auditee_contact", sa.String(255)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    # audit_team_members
    op.create_table(
        "audit_team_members",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("audit_id", UUID(as_uuid=True), sa.ForeignKey("audits.id"), nullable=False),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("role_in_audit", sa.String(100)),
    )

    # audit_locations
    op.create_table(
        "audit_locations",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("audit_id", UUID(as_uuid=True), sa.ForeignKey("audits.id"), nullable=False),
        sa.Column("site_name", sa.String(255), nullable=False),
        sa.Column("is_main_location", sa.Boolean(), server_default="false"),
        sa.Column("confirmed_flag", sa.Boolean(), server_default="false"),
    )

    # audit_processes
    op.create_table(
        "audit_processes",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("audit_id", UUID(as_uuid=True), sa.ForeignKey("audits.id"), nullable=False),
        sa.Column("process_id", UUID(as_uuid=True), sa.ForeignKey("processes.id"), nullable=False),
    )

    # audit_prompts
    op.create_table(
        "audit_prompts",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("audit_id", UUID(as_uuid=True), sa.ForeignKey("audits.id"), nullable=False),
        sa.Column("process_id", UUID(as_uuid=True), sa.ForeignKey("processes.id")),
        sa.Column("clause_id", UUID(as_uuid=True), sa.ForeignKey("clauses.id")),
        sa.Column("prompt_text", sa.Text(), nullable=False),
        sa.Column("prompt_type", sa.String(20), nullable=False, server_default="DocumentCheck"),
        sa.Column("evidence_required", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("sequence_no", sa.Integer()),
        sa.Column("response_status", sa.String(10), nullable=False, server_default="Pending"),
        sa.Column("comments", sa.Text()),
        sa.Column("responded_at", sa.DateTime(timezone=True)),
        sa.Column("responded_by", UUID(as_uuid=True), sa.ForeignKey("users.id")),
    )

    # evidence
    op.create_table(
        "evidence",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("audit_id", UUID(as_uuid=True), sa.ForeignKey("audits.id")),
        sa.Column("audit_prompt_id", UUID(as_uuid=True), sa.ForeignKey("audit_prompts.id")),
        sa.Column("monitoring_run_id", UUID(as_uuid=True), sa.ForeignKey("monitoring_runs.id")),
        sa.Column("process_id", UUID(as_uuid=True), sa.ForeignKey("processes.id")),
        sa.Column("clause_id", UUID(as_uuid=True), sa.ForeignKey("clauses.id")),
        sa.Column("evidence_type", sa.String(20), nullable=False),
        sa.Column("file_uri", sa.Text()),
        sa.Column("note_text", sa.Text()),
        sa.Column("uploaded_by", UUID(as_uuid=True), sa.ForeignKey("users.id")),
        sa.Column("uploaded_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    # findings
    op.create_table(
        "findings",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("audit_id", UUID(as_uuid=True), sa.ForeignKey("audits.id")),
        sa.Column("process_id", UUID(as_uuid=True), sa.ForeignKey("processes.id")),
        sa.Column("clause_id", UUID(as_uuid=True), sa.ForeignKey("clauses.id")),
        sa.Column("finding_code", sa.String(20), nullable=False),
        sa.Column("finding_type", sa.String(40), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("requirement_text", sa.Text()),
        sa.Column("evidence_summary", sa.Text()),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("severity_score", sa.Integer()),
        sa.Column("created_by", UUID(as_uuid=True), sa.ForeignKey("users.id")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    # actions
    op.create_table(
        "actions",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("finding_id", UUID(as_uuid=True), sa.ForeignKey("findings.id")),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("description", sa.Text()),
        sa.Column("assigned_to_user_id", UUID(as_uuid=True), sa.ForeignKey("users.id")),
        sa.Column("assigned_to_role_id", UUID(as_uuid=True), sa.ForeignKey("roles.id")),
        sa.Column("due_date", sa.DateTime(timezone=True)),
        sa.Column("status", sa.String(30), nullable=False, server_default="Open"),
        sa.Column("escalation_level", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("lag_status", sa.String(20), nullable=False, server_default="OnTrack"),
        sa.Column("last_activity_at", sa.DateTime(timezone=True)),
        sa.Column("verification_required", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("verification_evidence", sa.Text()),
        sa.Column("closed_at", sa.DateTime(timezone=True)),
    )

    # action_comments
    op.create_table(
        "action_comments",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("action_id", UUID(as_uuid=True), sa.ForeignKey("actions.id"), nullable=False),
        sa.Column("comment_text", sa.Text(), nullable=False),
        sa.Column("created_by", UUID(as_uuid=True), sa.ForeignKey("users.id")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    # notifications
    op.create_table(
        "notifications",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("action_id", UUID(as_uuid=True), sa.ForeignKey("actions.id")),
        sa.Column("audit_id", UUID(as_uuid=True), sa.ForeignKey("audits.id")),
        sa.Column("notification_type", sa.String(30), nullable=False),
        sa.Column("recipient_user_id", UUID(as_uuid=True), sa.ForeignKey("users.id")),
        sa.Column("subject", sa.String(255)),
        sa.Column("body", sa.Text()),
        sa.Column("sent_at", sa.DateTime(timezone=True)),
    )


def downgrade() -> None:
    op.drop_table("notifications")
    op.drop_table("action_comments")
    op.drop_table("actions")
    op.drop_table("findings")
    op.drop_table("evidence")
    op.drop_table("audit_prompts")
    op.drop_table("audit_processes")
    op.drop_table("audit_locations")
    op.drop_table("audit_team_members")
    op.drop_table("audits")
    op.drop_table("monitoring_runs")
    op.drop_table("monitoring_tasks")
    op.drop_table("monitoring_methods")
    op.drop_table("risk_frequency_rules")
    op.drop_table("control_mappings")
    op.drop_table("process_clause_maps")
    op.drop_table("clauses")
    op.drop_table("standards")
    op.drop_table("processes")
    op.drop_table("users")
    op.drop_table("sites")
    op.drop_table("roles")
    op.drop_table("organisations")
