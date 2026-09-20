from datetime import date
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.platform.persistence.base import Base, TenantScopedRecord


class CaseExportRequestRecord(TenantScopedRecord, Base):
    """One Patron request to prepare an export; never evidence of delivery."""

    __tablename__ = "case_export_requests"
    __table_args__ = (
        sa.UniqueConstraint("tenant_id", "id", name="uq_case_export_requests__tenant_id_id"),
        sa.CheckConstraint(
            "artifact_kind IN ('CASE_DOSSIER', 'P7_RESULT', 'REX', 'AUDIT_TRAIL')",
            name="artifact_kind",
        ),
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True)
    case_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    artifact_kind: Mapped[str] = mapped_column(sa.String(24), nullable=False)
    recipient_label: Mapped[str | None] = mapped_column(sa.String(240))
    purpose: Mapped[str] = mapped_column(sa.String(2_000), nullable=False)
    source_locator: Mapped[str | None] = mapped_column(sa.String(500))
    actor_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    membership_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    command_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    idempotency_key: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    correlation_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True))


class CaseRetentionRecord(TenantScopedRecord, Base):
    """One retention decision for an internal Case evidence reference."""

    __tablename__ = "case_retentions"
    __table_args__ = (
        sa.UniqueConstraint("tenant_id", "id", name="uq_case_retentions__tenant_id_id"),
        sa.CheckConstraint(
            "retention_basis IN ('MARKET_RECORD', 'OPEN_LITIGATION', 'INTERNAL_POLICY')",
            name="retention_basis",
        ),
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True)
    case_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    evidence_locator: Mapped[str] = mapped_column(sa.String(500), nullable=False)
    retention_basis: Mapped[str] = mapped_column(sa.String(24), nullable=False)
    retain_until: Mapped[date] = mapped_column(sa.Date(), nullable=False)
    rationale: Mapped[str] = mapped_column(sa.String(2_000), nullable=False)
    actor_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    membership_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    command_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    idempotency_key: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    correlation_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True))
