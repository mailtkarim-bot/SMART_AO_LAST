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
            "tenant_id",
            "case_id",
            "id",
            "handover_snapshot_id",
            name="uq_case_contract_change_events__event_handover",
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
        sa.UniqueConstraint(
            "tenant_id",
            "case_id",
            "event_id",
            "id",
            name="uq_case_contract_change_actions__event_id",
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


class CaseContractChangeEngagementLinkRecord(TenantScopedRecord, Base):
    """Append-only Patron selection of A1 sources frozen by the linked B1 snapshot."""

    __tablename__ = "case_contract_change_engagement_links"
    __table_args__ = (
        sa.ForeignKeyConstraint(
            ["tenant_id", "case_id", "event_id", "handover_snapshot_id"],
            [
                "case_contract_change_events.tenant_id",
                "case_contract_change_events.case_id",
                "case_contract_change_events.id",
                "case_contract_change_events.handover_snapshot_id",
            ],
            name="fk_case_change_engagement_links__event_handover",
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
        sa.UniqueConstraint("tenant_id", "id", name="uq_case_change_engagement_links__tenant_id"),
        sa.UniqueConstraint(
            "tenant_id", "command_id", name="uq_case_change_engagement_links__command"
        ),
        sa.UniqueConstraint(
            "tenant_id", "idempotency_key", name="uq_case_change_engagement_links__idempotency"
        ),
        sa.UniqueConstraint(
            "tenant_id",
            "case_id",
            "event_id",
            "revision",
            name="uq_case_change_engagement_links__revision",
        ),
        sa.CheckConstraint("revision > 0", name="revision_positive"),
        sa.CheckConstraint("state IN ('LINKED', 'UNKNOWN')", name="state_closed"),
        sa.CheckConstraint("length(trim(rationale)) > 0", name="rationale_required"),
        sa.CheckConstraint(
            "(state = 'LINKED' AND jsonb_array_length(selected_sources_json) > 0 "
            "AND unknown_reason IS NULL) OR "
            "(state = 'UNKNOWN' AND jsonb_array_length(selected_sources_json) = 0 "
            "AND NULLIF(BTRIM(unknown_reason), '') IS NOT NULL)",
            name="state_matches_selection",
        ),
        sa.Index(
            "ix_case_change_engagement_links__event_revision",
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
    revision: Mapped[int] = mapped_column(sa.Integer, nullable=False)
    state: Mapped[str] = mapped_column(sa.String(16), nullable=False)
    selected_sources_json: Mapped[list[dict[str, object]]] = mapped_column(JSONB, nullable=False)
    rationale: Mapped[str] = mapped_column(sa.Text, nullable=False)
    unknown_reason: Mapped[str | None] = mapped_column(sa.Text)
    actor_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    membership_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    command_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    idempotency_key: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    correlation_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True))


class CaseContractChangeImpactDeclarationRecord(TenantScopedRecord, Base):
    """Append-only human C3 impact declaration for one exact C2/A1 source and axis."""

    __tablename__ = "case_contract_change_impact_declarations"
    __table_args__ = (
        sa.ForeignKeyConstraint(
            ["tenant_id", "case_id", "event_id"],
            [
                "case_contract_change_events.tenant_id",
                "case_contract_change_events.case_id",
                "case_contract_change_events.id",
            ],
            name="fk_case_change_impact__event",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id", "linkage_id"],
            [
                "case_contract_change_engagement_links.tenant_id",
                "case_contract_change_engagement_links.id",
            ],
            name="fk_case_change_impact__c2_linkage",
            ondelete="RESTRICT",
        ),
        sa.UniqueConstraint("tenant_id", "id", name="uq_case_change_impacts__tenant_id"),
        sa.UniqueConstraint("tenant_id", "command_id", name="uq_case_change_impacts__command"),
        sa.UniqueConstraint(
            "tenant_id", "idempotency_key", name="uq_case_change_impacts__idempotency"
        ),
        sa.UniqueConstraint(
            "tenant_id",
            "case_id",
            "event_id",
            "id",
            name="uq_case_change_impacts__event_id",
        ),
        sa.UniqueConstraint(
            "tenant_id",
            "case_id",
            "event_id",
            "linkage_id",
            "condition_id",
            "impact_id",
            "impact_revision",
            "axis",
            "revision",
            name="uq_case_change_impact__source_axis_revision",
        ),
        sa.CheckConstraint("revision > 0", name="revision_positive"),
        sa.CheckConstraint("impact_revision > 0", name="impact_revision_positive"),
        sa.CheckConstraint(
            "axis IN ('SCOPE', 'COST', 'CASH', 'SCHEDULE', 'CAPACITY')", name="axis_closed"
        ),
        sa.CheckConstraint("impact_state IN ('DECLARED', 'UNKNOWN')", name="impact_state_closed"),
        sa.CheckConstraint(
            "measurement_state IN ('DECLARED', 'UNKNOWN', 'NOT_APPLICABLE')",
            name="measurement_state_closed",
        ),
        sa.CheckConstraint(
            "(impact_state = 'DECLARED' AND NULLIF(BTRIM(impact_summary), '') IS NOT NULL "
            "AND impact_unknown_reason IS NULL AND jsonb_array_length(evidence_refs_json) > 0) OR "
            "(impact_state = 'UNKNOWN' AND impact_summary IS NULL "
            "AND NULLIF(BTRIM(impact_unknown_reason), '') IS NOT NULL)",
            name="impact_state_matches_summary",
        ),
        sa.CheckConstraint(
            "(axis = 'SCOPE' AND measurement_state = 'NOT_APPLICABLE' "
            "AND value_as_declared IS NULL AND currency_code IS NULL AND unit IS NULL "
            "AND measurement_unknown_reason IS NULL) OR "
            "(axis <> 'SCOPE' AND impact_state = 'UNKNOWN' "
            "AND measurement_state = 'UNKNOWN' AND value_as_declared IS NULL "
            "AND currency_code IS NULL AND unit IS NULL) OR "
            "(axis IN ('COST', 'CASH') AND impact_state = 'DECLARED' "
            "AND measurement_state = 'DECLARED' "
            "AND value_as_declared ~ '^-?[0-9]+([,.][0-9]{1,6})?$' "
            "AND currency_code ~ '^[A-Z]{3}$' AND unit IS NULL "
            "AND measurement_unknown_reason IS NULL) OR "
            "(axis IN ('SCHEDULE', 'CAPACITY') AND impact_state = 'DECLARED' "
            "AND measurement_state = 'DECLARED' "
            "AND value_as_declared ~ '^-?[0-9]+([,.][0-9]{1,6})?$' "
            "AND NULLIF(BTRIM(unit), '') IS NOT NULL AND currency_code IS NULL "
            "AND measurement_unknown_reason IS NULL) OR "
            "(axis <> 'SCOPE' AND impact_state = 'DECLARED' "
            "AND measurement_state = 'UNKNOWN' AND value_as_declared IS NULL "
            "AND currency_code IS NULL AND unit IS NULL "
            "AND NULLIF(BTRIM(measurement_unknown_reason), '') IS NOT NULL)",
            name="measurement_matches_axis_state",
        ),
        sa.CheckConstraint("length(trim(rationale)) > 0", name="rationale_required"),
        sa.CheckConstraint("jsonb_array_length(source_refs_json) > 0", name="source_refs_required"),
        sa.Index(
            "ix_case_change_impacts__event_linkage_revision",
            "tenant_id",
            "case_id",
            "event_id",
            "linkage_id",
            "revision",
        ),
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True)
    case_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    event_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    linkage_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    condition_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    impact_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    impact_revision: Mapped[int] = mapped_column(sa.Integer, nullable=False)
    source_a1_json: Mapped[dict[str, object]] = mapped_column(JSONB, nullable=False)
    axis: Mapped[str] = mapped_column(sa.String(16), nullable=False)
    revision: Mapped[int] = mapped_column(sa.Integer, nullable=False)
    impact_state: Mapped[str] = mapped_column(sa.String(16), nullable=False)
    impact_summary: Mapped[str | None] = mapped_column(sa.Text)
    impact_unknown_reason: Mapped[str | None] = mapped_column(sa.Text)
    measurement_state: Mapped[str] = mapped_column(sa.String(16), nullable=False)
    value_as_declared: Mapped[str | None] = mapped_column(sa.String(80))
    currency_code: Mapped[str | None] = mapped_column(sa.CHAR(3))
    unit: Mapped[str | None] = mapped_column(sa.String(32))
    measurement_unknown_reason: Mapped[str | None] = mapped_column(sa.Text)
    assumptions_json: Mapped[list[str]] = mapped_column(JSONB, nullable=False)
    source_refs_json: Mapped[list[str]] = mapped_column(JSONB, nullable=False)
    evidence_refs_json: Mapped[list[str]] = mapped_column(JSONB, nullable=False)
    rationale: Mapped[str] = mapped_column(sa.Text, nullable=False)
    actor_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    membership_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    command_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    idempotency_key: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    correlation_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True))


