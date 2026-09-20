"""Allow an explicitly justified candidature-only package without pricing."""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "20260919_0075"
down_revision = "20260919_0074"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.alter_column(
        "submission_packages",
        "financial_snapshot_id",
        existing_type=postgresql.UUID(as_uuid=True),
        nullable=True,
    )
    op.alter_column(
        "submission_packages",
        "financial_snapshot_revision",
        existing_type=sa.Integer(),
        nullable=True,
    )


def downgrade() -> None:
    op.execute("DROP TRIGGER IF EXISTS submission_packages_append_only ON submission_packages")
    op.execute("DROP FUNCTION IF EXISTS prevent_submission_package_mutation()")
    op.execute(
        "DELETE FROM submission_packages WHERE financial_snapshot_id IS NULL "
        "OR financial_snapshot_revision IS NULL"
    )
    op.alter_column(
        "submission_packages",
        "financial_snapshot_revision",
        existing_type=sa.Integer(),
        nullable=False,
    )
    op.alter_column(
        "submission_packages",
        "financial_snapshot_id",
        existing_type=postgresql.UUID(as_uuid=True),
        nullable=False,
    )
