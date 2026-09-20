"""Persist nominative handover acceptance and bounded R03 recovery proofs."""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB

revision = "20260920_0088"
down_revision = "20260920_0087"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "tenant_handovers",
        sa.Column("id", sa.UUID(), primary_key=True),
        sa.Column("tenant_id", sa.UUID(), nullable=False),
        sa.Column("requested_by_membership_id", sa.UUID(), nullable=False),
        sa.Column("successor_membership_id", sa.UUID(), nullable=False),
        sa.Column("assignment_ids_json", JSONB(), nullable=False),
        sa.Column("state", sa.String(16), nullable=False),
        sa.Column("rationale", sa.String(2000), nullable=False),
        sa.Column("requested_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("accepted_at", sa.DateTime(timezone=True)),
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
            ["tenant_id", "requested_by_membership_id"],
            ["tenant_memberships.tenant_id", "tenant_memberships.id"],
            name="fk_handovers__requester",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id", "successor_membership_id"],
            ["tenant_memberships.tenant_id", "tenant_memberships.id"],
            name="fk_handovers__successor",
            ondelete="RESTRICT",
        ),
        sa.UniqueConstraint("tenant_id", "id", name="uq_handovers__tenant_id"),
        sa.UniqueConstraint(
            "tenant_id",
            "requested_by_membership_id",
            "idempotency_key",
            name="uq_handovers__idempotency",
        ),
        sa.CheckConstraint(
            "state IN ('REQUESTED', 'ACCEPTED', 'REFUSED', 'EXPIRED')", name="state"
        ),
        sa.CheckConstraint("jsonb_typeof(assignment_ids_json) = 'array'", name="assignment_ids"),
    )
    op.create_table(
        "tenant_handover_events",
        sa.Column("id", sa.UUID(), primary_key=True),
        sa.Column("tenant_id", sa.UUID(), nullable=False),
        sa.Column("handover_id", sa.UUID(), nullable=False),
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
            ["tenant_id", "handover_id"],
            ["tenant_handovers.tenant_id", "tenant_handovers.id"],
            name="fk_handover_events__handover",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id", "actor_membership_id"],
            ["tenant_memberships.tenant_id", "tenant_memberships.id"],
            name="fk_handover_events__actor",
            ondelete="RESTRICT",
        ),
        sa.UniqueConstraint("tenant_id", "id", name="uq_handover_events__tenant_id"),
        sa.UniqueConstraint(
            "tenant_id",
            "handover_id",
            "event_type",
            "command_id",
            name="uq_handover_events__command",
        ),
        sa.CheckConstraint("event_type IN ('REQUESTED', 'ACCEPTED', 'REFUSED')", name="event_type"),
    )
    op.create_table(
        "tenant_recoveries",
        sa.Column("id", sa.UUID(), primary_key=True),
        sa.Column("tenant_id", sa.UUID(), nullable=False),
        sa.Column("target_membership_id", sa.UUID(), nullable=False),
        sa.Column("first_support_membership_id", sa.UUID(), nullable=False),
        sa.Column("second_support_membership_id", sa.UUID(), nullable=False),
        sa.Column("authority_evidence_ref", sa.String(500), nullable=False),
        sa.Column("approval_ref", sa.String(500), nullable=False),
        sa.Column("status", sa.String(16), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=False),
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
            ["tenant_id", "target_membership_id"],
            ["tenant_memberships.tenant_id", "tenant_memberships.id"],
            name="fk_recoveries__target",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id", "first_support_membership_id"],
            ["tenant_memberships.tenant_id", "tenant_memberships.id"],
            name="fk_recoveries__first_support",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id", "second_support_membership_id"],
            ["tenant_memberships.tenant_id", "tenant_memberships.id"],
            name="fk_recoveries__second_support",
            ondelete="RESTRICT",
        ),
        sa.UniqueConstraint("tenant_id", "id", name="uq_recoveries__tenant_id"),
        sa.UniqueConstraint(
            "tenant_id",
            "first_support_membership_id",
            "idempotency_key",
            name="uq_recoveries__idempotency",
        ),
        sa.CheckConstraint("status IN ('COMPLETED', 'REFUSED')", name="status"),
    )


def downgrade() -> None:
    op.drop_table("tenant_recoveries")
    op.drop_table("tenant_handover_events")
    op.drop_table("tenant_handovers")
