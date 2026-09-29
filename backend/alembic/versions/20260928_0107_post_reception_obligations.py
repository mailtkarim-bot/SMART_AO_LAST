"""Create tenant-scoped append-only post-reception obligations."""
# ruff: noqa: E501
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB

revision = "20260928_0107"
down_revision = "20260928_0106"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "post_reception_obligations",
        sa.Column("id", sa.UUID(), primary_key=True),
        sa.Column("tenant_id", sa.UUID(), nullable=False),
        sa.Column("case_id", sa.UUID(), nullable=False),
        sa.Column("obligation_type", sa.String(32), nullable=False),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column("source_refs_json", JSONB(), nullable=False),
        sa.Column("due_date", sa.Date(), nullable=True),
        sa.Column("resource_note", sa.Text(), nullable=True),
        sa.Column("cost_estimate_note", sa.Text(), nullable=True),
        sa.Column("fulfillment_proof_refs_json", JSONB(), nullable=False, server_default="[]"),
        sa.Column("sanction_ref", sa.Text(), nullable=True),
        sa.Column("status", sa.String(24), nullable=False, server_default="REVIEW_REQUIRED"),
        sa.Column("actor_id", sa.UUID(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["tenant_id", "case_id"], ["cases.tenant_id", "cases.id"], ondelete="RESTRICT"),
        sa.UniqueConstraint("tenant_id", "id", name="uq_post_reception_obligations__tenant_id"),
        sa.CheckConstraint(
            "obligation_type IN ('OPR', 'TESTS', 'COMMISSIONING', 'TRAINING', 'DOE_DIUO', 'RESERVES_LIFTING', 'GPA', 'INITIAL_MAINTENANCE', 'SPARE_STOCK', 'ON_CALL', 'ADMIN_CLOSURE', 'GUARANTEE_RELEASE')",
            name="post_reception_obligation_type_closed",
        ),
        sa.CheckConstraint("status = 'REVIEW_REQUIRED'", name="post_reception_obligation_initial_status"),
        sa.CheckConstraint("jsonb_array_length(source_refs_json) > 0", name="post_reception_obligation_source_required"),
        sa.Index("ix_post_reception_obligations_tenant_case_created", "tenant_id", "case_id", "created_at"),
    )
    op.execute(
        """
        CREATE FUNCTION reject_post_reception_obligation_mutation() RETURNS trigger AS $$
        BEGIN
            RAISE EXCEPTION 'post reception obligations are append-only';
        END;
        $$ LANGUAGE plpgsql;
        """
    )
    op.execute(
        """
        CREATE TRIGGER post_reception_obligations_append_only
        BEFORE UPDATE OR DELETE ON post_reception_obligations
        FOR EACH ROW EXECUTE FUNCTION reject_post_reception_obligation_mutation();
        """
    )


def downgrade() -> None:
    op.execute("DROP TRIGGER IF EXISTS post_reception_obligations_append_only ON post_reception_obligations")
    op.execute("DROP FUNCTION IF EXISTS reject_post_reception_obligation_mutation()")
    op.drop_table("post_reception_obligations")
