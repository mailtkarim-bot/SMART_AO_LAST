"""Persist bounded nominative delegations and their append-only events."""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB

revision = "20260920_0087"
down_revision = "20260920_0086"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "tenant_delegations",
        sa.Column("id", sa.UUID(), primary_key=True),
        sa.Column("tenant_id", sa.UUID(), nullable=False),
        sa.Column("delegator_membership_id", sa.UUID(), nullable=False),
        sa.Column("delegatee_membership_id", sa.UUID(), nullable=False),
        sa.Column("capabilities_json", JSONB(), nullable=False),
        sa.Column("doors_json", JSONB(), nullable=False),
        sa.Column("case_ids_json", JSONB(), nullable=False),
        sa.Column("starts_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("state", sa.String(16), nullable=False),
        sa.Column("rationale", sa.String(2000), nullable=False),
        sa.Column("command_id", sa.UUID(), nullable=False),
        sa.Column("idempotency_key", sa.UUID(), nullable=False),
        sa.Column("correlation_id", sa.UUID(), nullable=True),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("revoke_reason", sa.String(64), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id", "delegator_membership_id"],
            ["tenant_memberships.tenant_id", "tenant_memberships.id"],
            name="fk_delegations__delegator",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id", "delegatee_membership_id"],
            ["tenant_memberships.tenant_id", "tenant_memberships.id"],
            name="fk_delegations__delegatee",
            ondelete="RESTRICT",
        ),
        sa.UniqueConstraint("tenant_id", "id", name="uq_delegations__tenant_id"),
        sa.UniqueConstraint(
            "tenant_id",
            "delegator_membership_id",
            "idempotency_key",
            name="uq_delegations__idempotency",
        ),
        sa.CheckConstraint("state IN ('ACTIVE', 'REVOKED', 'EXPIRED')", name="state"),
        sa.CheckConstraint("jsonb_typeof(capabilities_json) = 'array'", name="capabilities"),
        sa.CheckConstraint("jsonb_typeof(doors_json) = 'array'", name="doors"),
        sa.CheckConstraint("jsonb_typeof(case_ids_json) = 'array'", name="case_ids"),
        sa.CheckConstraint("expires_at > starts_at", name="expiry"),
        sa.CheckConstraint(
            "(state = 'ACTIVE' AND revoked_at IS NULL) OR "
            "(state IN ('REVOKED', 'EXPIRED') AND revoked_at IS NOT NULL)",
            name="revocation",
        ),
    )
    op.create_table(
        "tenant_delegation_events",
        sa.Column("id", sa.UUID(), primary_key=True),
        sa.Column("tenant_id", sa.UUID(), nullable=False),
        sa.Column("delegation_id", sa.UUID(), nullable=False),
        sa.Column("event_type", sa.String(16), nullable=False),
        sa.Column("actor_membership_id", sa.UUID(), nullable=False),
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("command_id", sa.UUID(), nullable=False),
        sa.Column("reason", sa.String(2000), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id", "delegation_id"],
            ["tenant_delegations.tenant_id", "tenant_delegations.id"],
            name="fk_delegation_events__delegation",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id", "actor_membership_id"],
            ["tenant_memberships.tenant_id", "tenant_memberships.id"],
            name="fk_delegation_events__actor",
            ondelete="RESTRICT",
        ),
        sa.UniqueConstraint("tenant_id", "id", name="uq_delegation_events__tenant_id"),
        sa.UniqueConstraint(
            "tenant_id",
            "delegation_id",
            "event_type",
            "command_id",
            name="uq_delegation_events__command",
        ),
        sa.CheckConstraint("event_type IN ('GRANTED', 'REVOKED')", name="event_type"),
    )


def downgrade() -> None:
    op.drop_table("tenant_delegation_events")
    op.drop_table("tenant_delegations")
