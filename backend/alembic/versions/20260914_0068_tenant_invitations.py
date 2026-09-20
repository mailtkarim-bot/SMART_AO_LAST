"""Create nominative tenant invitations.

Revision ID: 20260914_0068
Revises: 20260826_0067
Create Date: 2026-09-14
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "20260914_0068"
down_revision = "20260826_0067"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "tenant_invitations",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("membership_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("token_hash", sa.CHAR(length=64), nullable=False),
        sa.Column("issued_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("reissued_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("accepted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.CheckConstraint("token_hash ~ '^[a-f0-9]{64}$'", name="token_hash"),
        sa.CheckConstraint("expires_at > issued_at", name="expiry"),
        sa.CheckConstraint(
            "reissued_at IS NULL OR reissued_at >= issued_at",
            name="reissued_at",
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id", "membership_id"],
            ["tenant_memberships.tenant_id", "tenant_memberships.id"],
            name="fk_invitations__membership",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_tenant_invitations"),
        sa.UniqueConstraint(
            "tenant_id", "membership_id", name="uq_invitations__membership"
        ),
        sa.UniqueConstraint("token_hash", name="uq_invitations__token_hash"),
    )
    op.create_index(
        "ix_tenant_invitations_tenant_id",
        "tenant_invitations",
        ["tenant_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_tenant_invitations_tenant_id", table_name="tenant_invitations")
    op.drop_table("tenant_invitations")
