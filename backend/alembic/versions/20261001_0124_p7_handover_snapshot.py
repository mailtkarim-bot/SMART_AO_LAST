"""Persist exact, finance-redacted P7 handover snapshots."""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "20261001_0124"
down_revision = "20261001_0123"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "case_handover_snapshots",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("case_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("outcome_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("lot_reference", sa.String(120), nullable=False),
        sa.Column("submission_package_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("package_version", sa.Integer(), nullable=False),
        sa.Column("manifest_sha256", sa.CHAR(64), nullable=False),
        sa.Column("revision", sa.Integer(), nullable=False),
        sa.Column("snapshot_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("actor_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("membership_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("command_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("idempotency_key", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("correlation_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id", "case_id"],
            ["cases.tenant_id", "cases.id"],
            name="fk_case_handover_snapshots__case",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id", "outcome_id"],
            ["case_outcomes.tenant_id", "case_outcomes.id"],
            name="fk_case_handover_snapshots__outcome",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id", "submission_package_id"],
            ["submission_packages.tenant_id", "submission_packages.id"],
            name="fk_case_handover_snapshots__package",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("tenant_id", "id", name="uq_case_handover_snapshots__tenant_id_id"),
        sa.UniqueConstraint(
            "tenant_id", "case_id", "id", name="uq_case_handover_snapshots__tenant_case_id"
        ),
        sa.UniqueConstraint("tenant_id", "command_id", name="uq_case_handover_snapshots__command"),
        sa.UniqueConstraint(
            "tenant_id", "idempotency_key", name="uq_case_handover_snapshots__idempotency"
        ),
        sa.UniqueConstraint(
            "tenant_id", "outcome_id", "revision", name="uq_case_handover_snapshots__revision"
        ),
        sa.CheckConstraint("revision > 0", name="ck_case_handover_snapshots__revision_positive"),
        sa.CheckConstraint(
            "package_version > 0", name="ck_case_handover_snapshots__package_version_positive"
        ),
        sa.CheckConstraint(
            "manifest_sha256 ~ '^[a-f0-9]{64}$'", name="ck_case_handover_snapshots__manifest_sha256"
        ),
    )
    op.create_index(
        "ix_case_handover_snapshots__tenant_case",
        "case_handover_snapshots",
        ["tenant_id", "case_id", "created_at"],
    )
    op.execute("""
        CREATE FUNCTION reject_case_handover_snapshot_mutation() RETURNS trigger AS $$
        BEGIN RAISE EXCEPTION 'case_handover_snapshots is append-only'; END;
        $$ LANGUAGE plpgsql;
    """)
    op.execute("""
        CREATE TRIGGER case_handover_snapshots_append_only
        BEFORE UPDATE OR DELETE ON case_handover_snapshots
        FOR EACH ROW EXECUTE FUNCTION reject_case_handover_snapshot_mutation();
    """)


def downgrade() -> None:
    op.execute(
        "DROP TRIGGER IF EXISTS case_handover_snapshots_append_only ON case_handover_snapshots"
    )
    op.execute("DROP FUNCTION IF EXISTS reject_case_handover_snapshot_mutation()")
    op.drop_index("ix_case_handover_snapshots__tenant_case", table_name="case_handover_snapshots")
    op.drop_table("case_handover_snapshots")
