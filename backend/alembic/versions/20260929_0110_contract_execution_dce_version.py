"""Link human contract acts to the Case DCE version captured at recording."""

# ruff: noqa: E501
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision = "20260929_0110"
down_revision = "20260928_0109"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "contract_execution_evidence",
        sa.Column("case_dce_version_id_at_recording", sa.UUID(), nullable=True),
    )
    op.create_foreign_key(
        "fk_contract_exec_evidence__dce_version",
        "contract_execution_evidence",
        "dce_versions",
        ["tenant_id", "case_dce_version_id_at_recording"],
        ["tenant_id", "id"],
        ondelete="RESTRICT",
    )
    op.create_index(
        "ix_contract_exec_evidence_tenant_case_dce_version",
        "contract_execution_evidence",
        ["tenant_id", "case_id", "case_dce_version_id_at_recording"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_contract_exec_evidence_tenant_case_dce_version",
        table_name="contract_execution_evidence",
    )
    op.drop_constraint(
        "fk_contract_exec_evidence__dce_version",
        "contract_execution_evidence",
        type_="foreignkey",
    )
    op.drop_column("contract_execution_evidence", "case_dce_version_id_at_recording")
