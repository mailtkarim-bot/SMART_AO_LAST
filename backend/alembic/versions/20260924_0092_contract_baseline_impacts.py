"""Persist source-bound baseline/deviation/impact proofs."""

from collections.abc import Sequence
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB

revision = "20260924_0092"
down_revision = "20260924_0091"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "contract_baseline_deviation_impacts",
        sa.Column("id", sa.UUID(), primary_key=True),
        sa.Column("tenant_id", sa.UUID(), nullable=False),
        sa.Column("case_id", sa.UUID(), nullable=False),
        sa.Column("baseline_observation_id", sa.UUID(), nullable=False),
        sa.Column("proof_revision", sa.Integer(), nullable=False),
        sa.Column("baseline_source_refs_json", JSONB(), nullable=False),
        sa.Column("baseline_statement", sa.Text(), nullable=False),
        sa.Column("deviation_statement", sa.Text()),
        sa.Column("impact_statement", sa.Text()),
        sa.Column("status", sa.String(32), nullable=False),
        sa.Column("created_by_actor_id", sa.UUID()),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(
            ["tenant_id", "case_id"], ["cases.tenant_id", "cases.id"], ondelete="RESTRICT"
        ),
        sa.UniqueConstraint("tenant_id", "id", name="uq_contract_baseline_impacts__tenant_id"),
        sa.UniqueConstraint(
            "tenant_id",
            "case_id",
            "baseline_observation_id",
            "proof_revision",
            name="uq_contract_baseline_impacts__functional",
        ),
        sa.CheckConstraint("proof_revision > 0", name="contract_proof_revision_positive"),
        sa.CheckConstraint(
            "status IN ('SOURCE_SIGNAL_ONLY', 'HUMAN_REVIEW_REQUIRED', 'CONFIRMED', 'UNKNOWN')",
            name="contract_assessment_status_closed",
        ),
        sa.CheckConstraint(
            "jsonb_array_length(baseline_source_refs_json) > 0",
            name="contract_baseline_sources_nonempty",
        ),
    )


def downgrade() -> None:
    op.drop_table("contract_baseline_deviation_impacts")
