"""Persist the append-only P7 execution result after an approved P6."""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision = "20260919_0081"
down_revision = "20260919_0080"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "case_p7_results",
        sa.Column("id", sa.UUID(), primary_key=True),
        sa.Column("tenant_id", sa.UUID(), nullable=False),
        sa.Column("p6_control_id", sa.UUID(), nullable=False),
        sa.Column("case_id", sa.UUID(), nullable=False),
        sa.Column("lot_reference", sa.String(120), nullable=False),
        sa.Column("result", sa.String(16), nullable=False),
        sa.Column("source_locator", sa.String(500)),
        sa.Column("reason", sa.String(2000)),
        sa.Column("reservations_json", sa.JSON(), nullable=False),
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
            ["tenant_id", "p6_control_id"],
            ["case_p6_controls.tenant_id", "case_p6_controls.id"],
            ondelete="RESTRICT",
        ),
        sa.UniqueConstraint("tenant_id", "id", name="uq_case_p7_results__tenant_id_id"),
        sa.UniqueConstraint(
            "tenant_id", "p6_control_id", name="uq_case_p7_results__tenant_id_p6_control_id"
        ),
        sa.CheckConstraint("result IN ('COMPLETED', 'UNKNOWN', 'INTERRUPTED')", name="result"),
    )


def downgrade() -> None:
    op.drop_table("case_p7_results")
