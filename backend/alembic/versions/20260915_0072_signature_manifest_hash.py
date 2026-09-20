"""Bind signature intents to the exact immutable submission manifest.

Revision ID: 20260915_0072
Revises: 20260915_0071
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision = "20260915_0072"
down_revision = "20260915_0071"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "submission_signatures",
        sa.Column("manifest_sha256", sa.CHAR(length=64), nullable=True),
    )
    op.execute(
        """
        UPDATE submission_signatures AS signatures
        SET manifest_sha256 = packages.manifest_sha256
        FROM submission_packages AS packages
        WHERE packages.tenant_id = signatures.tenant_id
          AND packages.id = signatures.submission_package_id
        """
    )
    op.alter_column("submission_signatures", "manifest_sha256", nullable=False)
    op.create_check_constraint(
        "submission_signatures_manifest_sha256",
        "submission_signatures",
        "manifest_sha256 ~ '^[a-f0-9]{64}$'",
    )


def downgrade() -> None:
    op.drop_constraint(
        "submission_signatures_manifest_sha256",
        "submission_signatures",
        type_="check",
    )
    op.drop_column("submission_signatures", "manifest_sha256")
