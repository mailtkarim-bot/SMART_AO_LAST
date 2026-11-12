"""Add clean, immutable C5 evidence objects and separate external confirmations."""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "20261003_0130"
down_revision = "20261003_0129"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.drop_constraint(
        op.f(
            "ck_case_contract_change_action_executions__case_change_action_execution_evidence_matches_refs"
        ),
        "case_contract_change_action_executions",
        type_="check",
    )
    op.create_check_constraint(
        "case_change_action_execution_evidence_matches_refs",
        "case_contract_change_action_executions",
        "evidence_state IN ('UNKNOWN', 'REFERENCED', 'RETRIEVED') AND "
        "((evidence_state = 'UNKNOWN' AND jsonb_array_length(evidence_refs_json) = 0) OR "
        "(evidence_state = 'REFERENCED' AND jsonb_array_length(evidence_refs_json) > 0) OR "
        "evidence_state = 'RETRIEVED')",
    )
    op.create_unique_constraint(
        "uq_case_change_action_executions__exact_parent",
        "case_contract_change_action_executions",
        ["tenant_id", "case_id", "event_id", "id", "action_id", "c4_relation_id"],
    )

    op.create_table(
        "case_contract_change_evidence_objects",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("case_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("event_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("action_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("c4_relation_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("evidence_kind", sa.String(32), nullable=False),
        sa.Column("version", sa.Integer(), server_default="1", nullable=False),
        sa.Column("storage_key", sa.String(1000), nullable=False),
        sa.Column("expected_byte_size", sa.BigInteger(), nullable=False),
        sa.Column("actual_byte_size", sa.BigInteger(), nullable=True),
        sa.Column("sha256", sa.CHAR(64), nullable=True),
        sa.Column("media_type", sa.String(180), nullable=True),
        sa.Column("state", sa.String(24), nullable=False),
        sa.Column("scan_verdict", sa.String(16), nullable=True),
        sa.Column("scanner_name", sa.String(120), nullable=True),
        sa.Column("scanner_signature_version", sa.String(240), nullable=True),
        sa.Column("scanned_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
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
            name="fk_case_change_evidence_objects__action",
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
            name="fk_case_change_evidence_objects__c4",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("tenant_id", "id", name="uq_case_change_evidence_objects__tenant_id"),
        sa.UniqueConstraint(
            "tenant_id",
            "case_id",
            "event_id",
            "action_id",
            "c4_relation_id",
            "id",
            "evidence_kind",
            name="uq_case_change_evidence_objects__source",
        ),
        sa.UniqueConstraint("storage_key", name="uq_case_change_evidence_objects__storage_key"),
        sa.UniqueConstraint(
            "tenant_id", "command_id", name="uq_case_change_evidence_objects__command"
        ),
        sa.UniqueConstraint(
            "tenant_id", "idempotency_key", name="uq_case_change_evidence_objects__idempotency"
        ),
        sa.CheckConstraint(
            "evidence_kind IN ('EXECUTION_EVIDENCE', 'EXTERNAL_CONFIRMATION')",
            name="case_change_evidence_kind_closed",
        ),
        sa.CheckConstraint("version = 1", name="case_change_evidence_version_immutable"),
        sa.CheckConstraint(
            "state IN ('AWAITING_UPLOAD', 'UPLOADING', 'CLEAN', 'REJECTED')",
            name="case_change_evidence_state_closed",
        ),
        sa.CheckConstraint(
            "expected_byte_size > 0 AND expected_byte_size <= 150000000",
            name="case_change_evidence_expected_size",
        ),
        sa.CheckConstraint(
            "actual_byte_size IS NULL OR actual_byte_size > 0",
            name="case_change_evidence_actual_size",
        ),
        sa.CheckConstraint(
            "sha256 IS NULL OR sha256 ~ '^[0-9a-f]{64}$'", name="case_change_evidence_sha256"
        ),
        sa.CheckConstraint(
            "scan_verdict IS NULL OR scan_verdict IN ('CLEAN', 'INFECTED', 'ERROR')",
            name="case_change_evidence_scan_verdict",
        ),
        sa.CheckConstraint(
            "state <> 'CLEAN' OR (actual_byte_size IS NOT NULL AND sha256 IS NOT NULL "
            "AND media_type IS NOT NULL AND scan_verdict = 'CLEAN' AND scanner_name IS NOT NULL "
            "AND scanner_signature_version IS NOT NULL AND scanned_at IS NOT NULL)",
            name="case_change_evidence_clean_metadata_required",
        ),
    )
    op.create_index(
        "ix_case_contract_change_evidence_objects_tenant_id",
        "case_contract_change_evidence_objects",
        ["tenant_id"],
    )
    op.create_index(
        "ix_case_change_evidence_objects__action_created",
        "case_contract_change_evidence_objects",
        ["tenant_id", "case_id", "event_id", "action_id", "created_at"],
    )

    op.create_table(
        "case_contract_change_action_execution_evidence_links",
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("case_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("event_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("act_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("action_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("c4_relation_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("evidence_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("evidence_kind", sa.String(32), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id", "case_id", "event_id", "act_id", "action_id", "c4_relation_id"],
            [
                "case_contract_change_action_executions.tenant_id",
                "case_contract_change_action_executions.case_id",
                "case_contract_change_action_executions.event_id",
                "case_contract_change_action_executions.id",
                "case_contract_change_action_executions.action_id",
                "case_contract_change_action_executions.c4_relation_id",
            ],
            name="fk_case_change_execution_evidence_links__act",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            [
                "tenant_id",
                "case_id",
                "event_id",
                "action_id",
                "c4_relation_id",
                "evidence_id",
                "evidence_kind",
            ],
            [
                "case_contract_change_evidence_objects.tenant_id",
                "case_contract_change_evidence_objects.case_id",
                "case_contract_change_evidence_objects.event_id",
                "case_contract_change_evidence_objects.action_id",
                "case_contract_change_evidence_objects.c4_relation_id",
                "case_contract_change_evidence_objects.id",
                "case_contract_change_evidence_objects.evidence_kind",
            ],
            name="fk_case_change_execution_evidence_links__object",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("tenant_id", "act_id", "evidence_id"),
        sa.UniqueConstraint(
            "tenant_id",
            "act_id",
            "position",
            name="uq_case_change_execution_evidence_links__position",
        ),
        sa.CheckConstraint(
            "evidence_kind = 'EXECUTION_EVIDENCE'", name="case_change_execution_evidence_links_kind"
        ),
        sa.CheckConstraint(
            "position >= 0", name="case_change_execution_evidence_position_nonnegative"
        ),
    )
    op.create_index(
        "ix_case_change_execution_evidence_links__event",
        "case_contract_change_action_execution_evidence_links",
        ["tenant_id", "case_id", "event_id", "act_id"],
    )

    op.create_table(
        "case_contract_change_external_confirmations",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("case_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("event_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("action_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("act_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("c4_relation_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("evidence_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("evidence_kind", sa.String(32), nullable=False),
        sa.Column("revision", sa.Integer(), nullable=False),
        sa.Column("received_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("external_party", sa.String(240), nullable=True),
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
            ["tenant_id", "case_id", "event_id", "action_id", "act_id", "c4_relation_id"],
            [
                "case_contract_change_action_executions.tenant_id",
                "case_contract_change_action_executions.case_id",
                "case_contract_change_action_executions.event_id",
                "case_contract_change_action_executions.action_id",
                "case_contract_change_action_executions.id",
                "case_contract_change_action_executions.c4_relation_id",
            ],
            name="fk_case_change_external_confirmations__act",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            [
                "tenant_id",
                "case_id",
                "event_id",
                "action_id",
                "c4_relation_id",
                "evidence_id",
                "evidence_kind",
            ],
            [
                "case_contract_change_evidence_objects.tenant_id",
                "case_contract_change_evidence_objects.case_id",
                "case_contract_change_evidence_objects.event_id",
                "case_contract_change_evidence_objects.action_id",
                "case_contract_change_evidence_objects.c4_relation_id",
                "case_contract_change_evidence_objects.id",
                "case_contract_change_evidence_objects.evidence_kind",
            ],
            name="fk_case_change_external_confirmations__source",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "tenant_id", "id", name="uq_case_change_external_confirmations__tenant_id"
        ),
        sa.UniqueConstraint(
            "tenant_id", "command_id", name="uq_case_change_external_confirmations__command"
        ),
        sa.UniqueConstraint(
            "tenant_id",
            "idempotency_key",
            name="uq_case_change_external_confirmations__idempotency",
        ),
        sa.UniqueConstraint(
            "tenant_id",
            "act_id",
            "revision",
            name="uq_case_change_external_confirmations__revision",
        ),
        sa.CheckConstraint(
            "revision > 0", name="case_change_external_confirmation_revision_positive"
        ),
        sa.CheckConstraint(
            "evidence_kind = 'EXTERNAL_CONFIRMATION'", name="case_change_external_confirmation_kind"
        ),
        sa.CheckConstraint(
            "length(trim(rationale)) > 0", name="case_change_external_confirmation_rationale"
        ),
        sa.CheckConstraint(
            "external_party IS NULL OR length(trim(external_party)) > 0",
            name="case_change_external_confirmation_party",
        ),
    )
    op.create_index(
        "ix_case_contract_change_external_confirmations_tenant_id",
        "case_contract_change_external_confirmations",
        ["tenant_id"],
    )
    op.create_index(
        "ix_case_change_external_confirmations__act_revision",
        "case_contract_change_external_confirmations",
        ["tenant_id", "act_id", "revision"],
    )

    op.execute(
        """
        CREATE FUNCTION validate_case_change_evidence_object() RETURNS trigger AS $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM case_contract_change_action_impact_relations r
                WHERE r.tenant_id = NEW.tenant_id AND r.case_id = NEW.case_id
                  AND r.event_id = NEW.event_id AND r.id = NEW.c4_relation_id
                  AND r.action_id = NEW.action_id
            ) THEN
                RAISE EXCEPTION 'C5 evidence source must reference the exact C1/C4 pair';
            END IF;
            IF TG_OP = 'INSERT' AND NEW.state <> 'AWAITING_UPLOAD' THEN
                RAISE EXCEPTION 'C5 evidence source must start awaiting upload';
            END IF;
            IF TG_OP = 'UPDATE' THEN
                IF OLD.state IN ('CLEAN', 'REJECTED') THEN
                    RAISE EXCEPTION 'C5 evidence source is immutable after admission';
                END IF;
                IF (NEW.id, NEW.tenant_id, NEW.case_id, NEW.event_id, NEW.action_id,
                    NEW.c4_relation_id, NEW.evidence_kind, NEW.version, NEW.storage_key,
                    NEW.expected_byte_size, NEW.expires_at, NEW.actor_id, NEW.membership_id,
                    NEW.command_id, NEW.idempotency_key, NEW.correlation_id)
                   IS DISTINCT FROM
                   (OLD.id, OLD.tenant_id, OLD.case_id, OLD.event_id, OLD.action_id,
                    OLD.c4_relation_id, OLD.evidence_kind, OLD.version, OLD.storage_key,
                    OLD.expected_byte_size, OLD.expires_at, OLD.actor_id, OLD.membership_id,
                    OLD.command_id, OLD.idempotency_key, OLD.correlation_id) THEN
                    RAISE EXCEPTION 'C5 evidence source identity is immutable';
                END IF;
                IF OLD.state = 'AWAITING_UPLOAD' AND NEW.state NOT IN ('UPLOADING', 'REJECTED') THEN
                    RAISE EXCEPTION 'invalid C5 evidence upload transition';
                END IF;
                IF OLD.state = 'UPLOADING' AND NEW.state NOT IN ('CLEAN', 'REJECTED') THEN
                    RAISE EXCEPTION 'invalid C5 evidence upload transition';
                END IF;
            END IF;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql
        """
    )
    op.execute(
        "CREATE TRIGGER case_change_evidence_object_guard BEFORE INSERT OR UPDATE "
        "ON case_contract_change_evidence_objects FOR EACH ROW "
        "EXECUTE FUNCTION validate_case_change_evidence_object()"
    )
    op.execute(
        """
        CREATE FUNCTION reject_case_change_evidence_mutation() RETURNS trigger AS $$
        BEGIN
            RAISE EXCEPTION 'case contract change evidence records are append-only';
        END;
        $$ LANGUAGE plpgsql
        """
    )
    op.execute(
        "CREATE TRIGGER case_change_evidence_objects_no_delete "
        "BEFORE DELETE ON case_contract_change_evidence_objects "
        "FOR EACH ROW EXECUTE FUNCTION reject_case_change_evidence_mutation()"
    )
    op.execute(
        "CREATE TRIGGER case_change_execution_evidence_links_append_only "
        "BEFORE UPDATE OR DELETE ON case_contract_change_action_execution_evidence_links "
        "FOR EACH ROW EXECUTE FUNCTION reject_case_change_evidence_mutation()"
    )
    op.execute(
        "CREATE TRIGGER case_change_external_confirmations_append_only "
        "BEFORE UPDATE OR DELETE ON case_contract_change_external_confirmations "
        "FOR EACH ROW EXECUTE FUNCTION reject_case_change_evidence_mutation()"
    )
    op.execute(
        """
        CREATE FUNCTION validate_case_change_evidence_links() RETURNS trigger AS $$
        DECLARE
            v_tenant UUID;
            v_case UUID;
            v_event UUID;
            v_act UUID;
            v_state TEXT;
            v_link_count INTEGER;
        BEGIN
            IF TG_TABLE_NAME = 'case_contract_change_action_executions' THEN
                v_tenant := NEW.tenant_id;
                v_case := NEW.case_id;
                v_event := NEW.event_id;
                v_act := NEW.id;
            ELSE
                v_tenant := NEW.tenant_id;
                v_case := NEW.case_id;
                v_event := NEW.event_id;
                v_act := NEW.act_id;
            END IF;
            SELECT evidence_state INTO v_state FROM case_contract_change_action_executions
            WHERE tenant_id = v_tenant AND case_id = v_case AND event_id = v_event AND id = v_act;
            SELECT count(*) INTO v_link_count
            FROM case_contract_change_action_execution_evidence_links
            WHERE tenant_id = v_tenant AND case_id = v_case
              AND event_id = v_event AND act_id = v_act;
            IF v_state = 'RETRIEVED' AND v_link_count = 0 THEN
                RAISE EXCEPTION 'C5 RETRIEVED requires at least one verified evidence link';
            END IF;
            IF v_state IN ('UNKNOWN', 'REFERENCED') AND v_link_count > 0 THEN
                RAISE EXCEPTION 'C5 evidence links require RETRIEVED state';
            END IF;
            RETURN NULL;
        END;
        $$ LANGUAGE plpgsql
        """
    )
    op.execute(
        "CREATE CONSTRAINT TRIGGER case_change_c5_evidence_state_guard "
        "AFTER INSERT ON case_contract_change_action_executions "
        "DEFERRABLE INITIALLY DEFERRED FOR EACH ROW "
        "EXECUTE FUNCTION validate_case_change_evidence_links()"
    )
    op.execute(
        "CREATE CONSTRAINT TRIGGER case_change_c5_evidence_link_guard "
        "AFTER INSERT ON case_contract_change_action_execution_evidence_links "
        "DEFERRABLE INITIALLY DEFERRED FOR EACH ROW "
        "EXECUTE FUNCTION validate_case_change_evidence_links()"
    )
    op.execute(
        """
        CREATE FUNCTION validate_case_change_external_confirmation() RETURNS trigger AS $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM case_contract_change_evidence_objects e
                WHERE e.tenant_id = NEW.tenant_id AND e.case_id = NEW.case_id
                  AND e.event_id = NEW.event_id AND e.action_id = NEW.action_id
                  AND e.c4_relation_id = NEW.c4_relation_id AND e.id = NEW.evidence_id
                  AND e.evidence_kind = 'EXTERNAL_CONFIRMATION' AND e.state = 'CLEAN'
            ) THEN
                RAISE EXCEPTION 'C5 external confirmation requires a clean exact external source';
            END IF;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql
        """
    )
    op.execute(
        "CREATE TRIGGER case_change_external_confirmation_source_guard "
        "BEFORE INSERT ON case_contract_change_external_confirmations "
        "FOR EACH ROW EXECUTE FUNCTION validate_case_change_external_confirmation()"
    )


def downgrade() -> None:
    has_persisted_evidence = (
        op.get_bind()
        .execute(
            sa.text(
                "SELECT EXISTS (SELECT 1 FROM case_contract_change_evidence_objects) "
                "OR EXISTS (SELECT 1 FROM case_contract_change_action_execution_evidence_links) "
                "OR EXISTS (SELECT 1 FROM case_contract_change_external_confirmations) "
                "OR EXISTS (SELECT 1 FROM case_contract_change_action_executions "
                "WHERE evidence_state = 'RETRIEVED')"
            )
        )
        .scalar_one()
    )
    if has_persisted_evidence:
        raise RuntimeError(
            "C5 evidence has durable bytes or retrieval acts; export/archive it before downgrade"
        )
    op.execute(
        "DROP TRIGGER IF EXISTS case_change_external_confirmation_source_guard "
        "ON case_contract_change_external_confirmations"
    )
    op.execute("DROP FUNCTION IF EXISTS validate_case_change_external_confirmation()")
    op.execute(
        "DROP TRIGGER IF EXISTS case_change_c5_evidence_link_guard "
        "ON case_contract_change_action_execution_evidence_links"
    )
    op.execute(
        "DROP TRIGGER IF EXISTS case_change_c5_evidence_state_guard "
        "ON case_contract_change_action_executions"
    )
    op.execute("DROP FUNCTION IF EXISTS validate_case_change_evidence_links()")
    op.execute(
        "DROP TRIGGER IF EXISTS case_change_external_confirmations_append_only "
        "ON case_contract_change_external_confirmations"
    )
    op.execute(
        "DROP TRIGGER IF EXISTS case_change_execution_evidence_links_append_only "
        "ON case_contract_change_action_execution_evidence_links"
    )
    op.execute(
        "DROP TRIGGER IF EXISTS case_change_evidence_objects_no_delete "
        "ON case_contract_change_evidence_objects"
    )
    op.execute(
        "DROP TRIGGER IF EXISTS case_change_evidence_object_guard "
        "ON case_contract_change_evidence_objects"
    )
    op.execute("DROP FUNCTION IF EXISTS validate_case_change_evidence_object()")
    op.execute("DROP FUNCTION IF EXISTS reject_case_change_evidence_mutation()")
    for name, table in (
        (
            "ix_case_change_external_confirmations__act_revision",
            "case_contract_change_external_confirmations",
        ),
        (
            "ix_case_contract_change_external_confirmations_tenant_id",
            "case_contract_change_external_confirmations",
        ),
        (
            "ix_case_change_execution_evidence_links__event",
            "case_contract_change_action_execution_evidence_links",
        ),
        (
            "ix_case_change_evidence_objects__action_created",
            "case_contract_change_evidence_objects",
        ),
        (
            "ix_case_contract_change_evidence_objects_tenant_id",
            "case_contract_change_evidence_objects",
        ),
    ):
        op.drop_index(name, table_name=table)
    op.drop_table("case_contract_change_external_confirmations")
    op.drop_table("case_contract_change_action_execution_evidence_links")
    op.drop_table("case_contract_change_evidence_objects")
    op.drop_constraint(
        "uq_case_change_action_executions__exact_parent",
        "case_contract_change_action_executions",
        type_="unique",
    )
    op.drop_constraint(
        op.f(
            "ck_case_contract_change_action_executions__case_change_action_execution_evidence_matches_refs"
        ),
        "case_contract_change_action_executions",
        type_="check",
    )
    op.create_check_constraint(
        "case_change_action_execution_evidence_matches_refs",
        "case_contract_change_action_executions",
        "evidence_state IN ('UNKNOWN', 'REFERENCED') AND "
        "((evidence_state = 'UNKNOWN' AND jsonb_array_length(evidence_refs_json) = 0) OR "
        "(evidence_state = 'REFERENCED' AND jsonb_array_length(evidence_refs_json) > 0))",
    )
