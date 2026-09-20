from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision = "20260919_0078"
down_revision = "20260919_0077"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "case_outcome_transmissions",
        sa.Column("id", sa.UUID(), primary_key=True),
        sa.Column("tenant_id", sa.UUID(), nullable=False),
        sa.Column("outcome_id", sa.UUID(), nullable=False),
        sa.Column("case_id", sa.UUID(), nullable=False),
        sa.Column("lot_reference", sa.String(120), nullable=False),
        sa.Column("recipient", sa.String(120), nullable=False),
        sa.Column("reservations_json", sa.JSON(), nullable=False),
        sa.Column("actor_id", sa.UUID(), nullable=False),
        sa.Column("membership_id", sa.UUID(), nullable=False),
        sa.Column("command_id", sa.UUID(), nullable=False),
        sa.Column("idempotency_key", sa.UUID(), nullable=False),
        sa.Column("correlation_id", sa.UUID()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["tenant_id", "outcome_id"],
            ["case_outcomes.tenant_id", "case_outcomes.id"],
            ondelete="RESTRICT",
        ),
        sa.UniqueConstraint("tenant_id", "id", name="uq_case_outcome_transmissions__tenant_id_id"),
        sa.UniqueConstraint(
            "tenant_id", "outcome_id", name="uq_case_outcome_transmissions__tenant_id_outcome_id"
        ),
    )


def downgrade() -> None:
    op.drop_table("case_outcome_transmissions")
