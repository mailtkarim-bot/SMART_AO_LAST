"""Persist append-only contract timeline query receipts."""
# ruff: noqa: E501
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision = "20260925_0095"
down_revision = "20260925_0094"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None

def upgrade() -> None:
    op.create_table(
        "contract_query_receipts",
        sa.Column("id", sa.UUID(), primary_key=True), sa.Column("tenant_id", sa.UUID(), nullable=False),
        sa.Column("case_id", sa.UUID(), nullable=False), sa.Column("filters_json", sa.JSON(), nullable=False),
        sa.Column("order_key", sa.String(64), nullable=False), sa.Column("limit_value", sa.Integer(), nullable=False),
        sa.Column("offset_value", sa.Integer(), nullable=False), sa.Column("actor_id", sa.UUID(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["tenant_id", "case_id"], ["cases.tenant_id", "cases.id"], ondelete="RESTRICT"),
        sa.UniqueConstraint("tenant_id", "id", name="uq_contract_query_receipts__tenant_id"),
        sa.CheckConstraint("limit_value > 0 AND limit_value <= 100", name="contract_query_receipt_limit_closed"),
        sa.CheckConstraint("offset_value >= 0", name="contract_query_receipt_offset_closed"),
    )

def downgrade() -> None:
    op.drop_table("contract_query_receipts")
