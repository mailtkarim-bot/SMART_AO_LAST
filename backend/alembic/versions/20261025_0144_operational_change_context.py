"""Explicit operational context/publication on native immutable change records."""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "20261025_0144"
down_revision = "20261025_0143"
branch_labels = None
depends_on = None
COLUMNS = (
    ("case_contract_change_events", "operational_context_json"),
    ("case_contract_change_applicabilities", "operational_review_json"),
    ("case_contract_change_actions", "operational_details_json"),
    ("case_contract_change_action_executions", "operational_publication_json"),
)


def upgrade():
    for table, column in COLUMNS:
        op.add_column(table, sa.Column(column, postgresql.JSONB(), nullable=True))


def downgrade():
    for table, column in COLUMNS:
        if op.get_bind().scalar(
            sa.text(f"SELECT EXISTS (SELECT 1 FROM {table} WHERE {column} IS NOT NULL)")
        ):
            raise RuntimeError("OPERATIONAL_CHANGE_HISTORY_DOWNGRADE_REFUSED")
    for table, column in reversed(COLUMNS):
        op.drop_column(table, column)
