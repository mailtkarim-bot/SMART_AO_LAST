"""Add a sourced C1 contract-change event, human applicability and follow-up action."""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "20261001_0125"
down_revision = "20261001_0124"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def _append_only(table: str, function: str, trigger: str) -> None:
    op.execute(
        f"""
        CREATE FUNCTION {function}() RETURNS trigger AS $$
        BEGIN RAISE EXCEPTION '{table} is append-only'; END;
        $$ LANGUAGE plpgsql;
        """
    )
    op.execute(
        f"""
        CREATE TRIGGER {trigger}
        BEFORE UPDATE OR DELETE ON {table}
        FOR EACH ROW EXECUTE FUNCTION {function}();
        """
    )


def upgrade() -> None:
    op.create_table(
        "case_contract_change_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("case_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("handover_snapshot_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("contract_instrument_version_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("change_kind", sa.String(32), nullable=False),
        sa.Column("issuer", sa.String(240), nullable=True),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column("scope_note", sa.Text(), nullable=False),
        sa.Column("source_refs_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("evidence_refs_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("declared_received_at", sa.DateTime(timezone=True), nullable=False),
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
            ["tenant_id", "case_id"],
            ["cases.tenant_id", "cases.id"],
            name="fk_case_contract_change_events__case",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id", "case_id", "handover_snapshot_id"],
            [
                "case_handover_snapshots.tenant_id",
                "case_handover_snapshots.case_id",
                "case_handover_snapshots.id",
            ],
            name="fk_case_contract_change_events__handover",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id", "case_id", "contract_instrument_version_id"],
            [
                "contract_instrument_versions.tenant_id",
                "contract_instrument_versions.case_id",
                "contract_instrument_versions.id",
            ],
            name="fk_case_contract_change_events__instrument",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("tenant_id", "id", name="uq_case_contract_change_events__tenant_id"),
        sa.UniqueConstraint(
            "tenant_id", "case_id", "id", name="uq_case_contract_change_events__tenant_case_id"
        ),
        sa.UniqueConstraint(
            "tenant_id", "command_id", name="uq_case_contract_change_events__command"
        ),
        sa.UniqueConstraint(
            "tenant_id", "idempotency_key", name="uq_case_contract_change_events__idempotency"
        ),
        sa.CheckConstraint(
            "change_kind IN ('ORDER_OF_SERVICE', 'CHANGE_REQUEST', 'ADDENDUM', 'SCHEDULE_CHANGE')",
            name="ck_case_contract_change_events__kind",
        ),
        sa.CheckConstraint(
            "length(trim(summary)) > 0", name="ck_case_contract_change_events__summary"
        ),
        sa.CheckConstraint(
            "length(trim(scope_note)) > 0", name="ck_case_contract_change_events__scope"
        ),
        sa.CheckConstraint(
            "jsonb_array_length(source_refs_json) > 0",
            name="ck_case_contract_change_events__sources",
        ),
        sa.CheckConstraint(
            "jsonb_array_length(evidence_refs_json) > 0",
            name="ck_case_contract_change_events__evidence",
        ),
    )
    op.create_index(
        "ix_case_contract_change_events__tenant_case_created",
        "case_contract_change_events",
        ["tenant_id", "case_id", "created_at", "id"],
    )

    op.create_table(
        "case_contract_change_applicabilities",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("case_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("event_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("handover_snapshot_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("contract_instrument_version_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("revision", sa.Integer(), nullable=False),
        sa.Column("decision", sa.String(32), nullable=False),
        sa.Column("delta_state", sa.String(16), nullable=False),
        sa.Column("delta_note", sa.Text(), nullable=True),
        sa.Column("rationale", sa.Text(), nullable=False),
        sa.Column("evidence_refs_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
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
            ["tenant_id", "case_id", "event_id"],
            [
                "case_contract_change_events.tenant_id",
                "case_contract_change_events.case_id",
                "case_contract_change_events.id",
            ],
            name="fk_case_contract_change_applicabilities__event",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id", "case_id", "handover_snapshot_id"],
            [
                "case_handover_snapshots.tenant_id",
                "case_handover_snapshots.case_id",
                "case_handover_snapshots.id",
            ],
            name="fk_case_contract_change_applicabilities__handover",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id", "case_id", "contract_instrument_version_id"],
            [
                "contract_instrument_versions.tenant_id",
                "contract_instrument_versions.case_id",
                "contract_instrument_versions.id",
            ],
            name="fk_case_contract_change_applicabilities__instrument",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "tenant_id", "id", name="uq_case_contract_change_applicabilities__tenant_id"
        ),
        sa.UniqueConstraint(
            "tenant_id",
            "case_id",
            "event_id",
            "id",
            name="uq_case_contract_change_applicabilities__event_id",
        ),
        sa.UniqueConstraint(
            "tenant_id", "command_id", name="uq_case_contract_change_applicabilities__command"
        ),
        sa.UniqueConstraint(
            "tenant_id",
            "idempotency_key",
            name="uq_case_contract_change_applicabilities__idempotency",
        ),
        sa.UniqueConstraint(
            "tenant_id",
            "case_id",
            "event_id",
            "revision",
            name="uq_case_contract_change_applicabilities__revision",
        ),
        sa.CheckConstraint(
            "revision > 0", name="ck_case_contract_change_applicabilities__revision"
        ),
        sa.CheckConstraint(
            "decision IN ('APPLICABLE_TO_HANDOVER', 'NOT_APPLICABLE', 'NEEDS_CLARIFICATION')",
            name="ck_case_contract_change_applicabilities__decision",
        ),
        sa.CheckConstraint(
            "delta_state IN ('UNKNOWN', 'DECLARED')",
            name="ck_case_contract_change_applicabilities__delta_state",
        ),
        sa.CheckConstraint(
            "(delta_state = 'UNKNOWN' AND delta_note IS NULL) OR "
            "(delta_state = 'DECLARED' AND NULLIF(BTRIM(delta_note), '') IS NOT NULL)",
            name="ck_case_contract_change_applicabilities__delta_note",
        ),
        sa.CheckConstraint(
            "length(trim(rationale)) > 0", name="ck_case_contract_change_applicabilities__rationale"
        ),
        sa.CheckConstraint(
            "jsonb_array_length(evidence_refs_json) > 0",
            name="ck_case_contract_change_applicabilities__evidence",
        ),
    )
    op.create_index(
        "ix_case_contract_change_applicabilities__event_revision",
        "case_contract_change_applicabilities",
        ["tenant_id", "case_id", "event_id", "revision"],
    )

    op.create_table(
        "case_contract_change_actions",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("case_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("event_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("applicability_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("revision", sa.Integer(), nullable=False),
        sa.Column("action_summary", sa.Text(), nullable=False),
        sa.Column("evidence_refs_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("due_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("due_date_absence_reason", sa.Text(), nullable=True),
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
            ["tenant_id", "case_id", "event_id"],
            [
                "case_contract_change_events.tenant_id",
                "case_contract_change_events.case_id",
                "case_contract_change_events.id",
            ],
            name="fk_case_contract_change_actions__event",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id", "case_id", "event_id", "applicability_id"],
            [
                "case_contract_change_applicabilities.tenant_id",
                "case_contract_change_applicabilities.case_id",
                "case_contract_change_applicabilities.event_id",
                "case_contract_change_applicabilities.id",
            ],
            name="fk_case_contract_change_actions__applicability",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("tenant_id", "id", name="uq_case_contract_change_actions__tenant_id"),
        sa.UniqueConstraint(
            "tenant_id", "command_id", name="uq_case_contract_change_actions__command"
        ),
        sa.UniqueConstraint(
            "tenant_id", "idempotency_key", name="uq_case_contract_change_actions__idempotency"
        ),
        sa.UniqueConstraint(
            "tenant_id",
            "case_id",
            "event_id",
            "revision",
            name="uq_case_contract_change_actions__revision",
        ),
        sa.CheckConstraint("revision > 0", name="ck_case_contract_change_actions__revision"),
        sa.CheckConstraint(
            "length(trim(action_summary)) > 0", name="ck_case_contract_change_actions__summary"
        ),
        sa.CheckConstraint(
            "jsonb_array_length(evidence_refs_json) > 0",
            name="ck_case_contract_change_actions__evidence",
        ),
        sa.CheckConstraint(
            "due_at IS NOT NULL OR NULLIF(BTRIM(due_date_absence_reason), '') IS NOT NULL",
            name="ck_case_contract_change_actions__due",
        ),
    )
    op.create_index(
        "ix_case_contract_change_actions__event_revision",
        "case_contract_change_actions",
        ["tenant_id", "case_id", "event_id", "revision"],
    )
    _append_only(
        "case_contract_change_events",
        "reject_case_contract_change_event_mutation",
        "case_contract_change_events_append_only",
    )
    _append_only(
        "case_contract_change_applicabilities",
        "reject_case_contract_change_applicability_mutation",
        "case_contract_change_applicabilities_append_only",
    )
    _append_only(
        "case_contract_change_actions",
        "reject_case_contract_change_action_mutation",
        "case_contract_change_actions_append_only",
    )


def downgrade() -> None:
    op.execute(
        "DROP TRIGGER IF EXISTS case_contract_change_actions_append_only "
        "ON case_contract_change_actions"
    )
    op.execute("DROP FUNCTION IF EXISTS reject_case_contract_change_action_mutation()")
    op.execute(
        "DROP TRIGGER IF EXISTS case_contract_change_applicabilities_append_only "
        "ON case_contract_change_applicabilities"
    )
    op.execute("DROP FUNCTION IF EXISTS reject_case_contract_change_applicability_mutation()")
    op.execute(
        "DROP TRIGGER IF EXISTS case_contract_change_events_append_only "
        "ON case_contract_change_events"
    )
    op.execute("DROP FUNCTION IF EXISTS reject_case_contract_change_event_mutation()")
    op.drop_index(
        "ix_case_contract_change_actions__event_revision", table_name="case_contract_change_actions"
    )
    op.drop_table("case_contract_change_actions")
    op.drop_index(
        "ix_case_contract_change_applicabilities__event_revision",
        table_name="case_contract_change_applicabilities",
    )
    op.drop_table("case_contract_change_applicabilities")
    op.drop_index(
        "ix_case_contract_change_events__tenant_case_created",
        table_name="case_contract_change_events",
    )
    op.drop_table("case_contract_change_events")
