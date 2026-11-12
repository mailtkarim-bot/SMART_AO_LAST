"""Persist append-only C5 declarations tied to exact C1 and C4 acts."""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "20261003_0129"
down_revision = "20261003_0128"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "case_contract_change_action_executions",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("case_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("event_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("action_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("c4_relation_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("revision", sa.Integer(), nullable=False),
        sa.Column("declared_state", sa.String(32), nullable=False),
        sa.Column("declared_summary", sa.Text(), nullable=True),
        sa.Column("unknown_reason", sa.Text(), nullable=True),
        sa.Column("evidence_refs_json", postgresql.JSONB(), nullable=False),
        sa.Column("evidence_state", sa.String(16), nullable=False),
        sa.Column("external_confirmation_state", sa.String(16), nullable=False),
        sa.Column("external_confirmation_note", sa.Text(), nullable=True),
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
            ["tenant_id", "case_id", "event_id", "action_id"],
            [
                "case_contract_change_actions.tenant_id",
                "case_contract_change_actions.case_id",
                "case_contract_change_actions.event_id",
                "case_contract_change_actions.id",
            ],
            name="fk_case_change_action_executions__action",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id", "case_id", "event_id", "c4_relation_id"],
            [
                "case_contract_change_action_impact_relations.tenant_id",
                "case_contract_change_action_impact_relations.case_id",
                "case_contract_change_action_impact_relations.event_id",
                "case_contract_change_action_impact_relations.id",
            ],
            name="fk_case_change_action_executions__c4",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("tenant_id", "id", name="uq_case_change_action_executions__tenant_id"),
        sa.UniqueConstraint(
            "tenant_id", "command_id", name="uq_case_change_action_executions__command"
        ),
        sa.UniqueConstraint(
            "tenant_id", "idempotency_key", name="uq_case_change_action_executions__idempotency"
        ),
        sa.UniqueConstraint(
            "tenant_id",
            "case_id",
            "event_id",
            "action_id",
            "revision",
            name="uq_case_change_action_executions__revision",
        ),
        sa.CheckConstraint("revision > 0", name="case_change_action_execution_revision_positive"),
        sa.CheckConstraint(
            "declared_state IN ("
            "'DECLARED_PERFORMED', 'DECLARED_PARTIAL', 'DECLARED_NOT_PERFORMED', 'UNKNOWN')",
            name="case_change_action_execution_state_closed",
        ),
        sa.CheckConstraint(
            "(declared_state = 'UNKNOWN' AND declared_summary IS NULL "
            "AND NULLIF(BTRIM(unknown_reason), '') IS NOT NULL) OR "
            "(declared_state <> 'UNKNOWN' "
            "AND NULLIF(BTRIM(declared_summary), '') IS NOT NULL "
            "AND unknown_reason IS NULL)",
            name="case_change_action_execution_declaration_matches_state",
        ),
        sa.CheckConstraint(
            "evidence_state IN ('UNKNOWN', 'REFERENCED') AND "
            "((evidence_state = 'UNKNOWN' AND jsonb_array_length(evidence_refs_json) = 0) OR "
            "(evidence_state = 'REFERENCED' AND jsonb_array_length(evidence_refs_json) > 0))",
            name="case_change_action_execution_evidence_matches_refs",
        ),
        sa.CheckConstraint(
            "external_confirmation_state IN ('UNKNOWN', 'NOT_CONFIRMED') AND "
            "((external_confirmation_state = 'UNKNOWN' AND external_confirmation_note IS NULL) OR "
            "(external_confirmation_state = 'NOT_CONFIRMED' "
            "AND NULLIF(BTRIM(external_confirmation_note), '') IS NOT NULL))",
            name="case_change_action_execution_external_confirmation_matches_state",
        ),
    )
    op.create_index(
        "ix_case_contract_change_action_executions_tenant_id",
        "case_contract_change_action_executions",
        ["tenant_id"],
    )
    op.create_index(
        "ix_case_change_action_executions__action_revision",
        "case_contract_change_action_executions",
        ["tenant_id", "case_id", "event_id", "action_id", "revision"],
    )
    op.execute(
        """
        CREATE FUNCTION validate_case_change_action_execution() RETURNS trigger AS $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM case_contract_change_action_impact_relations r
                WHERE r.tenant_id = NEW.tenant_id AND r.case_id = NEW.case_id
                  AND r.event_id = NEW.event_id AND r.id = NEW.c4_relation_id
                  AND r.action_id = NEW.action_id
            ) THEN
                RAISE EXCEPTION 'case change C5 must reference its exact C1 action C4 relation';
            END IF;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql
        """
    )
    op.execute(
        """
        CREATE TRIGGER case_change_action_execution_guard
        BEFORE INSERT ON case_contract_change_action_executions
        FOR EACH ROW EXECUTE FUNCTION validate_case_change_action_execution()
        """
    )
    op.execute(
        """
        CREATE FUNCTION reject_case_change_action_execution_mutation() RETURNS trigger AS $$
        BEGIN
            RAISE EXCEPTION 'case contract change action executions are append-only';
        END;
        $$ LANGUAGE plpgsql
        """
    )
    op.execute(
        """
        CREATE TRIGGER case_change_action_executions_append_only
        BEFORE UPDATE OR DELETE ON case_contract_change_action_executions
        FOR EACH ROW EXECUTE FUNCTION reject_case_change_action_execution_mutation()
        """
    )


def downgrade() -> None:
    op.execute(
        "DROP TRIGGER IF EXISTS case_change_action_executions_append_only "
        "ON case_contract_change_action_executions"
    )
    op.execute(
        "DROP TRIGGER IF EXISTS case_change_action_execution_guard "
        "ON case_contract_change_action_executions"
    )
    op.execute("DROP FUNCTION IF EXISTS reject_case_change_action_execution_mutation()")
    op.execute("DROP FUNCTION IF EXISTS validate_case_change_action_execution()")
    op.drop_index(
        "ix_case_change_action_executions__action_revision",
        table_name="case_contract_change_action_executions",
    )
    op.drop_index(
        "ix_case_contract_change_action_executions_tenant_id",
        table_name="case_contract_change_action_executions",
    )
    op.drop_table("case_contract_change_action_executions")
