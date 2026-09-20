"""Persist version-pinned, revocable resource shares."""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision = "20260920_0089"
down_revision = "20260920_0088"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "tenant_resource_shares",
        sa.Column("id", sa.UUID(), primary_key=True),
        sa.Column("tenant_id", sa.UUID(), nullable=False),
        sa.Column("resource_type", sa.String(64), nullable=False),
        sa.Column("resource_id", sa.UUID(), nullable=False),
        sa.Column("resource_fingerprint", sa.CHAR(64), nullable=False),
        sa.Column("recipient_ref", sa.String(320), nullable=False),
        sa.Column("purpose", sa.String(500), nullable=False),
        sa.Column("classification", sa.String(64), nullable=False),
        sa.Column("access_token_hash", sa.CHAR(64), nullable=False),
        sa.Column("starts_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("state", sa.String(16), nullable=False),
        sa.Column("created_by_membership_id", sa.UUID(), nullable=False),
        sa.Column("command_id", sa.UUID(), nullable=False),
        sa.Column("idempotency_key", sa.UUID(), nullable=False),
        sa.Column("correlation_id", sa.UUID()),
        sa.Column("revoked_at", sa.DateTime(timezone=True)),
        sa.Column("revoke_reason", sa.String(500)),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id", "created_by_membership_id"],
            ["tenant_memberships.tenant_id", "tenant_memberships.id"],
            name="fk_resource_shares__creator",
            ondelete="RESTRICT",
        ),
        sa.UniqueConstraint("tenant_id", "id", name="uq_resource_shares__tenant_id"),
        sa.UniqueConstraint(
            "tenant_id",
            "created_by_membership_id",
            "idempotency_key",
            name="uq_resource_shares__idempotency",
        ),
        sa.CheckConstraint("state IN ('ACTIVE', 'REVOKED', 'EXPIRED')", name="state"),
        sa.CheckConstraint("expires_at > starts_at", name="expiry"),
        sa.CheckConstraint("length(trim(recipient_ref)) > 0", name="recipient"),
    )
    op.create_table(
        "tenant_resource_share_events",
        sa.Column("id", sa.UUID(), primary_key=True),
        sa.Column("tenant_id", sa.UUID(), nullable=False),
        sa.Column("share_id", sa.UUID(), nullable=False),
        sa.Column("event_type", sa.String(16), nullable=False),
        sa.Column("actor_membership_id", sa.UUID()),
        sa.Column("recipient_ref", sa.String(320)),
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("command_id", sa.UUID(), nullable=False),
        sa.Column("reason", sa.String(500), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id", "share_id"],
            ["tenant_resource_shares.tenant_id", "tenant_resource_shares.id"],
            name="fk_resource_share_events__share",
            ondelete="RESTRICT",
        ),
        sa.UniqueConstraint("tenant_id", "id", name="uq_resource_share_events__tenant_id"),
        sa.UniqueConstraint(
            "tenant_id",
            "share_id",
            "event_type",
            "command_id",
            name="uq_resource_share_events__command",
        ),
        sa.CheckConstraint(
            "event_type IN ('CREATED', 'ACCESSED', 'REVOKED', 'EXPIRED')", name="event_type"
        ),
    )


def downgrade() -> None:
    op.drop_table("tenant_resource_share_events")
    op.drop_table("tenant_resource_shares")
