from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision = "20260919_0077"
down_revision = "20260919_0076"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "case_outcomes",
        sa.Column("id", sa.UUID(), primary_key=True),
        sa.Column("tenant_id", sa.UUID(), nullable=False),
        sa.Column("case_id", sa.UUID(), nullable=False),
        sa.Column("lot_reference", sa.String(120), nullable=False),
        sa.Column("outcome", sa.String(16), nullable=False),
        sa.Column("source_locator", sa.String(500)),
        sa.Column("reservations_json", sa.JSON(), nullable=False),
        sa.Column("unknown_reason", sa.String(1000)),
        sa.Column("actor_id", sa.UUID(), nullable=False),
        sa.Column("membership_id", sa.UUID(), nullable=False),
        sa.Column("command_id", sa.UUID(), nullable=False),
        sa.Column("idempotency_key", sa.UUID(), nullable=False),
        sa.Column("correlation_id", sa.UUID()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["tenant_id", "case_id"], ["cases.tenant_id", "cases.id"], ondelete="RESTRICT"
        ),
        sa.UniqueConstraint("tenant_id", "id"),
        sa.CheckConstraint("outcome IN ('WON', 'LOST', 'UNKNOWN')", name="outcome"),
    )


def downgrade() -> None:
    op.drop_table("case_outcomes")
