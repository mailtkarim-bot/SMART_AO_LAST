"""Persist append-only Case suspension, resumption, and closure facts."""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision = "20260920_0083"
down_revision = "20260919_0082"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "case_dispositions",
        sa.Column("id", sa.UUID(), primary_key=True),
        sa.Column("tenant_id", sa.UUID(), nullable=False),
        sa.Column("case_id", sa.UUID(), nullable=False),
        sa.Column("p7_result_id", sa.UUID()),
        sa.Column("state", sa.String(16), nullable=False),
        sa.Column("reason_code", sa.String(64), nullable=False),
        sa.Column("rationale", sa.String(2000), nullable=False),
        sa.Column("source_locator", sa.String(500)),
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
            ["tenant_id", "p7_result_id"],
            ["case_p7_results.tenant_id", "case_p7_results.id"],
            ondelete="RESTRICT",
        ),
        sa.UniqueConstraint("tenant_id", "id", name="uq_case_dispositions__tenant_id_id"),
        sa.CheckConstraint("state IN ('SUSPENDED', 'RESUMED', 'CLOSED')", name="state"),
    )


def downgrade() -> None:
    op.drop_table("case_dispositions")
