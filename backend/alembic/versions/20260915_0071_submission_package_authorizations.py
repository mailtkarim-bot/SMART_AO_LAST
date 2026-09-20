"""Add append-only P5 authorization facts for immutable submission packages.

Revision ID: 20260915_0071
Revises: 20260914_0070
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "20260915_0071"
down_revision = "20260914_0070"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "submission_package_authorizations",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column("submission_package_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("package_version", sa.Integer, nullable=False),
        sa.Column("manifest_sha256", sa.CHAR(length=64), nullable=False),
        sa.Column("state", sa.String(length=16), nullable=False),
        sa.Column("rationale", sa.String(length=2000), nullable=False),
        sa.Column("actor_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("membership_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("command_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("idempotency_key", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("correlation_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["tenant_id"],
            ["tenants.id"],
            name="fk_submission_authorization__tenant",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id", "submission_package_id"],
            ["submission_packages.tenant_id", "submission_packages.id"],
            name="fk_submission_authorization__package",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_submission_package_authorizations"),
        sa.UniqueConstraint("tenant_id", "id", name="uq_submission_authorization__tenant_id"),
        sa.UniqueConstraint("tenant_id", "command_id", name="uq_submission_authorization__command"),
        sa.UniqueConstraint(
            "tenant_id",
            "submission_package_id",
            "package_version",
            name="uq_submission_authorization__package_version",
        ),
        sa.CheckConstraint("package_version > 0", name="package_version_positive"),
        sa.CheckConstraint("manifest_sha256 ~ '^[a-f0-9]{64}$'", name="manifest_sha256"),
        sa.CheckConstraint("state = 'AUTHORIZED'", name="state"),
    )
    op.create_index(
        "ix_submission_authorizations_tenant_id",
        "submission_package_authorizations",
        ["tenant_id"],
    )
    op.create_index(
        "ix_submission_authorizations__tenant_package",
        "submission_package_authorizations",
        ["tenant_id", "submission_package_id"],
    )
    op.execute(
        """
        CREATE FUNCTION prevent_submission_package_authorization_mutation()
        RETURNS trigger LANGUAGE plpgsql AS $$
        BEGIN
          RAISE EXCEPTION 'submission package authorizations are append-only';
        END;
        $$
        """
    )
    op.execute(
        """
        CREATE TRIGGER submission_package_authorizations_append_only
        BEFORE UPDATE OR DELETE ON submission_package_authorizations
        FOR EACH ROW EXECUTE FUNCTION prevent_submission_package_authorization_mutation();
        """
    )


def downgrade() -> None:
    op.execute(
        """
        DROP TRIGGER IF EXISTS submission_package_authorizations_append_only
        ON submission_package_authorizations
        """
    )
    op.execute("DROP FUNCTION IF EXISTS prevent_submission_package_authorization_mutation()")
    op.drop_index(
        "ix_submission_authorizations__tenant_package",
        table_name="submission_package_authorizations",
    )
    op.drop_index(
        "ix_submission_authorizations_tenant_id",
        table_name="submission_package_authorizations",
    )
    op.drop_table("submission_package_authorizations")
