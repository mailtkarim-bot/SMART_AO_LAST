"""Persist BOAMP transport contract and response digest with each run link."""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision = "20261005_0132"
down_revision = "20261005_0131"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "boamp_ingestion_observation_links",
        sa.Column("source_contract_version", sa.String(length=64), nullable=True),
    )
    op.add_column(
        "boamp_ingestion_observation_links",
        sa.Column("source_response_sha256", sa.CHAR(length=64), nullable=True),
    )
    op.create_check_constraint(
        "boamp_links_transport_source_pair",
        "boamp_ingestion_observation_links",
        "(source_contract_version IS NULL AND source_response_sha256 IS NULL) OR "
        "(source_contract_version IS NOT NULL AND source_response_sha256 IS NOT NULL)",
    )
    op.create_check_constraint(
        "boamp_links_transport_source_contract",
        "boamp_ingestion_observation_links",
        "source_contract_version IS NULL OR source_contract_version ~ '^[A-Z0-9_]{1,64}$'",
    )
    op.create_check_constraint(
        "boamp_links_transport_source_hash",
        "boamp_ingestion_observation_links",
        "source_response_sha256 IS NULL OR source_response_sha256 ~ '^[a-f0-9]{64}$'",
    )


def downgrade() -> None:
    op.drop_constraint(
        "boamp_links_transport_source_hash",
        "boamp_ingestion_observation_links",
        type_="check",
    )
    op.drop_constraint(
        "boamp_links_transport_source_contract",
        "boamp_ingestion_observation_links",
        type_="check",
    )
    op.drop_constraint(
        "boamp_links_transport_source_pair",
        "boamp_ingestion_observation_links",
        type_="check",
    )
    op.drop_column("boamp_ingestion_observation_links", "source_response_sha256")
    op.drop_column("boamp_ingestion_observation_links", "source_contract_version")
