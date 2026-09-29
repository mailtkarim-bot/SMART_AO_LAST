"""Store Patron-declared, proof-backed contract execution acts append-only."""
# ruff: noqa: E501
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB

revision = "20260928_0109"
down_revision = "20260928_0108"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "contract_execution_evidence",
        sa.Column("id", sa.UUID(), primary_key=True),
        sa.Column("tenant_id", sa.UUID(), nullable=False),
        sa.Column("case_id", sa.UUID(), nullable=False),
        sa.Column("act_kind", sa.String(32), nullable=False),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column("source_refs_json", JSONB(), nullable=False),
        sa.Column("evidence_refs_json", JSONB(), nullable=False),
        sa.Column("declared_event_date", sa.Date(), nullable=True),
        sa.Column("actor_id", sa.UUID(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["tenant_id", "case_id"], ["cases.tenant_id", "cases.id"], ondelete="RESTRICT"),
        sa.UniqueConstraint("tenant_id", "id", name="uq_contract_execution_evidence__tenant_id"),
        sa.CheckConstraint("act_kind IN ('WORK_RECEPTION', 'RIGHTS_PRESERVATION', 'CONTRACT_EXIT')", name="contract_execution_evidence_kind_closed"),
        sa.CheckConstraint("length(trim(summary)) > 0", name="contract_execution_evidence_summary_required"),
        sa.CheckConstraint("jsonb_array_length(source_refs_json) > 0", name="contract_execution_evidence_source_required"),
        sa.CheckConstraint("jsonb_array_length(evidence_refs_json) > 0", name="contract_execution_evidence_proof_required"),
        sa.Index("ix_contract_exec_evidence_tenant_case_created", "tenant_id", "case_id", "created_at", "id"),
    )
    op.execute("""
        CREATE FUNCTION reject_contract_execution_evidence_mutation() RETURNS trigger AS $$
        BEGIN
            RAISE EXCEPTION 'contract execution evidence is append-only';
        END;
        $$ LANGUAGE plpgsql;
    """)
    op.execute("""
        CREATE TRIGGER contract_execution_evidence_append_only
        BEFORE UPDATE OR DELETE ON contract_execution_evidence
        FOR EACH ROW EXECUTE FUNCTION reject_contract_execution_evidence_mutation();
    """)


def downgrade() -> None:
    op.execute("DROP TRIGGER IF EXISTS contract_execution_evidence_append_only ON contract_execution_evidence")
    op.execute("DROP FUNCTION IF EXISTS reject_contract_execution_evidence_mutation()")
    op.drop_table("contract_execution_evidence")
