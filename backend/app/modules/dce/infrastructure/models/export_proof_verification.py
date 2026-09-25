# ruff: noqa: E501
from __future__ import annotations

from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.platform.persistence.base import Base, TenantScopedRecord


class ExportProofVerificationRecord(TenantScopedRecord, Base):
    __tablename__ = "export_proof_verifications"
    __table_args__ = (
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["tenant_id", "export_id"], ["contract_query_exports.tenant_id", "contract_query_exports.id"], ondelete="RESTRICT"),
        sa.UniqueConstraint("tenant_id", "id", name="uq_export_proof_verifications__tenant_id"),
        sa.CheckConstraint("outcome IN ('MATCH', 'MISMATCH', 'UNAVAILABLE')", name="export_proof_verification_outcome_closed"),
    )
    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True)
    export_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    outcome: Mapped[str] = mapped_column(sa.String(16), nullable=False)
    calculated_sha256: Mapped[str | None] = mapped_column(sa.String(64))
    checked_by_actor_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)