class CaseContractChangeActionImpactRelationRecord(TenantScopedRecord, Base):
    """Append-only Patron relation between one C1 action and exact C3 declarations."""

    __tablename__ = "case_contract_change_action_impact_relations"
    __table_args__ = (
        sa.ForeignKeyConstraint(
            ["tenant_id", "case_id", "event_id"],
            [
                "case_contract_change_events.tenant_id",
                "case_contract_change_events.case_id",
                "case_contract_change_events.id",
            ],
            name="fk_case_change_action_impact_relations__event",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id", "case_id", "event_id", "action_id"],
            [
                "case_contract_change_actions.tenant_id",
                "case_contract_change_actions.case_id",
                "case_contract_change_actions.event_id",
                "case_contract_change_actions.id",
            ],
            name="fk_case_change_action_impact_relations__action",
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
            name="fk_case_change_action_impact_relations__applicability",
            ondelete="RESTRICT",
        ),
        sa.UniqueConstraint(
            "tenant_id", "id", name="uq_case_change_action_impact_relations__tenant_id"
        ),
        sa.UniqueConstraint(
            "tenant_id",
            "case_id",
            "event_id",
            "id",
            name="uq_case_change_action_impact_relations__event_id",
        ),
        sa.UniqueConstraint(
            "tenant_id",
            "case_id",
            "event_id",
            "action_id",
            "revision",
            name="uq_case_change_action_impact_relations__revision",
        ),
        sa.UniqueConstraint(
            "tenant_id",
            "command_id",
            name="uq_case_change_action_impact_relations__command",
        ),
        sa.UniqueConstraint(
            "tenant_id",
            "idempotency_key",
            name="uq_case_change_action_impact_relations__idempotency",
        ),
        sa.CheckConstraint("revision > 0", name="revision_positive"),
        sa.CheckConstraint("state IN ('LINKED', 'UNKNOWN', 'NOT_APPLICABLE')", name="state_closed"),
        sa.CheckConstraint("length(trim(rationale)) > 0", name="rationale_required"),
        sa.CheckConstraint(
            "(state = 'LINKED' AND unknown_reason IS NULL) OR "
            "(state IN ('UNKNOWN', 'NOT_APPLICABLE') "
            "AND NULLIF(BTRIM(unknown_reason), '') IS NOT NULL)",
            name="state_matches_reason",
        ),
        sa.Index(
            "ix_case_change_action_impact_relations__event_revision",
            "tenant_id",
            "case_id",
            "event_id",
            "action_id",
            "revision",
        ),
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True)
    case_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    event_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    action_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    applicability_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    revision: Mapped[int] = mapped_column(sa.Integer, nullable=False)
    state: Mapped[str] = mapped_column(sa.String(24), nullable=False)
    rationale: Mapped[str] = mapped_column(sa.Text, nullable=False)
    unknown_reason: Mapped[str | None] = mapped_column(sa.Text)
    actor_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    membership_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    command_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    idempotency_key: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    correlation_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True))


