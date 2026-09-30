"""Private hotel audit aggregates and evidence files.

Revision ID: 0002
Revises: 0001
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade():
    # The original app may have run metadata.create_all during development.
    # Check first so migrating such a database does not drop or overwrite data.
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if not inspector.has_table("hospitality_audits"):
        op.create_table(
            "hospitality_audits",
            sa.Column("id", UUID(as_uuid=True), primary_key=True),
            sa.Column("organisation_id", UUID(as_uuid=True), sa.ForeignKey("organisations.id"), nullable=False),
            sa.Column("created_by", UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
            sa.Column("title", sa.String(255), nullable=False),
            sa.Column("site_name", sa.String(255), nullable=False),
            sa.Column("status", sa.String(30), nullable=False),
            sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
            sa.Column("bundle", sa.JSON(), nullable=False),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        )
        op.create_index("ix_hospitality_audits_organisation_id", "hospitality_audits", ["organisation_id"])
    if not inspector.has_table("hospitality_files"):
        op.create_table(
            "hospitality_files",
            sa.Column("id", UUID(as_uuid=True), primary_key=True),
            sa.Column("audit_id", UUID(as_uuid=True), sa.ForeignKey("hospitality_audits.id"), nullable=False),
            sa.Column("evidence_id", sa.String(80), nullable=False, unique=True),
            sa.Column("file_name", sa.String(255), nullable=False),
            sa.Column("content_type", sa.String(100), nullable=False),
            sa.Column("sha256", sa.String(64), nullable=False),
            sa.Column("content", sa.LargeBinary(), nullable=False),
        )
        op.create_index("ix_hospitality_files_audit_id", "hospitality_files", ["audit_id"])


def downgrade():
    op.drop_table("hospitality_files")
    op.drop_table("hospitality_audits")
