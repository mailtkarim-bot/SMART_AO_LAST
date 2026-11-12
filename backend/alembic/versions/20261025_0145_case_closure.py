"""Exact human financial declarations for the native closure workflow."""

import sqlalchemy as sa
from alembic import op

revision = "20261025_0145"
down_revision = "20261025_0144"
branch_labels = None
depends_on = None


def upgrade():
    from sqlalchemy.dialects.postgresql import JSONB, UUID

    for table in ("contract_execution_evidence", "post_reception_obligations"):
        op.add_column(table, sa.Column("closure_review_json", JSONB, nullable=True))
    op.alter_column("case_rex", "p7_result_id", nullable=True)
    op.add_column("case_rex", sa.Column("execution_exit_act_id", UUID(as_uuid=True), nullable=True))
    op.add_column("case_rex", sa.Column("execution_source_json", JSONB, nullable=True))
    op.create_foreign_key(
        "fk_case_rex_execution_exit",
        "case_rex",
        "contract_execution_evidence",
        ["tenant_id", "case_id", "execution_exit_act_id"],
        ["tenant_id", "case_id", "id"],
        ondelete="RESTRICT",
    )
    op.create_check_constraint(
        "case_rex_one_origin",
        "case_rex",
        "(p7_result_id IS NOT NULL AND execution_exit_act_id IS NULL "
        "AND execution_source_json IS NULL) OR (p7_result_id IS NULL "
        "AND execution_exit_act_id IS NOT NULL AND execution_source_json IS NOT NULL)",
    )
    op.create_unique_constraint(
        "uq_payment_cycle__tenant_case_id",
        "payment_post_reception_cycles",
        ["tenant_id", "case_id", "id"],
    )
    op.create_table(
        "payment_cycle_facts",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", UUID(as_uuid=True), nullable=False),
        sa.Column("case_id", UUID(as_uuid=True), nullable=False),
        sa.Column("cycle_id", UUID(as_uuid=True), nullable=False),
        sa.Column("compared_to_fact_id", UUID(as_uuid=True)),
        sa.Column("kind", sa.String(24), nullable=False),
        sa.Column("amount_minor", sa.BigInteger, nullable=False),
        sa.Column("currency_code", sa.String(3), nullable=False),
        sa.Column("declared_date", sa.Date, nullable=False),
        sa.Column("source_refs_json", JSONB, nullable=False),
        sa.Column("evidence_refs_json", JSONB, nullable=False),
        sa.Column("justification", sa.String(2000), nullable=False),
        sa.Column("source_snapshot_json", JSONB, nullable=False),
        sa.Column("actor_id", UUID(as_uuid=True), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id", "case_id"], ["cases.tenant_id", "cases.id"], ondelete="RESTRICT"
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id", "case_id", "cycle_id"],
            [
                "payment_post_reception_cycles.tenant_id",
                "payment_post_reception_cycles.case_id",
                "payment_post_reception_cycles.id",
            ],
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id", "case_id", "cycle_id", "compared_to_fact_id"],
            [
                "payment_cycle_facts.tenant_id",
                "payment_cycle_facts.case_id",
                "payment_cycle_facts.cycle_id",
                "payment_cycle_facts.id",
            ],
            ondelete="RESTRICT",
        ),
        sa.UniqueConstraint(
            "tenant_id", "case_id", "cycle_id", "id", name="uq_payment_facts__context"
        ),
        sa.CheckConstraint(
            "kind IN ('INVOICE_DECLARED','PAYMENT_EXPECTED','COLLECTION_RECORDED')",
            name="payment_fact_kind",
        ),
        sa.CheckConstraint(
            "amount_minor > 0 AND amount_minor <= 9000000000000000", name="payment_fact_amount"
        ),
        sa.CheckConstraint("currency_code ~ '^[A-Z]{3}$'", name="payment_fact_currency"),
        sa.CheckConstraint(
            "jsonb_array_length(source_refs_json) BETWEEN 1 AND 32 "
            "AND jsonb_array_length(evidence_refs_json) BETWEEN 1 AND 32",
            name="payment_fact_sources",
        ),
        sa.CheckConstraint("length(trim(justification)) > 0", name="payment_fact_justification"),
        sa.CheckConstraint(
            "compared_to_fact_id IS NULL OR "
            "(compared_to_fact_id <> id AND kind <> 'INVOICE_DECLARED')",
            name="payment_fact_parent",
        ),
    )
    op.create_index(
        "ix_payment_fact_tenant_case",
        "payment_cycle_facts",
        ["tenant_id", "case_id", "created_at", "id"],
    )
    op.create_index("ix_payment_cycle_facts_tenant_id", "payment_cycle_facts", ["tenant_id"])
    op.execute("""
        CREATE FUNCTION guard_execution_rex() RETURNS trigger AS $$
        BEGIN
            IF TG_OP='DELETE' AND OLD.execution_exit_act_id IS NOT NULL THEN
                RAISE EXCEPTION 'execution REX is append-only';
            END IF;
            IF TG_OP='UPDATE' AND (OLD.execution_exit_act_id IS NOT NULL
                OR NEW.execution_exit_act_id IS NOT NULL) THEN
                RAISE EXCEPTION 'execution REX is append-only';
            END IF;
            IF TG_OP='INSERT' AND NEW.execution_exit_act_id IS NOT NULL AND NOT EXISTS (
                SELECT 1 FROM contract_execution_evidence a
                WHERE a.tenant_id=NEW.tenant_id AND a.case_id=NEW.case_id
                AND a.id=NEW.execution_exit_act_id
                AND a.act_kind='CONTRACT_EXIT' AND a.closure_review_json IS NOT NULL
            ) THEN
                RAISE EXCEPTION 'execution REX requires reviewed exit';
            END IF;
            IF TG_OP='DELETE' THEN RETURN OLD; END IF;
            RETURN NEW;
        END; $$ LANGUAGE plpgsql;
        CREATE TRIGGER trg_execution_rex_guard BEFORE INSERT OR UPDATE OR DELETE ON case_rex
        FOR EACH ROW EXECUTE FUNCTION guard_execution_rex();
    """)
    op.execute("""
        CREATE FUNCTION guard_payment_cycle_fact() RETURNS trigger AS $$
        BEGIN
            IF TG_OP <> 'INSERT' THEN
                RAISE EXCEPTION 'payment facts are append-only';
            END IF;
            IF NEW.compared_to_fact_id IS NOT NULL AND NOT EXISTS (
                SELECT 1 FROM payment_cycle_facts f
                WHERE f.tenant_id=NEW.tenant_id AND f.case_id=NEW.case_id
                AND f.cycle_id=NEW.cycle_id AND f.id=NEW.compared_to_fact_id
                AND f.currency_code=NEW.currency_code
                AND ((NEW.kind='PAYMENT_EXPECTED' AND f.kind='INVOICE_DECLARED')
                  OR (NEW.kind='COLLECTION_RECORDED' AND f.kind='PAYMENT_EXPECTED'))
            ) THEN
                RAISE EXCEPTION 'payment comparison incompatible';
            END IF;
            RETURN NEW;
        END; $$ LANGUAGE plpgsql;
        CREATE TRIGGER trg_payment_cycle_fact_guard
        BEFORE INSERT OR UPDATE OR DELETE ON payment_cycle_facts
        FOR EACH ROW EXECUTE FUNCTION guard_payment_cycle_fact();
    """)