class CaseContractChangeActionImpactLinkRecord(TenantScopedRecord, Base):
    """Typed FK from a C4 relation to one exact C3 declaration."""

    __tablename__ = "case_contract_change_action_impact_links"
    __table_args__ = (
        sa.ForeignKeyConstraint(
            ["tenant_id", "case_id", "event_id", "relation_id"],
            [
                "case_contract_change_action_impact_relations.tenant_id",
                "case_contract_change_action_impact_relations.case_id",
                "case_contract_change_action_impact_relations.event_id",
                "case_contract_change_action_impact_relations.id",
            ],
            name="fk_case_change_action_impact_links__relation",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id", "case_id", "event_id", "declaration_id"],
            [
                "case_contract_change_impact_declarations.tenant_id",
                "case_contract_change_impact_declarations.case_id",
                "case_contract_change_impact_declarations.event_id",
                "case_contract_change_impact_declarations.id",
            ],
            name="fk_case_change_action_impact_links__declaration",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint(
            "tenant_id",
            "relation_id",
            "declaration_id",
            name="pk_case_contract_change_action_impact_links",
        ),
        sa.UniqueConstraint(
            "tenant_id",
            "relation_id",
            "position",
            name="uq_case_change_action_impact_links__position",
        ),
        sa.Index(
            "ix_case_change_action_impact_links__event",
            "tenant_id",
            "case_id",
            "event_id",
            "relation_id",
        ),
    )

    tenant_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    case_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    event_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    relation_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    declaration_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    position: Mapped[int] = mapped_column(sa.Integer, nullable=False)


class CaseContractChangeActionExecutionRecord(TenantScopedRecord, Base):
    """Append-only C5 declaration tied to one exact C1 action and C4 revision."""

    __tablename__ = "case_contract_change_action_executions"
    __table_args__ = (
        sa.ForeignKeyConstraint(
            ["tenant_id", "case_id", "event_id", "action_id"],
            [
                "case_contract_change_actions.tenant_id",
                "case_contract_change_actions.case_id",
                "case_contract_change_actions.event_id",
                "case_contract_change_actions.id",
            ],
            name="fk_case_change_action_executions__action",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id", "case_id", "event_id", "c4_relation_id"],
            [
                "case_contract_change_action_impact_relations.tenant_id",
                "case_contract_change_action_impact_relations.case_id",
                "case_contract_change_action_impact_relations.event_id",
                "case_contract_change_action_impact_relations.id",
            ],
            name="fk_case_change_action_executions__c4",
            ondelete="RESTRICT",
        ),
        sa.UniqueConstraint("tenant_id", "id", name="uq_case_change_action_executions__tenant_id"),
        sa.UniqueConstraint(
            "tenant_id", "command_id", name="uq_case_change_action_executions__command"
        ),
        sa.UniqueConstraint(
            "tenant_id", "idempotency_key", name="uq_case_change_action_executions__idempotency"
        ),
        sa.UniqueConstraint(
            "tenant_id",
            "case_id",
            "event_id",
            "action_id",
            "revision",
            name="uq_case_change_action_executions__revision",
        ),
        sa.UniqueConstraint(
            "tenant_id",
            "case_id",
            "event_id",
            "id",
            "action_id",
            "c4_relation_id",
            name="uq_case_change_action_executions__exact_parent",
        ),
        sa.CheckConstraint("revision > 0", name="case_change_action_execution_revision_positive"),
        sa.CheckConstraint(
            "declared_state IN ('DECLARED_PERFORMED', 'DECLARED_PARTIAL', "
            "'DECLARED_NOT_PERFORMED', 'UNKNOWN')",
            name="case_change_action_execution_state_closed",
        ),
        sa.CheckConstraint(
            "(declared_state = 'UNKNOWN' AND declared_summary IS NULL "
            "AND NULLIF(BTRIM(unknown_reason), '') IS NOT NULL) OR "
            "(declared_state <> 'UNKNOWN' AND NULLIF(BTRIM(declared_summary), '') IS NOT NULL "
            "AND unknown_reason IS NULL)",
            name="case_change_action_execution_declaration_matches_state",
        ),
        sa.CheckConstraint(
            "evidence_state IN ('UNKNOWN', 'REFERENCED', 'RETRIEVED') AND "
            "((evidence_state = 'UNKNOWN' AND jsonb_array_length(evidence_refs_json) = 0) OR "
            "(evidence_state = 'REFERENCED' AND jsonb_array_length(evidence_refs_json) > 0) OR "
            "evidence_state = 'RETRIEVED')",
            name="case_change_action_execution_evidence_matches_refs",
        ),
        sa.CheckConstraint(
            "external_confirmation_state IN ('UNKNOWN', 'NOT_CONFIRMED') AND "
            "((external_confirmation_state = 'UNKNOWN' AND external_confirmation_note IS NULL) OR "
            "(external_confirmation_state = 'NOT_CONFIRMED' "
            "AND NULLIF(BTRIM(external_confirmation_note), '') IS NOT NULL))",
            name="case_change_action_execution_external_confirmation_matches_state",
        ),
        sa.Index(
            "ix_case_change_action_executions__action_revision",
            "tenant_id",
            "case_id",
            "event_id",
            "action_id",
            "revision",
        ),
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True)
    case_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    event_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    action_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    c4_relation_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    revision: Mapped[int] = mapped_column(sa.Integer, nullable=False)
    declared_state: Mapped[str] = mapped_column(sa.String(32), nullable=False)
    declared_summary: Mapped[str | None] = mapped_column(sa.Text)
    unknown_reason: Mapped[str | None] = mapped_column(sa.Text)
    evidence_refs_json: Mapped[list[str]] = mapped_column(JSONB, nullable=False)
    evidence_state: Mapped[str] = mapped_column(sa.String(16), nullable=False)
    external_confirmation_state: Mapped[str] = mapped_column(sa.String(16), nullable=False)
    external_confirmation_note: Mapped[str | None] = mapped_column(sa.Text)
    actor_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    membership_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    command_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    idempotency_key: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    correlation_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True))


