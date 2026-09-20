"""Record the lot identity carried by an operational task result."""

from collections.abc import Sequence
import sqlalchemy as sa
from alembic import op

revision = "20260919_0076"
down_revision = "20260919_0075"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None

def upgrade() -> None:
    op.add_column("collaborator_task_results", sa.Column("lot_reference", sa.String(120)))

def downgrade() -> None:
    op.drop_column("collaborator_task_results", "lot_reference")
