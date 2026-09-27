"""Persist append-only human payment cycle reviews."""
# ruff: noqa: E501
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision = "20260927_0104"
down_revision = "20260927_0103"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None

def upgrade() -> None:
    op.create_table("payment_cycle_reviews", sa.Column("id", sa.UUID(), primary_key=True), sa.Column("tenant_id", sa.UUID(), nullable=False), sa.Column("cycle_id", sa.UUID(), nullable=False), sa.Column("reviewer_id", sa.UUID(), nullable=False), sa.Column("decision", sa.String(32), nullable=False), sa.Column("rationale", sa.Text(), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()), sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()), sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="RESTRICT"), sa.ForeignKeyConstraint(["tenant_id", "cycle_id"], ["payment_post_reception_cycles.tenant_id", "payment_post_reception_cycles.id"], ondelete="RESTRICT"), sa.UniqueConstraint("tenant_id", "id", name="uq_payment_cycle_reviews__tenant_id"), sa.CheckConstraint("decision IN ('ACCEPTED_FOR_PLANNING', 'REVIEW_REQUIRED', 'REJECTED')", name="payment_cycle_review_decision_closed"))

def downgrade() -> None:
    op.drop_table("payment_cycle_reviews")
