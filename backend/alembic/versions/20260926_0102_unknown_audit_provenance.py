"""Persist tenant-scoped unknown audit provenance."""
# ruff: noqa: E501
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision = "20260926_0102"
down_revision = "20260926_0101"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None

def upgrade() -> None:
    op.create_table("unknown_audit_provenance", sa.Column("id", sa.UUID(), primary_key=True), sa.Column("tenant_id", sa.UUID(), nullable=False), sa.Column("export_id", sa.UUID(), nullable=False), sa.Column("source_type", sa.String(24), nullable=False), sa.Column("source_event_id", sa.UUID(), nullable=False), sa.Column("actor_id", sa.UUID(), nullable=False), sa.Column("status", sa.String(32), nullable=False), sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False), sa.Column("rationale", sa.Text()), sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()), sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()), sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="RESTRICT"), sa.ForeignKeyConstraint(["tenant_id", "export_id"], ["contract_query_exports.tenant_id", "contract_query_exports.id"], ondelete="RESTRICT"), sa.UniqueConstraint("tenant_id", "id", name="uq_unknown_audit_provenance__tenant_id"), sa.CheckConstraint("source_type IN ('TRANSITION', 'HUMAN_RESUMPTION', 'VERIFICATION')", name="unknown_audit_source_closed"))

def downgrade() -> None:
    op.drop_table("unknown_audit_provenance")
