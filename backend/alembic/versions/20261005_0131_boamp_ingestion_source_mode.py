"""Distinguish live BOAMP collection from synthetic replays."""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision = "20261005_0131"
down_revision = "20261003_0130"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "boamp_ingestion_runs",
        sa.Column("source_mode", sa.String(length=16), server_default="LIVE", nullable=False),
    )
    op.create_check_constraint(
        "boamp_ingestion_runs_source_mode",
        "boamp_ingestion_runs",
        "source_mode IN ('LIVE', 'REPLAY')",
    )


def downgrade() -> None:
    op.drop_constraint(
        "boamp_ingestion_runs_source_mode",
        "boamp_ingestion_runs",
        type_="check",
    )
    op.drop_column("boamp_ingestion_runs", "source_mode")
