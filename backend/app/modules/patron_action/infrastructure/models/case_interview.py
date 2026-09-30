# ruff: noqa: E501, I001
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from datetime import date
from uuid import UUID
from app.platform.persistence.base import Base, TenantScopedRecord

class CaseInterviewRecord(TenantScopedRecord, Base):
    __tablename__ = "case_interviews"
    __table_args__ = (
        sa.ForeignKeyConstraint(
            ["tenant_id", "case_id"],
            ["cases.tenant_id", "cases.id"],
            ondelete="RESTRICT",
        ),
        sa.UniqueConstraint("tenant_id", "id", name="uq_case_interviews__tenant_id_id"),
        sa.CheckConstraint("expires_on > held_on", name="interview_expiry_after_holding"),
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True)
    case_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    held_on: Mapped[date] = mapped_column(sa.Date, nullable=False)
    source_locator: Mapped[str] = mapped_column(sa.String(500), nullable=False)
    rationale: Mapped[str] = mapped_column(sa.String(2_000), nullable=False)
    expires_on: Mapped[date] = mapped_column(sa.Date, nullable=False)
    snapshot_json: Mapped[dict] = mapped_column(JSONB, nullable=False)
    actor_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    membership_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    command_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    idempotency_key: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    correlation_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), nullable=True)
