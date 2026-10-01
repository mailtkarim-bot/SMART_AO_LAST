from __future__ import annotations

from datetime import date
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.platform.persistence.base import Base, TenantScopedRecord


class CasePartnerEventRecord(TenantScopedRecord, Base):
    __tablename__ = "case_partner_events"
    __table_args__ = (
        sa.ForeignKeyConstraint(
            ["tenant_id", "case_id"],
            ["cases.tenant_id", "cases.id"],
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id", "related_event_id"],
            ["case_partner_events.tenant_id", "case_partner_events.event_id"],
            ondelete="RESTRICT",
        ),
        sa.UniqueConstraint("tenant_id", "event_id", name="uq_case_partner_events__tenant_event"),
        sa.UniqueConstraint(
            "tenant_id", "case_id", "event_id", name="uq_case_partner_events__tenant_case_event"
        ),
        sa.UniqueConstraint(
            "tenant_id",
            "case_id",
            "partner_id",
            "revision",
            name="uq_case_partner_events__partner_revision",
        ),
        sa.CheckConstraint("revision >= 1", name="revision_positive"),
        sa.CheckConstraint(
            "event_type IN ('REQUESTED', 'RECEIVED', 'ENGAGEMENT_DECLARED')",
            name="event_type",
        ),
        sa.CheckConstraint(
            "partner_kind IN ('SUPPLIER', 'SUBCONTRACTOR', 'CO_CONTRACTOR')",
            name="partner_kind",
        ),
        sa.CheckConstraint(
            "validity_at_recording IN ('UNKNOWN', 'VALID', 'EXPIRED')",
            name="validity_at_recording",
        ),
        sa.CheckConstraint("exclusions_state IN ('UNKNOWN', 'DECLARED')", name="exclusions_state"),
        sa.CheckConstraint(
            "mandate_state IN ("
            "'NOT_APPLICABLE', 'UNKNOWN', 'REQUESTED', 'RECEIVED', 'REVIEW_REQUIRED')",
            name="mandate_state",
        ),
        sa.CheckConstraint("jsonb_typeof(exclusions_json) = 'array'", name="exclusions_array"),
        sa.CheckConstraint(
            "exclusions_state <> 'UNKNOWN' OR jsonb_array_length(exclusions_json) = 0",
            name="unknown_exclusions_empty",
        ),
        sa.CheckConstraint(
            "mandate_state <> 'RECEIVED' OR mandate_source_locator IS NOT NULL",
            name="received_mandate_source",
        ),
        sa.CheckConstraint(
            "event_type <> 'REQUESTED' OR (related_event_id IS NULL AND valid_until IS NULL "
            "AND validity_at_recording = 'UNKNOWN' AND exclusions_state = 'UNKNOWN' "
            "AND jsonb_array_length(exclusions_json) = 0)",
            name="request_state_unknown",
        ),
        sa.CheckConstraint(
            "event_type <> 'ENGAGEMENT_DECLARED' OR related_event_id IS NOT NULL",
            name="engagement_receipt_required",
        ),
        sa.Index(
            "ix_case_partner_events__tenant_case_created",
            "tenant_id",
            "case_id",
            "created_at",
            "event_id",
        ),
        sa.Index(
            "uq_case_partner_events__receipt_engagement",
            "tenant_id",
            "related_event_id",
            unique=True,
            postgresql_where=sa.text("event_type = 'ENGAGEMENT_DECLARED'"),
        ),
    )

    event_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True)
    case_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    partner_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    revision: Mapped[int] = mapped_column(sa.Integer, nullable=False)
    event_type: Mapped[str] = mapped_column(sa.String(24), nullable=False)
    partner_kind: Mapped[str] = mapped_column(sa.String(24), nullable=False)
    partner_label: Mapped[str] = mapped_column(sa.String(240), nullable=False)
    related_event_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True))
    source_locator: Mapped[str] = mapped_column(sa.String(500), nullable=False)
    rationale: Mapped[str] = mapped_column(sa.String(2_000), nullable=False)
    valid_until: Mapped[date | None] = mapped_column(sa.Date)
    validity_at_recording: Mapped[str] = mapped_column(sa.String(8), nullable=False)
    exclusions_state: Mapped[str] = mapped_column(sa.String(16), nullable=False)
    exclusions_json: Mapped[list[str]] = mapped_column(JSONB, nullable=False)
    mandate_state: Mapped[str] = mapped_column(sa.String(24), nullable=False)
    mandate_source_locator: Mapped[str | None] = mapped_column(sa.String(500))
    actor_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    membership_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    command_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    idempotency_key: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    correlation_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True))
