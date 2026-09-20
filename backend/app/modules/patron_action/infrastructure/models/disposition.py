from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.platform.persistence.base import Base, TenantScopedRecord


class CaseDispositionRecord(TenantScopedRecord, Base):
    """Append-only operational suspension, resumption, or closure fact."""

    __tablename__ = "case_dispositions"
    __table_args__ = (
        sa.ForeignKeyConstraint(
            ["tenant_id", "p7_result_id"],
            ["case_p7_results.tenant_id", "case_p7_results.id"],
            ondelete="RESTRICT",
        ),
        sa.UniqueConstraint("tenant_id", "id", name="uq_case_dispositions__tenant_id_id"),
        sa.CheckConstraint("state IN ('SUSPENDED', 'RESUMED', 'CLOSED')", name="state"),
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True)
    case_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    p7_result_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True))
    state: Mapped[str] = mapped_column(sa.String(16), nullable=False)
    reason_code: Mapped[str] = mapped_column(sa.String(64), nullable=False)
    rationale: Mapped[str] = mapped_column(sa.String(2_000), nullable=False)
    source_locator: Mapped[str | None] = mapped_column(sa.String(500))
    actor_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    membership_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    command_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    idempotency_key: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    correlation_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True))
