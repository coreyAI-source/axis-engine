"""Readiness report details and AI narrative draft on hotel audits.

Revision ID: 0003
Revises: 0002
"""
from alembic import op
import sqlalchemy as sa

revision = "0003"
down_revision = "0002"
branch_labels = None
depends_on = None


def upgrade():
    existing = {column["name"] for column in sa.inspect(op.get_bind()).get_columns("hospitality_audits")}
    for name in ("report_profile", "report_draft"):
        if name not in existing:
            op.add_column("hospitality_audits", sa.Column(name, sa.JSON(), nullable=True))


def downgrade():
    op.drop_column("hospitality_audits", "report_draft")
    op.drop_column("hospitality_audits", "report_profile")
