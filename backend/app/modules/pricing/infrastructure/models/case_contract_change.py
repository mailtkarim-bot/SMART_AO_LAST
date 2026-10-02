from datetime import datetime
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.platform.persistence.base import Base, TenantScopedRecord


class CaseContractChangeEventRecord(TenantScopedRecord, Base):
    __tablename__ = "case_contract_change_events"
    __table_args__ = (
        sa.ForeignKeyConstraint(
            ["tenant_id", "case_id"], ["cases.tenant_id", "cases.id"], ondelete="RESTRICT"
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id", "case_id", "handover_snapshot_id"],
            [
                "case_handover_snapshots.tenant_id",
                "case_handover_snapshots.case_id",
                "case_handover_snapshots.id",
            ],
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id", "case_id", "contract_instrument_version_id"],
            [
                "contract_instrument_versions.tenant_id",
                "contract_instrument_versions.case_id",
                "contract_instrument_versions.id",
            ],
            ondelete="RESTRICT",
        ),
        sa.UniqueConstraint("tenant_id", "id", name="uq_case_contract_change_events__tenant_id"),
        sa.UniqueConstraint(
            "tenant_id", "case_id", "id", name="uq_case_contract_change_events__tenant_case_id"
        ),
        sa.UniqueConstraint(
            "tenant_id", "command_id", name="uq_case_contract_change_events__command"
        ),
        sa.UniqueConstraint(
            "tenant_id", "idempotency_key", name="uq_case_contract_change_events__idempotency"
        ),
        sa.CheckConstraint(
            "change_kind IN ('ORDER_OF_SERVICE', 'CHANGE_REQUEST', 'ADDENDUM', 'SCHEDULE_CHANGE')",
            name="case_contract_change_kind_closed",
        ),
        sa.CheckConstraint("length(trim(summary)) > 0", name="summary_required"),
        sa.CheckConstraint("length(trim(scope_note)) > 0", name="scope_note_required"),
        sa.CheckConstraint("jsonb_array_length(source_refs_json) > 0", name="source_required"),
        sa.CheckConstraint("jsonb_array_length(evidence_refs_json) > 0", name="evidence_required"),
        sa.Index(
            "ix_case_contract_change_events__tenant_case_created",
            "tenant_id",
            "case_id",
            "created_at",
            "id",
        ),
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True)
    case_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    handover_snapshot_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    contract_instrument_version_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True))
    change_kind: Mapped[str] = mapped_column(sa.String(32), nullable=False)
    issuer: Mapped[str | None] = mapped_column(sa.String(240))
    summary: Mapped[str] = mapped_column(sa.Text, nullable=False)
    scope_note: Mapped[str] = mapped_column(sa.Text, nullable=False)
    source_refs_json: Mapped[list[str]] = mapped_column(JSONB, nullable=False)
    evidence_refs_json: Mapped[list[str]] = mapped_column(JSONB, nullable=False)
    declared_received_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True), nullable=False
    )
    actor_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    membership_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    command_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    idempotency_key: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    correlation_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True))


