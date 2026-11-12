"""Keep exact worksheet/cell provenance without inventing legacy sources."""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB

revision = "20261022_0140"
down_revision = "20261021_0139"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("pricing_import_rows", sa.Column("source_locator_json", JSONB(), nullable=True))


def downgrade():
    if op.get_bind().scalar(
        sa.text(
            "SELECT EXISTS (SELECT 1 FROM pricing_import_rows "
            "WHERE source_locator_json IS NOT NULL "
            "AND source_locator_json <> 'null'::jsonb)"
        )
    ):
        raise RuntimeError("PRICING_IMPORT_SOURCE_PROOF_LOSS_REFUSED")
    op.drop_column("pricing_import_rows", "source_locator_json")
