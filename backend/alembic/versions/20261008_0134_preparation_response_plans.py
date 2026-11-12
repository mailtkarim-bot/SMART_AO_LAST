"""Add immutable, versioned response plans to preparation packages."""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "20261008_0134"
down_revision = "20261007_0133"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "preparation_response_plans",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column("plan_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("package_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("dce_version_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("state", sa.String(length=24), nullable=False),
        sa.Column("content_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("plan_sha256", sa.CHAR(length=64), nullable=False),
        sa.Column("source_evidence_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("source_evidence_sha256", sa.CHAR(length=64), nullable=False),
        sa.Column("actor_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("membership_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("command_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("idempotency_key", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("correlation_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["tenant_id"], ["tenants.id"], name="fk_response_plan__tenant", ondelete="RESTRICT"
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id", "package_id"],
            ["preparation_packages.tenant_id", "preparation_packages.id"],
            name="fk_response_plan__package",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id", "dce_version_id"],
            ["dce_versions.tenant_id", "dce_versions.id"],
            name="fk_response_plan__dce_version",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id", "membership_id"],
            ["tenant_memberships.tenant_id", "tenant_memberships.id"],
            name="fk_response_plan__membership",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_preparation_response_plans"),
        sa.UniqueConstraint("tenant_id", "id", name="uq_response_plan__tenant_id"),
        sa.UniqueConstraint("tenant_id", "command_id", name="uq_response_plan__command"),
        sa.UniqueConstraint(
            "tenant_id", "package_id", "plan_id", "version", name="uq_response_plan__version"
        ),
        sa.CheckConstraint("version > 0", name="version_positive"),
        sa.CheckConstraint("state IN ('UNKNOWN', 'SOURCES_CURRENT')", name="state"),
        sa.CheckConstraint("plan_sha256 ~ '^[0-9a-f]{64}$'", name="plan_sha256"),
        sa.CheckConstraint(
            "source_evidence_sha256 ~ '^[0-9a-f]{64}$'", name="source_evidence_sha256"
        ),
    )
    op.add_column(
        "technical_response_drafts",
        sa.Column("response_plan_id", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.add_column(
        "technical_response_drafts",
        sa.Column("response_plan_version", sa.Integer(), nullable=True),
    )
    op.create_check_constraint(
        "ck_technical_response_drafts__response_plan_pair",
        "technical_response_drafts",
        "(response_plan_id IS NULL AND response_plan_version IS NULL) OR "
        "(response_plan_id IS NOT NULL AND response_plan_version IS NOT NULL)",
    )
    op.create_foreign_key(
        "fk_technical_draft__response_plan",
        "technical_response_drafts",
        "preparation_response_plans",
        ["tenant_id", "package_id", "response_plan_id", "response_plan_version"],
        ["tenant_id", "package_id", "plan_id", "version"],
        ondelete="RESTRICT",
    )
    op.create_index(
        "ix_preparation_response_plans_tenant_id", "preparation_response_plans", ["tenant_id"]
    )
    op.create_index(
        "ix_response_plans__tenant_package_version",
        "preparation_response_plans",
        ["tenant_id", "package_id", "version"],
    )
    op.execute(
        """
        CREATE FUNCTION preparation_response_plans_append_only() RETURNS trigger
        LANGUAGE plpgsql AS $$
        BEGIN
            RAISE EXCEPTION 'preparation response plans are append-only';
        END;
        $$;
        """
    )
    op.execute(
        """
        CREATE TRIGGER preparation_response_plans_append_only
        BEFORE UPDATE OR DELETE ON preparation_response_plans
        FOR EACH ROW EXECUTE FUNCTION preparation_response_plans_append_only();
        """
    )


def downgrade() -> None:
    op.drop_constraint(
        "fk_technical_draft__response_plan", "technical_response_drafts", type_="foreignkey"
    )
    op.drop_constraint(
        "ck_technical_response_drafts__response_plan_pair",
        "technical_response_drafts",
        type_="check",
    )
    op.drop_column("technical_response_drafts", "response_plan_version")
    op.drop_column("technical_response_drafts", "response_plan_id")
    op.execute(
        "DROP TRIGGER IF EXISTS preparation_response_plans_append_only "
        "ON preparation_response_plans"
    )
    op.execute("DROP FUNCTION IF EXISTS preparation_response_plans_append_only()")
    op.drop_index(
        "ix_response_plans__tenant_package_version", table_name="preparation_response_plans"
    )
    op.drop_index(
        "ix_preparation_response_plans_tenant_id", table_name="preparation_response_plans"
    )
    op.drop_table("preparation_response_plans")
