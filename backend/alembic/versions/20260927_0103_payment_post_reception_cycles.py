"""Persist tenant-scoped payment and post-reception cycle facts."""
# ruff: noqa: E501
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision = "20260927_0103"
down_revision = "20260926_0102"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None

def upgrade() -> None:
    op.create_table("payment_post_reception_cycles", sa.Column("id", sa.UUID(), primary_key=True), sa.Column("tenant_id", sa.UUID(), nullable=False), sa.Column("case_id", sa.UUID(), nullable=False), sa.Column("source_refs_json", sa.JSON(), nullable=False), sa.Column("trigger_event", sa.String(128), nullable=False), sa.Column("status", sa.String(24), nullable=False), sa.Column("cash_assumption", sa.Text()), sa.Column("post_reception_cost_note", sa.Text()), sa.Column("actor_id", sa.UUID(), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()), sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()), sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="RESTRICT"), sa.ForeignKeyConstraint(["tenant_id", "case_id"], ["cases.tenant_id", "cases.id"], ondelete="RESTRICT"), sa.UniqueConstraint("tenant_id", "id", name="uq_payment_post_reception_cycles__tenant_id"), sa.CheckConstraint("status IN ('SOURCE_SIGNAL_ONLY', 'REVIEW_REQUIRED', 'UNKNOWN')", name="payment_cycle_status_closed"))

def downgrade() -> None:
    op.drop_table("payment_post_reception_cycles")
