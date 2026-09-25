"""Add local proof hash for READY export transitions."""
# ruff: noqa: E501
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision = "20260925_0098"
down_revision = "20260925_0097"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None

def upgrade() -> None:
    op.add_column("contract_query_export_transitions", sa.Column("local_proof_sha256", sa.String(64), nullable=True))

def downgrade() -> None:
    op.drop_column("contract_query_export_transitions", "local_proof_sha256")
