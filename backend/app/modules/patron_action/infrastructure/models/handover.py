from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.platform.persistence.base import Base, TenantScopedRecord


class CaseHandoverSnapshotRecord(TenantScopedRecord, Base):
    """Immutable, owner-issued transfer snapshot for one awarded lot."""

    __tablename__ = "case_handover_snapshots"
    __table_args__ = (
        sa.ForeignKeyConstraint(
            ["tenant_id", "case_id"], ["cases.tenant_id", "cases.id"], ondelete="RESTRICT"
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id", "outcome_id"],
            ["case_outcomes.tenant_id", "case_outcomes.id"],
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id", "submission_package_id"],
            ["submission_packages.tenant_id", "submission_packages.id"],
            ondelete="RESTRICT",
        ),
        sa.UniqueConstraint("tenant_id", "id", name="uq_case_handover_snapshots__tenant_id_id"),
        sa.UniqueConstraint(
            "tenant_id", "case_id", "id", name="uq_case_handover_snapshots__tenant_case_id"
        ),
        sa.UniqueConstraint("tenant_id", "command_id", name="uq_case_handover_snapshots__command"),
        sa.UniqueConstraint(
            "tenant_id", "idempotency_key", name="uq_case_handover_snapshots__idempotency"
        ),
        sa.UniqueConstraint(
            "tenant_id", "outcome_id", "revision", name="uq_case_handover_snapshots__revision"
        ),
        sa.CheckConstraint("revision > 0", name="revision_positive"),
        sa.CheckConstraint("package_version > 0", name="package_version_positive"),
        sa.CheckConstraint("manifest_sha256 ~ '^[a-f0-9]{64}$'", name="manifest_sha256"),
        sa.Index("ix_case_handover_snapshots__tenant_case", "tenant_id", "case_id", "created_at"),
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True)
    case_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    outcome_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    lot_reference: Mapped[str] = mapped_column(sa.String(120), nullable=False)
    submission_package_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    package_version: Mapped[int] = mapped_column(sa.Integer, nullable=False)
    manifest_sha256: Mapped[str] = mapped_column(sa.CHAR(64), nullable=False)
    revision: Mapped[int] = mapped_column(sa.Integer, nullable=False)
    snapshot_json: Mapped[dict[str, object]] = mapped_column(JSONB, nullable=False)
    actor_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    membership_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    command_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    idempotency_key: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    correlation_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True))
