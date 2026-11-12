"""One append-only declared schedule revision; amounts are not copied into accounting."""

from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.platform.persistence.base import Base, TenantScopedRecord


class CashScheduleRevisionRecord(TenantScopedRecord, Base):
    __tablename__ = "cash_schedule_revisions"
    __table_args__ = (
        sa.ForeignKeyConstraint(
            ["tenant_id", "case_id"], ["cases.tenant_id", "cases.id"], ondelete="RESTRICT"
        ),
        sa.UniqueConstraint("tenant_id", "case_id", "revision", name="uq_cash_schedule_revision"),
        sa.CheckConstraint("revision > 0", name="cash_schedule_revision_positive"),
        sa.CheckConstraint(
            "jsonb_typeof(declaration_json)='object' AND "
            "jsonb_typeof(source_snapshot_json)='object'",
            name="cash_schedule_objects",
        ),
        sa.CheckConstraint(
            "length(trim(justification)) > 0 AND human_confirmed", name="cash_schedule_consent"
        ),
    )
    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True)
    tenant_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, index=True)
    case_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    revision: Mapped[int] = mapped_column(sa.Integer, nullable=False)
    declaration_json: Mapped[dict] = mapped_column(JSONB, nullable=False)
    source_snapshot_json: Mapped[dict] = mapped_column(JSONB, nullable=False)
    justification: Mapped[str] = mapped_column(sa.String(2000), nullable=False)
    human_confirmed: Mapped[bool] = mapped_column(sa.Boolean, nullable=False)
    actor_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
