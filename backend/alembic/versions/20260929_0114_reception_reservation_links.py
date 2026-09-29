"""Structure declared receipt outcomes and reserve-lifting source links."""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision = "20260929_0114"
down_revision = "20260929_0113"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "contract_execution_evidence", sa.Column("reception_outcome", sa.String(32), nullable=True)
    )
    op.create_check_constraint(
        "contract_execution_evidence_reception_outcome_closed",
        "contract_execution_evidence",
        "reception_outcome IS NULL OR (act_kind = 'WORK_RECEPTION' AND reception_outcome IN ("
        "'WITH_RESERVATIONS', 'UNDER_RESERVATIONS', 'WITHOUT_RESERVATIONS'))",
    )
    op.add_column(
        "post_reception_obligations", sa.Column("origin_reception_act_id", sa.UUID(), nullable=True)
    )
    op.create_unique_constraint(
        "uq_post_reception_obligations__tenant_case_id",
        "post_reception_obligations",
        ["tenant_id", "case_id", "id"],
    )
    op.create_foreign_key(
        "fk_post_reception_obligation_origin_reception_same_case",
        "post_reception_obligations",
        "contract_execution_evidence",
        ["tenant_id", "case_id", "origin_reception_act_id"],
        ["tenant_id", "case_id", "id"],
        ondelete="RESTRICT",
    )
    op.create_check_constraint(
        "post_reception_obligation_reception_link_type",
        "post_reception_obligations",
        "origin_reception_act_id IS NULL OR obligation_type = 'RESERVES_LIFTING'",
    )
    op.create_index(
        "ix_post_reception_obligations_origin_reception",
        "post_reception_obligations",
        ["tenant_id", "case_id", "origin_reception_act_id"],
        postgresql_where=sa.text("origin_reception_act_id IS NOT NULL"),
    )


def downgrade() -> None:
    op.drop_index(
        "ix_post_reception_obligations_origin_reception", table_name="post_reception_obligations"
    )
    op.drop_constraint(
        "post_reception_obligation_reception_link_type", "post_reception_obligations", type_="check"
    )
    op.drop_constraint(
        "fk_post_reception_obligation_origin_reception_same_case",
        "post_reception_obligations",
        type_="foreignkey",
    )
    op.drop_constraint(
        "uq_post_reception_obligations__tenant_case_id",
        "post_reception_obligations",
        type_="unique",
    )
    op.drop_column("post_reception_obligations", "origin_reception_act_id")
    op.drop_constraint(
        "contract_execution_evidence_reception_outcome_closed",
        "contract_execution_evidence",
        type_="check",
    )
    op.drop_column("contract_execution_evidence", "reception_outcome")
