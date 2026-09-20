"""Persist the append-only order issued from a WON case outcome."""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision = "20260919_0079"
down_revision = "20260919_0078"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.alter_column("case_outcomes", "created_at", server_default=sa.func.now())
    op.alter_column("case_outcome_transmissions", "created_at", server_default=sa.func.now())
    op.add_column(
        "case_outcomes",
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
    )
    op.add_column(
        "case_outcome_transmissions",
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
    )
    op.create_table(
        "case_orders",
        sa.Column("id", sa.UUID(), primary_key=True),
        sa.Column("tenant_id", sa.UUID(), nullable=False),
        sa.Column("outcome_id", sa.UUID(), nullable=False),
        sa.Column("case_id", sa.UUID(), nullable=False),
        sa.Column("lot_reference", sa.String(120), nullable=False),
        sa.Column("decision", sa.String(16), nullable=False),
        sa.Column("source_locator", sa.String(500), nullable=False),
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
            ["tenant_id", "outcome_id"],
            ["case_outcomes.tenant_id", "case_outcomes.id"],
            ondelete="RESTRICT",
        ),
        sa.UniqueConstraint("tenant_id", "id", name="uq_case_orders__tenant_id_id"),
        sa.UniqueConstraint("tenant_id", "outcome_id", name="uq_case_orders__tenant_id_outcome_id"),
        sa.CheckConstraint("decision IN ('ACCEPTED', 'REJECTED')", name="decision"),
    )


def downgrade() -> None:
    op.drop_table("case_orders")
    op.drop_column("case_outcome_transmissions", "updated_at")
    op.drop_column("case_outcomes", "updated_at")
    op.alter_column("case_outcomes", "created_at", server_default=None)
    op.alter_column("case_outcome_transmissions", "created_at", server_default=None)