class CaseContractChangeEvidenceObjectRecord(TenantScopedRecord, Base):
    """Private, scanned C5 upload; immutable after clean admission."""

    __tablename__ = "case_contract_change_evidence_objects"
    __table_args__ = (
        sa.ForeignKeyConstraint(
            ["tenant_id", "case_id", "event_id", "action_id"],
            [
                "case_contract_change_actions.tenant_id",
                "case_contract_change_actions.case_id",
                "case_contract_change_actions.event_id",
                "case_contract_change_actions.id",
            ],
            name="fk_case_change_evidence_objects__action",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id", "case_id", "event_id", "c4_relation_id"],
            [
                "case_contract_change_action_impact_relations.tenant_id",
                "case_contract_change_action_impact_relations.case_id",
                "case_contract_change_action_impact_relations.event_id",
                "case_contract_change_action_impact_relations.id",
            ],
            name="fk_case_change_evidence_objects__c4",
            ondelete="RESTRICT",
        ),
        sa.UniqueConstraint("tenant_id", "id", name="uq_case_change_evidence_objects__tenant_id"),
        sa.UniqueConstraint(
            "tenant_id",
            "case_id",
            "event_id",
            "action_id",
            "c4_relation_id",
            "id",
            "evidence_kind",
            name="uq_case_change_evidence_objects__source",
        ),
        sa.UniqueConstraint("storage_key", name="uq_case_change_evidence_objects__storage_key"),
        sa.UniqueConstraint(
            "tenant_id", "command_id", name="uq_case_change_evidence_objects__command"
        ),
        sa.UniqueConstraint(
            "tenant_id", "idempotency_key", name="uq_case_change_evidence_objects__idempotency"
        ),
        sa.CheckConstraint(
            "expected_byte_size <= 150000000",
            name="case_change_evidence_expected_size_limit",
        ),
        sa.CheckConstraint(
            "evidence_kind IN ('EXECUTION_EVIDENCE', 'EXTERNAL_CONFIRMATION')",
            name="case_change_evidence_kind_closed",
        ),
        sa.CheckConstraint("version = 1", name="case_change_evidence_version_immutable"),
        sa.CheckConstraint(
            "state IN ('AWAITING_UPLOAD', 'UPLOADING', 'CLEAN', 'REJECTED')",
            name="case_change_evidence_state_closed",
        ),
        sa.CheckConstraint("expected_byte_size > 0", name="case_change_evidence_expected_size"),
        sa.CheckConstraint(
            "actual_byte_size IS NULL OR actual_byte_size > 0",
            name="case_change_evidence_actual_size",
        ),
        sa.CheckConstraint(
            "sha256 IS NULL OR sha256 ~ '^[0-9a-f]{64}$'",
            name="case_change_evidence_sha256",
        ),
        sa.CheckConstraint(
            "scan_verdict IS NULL OR scan_verdict IN ('CLEAN', 'INFECTED', 'ERROR')",
            name="case_change_evidence_scan_verdict",
        ),
        sa.CheckConstraint(
            "state <> 'CLEAN' OR (actual_byte_size IS NOT NULL AND sha256 IS NOT NULL "
            "AND media_type IS NOT NULL AND scan_verdict = 'CLEAN' "
            "AND scanner_name IS NOT NULL AND scanner_signature_version IS NOT NULL "
            "AND scanned_at IS NOT NULL)",
            name="case_change_evidence_clean_metadata_required",
        ),
        sa.Index(
            "ix_case_change_evidence_objects__action_created",
            "tenant_id",
            "case_id",
            "event_id",
            "action_id",
            "created_at",
        ),
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True)
    case_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    event_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    action_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    c4_relation_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    evidence_kind: Mapped[str] = mapped_column(sa.String(32), nullable=False)
    version: Mapped[int] = mapped_column(sa.Integer, nullable=False, default=1, server_default="1")
    storage_key: Mapped[str] = mapped_column(sa.String(1000), nullable=False)
    expected_byte_size: Mapped[int] = mapped_column(sa.BigInteger, nullable=False)
    actual_byte_size: Mapped[int | None] = mapped_column(sa.BigInteger)
    sha256: Mapped[str | None] = mapped_column(sa.CHAR(64))
    media_type: Mapped[str | None] = mapped_column(sa.String(180))
    state: Mapped[str] = mapped_column(sa.String(24), nullable=False)
    scan_verdict: Mapped[str | None] = mapped_column(sa.String(16))
    scanner_name: Mapped[str | None] = mapped_column(sa.String(120))
    scanner_signature_version: Mapped[str | None] = mapped_column(sa.String(240))
    scanned_at: Mapped[datetime | None] = mapped_column(sa.DateTime(timezone=True))
    expires_at: Mapped[datetime] = mapped_column(sa.DateTime(timezone=True), nullable=False)
    actor_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    membership_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    command_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    idempotency_key: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    correlation_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True))


