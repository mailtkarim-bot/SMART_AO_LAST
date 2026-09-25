"""Persist append-only owner acts for export verification."""
# ruff: noqa: E501
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision = "20260925_0100"
down_revision = "20260925_0099"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None

def upgrade() -> None:
    op.create_table("export_verification_owner_acts", sa.Column("id", sa.UUID(), primary_key=True), sa.Column("tenant_id", sa.UUID(), nullable=False), sa.Column("export_id", sa.UUID(), nullable=False), sa.Column("owner_id", sa.UUID(), nullable=False), sa.Column("approved", sa.Boolean(), nullable=False), sa.Column("rationale", sa.Text(), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()), sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()), sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="RESTRICT"), sa.ForeignKeyConstraint(["tenant_id", "export_id"], ["contract_query_exports.tenant_id", "contract_query_exports.id"], ondelete="RESTRICT"), sa.UniqueConstraint("tenant_id", "id", name="uq_export_verification_owner_acts__tenant_id"))

def downgrade() -> None:
    op.drop_table("export_verification_owner_acts")
