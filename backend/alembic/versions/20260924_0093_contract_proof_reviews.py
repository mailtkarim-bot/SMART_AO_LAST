"""Persist explicit human review acts for contract proofs."""
# ruff: noqa: E501
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision = "20260924_0093"
down_revision = "20260924_0092"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None

def upgrade() -> None:
    op.create_table(
        "contract_proof_reviews",
        sa.Column("id", sa.UUID(), primary_key=True), sa.Column("tenant_id", sa.UUID(), nullable=False),
        sa.Column("proof_id", sa.UUID(), nullable=False), sa.Column("reviewer_id", sa.UUID(), nullable=False),
        sa.Column("reviewed_revision", sa.Integer(), nullable=False), sa.Column("decision", sa.String(32), nullable=False),
        sa.Column("rationale", sa.Text(), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["tenant_id", "proof_id"], ["contract_baseline_deviation_impacts.tenant_id", "contract_baseline_deviation_impacts.id"], ondelete="RESTRICT"),
        sa.UniqueConstraint("tenant_id", "id", name="uq_contract_proof_reviews__tenant_id"),
        sa.UniqueConstraint("tenant_id", "proof_id", "reviewed_revision", name="uq_contract_proof_reviews__functional"),
        sa.CheckConstraint("reviewed_revision > 0", name="contract_review_revision_positive"),
        sa.CheckConstraint("decision IN ('ACCEPTED', 'REJECTED', 'NEEDS_CLARIFICATION')", name="contract_review_decision_closed"),
    )

def downgrade() -> None:
    op.drop_table("contract_proof_reviews")