class CaseContractChangeApplicabilityRecord(TenantScopedRecord, Base):
    __tablename__ = "case_contract_change_applicabilities"
    __table_args__ = (
        sa.ForeignKeyConstraint(
            ["tenant_id", "case_id", "event_id"],
            [
                "case_contract_change_events.tenant_id",
                "case_contract_change_events.case_id",
                "case_contract_change_events.id",
            ],
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id", "case_id", "handover_snapshot_id"],
            [
                "case_handover_snapshots.tenant_id",
                "case_handover_snapshots.case_id",
                "case_handover_snapshots.id",
            ],
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id", "case_id", "contract_instrument_version_id"],
            [
                "contract_instrument_versions.tenant_id",
                "contract_instrument_versions.case_id",
                "contract_instrument_versions.id",
            ],
            ondelete="RESTRICT",
        ),
        sa.UniqueConstraint(
            "tenant_id", "id", name="uq_case_contract_change_applicabilities__tenant_id"
        ),
        sa.UniqueConstraint(
            "tenant_id",
            "case_id",
            "event_id",
            "id",
            name="uq_case_contract_change_applicabilities__event_id",
        ),
        sa.UniqueConstraint(
            "tenant_id", "command_id", name="uq_case_contract_change_applicabilities__command"
        ),
        sa.UniqueConstraint(
            "tenant_id",
            "idempotency_key",
            name="uq_case_contract_change_applicabilities__idempotency",
        ),
        sa.UniqueConstraint(
            "tenant_id",
            "case_id",
            "event_id",
            "revision",
            name="uq_case_contract_change_applicabilities__revision",
        ),
        sa.CheckConstraint("revision > 0", name="revision_positive"),
        sa.CheckConstraint(
            "decision IN ('APPLICABLE_TO_HANDOVER', 'NOT_APPLICABLE', 'NEEDS_CLARIFICATION')",
            name="decision_closed",
        ),
        sa.CheckConstraint(
            "delta_state IN ('UNKNOWN', 'DECLARED')",
            name="delta_state_closed",
        ),
        sa.CheckConstraint(
            "(delta_state = 'UNKNOWN' AND delta_note IS NULL) OR "
            "(delta_state = 'DECLARED' AND NULLIF(BTRIM(delta_note), '') IS NOT NULL)",
            name="delta_note_matches_state",
        ),
        sa.CheckConstraint("length(trim(rationale)) > 0", name="rationale_required"),
        sa.CheckConstraint("jsonb_array_length(evidence_refs_json) > 0", name="evidence_required"),
        sa.Index(
            "ix_case_contract_change_applicabilities__event_revision",
            "tenant_id",
            "case_id",
            "event_id",
            "revision",
        ),
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True)
    case_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    event_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    handover_snapshot_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    contract_instrument_version_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), nullable=False
    )
    revision: Mapped[int] = mapped_column(sa.Integer, nullable=False)
    decision: Mapped[str] = mapped_column(sa.String(32), nullable=False)
    delta_state: Mapped[str] = mapped_column(sa.String(16), nullable=False)
    delta_note: Mapped[str | None] = mapped_column(sa.Text)
    rationale: Mapped[str] = mapped_column(sa.Text, nullable=False)
    evidence_refs_json: Mapped[list[str]] = mapped_column(JSONB, nullable=False)
    actor_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    membership_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    command_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    idempotency_key: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    correlation_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True))


class CaseContractChangeActionRecord(TenantScopedRecord, Base):
    __tablename__ = "case_contract_change_actions"
    __table_args__ = (
        sa.ForeignKeyConstraint(
            ["tenant_id", "case_id", "event_id"],
            [
                "case_contract_change_events.tenant_id",
                "case_contract_change_events.case_id",
                "case_contract_change_events.id",
            ],
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id", "case_id", "event_id", "applicability_id"],
            [
                "case_contract_change_applicabilities.tenant_id",
                "case_contract_change_applicabilities.case_id",
                "case_contract_change_applicabilities.event_id",
                "case_contract_change_applicabilities.id",
            ],
            ondelete="RESTRICT",
        ),
        sa.UniqueConstraint("tenant_id", "id", name="uq_case_contract_change_actions__tenant_id"),
        sa.UniqueConstraint(
            "tenant_id", "command_id", name="uq_case_contract_change_actions__command"
        ),
        sa.UniqueConstraint(
            "tenant_id", "idempotency_key", name="uq_case_contract_change_actions__idempotency"
        ),
        sa.UniqueConstraint(
            "tenant_id",
            "case_id",
            "event_id",
            "revision",
            name="uq_case_contract_change_actions__revision",
        ),
        sa.CheckConstraint("revision > 0", name="revision_positive"),
        sa.CheckConstraint("length(trim(action_summary)) > 0", name="action_summary_required"),
        sa.CheckConstraint("jsonb_array_length(evidence_refs_json) > 0", name="evidence_required"),
        sa.CheckConstraint(
            "due_at IS NOT NULL OR NULLIF(BTRIM(due_date_absence_reason), '') IS NOT NULL",
            name="due_date_or_reason",
        ),
        sa.Index(
            "ix_case_contract_change_actions__event_revision",
            "tenant_id",
            "case_id",
            "event_id",
            "revision",
        ),
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True)
    case_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    event_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    applicability_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    revision: Mapped[int] = mapped_column(sa.Integer, nullable=False)
    action_summary: Mapped[str] = mapped_column(sa.Text, nullable=False)
    evidence_refs_json: Mapped[list[str]] = mapped_column(JSONB, nullable=False)
    due_at: Mapped[datetime | None] = mapped_column(sa.DateTime(timezone=True))
    due_date_absence_reason: Mapped[str | None] = mapped_column(sa.Text)
    actor_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    membership_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    command_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    idempotency_key: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    correlation_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True))
