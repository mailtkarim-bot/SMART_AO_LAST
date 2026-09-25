"""Persist append-only local export proof verifications."""
# ruff: noqa: E501
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision = "20260925_0099"
down_revision = "20260925_0098"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None

def upgrade() -> None:
    op.create_table("export_proof_verifications", sa.Column("id", sa.UUID(), primary_key=True), sa.Column("tenant_id", sa.UUID(), nullable=False), sa.Column("export_id", sa.UUID(), nullable=False), sa.Column("outcome", sa.String(16), nullable=False), sa.Column("calculated_sha256", sa.String(64)), sa.Column("checked_by_actor_id", sa.UUID(), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()), sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()), sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="RESTRICT"), sa.ForeignKeyConstraint(["tenant_id", "export_id"], ["contract_query_exports.tenant_id", "contract_query_exports.id"], ondelete="RESTRICT"), sa.UniqueConstraint("tenant_id", "id", name="uq_export_proof_verifications__tenant_id"), sa.CheckConstraint("outcome IN ('MATCH', 'MISMATCH', 'UNAVAILABLE')", name="export_proof_verification_outcome_closed"))

def downgrade() -> None:
    op.drop_table("export_proof_verifications")
