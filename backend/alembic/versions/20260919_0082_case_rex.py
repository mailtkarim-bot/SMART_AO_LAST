"""Persist bounded, explicitly scoped returns of experience."""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision = "20260919_0082"
down_revision = "20260919_0081"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "case_rex",
        sa.Column("id", sa.UUID(), primary_key=True),
        sa.Column("tenant_id", sa.UUID(), nullable=False),
        sa.Column("p7_result_id", sa.UUID(), nullable=False),
        sa.Column("case_id", sa.UUID(), nullable=False),
        sa.Column("lot_reference", sa.String(120), nullable=False),
        sa.Column("motif", sa.String(16), nullable=False),
        sa.Column("scope", sa.String(24), nullable=False),
        sa.Column("validation", sa.String(16), nullable=False),
        sa.Column("observation", sa.String(2000), nullable=False),
        sa.Column("consequence", sa.String(2000), nullable=False),
        sa.Column("follow_up", sa.String(2000), nullable=False),
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
        sa.UniqueConstraint("tenant_id", "id", name="uq_case_rex__tenant_id_id"),
        sa.CheckConstraint("motif IN ('KNOWN', 'UNKNOWN')", name="motif"),
        sa.CheckConstraint(
            "scope IN ('CASE_ONLY', 'LOT_PATTERN', 'ENTERPRISE_PATTERN')", name="scope"
        ),
        sa.CheckConstraint("validation IN ('PENDING', 'APPROVED')", name="validation"),
    )


def downgrade() -> None:
    op.drop_table("case_rex")
