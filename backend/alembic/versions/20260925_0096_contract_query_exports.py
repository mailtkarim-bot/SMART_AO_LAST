"""Persist bounded local query export requests."""
# ruff: noqa: E501
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision = "20260925_0096"
down_revision = "20260925_0095"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None

def upgrade() -> None:
    op.create_table("contract_query_exports", sa.Column("id", sa.UUID(), primary_key=True), sa.Column("tenant_id", sa.UUID(), nullable=False), sa.Column("case_id", sa.UUID(), nullable=False), sa.Column("filters_json", sa.JSON(), nullable=False), sa.Column("status", sa.String(16), nullable=False), sa.Column("actor_id", sa.UUID(), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()), sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()), sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="RESTRICT"), sa.ForeignKeyConstraint(["tenant_id", "case_id"], ["cases.tenant_id", "cases.id"], ondelete="RESTRICT"), sa.UniqueConstraint("tenant_id", "id", name="uq_contract_query_exports__tenant_id"), sa.CheckConstraint("status IN ('REQUESTED', 'READY', 'UNKNOWN', 'REFUSED')", name="contract_query_export_status_closed"))

def downgrade() -> None:
    op.drop_table("contract_query_exports")
