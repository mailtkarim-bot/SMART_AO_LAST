"""Scope existing C09/C08 public identities by tenant and Case, without rewriting rows."""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision = "20261007_0133"
down_revision = "20261005_0132"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None

IDENTITIES = (
    ("case_partner_events", "event_id", "uq_case_partner_events__tenant_event"),
    ("partner_offer_price_declarations", "id", "uq_partner_offer_prices__tenant_id"),
    ("partner_offer_scope_reviews", "id", "uq_partner_scope_review__tenant_id"),
    ("partner_offer_line_comparisons", "id", "uq_partner_offer_line_comparisons__tenant_id"),
)


def _parent_fk_name() -> str:
    for constraint in sa.inspect(op.get_bind()).get_foreign_keys("case_partner_events"):
        if "related_event_id" in constraint["constrained_columns"]:
            name = constraint["name"]
            if name:
                return name
    raise RuntimeError("C09 parent foreign key is missing")


def _replace_primary_key(table: str, columns: list[str]) -> None:
    name = sa.inspect(op.get_bind()).get_pk_constraint(table)["name"]
    if not name:
        raise RuntimeError("C09/C08 primary key is missing")
    op.drop_constraint(name, table, type_="primary")
    op.create_primary_key(name, table, columns)


def _lock_identities() -> None:
    # DDL is local-only until lock duration and deployment are separately qualified.
    for table, _, _ in IDENTITIES:
        op.execute(sa.text(f"LOCK TABLE {table} IN ACCESS EXCLUSIVE MODE"))


def upgrade() -> None:
    _lock_identities()
    if (
        op.get_bind()
        .execute(
            sa.text("""
        SELECT 1 FROM case_partner_events child
        JOIN case_partner_events parent
          ON parent.tenant_id = child.tenant_id AND parent.event_id = child.related_event_id
        WHERE child.case_id <> parent.case_id LIMIT 1
    """)
        )
        .first()
    ):
        raise RuntimeError("C09 upgrade refused: historical parent belongs to another Case")
    op.drop_index("uq_case_partner_events__receipt_engagement", table_name="case_partner_events")
    parent_name = _parent_fk_name()
    op.drop_constraint(parent_name, "case_partner_events", type_="foreignkey")
    for table, identity, unique in IDENTITIES:
        op.drop_constraint(unique, table, type_="unique")
        _replace_primary_key(table, ["tenant_id", "case_id", identity])
    op.create_foreign_key(
        parent_name,
        "case_partner_events",
        "case_partner_events",
        ["tenant_id", "case_id", "related_event_id"],
        ["tenant_id", "case_id", "event_id"],
        ondelete="RESTRICT",
    )

    op.create_index(
        "uq_case_partner_events__receipt_engagement",
        "case_partner_events",
        ["tenant_id", "case_id", "related_event_id"],
        unique=True,
        postgresql_where=sa.text("event_type = 'ENGAGEMENT_DECLARED'"),
    )


def downgrade() -> None:
    _lock_identities()
    for table, identity, _ in IDENTITIES:
        if (
            op.get_bind()
            .execute(
                sa.text(f"SELECT 1 FROM {table} GROUP BY {identity} HAVING count(*) > 1 LIMIT 1")
            )
            .first()
        ):
            raise RuntimeError("C09/C08 downgrade refused: identities repeat across scopes")
    op.drop_index("uq_case_partner_events__receipt_engagement", table_name="case_partner_events")
    parent_name = _parent_fk_name()
    op.drop_constraint(parent_name, "case_partner_events", type_="foreignkey")
    for table, identity, unique in reversed(IDENTITIES):
        _replace_primary_key(table, [identity])
        op.create_unique_constraint(unique, table, ["tenant_id", identity])
    op.create_foreign_key(
        parent_name,
        "case_partner_events",
        "case_partner_events",
        ["tenant_id", "related_event_id"],
        ["tenant_id", "event_id"],
        ondelete="RESTRICT",
    )

    op.create_index(
        "uq_case_partner_events__receipt_engagement",
        "case_partner_events",
        ["tenant_id", "related_event_id"],
        unique=True,
        postgresql_where=sa.text("event_type = 'ENGAGEMENT_DECLARED'"),
    )
