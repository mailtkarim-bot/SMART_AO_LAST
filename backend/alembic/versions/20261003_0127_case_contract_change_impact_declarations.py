"""Persist source-specific human C3 impact declarations after C2."""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "20261003_0127"
down_revision = "20261003_0126"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "case_contract_change_impact_declarations",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("case_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("event_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("linkage_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("condition_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("impact_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("impact_revision", sa.Integer(), nullable=False),
        sa.Column("source_a1_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("axis", sa.String(16), nullable=False),
        sa.Column("revision", sa.Integer(), nullable=False),
        sa.Column("impact_state", sa.String(16), nullable=False),
        sa.Column("impact_summary", sa.Text(), nullable=True),
        sa.Column("impact_unknown_reason", sa.Text(), nullable=True),
        sa.Column("measurement_state", sa.String(16), nullable=False),
        sa.Column("value_as_declared", sa.String(80), nullable=True),
        sa.Column("currency_code", sa.CHAR(length=3), nullable=True),
        sa.Column("unit", sa.String(32), nullable=True),
        sa.Column("measurement_unknown_reason", sa.Text(), nullable=True),
        sa.Column(
            "assumptions_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False
        ),
        sa.Column("source_refs_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("evidence_refs_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("rationale", sa.Text(), nullable=False),
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
            name="fk_case_change_impact__event",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id", "linkage_id"],
            [
                "case_contract_change_engagement_links.tenant_id",
                "case_contract_change_engagement_links.id",
            ],
            name="fk_case_change_impact__c2_linkage",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("tenant_id", "id", name="uq_case_change_impacts__tenant_id"),
        sa.UniqueConstraint("tenant_id", "command_id", name="uq_case_change_impacts__command"),
        sa.UniqueConstraint(
            "tenant_id", "idempotency_key", name="uq_case_change_impacts__idempotency"
        ),
        sa.UniqueConstraint(
            "tenant_id",
            "case_id",
            "event_id",
            "linkage_id",
            "condition_id",
            "impact_id",
            "impact_revision",
            "axis",
            "revision",
            name="uq_case_change_impact__source_axis_revision",
        ),
        sa.CheckConstraint("revision > 0", name="ck_case_change_impacts__revision"),
        sa.CheckConstraint(
            "impact_revision > 0", name="ck_case_change_impacts__impact_revision"
        ),
        sa.CheckConstraint(
            "axis IN ('SCOPE', 'COST', 'CASH', 'SCHEDULE', 'CAPACITY')",
            name="ck_case_change_impacts__axis",
        ),
        sa.CheckConstraint(
            "impact_state IN ('DECLARED', 'UNKNOWN')",
            name="ck_case_change_impacts__impact_state",
        ),
        sa.CheckConstraint(
            "measurement_state IN ('DECLARED', 'UNKNOWN', 'NOT_APPLICABLE')",
            name="ck_case_change_impacts__measurement_state",
        ),
        sa.CheckConstraint(
            "(impact_state = 'DECLARED' AND NULLIF(BTRIM(impact_summary), '') IS NOT NULL "
            "AND impact_unknown_reason IS NULL AND jsonb_array_length(evidence_refs_json) > 0) OR "
            "(impact_state = 'UNKNOWN' AND impact_summary IS NULL "
            "AND NULLIF(BTRIM(impact_unknown_reason), '') IS NOT NULL)",
            name="ck_case_change_impacts__impact_state_matches_summary",
        ),
        sa.CheckConstraint(
            "(axis = 'SCOPE' AND measurement_state = 'NOT_APPLICABLE' "
            "AND value_as_declared IS NULL AND currency_code IS NULL AND unit IS NULL "
            "AND measurement_unknown_reason IS NULL) OR "
            "(axis <> 'SCOPE' AND impact_state = 'UNKNOWN' "
            "AND measurement_state = 'UNKNOWN' AND value_as_declared IS NULL "
            "AND currency_code IS NULL AND unit IS NULL) OR "
            "(axis IN ('COST', 'CASH') AND impact_state = 'DECLARED' "
            "AND measurement_state = 'DECLARED' "
            "AND value_as_declared ~ '^-?[0-9]+([,.][0-9]{1,6})?$' "
            "AND currency_code ~ '^[A-Z]{3}$' AND unit IS NULL "
            "AND measurement_unknown_reason IS NULL) OR "
            "(axis IN ('SCHEDULE', 'CAPACITY') AND impact_state = 'DECLARED' "
            "AND measurement_state = 'DECLARED' "
            "AND value_as_declared ~ '^-?[0-9]+([,.][0-9]{1,6})?$' "
            "AND NULLIF(BTRIM(unit), '') IS NOT NULL AND currency_code IS NULL "
            "AND measurement_unknown_reason IS NULL) OR "
            "(axis <> 'SCOPE' AND impact_state = 'DECLARED' "
            "AND measurement_state = 'UNKNOWN' AND value_as_declared IS NULL "
            "AND currency_code IS NULL AND unit IS NULL "
            "AND NULLIF(BTRIM(measurement_unknown_reason), '') IS NOT NULL)",
            name="ck_case_change_impacts__measurement_matches_axis_state",
        ),
        sa.CheckConstraint(
            "length(trim(rationale)) > 0", name="ck_case_change_impacts__rationale"
        ),
        sa.CheckConstraint(
            "jsonb_array_length(source_refs_json) > 0", name="ck_case_change_impacts__sources"
        ),
    )
    op.create_index(
        "ix_case_change_impacts__event_linkage_revision",
        "case_contract_change_impact_declarations",
        ["tenant_id", "case_id", "event_id", "linkage_id", "revision"],
    )
    op.execute("""
        CREATE FUNCTION validate_case_change_impact_c2_source() RETURNS trigger AS $$
        DECLARE
            selected_sources JSONB;
            linkage_state TEXT;
            linkage_case_id UUID;
            linkage_event_id UUID;
            current_linkage_id UUID;
        BEGIN
            SELECT selected_sources_json, state, case_id, event_id
            INTO selected_sources, linkage_state, linkage_case_id, linkage_event_id
            FROM case_contract_change_engagement_links
            WHERE tenant_id = NEW.tenant_id
              AND id = NEW.linkage_id;

            IF NOT FOUND
               OR linkage_case_id <> NEW.case_id
               OR linkage_event_id <> NEW.event_id
               OR linkage_state <> 'LINKED' THEN
                RAISE EXCEPTION 'C2 linkage must exist, belong to C1, and be LINKED';
            END IF;
            IF NOT (selected_sources @> jsonb_build_array(NEW.source_a1_json)) THEN
                RAISE EXCEPTION 'C3 source must be selected by the exact C2 linkage';
            END IF;

            SELECT id
            INTO current_linkage_id
            FROM case_contract_change_engagement_links
            WHERE tenant_id = NEW.tenant_id
              AND case_id = NEW.case_id
              AND event_id = NEW.event_id
            ORDER BY revision DESC, id DESC
            LIMIT 1;
            IF current_linkage_id IS DISTINCT FROM NEW.linkage_id THEN
                RAISE EXCEPTION 'C3 linkage must be the current C2 revision';
            END IF;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)
    op.execute("""
        CREATE TRIGGER case_contract_change_impact_c2_source_guard
        BEFORE INSERT ON case_contract_change_impact_declarations
        FOR EACH ROW EXECUTE FUNCTION validate_case_change_impact_c2_source();
    """)
    op.execute("""
        CREATE FUNCTION reject_case_contract_change_impact_mutation() RETURNS trigger AS $$
        BEGIN
            RAISE EXCEPTION 'case_contract_change_impact_declarations is append-only';
        END;
        $$ LANGUAGE plpgsql;
    """)
    op.execute("""
        CREATE TRIGGER case_contract_change_impact_declarations_append_only
        BEFORE UPDATE OR DELETE ON case_contract_change_impact_declarations
        FOR EACH ROW EXECUTE FUNCTION reject_case_contract_change_impact_mutation();
    """)


def downgrade() -> None:
    op.execute(
        "DROP TRIGGER IF EXISTS case_contract_change_impact_c2_source_guard "
        "ON case_contract_change_impact_declarations"
    )
    op.execute("DROP FUNCTION IF EXISTS validate_case_change_impact_c2_source()")
    op.execute(
        "DROP TRIGGER IF EXISTS case_contract_change_impact_declarations_append_only "
        "ON case_contract_change_impact_declarations"
    )
    op.execute("DROP FUNCTION IF EXISTS reject_case_contract_change_impact_mutation()")
    op.drop_index(
        "ix_case_change_impacts__event_linkage_revision",
        table_name="case_contract_change_impact_declarations",
    )
    op.drop_table("case_contract_change_impact_declarations")
