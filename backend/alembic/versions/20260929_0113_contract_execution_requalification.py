"""Persist append-only human requalification decisions for replaced contract versions."""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision = "20260929_0113"
down_revision = "20260929_0112"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.create_unique_constraint(
        "uq_contract_execution_evidence__tenant_case_id",
        "contract_execution_evidence",
        ["tenant_id", "case_id", "id"],
    )
    op.create_table(
        "contract_execution_evidence_requalifications",
        sa.Column("id", sa.UUID(), primary_key=True),
        sa.Column("tenant_id", sa.UUID(), nullable=False),
        sa.Column("case_id", sa.UUID(), nullable=False),
        sa.Column("act_id", sa.UUID(), nullable=False),
        sa.Column("supersession_id", sa.UUID(), nullable=False),
        sa.Column("revision", sa.Integer(), nullable=False),
        sa.Column("decision", sa.String(40), nullable=False),
        sa.Column("resulting_contract_instrument_version_id", sa.UUID(), nullable=True),
        sa.Column("rationale", sa.String(2000), nullable=False),
        sa.Column("actor_id", sa.UUID(), nullable=False),
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
        sa.ForeignKeyConstraint(
            ["tenant_id", "case_id", "act_id"],
            [
                "contract_execution_evidence.tenant_id",
                "contract_execution_evidence.case_id",
                "contract_execution_evidence.id",
            ],
            ondelete="RESTRICT",
            name="fk_cer_act_same_case",
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id", "case_id", "supersession_id"],
            [
                "contract_instrument_supersessions.tenant_id",
                "contract_instrument_supersessions.case_id",
                "contract_instrument_supersessions.id",
            ],
            ondelete="RESTRICT",
            name="fk_cer_supersession_same_case",
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id", "case_id", "resulting_contract_instrument_version_id"],
            [
                "contract_instrument_versions.tenant_id",
                "contract_instrument_versions.case_id",
                "contract_instrument_versions.id",
            ],
            ondelete="RESTRICT",
            name="fk_cer_result_version_same_case",
        ),
        sa.UniqueConstraint("tenant_id", "id", name="uq_contract_exec_requal__tenant_id"),
        sa.UniqueConstraint(
            "tenant_id",
            "case_id",
            "act_id",
            "supersession_id",
            "revision",
            name="uq_contract_exec_requal__trigger_revision",
        ),
        sa.CheckConstraint("revision > 0", name="contract_exec_requal_revision_positive"),
        sa.CheckConstraint(
            "decision IN ("
            "'RETAINED_AS_DECLARED', 'RELINKED_TO_DECLARED_VERSION', 'NEEDS_CLARIFICATION')",
            name="contract_exec_requal_decision_closed",
        ),
        sa.CheckConstraint(
            "length(trim(rationale)) > 0",
            name="contract_exec_requal_rationale_required",
        ),
        sa.CheckConstraint(
            "(decision = 'NEEDS_CLARIFICATION' "
            "AND resulting_contract_instrument_version_id IS NULL) "
            "OR (decision IN ('RETAINED_AS_DECLARED', 'RELINKED_TO_DECLARED_VERSION') "
            "AND resulting_contract_instrument_version_id IS NOT NULL)",
            name="contract_exec_requal_result_matches_decision",
        ),
        sa.Index(
            "ix_contract_exec_requal_tenant_case_act",
            "tenant_id",
            "case_id",
            "act_id",
            "created_at",
            "revision",
        ),
    )
    op.execute("""
        CREATE FUNCTION reject_contract_execution_requalification_mutation() RETURNS trigger AS $$
        BEGIN
            RAISE EXCEPTION 'contract execution requalifications are append-only';
        END;
        $$ LANGUAGE plpgsql;
    """)
    op.execute("""
        CREATE TRIGGER contract_execution_requalifications_append_only
        BEFORE UPDATE OR DELETE ON contract_execution_evidence_requalifications
        FOR EACH ROW EXECUTE FUNCTION reject_contract_execution_requalification_mutation();
    """)


def downgrade() -> None:
    op.execute(
        "DROP TRIGGER IF EXISTS contract_execution_requalifications_append_only "
        "ON contract_execution_evidence_requalifications"
    )
    op.execute("DROP FUNCTION IF EXISTS reject_contract_execution_requalification_mutation()")
    op.drop_table("contract_execution_evidence_requalifications")
    op.drop_constraint(
        "uq_contract_execution_evidence__tenant_case_id",
        "contract_execution_evidence",
        type_="unique",
    )
