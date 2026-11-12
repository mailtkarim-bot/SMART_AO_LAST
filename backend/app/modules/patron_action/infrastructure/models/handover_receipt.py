from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.platform.persistence.base import Base, TenantScopedRecord


class CaseHandoverReceiptRecord(TenantScopedRecord, Base):
    """An operational document receipt; never a contract acceptance or OS."""

    __tablename__ = "case_handover_receipts"
    __table_args__ = (
        sa.ForeignKeyConstraint(
            ["tenant_id", "case_id", "snapshot_id"],
            [
                "case_handover_snapshots.tenant_id",
                "case_handover_snapshots.case_id",
                "case_handover_snapshots.id",
            ],
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id", "case_id"], ["cases.tenant_id", "cases.id"], ondelete="RESTRICT"
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id", "membership_id"],
            ["tenant_memberships.tenant_id", "tenant_memberships.id"],
            ondelete="RESTRICT",
        ),
        sa.UniqueConstraint("tenant_id", "id", name="uq_handover_receipt__tenant_id"),
        sa.UniqueConstraint("tenant_id", "command_id", name="uq_handover_receipt__command"),
        sa.UniqueConstraint(
            "tenant_id", "idempotency_key", name="uq_handover_receipt__idempotency"
        ),
        sa.CheckConstraint("snapshot_revision > 0", name="snapshot_revision_positive"),
        sa.CheckConstraint("view_sha256 ~ '^[a-f0-9]{64}$'", name="view_sha256"),
        sa.CheckConstraint(
            "receipt_kind IN ('RECEIVED','RECEIVED_WITH_GAPS')", name="receipt_kind"
        ),
        sa.CheckConstraint("length(trim(note)) > 0", name="note_required"),
        sa.Index(
            "ix_handover_receipts__case_snapshot",
            "tenant_id",
            "case_id",
            "snapshot_id",
            "created_at",
        ),
    )
    tenant_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True)
    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True)
    case_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    snapshot_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    snapshot_revision: Mapped[int] = mapped_column(sa.Integer, nullable=False)
    view_sha256: Mapped[str] = mapped_column(sa.CHAR(64), nullable=False)
    receipt_kind: Mapped[str] = mapped_column(sa.String(32), nullable=False)
    note: Mapped[str] = mapped_column(sa.Text, nullable=False)
    actor_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    membership_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    command_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    idempotency_key: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    correlation_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True))