def downgrade():
    if op.get_bind().scalar(sa.text("SELECT EXISTS (SELECT 1 FROM payment_cycle_facts)")):
        raise RuntimeError("PAYMENT_FACT_HISTORY_DOWNGRADE_REFUSED")
    if op.get_bind().scalar(
        sa.text(
            "SELECT EXISTS (SELECT 1 FROM case_rex WHERE execution_exit_act_id IS NOT NULL) "
            "OR EXISTS (SELECT 1 FROM contract_execution_evidence "
            "WHERE closure_review_json IS NOT NULL) "
            "OR EXISTS (SELECT 1 FROM post_reception_obligations "
            "WHERE closure_review_json IS NOT NULL)"
        )
    ):
        raise RuntimeError("CLOSURE_HISTORY_DOWNGRADE_REFUSED")
    op.execute("DROP TRIGGER trg_execution_rex_guard ON case_rex")
    op.execute("DROP FUNCTION guard_execution_rex()")
    op.drop_constraint(op.f("ck_case_rex__case_rex_one_origin"), "case_rex", type_="check")
    op.drop_constraint("fk_case_rex_execution_exit", "case_rex", type_="foreignkey")
    op.drop_column("case_rex", "execution_source_json")
    op.drop_column("case_rex", "execution_exit_act_id")
    op.alter_column("case_rex", "p7_result_id", nullable=False)
    for table in ("contract_execution_evidence", "post_reception_obligations"):
        op.drop_column(table, "closure_review_json")
    op.execute("DROP TRIGGER trg_payment_cycle_fact_guard ON payment_cycle_facts")
    op.execute("DROP FUNCTION guard_payment_cycle_fact()")
    op.drop_table("payment_cycle_facts")
    op.drop_constraint(
        "uq_payment_cycle__tenant_case_id", "payment_post_reception_cycles", type_="unique"
    )
