"""Store bounded operational profiles without changing authorization.

Revision ID: 20260914_0070
Revises: 20260914_0069
Create Date: 2026-09-14
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision = "20260914_0070"
down_revision = "20260914_0069"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None

_OPERATIONAL_PROFILE_CONSTRAINT = (
    "operational_profile IS NULL OR ("
    "role = 'COLLABORATEUR' AND operational_profile IN ('RESPONSABLE', 'EXPERT')"
    ")"
)


def upgrade() -> None:
    op.add_column(
        "tenant_memberships",
        sa.Column("operational_profile", sa.String(length=32), nullable=True),
    )
    op.create_check_constraint(
        "operational_profile",
        "tenant_memberships",
        _OPERATIONAL_PROFILE_CONSTRAINT,
    )


def downgrade() -> None:
    op.drop_constraint("operational_profile", "tenant_memberships", type_="check")
    op.drop_column("tenant_memberships", "operational_profile")
