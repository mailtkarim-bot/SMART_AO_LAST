"""Persist append-only organization-owner designation and transfer acts."""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision = "20260920_0086"
down_revision = "20260920_0085"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "tenant_owners",
        sa.Column("ended_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.drop_constraint("uq_tenant_owners__membership", "tenant_owners", type_="unique")
    op.create_index(
        "ux_tenant_owners__active_membership",
        "tenant_owners",
        ["tenant_id", "membership_id"],
        unique=True,
        postgresql_where=sa.text("ended_at IS NULL"),
    )
    op.create_table(
        "tenant_owner_changes",
        sa.Column("id", sa.UUID(), primary_key=True),
        sa.Column("tenant_id", sa.UUID(), nullable=False),
        sa.Column("action", sa.String(16), nullable=False),
        sa.Column("previous_owner_membership_id", sa.UUID(), nullable=True),
        sa.Column("new_owner_membership_id", sa.UUID(), nullable=False),
        sa.Column("changed_by_membership_id", sa.UUID(), nullable=False),
        sa.Column("rationale", sa.String(2000), nullable=False),
        sa.Column("changed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("command_id", sa.UUID(), nullable=False),
        sa.Column("idempotency_key", sa.UUID(), nullable=False),
        sa.Column("correlation_id", sa.UUID(), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id", "previous_owner_membership_id"],
            ["tenant_memberships.tenant_id", "tenant_memberships.id"],
            name="fk_owner_changes__previous_owner",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id", "new_owner_membership_id"],
            ["tenant_memberships.tenant_id", "tenant_memberships.id"],
            name="fk_owner_changes__new_owner",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id", "changed_by_membership_id"],
            ["tenant_memberships.tenant_id", "tenant_memberships.id"],
            name="fk_owner_changes__actor",
            ondelete="RESTRICT",
        ),
        sa.UniqueConstraint("tenant_id", "id", name="uq_owner_changes__tenant_id"),
        sa.UniqueConstraint(
            "tenant_id",
            "changed_by_membership_id",
            "idempotency_key",
            name="uq_owner_changes__idempotency",
        ),
        sa.CheckConstraint("action IN ('DESIGNATED', 'TRANSFERRED')", name="action"),
        sa.CheckConstraint(
            "(action = 'DESIGNATED' AND previous_owner_membership_id IS NULL) OR "
            "(action = 'TRANSFERRED' AND previous_owner_membership_id IS NOT NULL)",
            name="previous_owner_required",
        ),
    )


def downgrade() -> None:
    op.drop_table("tenant_owner_changes")
    op.drop_index("ux_tenant_owners__active_membership", table_name="tenant_owners")
    op.create_unique_constraint(
        "uq_tenant_owners__membership", "tenant_owners", ["tenant_id", "membership_id"]
    )
    op.drop_column("tenant_owners", "ended_at")