class CaseContractChangeActionExecutionEvidenceLinkRecord(TenantScopedRecord, Base):
    """Immutable relation from one C5 act to an exact scanned execution piece."""

    __tablename__ = "case_contract_change_action_execution_evidence_links"
    __table_args__ = (
        sa.ForeignKeyConstraint(
            ["tenant_id", "case_id", "event_id", "act_id", "action_id", "c4_relation_id"],
            [
                "case_contract_change_action_executions.tenant_id",
                "case_contract_change_action_executions.case_id",
                "case_contract_change_action_executions.event_id",
                "case_contract_change_action_executions.id",
                "case_contract_change_action_executions.action_id",
                "case_contract_change_action_executions.c4_relation_id",
            ],
            name="fk_case_change_execution_evidence_links__act",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            [
                "tenant_id",
                "case_id",
                "event_id",
                "action_id",
                "c4_relation_id",
                "evidence_id",
                "evidence_kind",
            ],
            [
                "case_contract_change_evidence_objects.tenant_id",
                "case_contract_change_evidence_objects.case_id",
                "case_contract_change_evidence_objects.event_id",
                "case_contract_change_evidence_objects.action_id",
                "case_contract_change_evidence_objects.c4_relation_id",
                "case_contract_change_evidence_objects.id",
                "case_contract_change_evidence_objects.evidence_kind",
            ],
            name="fk_case_change_execution_evidence_links__object",
            ondelete="RESTRICT",
        ),
        sa.CheckConstraint(
            "position >= 0", name="case_change_execution_evidence_position_nonnegative"
        ),
        sa.PrimaryKeyConstraint("tenant_id", "act_id", "evidence_id"),
        sa.UniqueConstraint(
            "tenant_id",
            "act_id",
            "position",
            name="uq_case_change_execution_evidence_links__position",
        ),
        sa.CheckConstraint(
            "evidence_kind = 'EXECUTION_EVIDENCE'",
            name="case_change_execution_evidence_links_kind",
        ),
        sa.Index(
            "ix_case_change_execution_evidence_links__event",
            "tenant_id",
            "case_id",
            "event_id",
            "act_id",
        ),
    )

    tenant_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    case_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    event_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    act_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    action_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    c4_relation_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    evidence_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    evidence_kind: Mapped[str] = mapped_column(sa.String(32), nullable=False)
    position: Mapped[int] = mapped_column(sa.Integer, nullable=False)


