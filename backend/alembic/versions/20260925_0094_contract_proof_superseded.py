"""Allow explicit append-only superseded contract proof state."""
# ruff: noqa: E501
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision = "20260925_0094"
down_revision = "20260924_0093"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None

def upgrade() -> None:
    bind = op.get_bind()
    for (name,) in bind.execute(sa.text("SELECT conname FROM pg_constraint WHERE conrelid = 'contract_baseline_deviation_impacts'::regclass AND contype = 'c' AND pg_get_constraintdef(oid) LIKE '%SOURCE_SIGNAL_ONLY%'")).all():
        op.drop_constraint(name, "contract_baseline_deviation_impacts", type_="check")
    op.create_check_constraint("contract_assessment_status_closed", "contract_baseline_deviation_impacts", "status IN ('SOURCE_SIGNAL_ONLY', 'HUMAN_REVIEW_REQUIRED', 'CONFIRMED', 'UNKNOWN', 'SUPERSEDED')")

def downgrade() -> None:
    bind = op.get_bind()
    for (name,) in bind.execute(sa.text("SELECT conname FROM pg_constraint WHERE conrelid = 'contract_baseline_deviation_impacts'::regclass AND contype = 'c' AND pg_get_constraintdef(oid) LIKE '%SOURCE_SIGNAL_ONLY%'")).all():
        op.drop_constraint(name, "contract_baseline_deviation_impacts", type_="check")
    op.create_check_constraint("contract_assessment_status_closed", "contract_baseline_deviation_impacts", "status IN ('SOURCE_SIGNAL_ONLY', 'HUMAN_REVIEW_REQUIRED', 'CONFIRMED', 'UNKNOWN')")
