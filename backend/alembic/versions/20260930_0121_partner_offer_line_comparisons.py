"""Persist manual, source-backed partner offer line comparisons."""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision = "20260930_0121"
down_revision = "20260930_0120"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "partner_offer_line_comparisons",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("tenant_id", sa.UUID(), nullable=False),
        sa.Column("case_id", sa.UUID(), nullable=False),
        sa.Column("comparison_id", sa.UUID(), nullable=False),
        sa.Column("revision", sa.Integer(), nullable=False),
        sa.Column("scope_review_id", sa.UUID(), nullable=False),
        sa.Column("actor_id", sa.UUID(), nullable=False),
        sa.Column("membership_id", sa.UUID(), nullable=False),
        sa.Column("command_id", sa.UUID(), nullable=False),
        sa.Column("idempotency_key", sa.UUID(), nullable=False),
        sa.Column("correlation_id", sa.UUID(), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id", "case_id"], ["cases.tenant_id", "cases.id"],
            name="fk_partner_offer_line_comparisons__case", ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id", "case_id", "scope_review_id"],
            [
                "partner_offer_scope_reviews.tenant_id",
                "partner_offer_scope_reviews.case_id",
                "partner_offer_scope_reviews.id",
            ],
            name="fk_partner_offer_line_comparisons__scope_review",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("tenant_id", "id", name="uq_partner_offer_line_comparisons__tenant_id"),
        sa.UniqueConstraint(
            "tenant_id", "case_id", "id", name="uq_partner_offer_line_comparisons__tenant_case_id"
        ),
        sa.UniqueConstraint(
            "tenant_id",
            "case_id",
            "comparison_id",
            "revision",
            name="uq_partner_offer_line_comparison_revision",
        ),
        sa.CheckConstraint("revision > 0", name="revision_positive"),
    )
    op.create_index(
        "ix_partner_offer_line_cmp__tenant_case_revision",
        "partner_offer_line_comparisons",
        ["tenant_id", "case_id", "comparison_id", "revision"],
    )
    op.create_index(
        "ix_partner_offer_line_comparisons_tenant_id",
        "partner_offer_line_comparisons",
        ["tenant_id"],
    )
    op.create_table(
        "partner_offer_line_groups",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("tenant_id", sa.UUID(), nullable=False),
        sa.Column("case_id", sa.UUID(), nullable=False),
        sa.Column("comparison_record_id", sa.UUID(), nullable=False),
        sa.Column("group_id", sa.UUID(), nullable=False),
        sa.Column("disposition", sa.String(32), nullable=False),
        sa.Column("rationale", sa.String(2000), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id", "case_id", "comparison_record_id"],
            [
                "partner_offer_line_comparisons.tenant_id",
                "partner_offer_line_comparisons.case_id",
                "partner_offer_line_comparisons.id",
            ],
            name="fk_partner_offer_line_groups__comparison",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("tenant_id", "id", name="uq_partner_offer_line_groups__tenant_id"),
        sa.UniqueConstraint(
            "tenant_id", "case_id", "id", name="uq_partner_offer_line_groups__tenant_case_id"
        ),
        sa.UniqueConstraint(
            "tenant_id",
            "case_id",
            "comparison_record_id",
            "group_id",
            name="uq_partner_offer_line_group_revision_id",
        ),
        sa.CheckConstraint(
            "disposition IN ('LINKED_BY_PATRON', 'DISTINCT_POSITIONS', 'NEEDS_CLARIFICATION')",
            name="disposition_closed",
        ),
        sa.CheckConstraint(
            "length(trim(rationale)) > 0", name="group_rationale_required"
        ),
    )
    op.create_index(
        "ix_partner_offer_line_groups__tenant_case_comparison",
        "partner_offer_line_groups",
        ["tenant_id", "case_id", "comparison_record_id"],
    )
    op.create_index(
        "ix_partner_offer_line_groups_tenant_id",
        "partner_offer_line_groups",
        ["tenant_id"],
    )

    op.create_table(
        "partner_offer_line_members",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("tenant_id", sa.UUID(), nullable=False),
        sa.Column("case_id", sa.UUID(), nullable=False),
        sa.Column("group_record_id", sa.UUID(), nullable=False),
        sa.Column("receipt_event_id", sa.UUID(), nullable=False),
        sa.Column("line_locator_state", sa.String(16), nullable=False),
        sa.Column("line_locator", sa.String(500), nullable=True),
        sa.Column("item_reference_state", sa.String(16), nullable=False),
        sa.Column("item_reference", sa.String(120), nullable=True),
        sa.Column("designation_state", sa.String(16), nullable=False),
        sa.Column("designation", sa.String(500), nullable=True),
        sa.Column("unit_state", sa.String(16), nullable=False),
        sa.Column("unit", sa.String(32), nullable=True),
        sa.Column("quantity_state", sa.String(16), nullable=False),
        sa.Column("quantity", sa.String(80), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id", "case_id", "group_record_id"],
            [
                "partner_offer_line_groups.tenant_id",
                "partner_offer_line_groups.case_id",
                "partner_offer_line_groups.id",
            ],
            name="fk_partner_offer_line_members__group",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id", "case_id", "receipt_event_id"],
            [
                "case_partner_events.tenant_id",
                "case_partner_events.case_id",
                "case_partner_events.event_id",
            ],
            name="fk_partner_offer_line_members__receipt",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("tenant_id", "id", name="uq_partner_offer_line_members__tenant_id"),
        sa.UniqueConstraint(
            "tenant_id",
            "case_id",
            "group_record_id",
            "receipt_event_id",
            name="uq_partner_offer_line_member_receipt",
        ),
        *_source_field_constraints("line_locator", 500),
        *_source_field_constraints("item_reference", 120),
        *_source_field_constraints("designation", 500),
        *_source_field_constraints("unit", 32),
        *_source_field_constraints("quantity", 80),
    )
    op.create_index(
        "ix_partner_offer_line_members__tenant_case_group",
        "partner_offer_line_members",
        ["tenant_id", "case_id", "group_record_id"],
    )
    op.create_index(
        "ix_partner_offer_line_members_tenant_id",
        "partner_offer_line_members",
        ["tenant_id"],
    )

    for table_name, suffix in (
        ("partner_offer_line_comparisons", "line_comparisons"),
        ("partner_offer_line_groups", "line_groups"),
        ("partner_offer_line_members", "line_members"),
    ):
        _install_append_only(table_name, suffix)

    op.execute("""
        CREATE FUNCTION validate_partner_offer_line_comparison() RETURNS trigger AS $$
        DECLARE
            group_count integer;
            parent_scope partner_offer_scope_reviews%ROWTYPE;
        BEGIN
            SELECT * INTO parent_scope
            FROM partner_offer_scope_reviews review
            WHERE review.tenant_id = NEW.tenant_id
              AND review.case_id = NEW.case_id
              AND review.id = NEW.scope_review_id;

            IF NOT FOUND OR parent_scope.decision <> 'SAME_SCOPE_CONFIRMED' THEN
                RAISE EXCEPTION 'partner offer line comparison requires confirmed scope review';
            END IF;
            IF parent_scope.revision IS DISTINCT FROM (
                SELECT max(current_review.revision)
                FROM partner_offer_scope_reviews current_review
                WHERE current_review.tenant_id = parent_scope.tenant_id
                  AND current_review.case_id = parent_scope.case_id
                  AND current_review.comparison_id = parent_scope.comparison_id
            ) THEN
                RAISE EXCEPTION 'partner offer line comparison requires current scope review';
            END IF;

            SELECT count(*) INTO group_count
            FROM partner_offer_line_groups line_group
            WHERE line_group.tenant_id = NEW.tenant_id
              AND line_group.case_id = NEW.case_id
              AND line_group.comparison_record_id = NEW.id;
            IF group_count < 1 OR group_count > 100 THEN
                RAISE EXCEPTION 'partner offer line comparison group count invalid';
            END IF;

            IF EXISTS (
                SELECT 1
                FROM partner_offer_line_groups line_group
                LEFT JOIN partner_offer_line_members member
                  ON member.tenant_id = line_group.tenant_id
                 AND member.case_id = line_group.case_id
                 AND member.group_record_id = line_group.id
                LEFT JOIN case_partner_events receipt
                  ON receipt.tenant_id = member.tenant_id
                 AND receipt.case_id = member.case_id
                 AND receipt.event_id = member.receipt_event_id
                WHERE line_group.tenant_id = NEW.tenant_id
                  AND line_group.case_id = NEW.case_id
                  AND line_group.comparison_record_id = NEW.id
                GROUP BY line_group.id
                HAVING count(member.id) < 2
                    OR count(member.id) > 20
                    OR count(DISTINCT receipt.partner_id) <> count(member.id)
                    OR count(*) FILTER (
                        WHERE member.id IS NOT NULL
                          AND NOT EXISTS (
                              SELECT 1
                              FROM partner_offer_scope_review_offers scope_member
                              WHERE scope_member.tenant_id = NEW.tenant_id
                                AND scope_member.case_id = NEW.case_id
                                AND scope_member.review_id = NEW.scope_review_id
                                AND scope_member.receipt_event_id = member.receipt_event_id
                          )
                    ) > 0
                    OR count(*) FILTER (
                        WHERE receipt.event_type IS DISTINCT FROM 'RECEIVED'
                          OR receipt.event_id IS DISTINCT FROM (
                              SELECT latest.event_id
                              FROM case_partner_events latest
                              WHERE latest.tenant_id = receipt.tenant_id
                                AND latest.case_id = receipt.case_id
                                AND latest.partner_id = receipt.partner_id
                                AND latest.event_type = 'RECEIVED'
                              ORDER BY latest.revision DESC
                              LIMIT 1
                          )
                    ) > 0
                    OR count(member.id) <> (
                        SELECT count(*)
                        FROM partner_offer_scope_review_offers scope_member
                        WHERE scope_member.tenant_id = NEW.tenant_id
                          AND scope_member.case_id = NEW.case_id
                          AND scope_member.review_id = NEW.scope_review_id
                    )
            ) THEN
                RAISE EXCEPTION 'partner offer line group scope is incomplete';
            END IF;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)
    op.execute("""
        CREATE CONSTRAINT TRIGGER partner_offer_line_comparison_complete
        AFTER INSERT ON partner_offer_line_comparisons
        DEFERRABLE INITIALLY DEFERRED
        FOR EACH ROW EXECUTE FUNCTION validate_partner_offer_line_comparison();
    """)


def _source_field_constraints(name: str, _max_length: int) -> tuple[sa.CheckConstraint, ...]:
    field_key = {
        "line_locator": "loc",
        "item_reference": "ref",
        "designation": "label",
        "unit": "unit",
        "quantity": "qty",
    }[name]
    return (
        sa.CheckConstraint(
            f"{name}_state IN ('UNKNOWN', 'DECLARED')",
            name=f"{field_key}_state",
        ),
        sa.CheckConstraint(
            f"({name}_state = 'UNKNOWN' AND {name} IS NULL) OR "
            f"({name}_state = 'DECLARED' AND {name} IS NOT NULL AND length(trim({name})) > 0)",
            name=f"{field_key}_value",
        ),
    )


def _install_append_only(table_name: str, suffix: str) -> None:
    op.execute(f"""
        CREATE FUNCTION reject_partner_offer_{suffix}_mutation() RETURNS trigger AS $$
        BEGIN
            RAISE EXCEPTION '{table_name} is append-only';
        END;
        $$ LANGUAGE plpgsql;
    """)
    op.execute(f"""
        CREATE TRIGGER {table_name}_append_only
        BEFORE UPDATE OR DELETE ON {table_name}
        FOR EACH ROW EXECUTE FUNCTION reject_partner_offer_{suffix}_mutation();
    """)


def downgrade() -> None:
    op.execute(
        "DROP TRIGGER IF EXISTS partner_offer_line_comparison_complete "
        "ON partner_offer_line_comparisons"
    )
    op.execute("DROP FUNCTION IF EXISTS validate_partner_offer_line_comparison()")
    for table_name, suffix in (
        ("partner_offer_line_members", "line_members"),
        ("partner_offer_line_groups", "line_groups"),
        ("partner_offer_line_comparisons", "line_comparisons"),
    ):
        op.execute(f"DROP TRIGGER IF EXISTS {table_name}_append_only ON {table_name}")
        op.execute(f"DROP FUNCTION IF EXISTS reject_partner_offer_{suffix}_mutation()")
    op.drop_index(
        "ix_partner_offer_line_members__tenant_case_group",
        table_name="partner_offer_line_members",
    )
    op.drop_index(
        "ix_partner_offer_line_members_tenant_id", table_name="partner_offer_line_members"
    )
    op.drop_table("partner_offer_line_members")
    op.drop_index(
        "ix_partner_offer_line_groups__tenant_case_comparison",
        table_name="partner_offer_line_groups",
    )
    op.drop_index("ix_partner_offer_line_groups_tenant_id", table_name="partner_offer_line_groups")
    op.drop_table("partner_offer_line_groups")
    op.drop_index(
        "ix_partner_offer_line_cmp__tenant_case_revision",
        table_name="partner_offer_line_comparisons",
    )
    op.drop_index(
        "ix_partner_offer_line_comparisons_tenant_id",
        table_name="partner_offer_line_comparisons",
    )
    op.drop_table("partner_offer_line_comparisons")
