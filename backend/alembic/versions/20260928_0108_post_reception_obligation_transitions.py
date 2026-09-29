"""Append human post-reception obligation transitions with proof on completion."""
# ruff: noqa: E501
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB

revision = "20260928_0108"
down_revision = "20260928_0107"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "post_reception_obligation_transitions",
        sa.Column("id", sa.UUID(), primary_key=True),
        sa.Column("tenant_id", sa.UUID(), nullable=False),
        sa.Column("obligation_id", sa.UUID(), nullable=False),
        sa.Column("revision", sa.Integer(), nullable=False),
        sa.Column("previous_status", sa.String(32), nullable=False),
        sa.Column("resulting_status", sa.String(32), nullable=False),
        sa.Column("evidence_refs_json", JSONB(), nullable=False, server_default="[]"),
        sa.Column("rationale", sa.Text(), nullable=False),
        sa.Column("actor_id", sa.UUID(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["tenant_id", "obligation_id"], ["post_reception_obligations.tenant_id", "post_reception_obligations.id"], ondelete="RESTRICT"),
        sa.UniqueConstraint("tenant_id", "id", name="uq_post_reception_obligation_transitions__tenant_id"),
        sa.UniqueConstraint("tenant_id", "obligation_id", "revision", name="uq_post_reception_obligation_transitions__revision"),
        sa.CheckConstraint("revision > 0", name="post_reception_obligation_transition_revision_positive"),
        sa.CheckConstraint("previous_status IN ('REVIEW_REQUIRED', 'IN_PROGRESS', 'FOLLOW_UP_REQUIRED', 'UNKNOWN')", name="post_reception_obligation_transition_previous_closed"),
        sa.CheckConstraint("resulting_status IN ('IN_PROGRESS', 'FOLLOW_UP_REQUIRED', 'UNKNOWN', 'COMPLETED')", name="post_reception_obligation_transition_result_closed"),
        sa.CheckConstraint("resulting_status != 'COMPLETED' OR jsonb_array_length(evidence_refs_json) > 0", name="post_reception_obligation_completion_requires_proof"),
        sa.Index("ix_post_rec_obl_tenant_obligation_revision", "tenant_id", "obligation_id", "revision"),
    )
    op.execute(
        """
        CREATE FUNCTION reject_post_reception_obligation_transition_mutation() RETURNS trigger AS $$
        BEGIN
            RAISE EXCEPTION 'post reception obligation transitions are append-only';
        END;
        $$ LANGUAGE plpgsql;
        """
    )
    op.execute(
        """
        CREATE TRIGGER post_reception_obligation_transitions_append_only
        BEFORE UPDATE OR DELETE ON post_reception_obligation_transitions
        FOR EACH ROW EXECUTE FUNCTION reject_post_reception_obligation_transition_mutation();
        """
    )


def downgrade() -> None:
    op.execute("DROP TRIGGER IF EXISTS post_reception_obligation_transitions_append_only ON post_reception_obligation_transitions")
    op.execute("DROP FUNCTION IF EXISTS reject_post_reception_obligation_transition_mutation()")
    op.drop_table("post_reception_obligation_transitions")
