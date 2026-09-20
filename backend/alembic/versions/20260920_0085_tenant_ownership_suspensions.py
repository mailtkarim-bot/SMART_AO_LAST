"""Separate organization ownership from Patron role and audit membership suspension."""

from collections.abc import Sequence
from uuid import uuid4

import sqlalchemy as sa
from alembic import op

revision = "20260920_0085"
down_revision = "20260920_0084"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.drop_index("ux_memberships__active_patron", table_name="tenant_memberships")
    op.create_table(
        "tenant_owners",
        sa.Column("id", sa.UUID(), primary_key=True),
        sa.Column("tenant_id", sa.UUID(), nullable=False),
        sa.Column("membership_id", sa.UUID(), nullable=False),
        sa.Column("designated_by_membership_id", sa.UUID(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id", "membership_id"],
            ["tenant_memberships.tenant_id", "tenant_memberships.id"],
            name="fk_tenant_owners__membership",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id", "designated_by_membership_id"],
            ["tenant_memberships.tenant_id", "tenant_memberships.id"],
            name="fk_tenant_owners__designator",
            ondelete="RESTRICT",
        ),
        sa.UniqueConstraint("tenant_id", "membership_id", name="uq_tenant_owners__membership"),
        sa.UniqueConstraint("tenant_id", "id", name="uq_tenant_owners__tenant_id"),
    )
    op.create_table(
        "membership_suspensions",
        sa.Column("id", sa.UUID(), primary_key=True),
        sa.Column("tenant_id", sa.UUID(), nullable=False),
        sa.Column("membership_id", sa.UUID(), nullable=False),
        sa.Column("suspended_by_membership_id", sa.UUID(), nullable=False),
        sa.Column("reason_code", sa.String(64), nullable=False),
        sa.Column("rationale", sa.String(2000), nullable=False),
        sa.Column("suspended_at", sa.DateTime(timezone=True), nullable=False),
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
            ["tenant_id", "membership_id"],
            ["tenant_memberships.tenant_id", "tenant_memberships.id"],
            name="fk_membership_suspensions__membership",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id", "suspended_by_membership_id"],
            ["tenant_memberships.tenant_id", "tenant_memberships.id"],
            name="fk_membership_suspensions__suspender",
            ondelete="RESTRICT",
        ),
        sa.UniqueConstraint("tenant_id", "id", name="uq_membership_suspensions__tenant_id"),
        sa.UniqueConstraint(
            "tenant_id",
            "suspended_by_membership_id",
            "idempotency_key",
            name="uq_membership_suspensions__idempotency",
        ),
        sa.CheckConstraint("reason_code ~ '^[A-Z0-9_]+$'", name="reason_code"),
    )
    bind = op.get_bind()
    patrons = bind.execute(
        sa.text(
            "SELECT tenant_id, id FROM tenant_memberships "
            "WHERE role = 'PATRON_ADMIN' AND state = 'ACTIVE'"
        )
    ).mappings()
    owner_table = sa.table(
        "tenant_owners",
        sa.column("id", sa.UUID()),
        sa.column("tenant_id", sa.UUID()),
        sa.column("membership_id", sa.UUID()),
        sa.column("designated_by_membership_id", sa.UUID()),
    )
    for patron in patrons:
        bind.execute(
            owner_table.insert().values(
                id=uuid4(),
                tenant_id=patron["tenant_id"],
                membership_id=patron["id"],
                designated_by_membership_id=patron["id"],
            )
        )


def downgrade() -> None:
    op.drop_table("membership_suspensions")
    op.drop_table("tenant_owners")
    op.execute(
        """
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1
                FROM tenant_memberships
                WHERE role = 'PATRON_ADMIN' AND state = 'ACTIVE'
                GROUP BY tenant_id
                HAVING count(*) > 1
            ) THEN
                CREATE UNIQUE INDEX ux_memberships__active_patron
                ON tenant_memberships (tenant_id)
                WHERE role = 'PATRON_ADMIN' AND state = 'ACTIVE';
            ELSE
                CREATE INDEX ux_memberships__active_patron
                ON tenant_memberships (tenant_id)
                WHERE role = 'PATRON_ADMIN' AND state = 'ACTIVE';
            END IF;
        END $$;
        """
    )