class CaseContractChangeExternalConfirmationRecord(TenantScopedRecord, Base):
    """Separate Patron act that links an exact external confirmation to C5."""

    __tablename__ = "case_contract_change_external_confirmations"
    __table_args__ = (
        sa.ForeignKeyConstraint(
            ["tenant_id", "case_id", "event_id", "action_id", "act_id", "c4_relation_id"],
            [
                "case_contract_change_action_executions.tenant_id",
                "case_contract_change_action_executions.case_id",
                "case_contract_change_action_executions.event_id",
                "case_contract_change_action_executions.action_id",
                "case_contract_change_action_executions.id",
                "case_contract_change_action_executions.c4_relation_id",
            ],
            name="fk_case_change_external_confirmations__act",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            [
                "tenant_id",
                "case_id",
                "event_id",
                "action_id",
                "c4_relation_id",
                "evidence_id",
                "evidence_kind",
            ],
            [
                "case_contract_change_evidence_objects.tenant_id",
                "case_contract_change_evidence_objects.case_id",
                "case_contract_change_evidence_objects.event_id",
                "case_contract_change_evidence_objects.action_id",
                "case_contract_change_evidence_objects.c4_relation_id",
                "case_contract_change_evidence_objects.id",
                "case_contract_change_evidence_objects.evidence_kind",
            ],
            name="fk_case_change_external_confirmations__source",
            ondelete="RESTRICT",
        ),
        sa.UniqueConstraint(
            "tenant_id", "id", name="uq_case_change_external_confirmations__tenant_id"
        ),
        sa.UniqueConstraint(
            "tenant_id", "command_id", name="uq_case_change_external_confirmations__command"
        ),
        sa.UniqueConstraint(
            "tenant_id",
            "idempotency_key",
            name="uq_case_change_external_confirmations__idempotency",
        ),
        sa.UniqueConstraint(
            "tenant_id",
            "act_id",
            "revision",
            name="uq_case_change_external_confirmations__revision",
        ),
        sa.CheckConstraint(
            "revision > 0", name="case_change_external_confirmation_revision_positive"
        ),
        sa.CheckConstraint(
            "evidence_kind = 'EXTERNAL_CONFIRMATION'", name="case_change_external_confirmation_kind"
        ),
        sa.CheckConstraint(
            "length(trim(rationale)) > 0", name="case_change_external_confirmation_rationale"
        ),
        sa.Index(
            "ix_case_change_external_confirmations__act_revision", "tenant_id", "act_id", "revision"
        ),
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True)
    case_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    event_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    action_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    act_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    c4_relation_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    evidence_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    evidence_kind: Mapped[str] = mapped_column(sa.String(32), nullable=False)
    revision: Mapped[int] = mapped_column(sa.Integer, nullable=False)
    received_at: Mapped[datetime] = mapped_column(sa.DateTime(timezone=True), nullable=False)
    external_party: Mapped[str | None] = mapped_column(sa.String(240))
    rationale: Mapped[str] = mapped_column(sa.Text, nullable=False)
    actor_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    membership_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    command_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    idempotency_key: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    correlation_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True))
