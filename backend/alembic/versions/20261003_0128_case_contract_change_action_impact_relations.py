"""Persist append-only Patron relations from C1 actions to exact C3 impacts."""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "20261003_0128"
down_revision = "20261003_0127"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.create_unique_constraint(
        "uq_case_contract_change_actions__event_id",
        "case_contract_change_actions",
        ["tenant_id", "case_id", "event_id", "id"],
    )
    op.create_unique_constraint(
        "uq_case_change_impacts__event_id",
        "case_contract_change_impact_declarations",
        ["tenant_id", "case_id", "event_id", "id"],
    )
    op.create_table(
        "case_contract_change_action_impact_relations",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("case_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("event_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("action_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("applicability_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("revision", sa.Integer(), nullable=False),
        sa.Column("state", sa.String(24), nullable=False),
        sa.Column("rationale", sa.Text(), nullable=False),
        sa.Column("unknown_reason", sa.Text(), nullable=True),
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
            name="fk_case_change_action_impact_relations__event",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id", "case_id", "event_id", "action_id"],
            [
                "case_contract_change_actions.tenant_id",
                "case_contract_change_actions.case_id",
                "case_contract_change_actions.event_id",
                "case_contract_change_actions.id",
            ],
            name="fk_case_change_action_impact_relations__action",
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
            name="fk_case_change_action_impact_relations__applicability",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "tenant_id", "id", name="uq_case_change_action_impact_relations__tenant_id"
        ),
        sa.UniqueConstraint(
            "tenant_id",
            "case_id",
            "event_id",
            "id",
            name="uq_case_change_action_impact_relations__event_id",
        ),
        sa.UniqueConstraint(
            "tenant_id",
            "case_id",
            "event_id",
            "action_id",
            "revision",
            name="uq_case_change_action_impact_relations__revision",
        ),
        sa.UniqueConstraint(
            "tenant_id", "command_id", name="uq_case_change_action_impact_relations__command"
        ),
        sa.UniqueConstraint(
            "tenant_id",
            "idempotency_key",
            name="uq_case_change_action_impact_relations__idempotency",
        ),
        sa.CheckConstraint(
            "revision > 0",
            name="ck_case_contract_change_action_impact_relations__revision_positive",
        ),
        sa.CheckConstraint(
            "state IN ('LINKED', 'UNKNOWN', 'NOT_APPLICABLE')",
            name="ck_case_contract_change_action_impact_relations__state_closed",
        ),
        sa.CheckConstraint(
            "length(trim(rationale)) > 0",
            name="ck_case_contract_change_action_impact_relations__rationale_required",
        ),
        sa.CheckConstraint(
            "(state = 'LINKED' AND unknown_reason IS NULL) OR "
            "(state IN ('UNKNOWN', 'NOT_APPLICABLE') "
            "AND NULLIF(BTRIM(unknown_reason), '') IS NOT NULL)",
            name="ck_case_contract_change_action_impact_relations__state_matches_reason",
        ),
    )
    op.create_index(
        "ix_case_contract_change_action_impact_relations_tenant_id",
        "case_contract_change_action_impact_relations",
        ["tenant_id"],
    )
    op.create_index(
        "ix_case_change_action_impact_relations__event_revision",
        "case_contract_change_action_impact_relations",
        ["tenant_id", "case_id", "event_id", "action_id", "revision"],
    )
    op.create_table(
        "case_contract_change_action_impact_links",
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("case_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("event_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("relation_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("declaration_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id", "case_id", "event_id", "relation_id"],
            [
                "case_contract_change_action_impact_relations.tenant_id",
                "case_contract_change_action_impact_relations.case_id",
                "case_contract_change_action_impact_relations.event_id",
                "case_contract_change_action_impact_relations.id",
            ],
            name="fk_case_change_action_impact_links__relation",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id", "case_id", "event_id", "declaration_id"],
            [
                "case_contract_change_impact_declarations.tenant_id",
                "case_contract_change_impact_declarations.case_id",
                "case_contract_change_impact_declarations.event_id",
                "case_contract_change_impact_declarations.id",
            ],
            name="fk_case_change_action_impact_links__declaration",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint(
            "tenant_id",
            "relation_id",
            "declaration_id",
            name="pk_case_contract_change_action_impact_links",
        ),
        sa.UniqueConstraint(
            "tenant_id",
            "relation_id",
            "position",
            name="uq_case_change_action_impact_links__position",
        ),
    )
    op.create_index(
        "ix_case_change_action_impact_links__event",
        "case_contract_change_action_impact_links",
        ["tenant_id", "case_id", "event_id", "relation_id"],
    )
    op.execute("""
        CREATE FUNCTION validate_case_change_action_impact_relation() RETURNS trigger AS $$
        DECLARE
            stored_applicability UUID;
            latest_review_id UUID;
            latest_decision TEXT;
        BEGIN
            SELECT applicability_id INTO stored_applicability
            FROM case_contract_change_actions
            WHERE tenant_id = NEW.tenant_id AND case_id = NEW.case_id
              AND event_id = NEW.event_id AND id = NEW.action_id;
            SELECT id, decision INTO latest_review_id, latest_decision
            FROM case_contract_change_applicabilities
            WHERE tenant_id = NEW.tenant_id AND case_id = NEW.case_id
              AND event_id = NEW.event_id
            ORDER BY revision DESC, id DESC LIMIT 1;
            IF stored_applicability IS DISTINCT FROM NEW.applicability_id
               OR latest_review_id IS DISTINCT FROM stored_applicability
               OR latest_decision IS DISTINCT FROM 'APPLICABLE_TO_HANDOVER' THEN
                RAISE EXCEPTION 'C4 action must retain its current applicable C1 review';
            END IF;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)
    op.execute("""
        CREATE TRIGGER case_change_action_impact_relation_guard
        BEFORE INSERT ON case_contract_change_action_impact_relations
        FOR EACH ROW EXECUTE FUNCTION validate_case_change_action_impact_relation();
    """)
    op.execute("""
        CREATE FUNCTION validate_case_change_action_impact_link() RETURNS trigger AS $$
        DECLARE
            relation_state TEXT;
            declaration_linkage UUID;
            latest_linkage UUID;
            latest_linkage_state TEXT;
        BEGIN
            SELECT state INTO relation_state
            FROM case_contract_change_action_impact_relations
            WHERE tenant_id = NEW.tenant_id AND case_id = NEW.case_id
              AND event_id = NEW.event_id AND id = NEW.relation_id;
            IF relation_state IS DISTINCT FROM 'LINKED' THEN
                RAISE EXCEPTION 'C4 child links require a LINKED parent';
            END IF;
            SELECT linkage_id INTO declaration_linkage
            FROM case_contract_change_impact_declarations
            WHERE tenant_id = NEW.tenant_id AND case_id = NEW.case_id
              AND event_id = NEW.event_id AND id = NEW.declaration_id;
            SELECT id, state INTO latest_linkage, latest_linkage_state
            FROM case_contract_change_engagement_links
            WHERE tenant_id = NEW.tenant_id AND case_id = NEW.case_id
              AND event_id = NEW.event_id
            ORDER BY revision DESC, id DESC LIMIT 1;
            IF latest_linkage_state IS DISTINCT FROM 'LINKED'
               OR declaration_linkage IS DISTINCT FROM latest_linkage THEN
                RAISE EXCEPTION 'C4 declaration must use the current linked C2 revision';
            END IF;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)
    op.execute("""
        CREATE TRIGGER case_change_action_impact_link_guard
        BEFORE INSERT ON case_contract_change_action_impact_links
        FOR EACH ROW EXECUTE FUNCTION validate_case_change_action_impact_link();
    """)
    op.execute("""
        CREATE FUNCTION validate_case_change_action_impact_relation_children() RETURNS trigger AS $$
        DECLARE
            link_count BIGINT;
            relation_state TEXT;
        BEGIN
            SELECT state INTO relation_state
            FROM case_contract_change_action_impact_relations
            WHERE tenant_id = NEW.tenant_id AND id = NEW.id;
            SELECT count(*) INTO link_count
            FROM case_contract_change_action_impact_links
            WHERE tenant_id = NEW.tenant_id AND relation_id = NEW.id;
            IF (relation_state = 'LINKED' AND link_count = 0)
               OR (relation_state IN ('UNKNOWN', 'NOT_APPLICABLE') AND link_count <> 0) THEN
                RAISE EXCEPTION 'C4 relation state does not match its exact C3 links';
            END IF;
            RETURN NULL;
        END;
        $$ LANGUAGE plpgsql;
    """)
    op.execute("""
        CREATE CONSTRAINT TRIGGER case_change_action_impact_relation_children_guard
        AFTER INSERT ON case_contract_change_action_impact_relations
        DEFERRABLE INITIALLY DEFERRED
        FOR EACH ROW EXECUTE FUNCTION validate_case_change_action_impact_relation_children();
    """)
    op.execute("""
        CREATE FUNCTION reject_case_change_action_impact_mutation() RETURNS trigger AS $$
        BEGIN
            RAISE EXCEPTION 'case contract change action impact records are append-only';
        END;
        $$ LANGUAGE plpgsql;
    """)
    op.execute("""
        CREATE TRIGGER case_change_action_impact_relations_append_only
        BEFORE UPDATE OR DELETE ON case_contract_change_action_impact_relations
        FOR EACH ROW EXECUTE FUNCTION reject_case_change_action_impact_mutation();
    """)
    op.execute("""
        CREATE TRIGGER case_change_action_impact_links_append_only
        BEFORE UPDATE OR DELETE ON case_contract_change_action_impact_links
        FOR EACH ROW EXECUTE FUNCTION reject_case_change_action_impact_mutation();
    """)


def downgrade() -> None:
    op.execute(
        "DROP TRIGGER IF EXISTS case_change_action_impact_links_append_only "
        "ON case_contract_change_action_impact_links"
    )
    op.execute(
        "DROP TRIGGER IF EXISTS case_change_action_impact_relations_append_only "
        "ON case_contract_change_action_impact_relations"
    )
    op.execute("DROP FUNCTION IF EXISTS reject_case_change_action_impact_mutation()")
    op.execute(
        "DROP TRIGGER IF EXISTS case_change_action_impact_relation_children_guard "
        "ON case_contract_change_action_impact_relations"
    )
    op.execute("DROP FUNCTION IF EXISTS validate_case_change_action_impact_relation_children()")
    op.execute(
        "DROP TRIGGER IF EXISTS case_change_action_impact_link_guard "
        "ON case_contract_change_action_impact_links"
    )
    op.execute("DROP FUNCTION IF EXISTS validate_case_change_action_impact_link()")
    op.execute(
        "DROP TRIGGER IF EXISTS case_change_action_impact_relation_guard "
        "ON case_contract_change_action_impact_relations"
    )
    op.execute("DROP FUNCTION IF EXISTS validate_case_change_action_impact_relation()")
    op.drop_index(
        "ix_case_change_action_impact_links__event",
        table_name="case_contract_change_action_impact_links",
    )
    op.drop_table("case_contract_change_action_impact_links")
    op.drop_index(
        "ix_case_change_action_impact_relations__event_revision",
        table_name="case_contract_change_action_impact_relations",
    )
    op.drop_index(
        "ix_case_contract_change_action_impact_relations_tenant_id",
        table_name="case_contract_change_action_impact_relations",
    )
    op.drop_table("case_contract_change_action_impact_relations")
    op.drop_constraint(
        "uq_case_change_impacts__event_id",
        "case_contract_change_impact_declarations",
        type_="unique",
    )
    op.drop_constraint(
        "uq_case_contract_change_actions__event_id",
        "case_contract_change_actions",
        type_="unique",
    )
