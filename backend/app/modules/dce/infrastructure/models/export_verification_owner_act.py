# ruff: noqa: E501
from __future__ import annotations

from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.platform.persistence.base import Base, TenantScopedRecord


class ExportVerificationOwnerActRecord(TenantScopedRecord, Base):
    __tablename__ = "export_verification_owner_acts"
    __table_args__ = (
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["tenant_id", "export_id"], ["contract_query_exports.tenant_id", "contract_query_exports.id"], ondelete="RESTRICT"),
        sa.UniqueConstraint("tenant_id", "id", name="uq_export_verification_owner_acts__tenant_id"),
    )
    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True)
    export_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    owner_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    approved: Mapped[bool] = mapped_column(sa.Boolean, nullable=False)
    rationale: Mapped[str] = mapped_column(sa.Text, nullable=False)

