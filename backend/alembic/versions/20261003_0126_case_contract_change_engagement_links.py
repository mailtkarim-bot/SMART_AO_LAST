"""Persist Patron links from C1 events to A1 sources frozen in B1."""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "20261003_0126"
down_revision = "20261001_0125"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.create_unique_constraint(
        "uq_case_contract_change_events__event_handover",
        "case_contract_change_events",
        ["tenant_id", "case_id", "id", "handover_snapshot_id"],
    )
    op.create_table(
        "case_contract_change_engagement_links",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("case_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("event_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("handover_snapshot_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("revision", sa.Integer(), nullable=False),
        sa.Column("state", sa.String(16), nullable=False),
        sa.Column("selected_sources_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
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
            ["tenant_id", "case_id", "event_id", "handover_snapshot_id"],
            [
                "case_contract_change_events.tenant_id",
                "case_contract_change_events.case_id",
                "case_contract_change_events.id",
                "case_contract_change_events.handover_snapshot_id",
            ],
            name="fk_case_change_engagement_links__event_handover",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id", "case_id", "handover_snapshot_id"],
            [
                "case_handover_snapshots.tenant_id",
                "case_handover_snapshots.case_id",
                "case_handover_snapshots.id",
            ],
            name="fk_case_change_engagement_links__handover",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "tenant_id", "id", name="uq_case_change_engagement_links__tenant_id"
        ),
        sa.UniqueConstraint(
            "tenant_id", "command_id", name="uq_case_change_engagement_links__command"
        ),
        sa.UniqueConstraint(
            "tenant_id",
            "idempotency_key",
            name="uq_case_change_engagement_links__idempotency",
        ),
        sa.UniqueConstraint(
            "tenant_id",
            "case_id",
            "event_id",
            "revision",
            name="uq_case_change_engagement_links__revision",
        ),
        sa.CheckConstraint("revision > 0", name="ck_case_change_engagement_links__revision"),
        sa.CheckConstraint(
            "state IN ('LINKED', 'UNKNOWN')", name="ck_case_change_engagement_links__state"
        ),
        sa.CheckConstraint(
            "length(trim(rationale)) > 0", name="ck_case_change_engagement_links__rationale"
        ),
        sa.CheckConstraint(
            "(state = 'LINKED' AND jsonb_array_length(selected_sources_json) > 0 "
            "AND unknown_reason IS NULL) OR "
            "(state = 'UNKNOWN' AND jsonb_array_length(selected_sources_json) = 0 "
            "AND NULLIF(BTRIM(unknown_reason), '') IS NOT NULL)",
            name="ck_case_change_engagement_links__state_selection",
        ),
    )
    op.create_index(
        "ix_case_change_engagement_links__event_revision",
        "case_contract_change_engagement_links",
        ["tenant_id", "case_id", "event_id", "revision"],
    )
    op.execute("""
        CREATE FUNCTION reject_case_change_engagement_link_mutation() RETURNS trigger AS $$
        BEGIN
            RAISE EXCEPTION 'case_contract_change_engagement_links is append-only';
        END;
        $$ LANGUAGE plpgsql;
    """)
    op.execute("""
        CREATE TRIGGER case_contract_change_engagement_links_append_only
        BEFORE UPDATE OR DELETE ON case_contract_change_engagement_links
        FOR EACH ROW EXECUTE FUNCTION reject_case_change_engagement_link_mutation();
    """)


def downgrade() -> None:
    op.execute(
        "DROP TRIGGER IF EXISTS case_contract_change_engagement_links_append_only "
        "ON case_contract_change_engagement_links"
    )
    op.execute("DROP FUNCTION IF EXISTS reject_case_change_engagement_link_mutation()")
    op.drop_index(
        "ix_case_change_engagement_links__event_revision",
        table_name="case_contract_change_engagement_links",
    )
    op.drop_table("case_contract_change_engagement_links")
    op.drop_constraint(
        "uq_case_contract_change_events__event_handover",
        "case_contract_change_events",
        type_="unique",
    )
