from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.platform.persistence.base import Base, TenantScopedRecord


class CaseRexRecord(TenantScopedRecord, Base):
    __tablename__ = "case_rex"
    __table_args__ = (
        sa.ForeignKeyConstraint(
            ["tenant_id", "p7_result_id"],
            ["case_p7_results.tenant_id", "case_p7_results.id"],
            ondelete="RESTRICT",
        ),
        sa.UniqueConstraint("tenant_id", "id", name="uq_case_rex__tenant_id_id"),
        sa.CheckConstraint("motif IN ('KNOWN', 'UNKNOWN')", name="motif"),
        sa.CheckConstraint(
            "scope IN ('CASE_ONLY', 'LOT_PATTERN', 'ENTERPRISE_PATTERN')", name="scope"
        ),
        sa.CheckConstraint("validation IN ('PENDING', 'APPROVED')", name="validation"),
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True)
    p7_result_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    case_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    lot_reference: Mapped[str] = mapped_column(sa.String(120), nullable=False)
    motif: Mapped[str] = mapped_column(sa.String(16), nullable=False)
    scope: Mapped[str] = mapped_column(sa.String(24), nullable=False)
    validation: Mapped[str] = mapped_column(sa.String(16), nullable=False)
    observation: Mapped[str] = mapped_column(sa.String(2_000), nullable=False)
    consequence: Mapped[str] = mapped_column(sa.String(2_000), nullable=False)
    follow_up: Mapped[str] = mapped_column(sa.String(2_000), nullable=False)
    source_locator: Mapped[str | None] = mapped_column(sa.String(500))
    actor_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    membership_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    command_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    idempotency_key: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    correlation_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True))
