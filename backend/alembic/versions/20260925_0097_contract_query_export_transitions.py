"""Persist append-only local export state transitions."""
# ruff: noqa: E501
from collections.abc import Sequence
import sqlalchemy as sa
from alembic import op
revision = "20260925_0097"
down_revision = "20260925_0096"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None

def upgrade() -> None:
    op.create_table("contract_query_export_transitions", sa.Column("id", sa.UUID(), primary_key=True), sa.Column("tenant_id", sa.UUID(), nullable=False), sa.Column("export_id", sa.UUID(), nullable=False), sa.Column("from_status", sa.String(16), nullable=False), sa.Column("to_status", sa.String(16), nullable=False), sa.Column("local_proof_ref", sa.String(255)), sa.Column("actor_id", sa.UUID(), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()), sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()), sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="RESTRICT"), sa.ForeignKeyConstraint(["tenant_id", "export_id"], ["contract_query_exports.tenant_id", "contract_query_exports.id"], ondelete="RESTRICT"), sa.UniqueConstraint("tenant_id", "id", name="uq_contract_query_export_transitions__tenant_id"), sa.CheckConstraint("from_status IN ('REQUESTED', 'READY', 'UNKNOWN', 'REFUSED')", name="contract_export_transition_from_closed"), sa.CheckConstraint("to_status IN ('REQUESTED', 'READY', 'UNKNOWN', 'REFUSED')", name="contract_export_transition_to_closed"))

def downgrade() -> None:
    op.drop_table("contract_query_export_transitions")
