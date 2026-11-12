"""Immutable human review of an exact Case analysis snapshot."""

from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.platform.persistence.base import Base, TenantScopedRecord


class AnalysisDossierReviewRecord(TenantScopedRecord, Base):
    __tablename__ = "case_analysis_dossier_reviews"
    __table_args__ = (
        sa.PrimaryKeyConstraint("tenant_id", "id"),
        sa.ForeignKeyConstraint(["tenant_id", "case_id"], ["cases.tenant_id", "cases.id"]),
        sa.ForeignKeyConstraint(
            ["tenant_id", "dce_version_id"], ["dce_versions.tenant_id", "dce_versions.id"]
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id", "previous_id"],
            ["case_analysis_dossier_reviews.tenant_id", "case_analysis_dossier_reviews.id"],
        ),
        sa.UniqueConstraint("tenant_id", "case_id", "revision"),
        sa.UniqueConstraint("tenant_id", "command_id"),
        sa.UniqueConstraint("tenant_id", "idempotency_key"),
        sa.CheckConstraint("phase IN ('PREPARED','REVIEWED')", name="analysis_review_phase"),
        sa.CheckConstraint("dossier_sha256 ~ '^[0-9a-f]{64}$'", name="analysis_review_hash"),
        sa.CheckConstraint(
            "jsonb_typeof(axes_json)='array' AND jsonb_array_length(axes_json)=12",
            name="analysis_review_axes",
        ),
        sa.CheckConstraint(
            "(revision=1 AND previous_id IS NULL) OR (revision>1 AND previous_id IS NOT NULL)",
            name="analysis_review_revision",
        ),
        sa.CheckConstraint(
            "length(btrim(justification)) BETWEEN 1 AND 2000", name="analysis_review_justification"
        ),
    )
    id: Mapped[UUID] = mapped_column(sa.Uuid(), nullable=False)
    case_id: Mapped[UUID] = mapped_column(sa.Uuid(), nullable=False)
    dce_version_id: Mapped[UUID] = mapped_column(sa.Uuid(), nullable=False)
    revision: Mapped[int] = mapped_column(nullable=False)
    previous_id: Mapped[UUID | None] = mapped_column(sa.Uuid())
    dossier_sha256: Mapped[str] = mapped_column(sa.CHAR(64), nullable=False)
    phase: Mapped[str] = mapped_column(sa.String(16), nullable=False)
    axes_json: Mapped[list] = mapped_column(JSONB, nullable=False)
    snapshot_json: Mapped[dict] = mapped_column(JSONB, nullable=False)
    justification: Mapped[str] = mapped_column(sa.Text, nullable=False)
    actor_id: Mapped[UUID] = mapped_column(sa.Uuid(), nullable=False)
    membership_id: Mapped[UUID] = mapped_column(sa.Uuid(), nullable=False)
    command_id: Mapped[UUID] = mapped_column(sa.Uuid(), nullable=False)
    idempotency_key: Mapped[UUID] = mapped_column(sa.Uuid(), nullable=False)
