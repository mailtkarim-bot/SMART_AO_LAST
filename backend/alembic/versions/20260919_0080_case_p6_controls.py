"""Persist the append-only P6 control for an accepted case order."""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision = "20260919_0080"
down_revision = "20260919_0079"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "case_p6_controls",
        sa.Column("id", sa.UUID(), primary_key=True),
        sa.Column("tenant_id", sa.UUID(), nullable=False),
        sa.Column("order_id", sa.UUID(), nullable=False),
        sa.Column("case_id", sa.UUID(), nullable=False),
        sa.Column("lot_reference", sa.String(120), nullable=False),
        sa.Column("decision", sa.String(16), nullable=False),
        sa.Column("reservations_json", sa.JSON(), nullable=False),
        sa.Column("rationale", sa.String(2000), nullable=False),
        sa.Column("actor_id", sa.UUID(), nullable=False),
        sa.Column("membership_id", sa.UUID(), nullable=False),
        sa.Column("command_id", sa.UUID(), nullable=False),
        sa.Column("idempotency_key", sa.UUID(), nullable=False),
        sa.Column("correlation_id", sa.UUID()),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id", "order_id"],
            ["case_orders.tenant_id", "case_orders.id"],
            ondelete="RESTRICT",
        ),
        sa.UniqueConstraint("tenant_id", "id", name="uq_case_p6_controls__tenant_id_id"),
        sa.UniqueConstraint(
            "tenant_id", "order_id", name="uq_case_p6_controls__tenant_id_order_id"
        ),
        sa.CheckConstraint("decision IN ('APPROVED', 'REJECTED')", name="decision"),
    )


def downgrade() -> None:
    op.drop_table("case_p6_controls")
