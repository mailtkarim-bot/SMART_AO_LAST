"""Transactional handler for sourced post-award contract changes."""

from __future__ import annotations

from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.orm import Session

from app.modules.case.infrastructure.models.case import CaseRecord
from app.modules.patron_action.infrastructure.models.handover import CaseHandoverSnapshotRecord
from app.modules.pricing.application.case_contract_change_commands import (
    RecordCaseContractChangeActionCommand,
    RecordCaseContractChangeActionImpactRelationCommand,
    RecordCaseContractChangeApplicabilityCommand,
    RecordCaseContractChangeEngagementLinkCommand,
    RecordCaseContractChangeEventCommand,
    RecordCaseContractChangeImpactDeclarationCommand,
)
from app.modules.pricing.infrastructure.models.case_contract_change import (
    CaseContractChangeActionImpactLinkRecord,
    CaseContractChangeActionImpactRelationRecord,
    CaseContractChangeActionRecord,
    CaseContractChangeApplicabilityRecord,
    CaseContractChangeEngagementLinkRecord,
    CaseContractChangeEventRecord,
    CaseContractChangeImpactDeclarationRecord,
)
from app.modules.pricing.infrastructure.models.contract_instrument_version import (
    ContractInstrumentVersionRecord,
)
from app.platform.events.dispatcher import (
    CommandContext,
    CommandExecutionError,
    CommandHandler,
    HandlerOutcome,
    PendingDomainEvent,
)


class CaseContractChangeHandler(CommandHandler):
    def execute(
        self,
        *,
        session: Session,
        command,
        context: CommandContext,
    ) -> HandlerOutcome:
        case_id = command.case_id
        tenant_id = UUID(str(context.tenant_id))
        case = session.scalar(
            sa.select(CaseRecord)
            .where(CaseRecord.tenant_id == tenant_id, CaseRecord.id == case_id)
            .with_for_update()
        )
        if case is None:
            raise CommandExecutionError("CASE_NOT_FOUND_OR_FORBIDDEN")
        if isinstance(command, RecordCaseContractChangeEventCommand):
            return self._record_event(session=session, command=command, context=context)
        if isinstance(command, RecordCaseContractChangeApplicabilityCommand):
            return self._record_applicability(session=session, command=command, context=context)
        if isinstance(command, RecordCaseContractChangeActionCommand):
            return self._record_action(session=session, command=command, context=context)
        if isinstance(command, RecordCaseContractChangeActionImpactRelationCommand):
            return self._record_action_impact_relation(
                session=session, command=command, context=context
            )
        if isinstance(command, RecordCaseContractChangeEngagementLinkCommand):
            return self._record_engagement_link(session=session, command=command, context=context)
        if isinstance(command, RecordCaseContractChangeImpactDeclarationCommand):
            return self._record_impact_declaration(
                session=session, command=command, context=context
            )
        raise CommandExecutionError("UNSUPPORTED_CASE_CONTRACT_CHANGE_COMMAND")

    def _record_event(
        self, *, session: Session, command, context: CommandContext
    ) -> HandlerOutcome:
        snapshot = session.scalar(
            sa.select(CaseHandoverSnapshotRecord).where(
                CaseHandoverSnapshotRecord.tenant_id == context.tenant_id,
                CaseHandoverSnapshotRecord.case_id == command.case_id,
                CaseHandoverSnapshotRecord.id == command.handover_snapshot_id,
            )
        )
        if snapshot is None:
            raise CommandExecutionError("HANDOVER_NOT_FOUND_OR_FORBIDDEN")
        if command.contract_instrument_version_id is not None:
            instrument = session.scalar(
                sa.select(ContractInstrumentVersionRecord.id).where(
                    ContractInstrumentVersionRecord.tenant_id == context.tenant_id,
                    ContractInstrumentVersionRecord.case_id == command.case_id,
                    ContractInstrumentVersionRecord.id == command.contract_instrument_version_id,
                )
            )
            if instrument is None:
                raise CommandExecutionError("CONTRACT_INSTRUMENT_NOT_FOUND_OR_FORBIDDEN")
        record = CaseContractChangeEventRecord(
            id=command.event_id,
            tenant_id=context.tenant_id,
            case_id=command.case_id,
            handover_snapshot_id=snapshot.id,
            contract_instrument_version_id=command.contract_instrument_version_id,
            change_kind=command.change_kind,
            issuer=command.issuer,
            summary=command.summary.strip(),
            scope_note=command.scope_note.strip(),
            source_refs_json=list(command.source_refs),
            evidence_refs_json=list(command.evidence_refs),
            declared_received_at=command.declared_received_at,
            actor_id=context.actor_id,
            membership_id=context.membership_id,
            command_id=command.command_id,
            idempotency_key=command.idempotency_key,
            correlation_id=command.correlation_id,
        )
        session.add(record)
        return self._outcome(
            record=record,
            revision=1,
            event_type="CaseContractChangeEventRecorded",
            result_code="CASE_CONTRACT_CHANGE_EVENT_RECORDED",
            payload={
                "case_id": str(command.case_id),
                "handover_snapshot_id": str(snapshot.id),
                "event_id": str(record.id),
                "change_kind": record.change_kind,
                "applicability": "UNKNOWN",
            },
        )

    def _record_applicability(
        self, *, session: Session, command, context: CommandContext
    ) -> HandlerOutcome:
        event = session.scalar(
            sa.select(CaseContractChangeEventRecord).where(
                CaseContractChangeEventRecord.tenant_id == context.tenant_id,
                CaseContractChangeEventRecord.case_id == command.case_id,
                CaseContractChangeEventRecord.id == command.event_id,
            )
        )
        if event is None or event.handover_snapshot_id != command.handover_snapshot_id:
            raise CommandExecutionError("CONTRACT_CHANGE_EVENT_NOT_FOUND_OR_FORBIDDEN")
        if (
            event.contract_instrument_version_id is not None
            and event.contract_instrument_version_id != command.contract_instrument_version_id
        ):
            raise CommandExecutionError("CONTRACT_VERSION_MISMATCH")
        instrument = session.scalar(
            sa.select(ContractInstrumentVersionRecord.id).where(
                ContractInstrumentVersionRecord.tenant_id == context.tenant_id,
                ContractInstrumentVersionRecord.case_id == command.case_id,
                ContractInstrumentVersionRecord.id == command.contract_instrument_version_id,
            )
        )
        if instrument is None:
            raise CommandExecutionError("CONTRACT_INSTRUMENT_NOT_FOUND_OR_FORBIDDEN")
        latest_revision = session.scalar(
            sa.select(
                sa.func.coalesce(sa.func.max(CaseContractChangeApplicabilityRecord.revision), 0)
            ).where(
                CaseContractChangeApplicabilityRecord.tenant_id == context.tenant_id,
                CaseContractChangeApplicabilityRecord.case_id == command.case_id,
                CaseContractChangeApplicabilityRecord.event_id == event.id,
            )
        )
        current_revision = int(latest_revision or 0)
        if command.expected_revision != current_revision:
            raise CommandExecutionError("CONTRACT_CHANGE_APPLICABILITY_VERSION_CONFLICT")
        revision = current_revision + 1
        record = CaseContractChangeApplicabilityRecord(
            id=command.review_id,
            tenant_id=context.tenant_id,
            case_id=command.case_id,
            event_id=event.id,
            handover_snapshot_id=event.handover_snapshot_id,
            contract_instrument_version_id=command.contract_instrument_version_id,
            revision=revision,
            decision=command.decision,
            delta_state=command.delta_state,
            delta_note=command.delta_note.strip() if command.delta_note else None,
            rationale=command.rationale.strip(),
            evidence_refs_json=list(command.evidence_refs),
            actor_id=context.actor_id,
            membership_id=context.membership_id,
            command_id=command.command_id,
            idempotency_key=command.idempotency_key,
            correlation_id=command.correlation_id,
        )
        session.add(record)
        return self._outcome(
            record=record,
            revision=revision,
            event_type="CaseContractChangeApplicabilityRecorded",
            result_code="CASE_CONTRACT_CHANGE_APPLICABILITY_RECORDED",
            payload={
                "case_id": str(command.case_id),
                "event_id": str(event.id),
                "handover_snapshot_id": str(event.handover_snapshot_id),
                "contract_instrument_version_id": str(command.contract_instrument_version_id),
                "decision": command.decision,
            },
        )

    def _record_action(
        self, *, session: Session, command, context: CommandContext
    ) -> HandlerOutcome:
        event = session.scalar(
            sa.select(CaseContractChangeEventRecord).where(
                CaseContractChangeEventRecord.tenant_id == context.tenant_id,
                CaseContractChangeEventRecord.case_id == command.case_id,
                CaseContractChangeEventRecord.id == command.event_id,
            )
        )
        review = session.scalar(
            sa.select(CaseContractChangeApplicabilityRecord).where(
                CaseContractChangeApplicabilityRecord.tenant_id == context.tenant_id,
                CaseContractChangeApplicabilityRecord.case_id == command.case_id,
                CaseContractChangeApplicabilityRecord.event_id == command.event_id,
                CaseContractChangeApplicabilityRecord.id == command.applicability_review_id,
            )
        )
        if event is None or review is None or review.decision != "APPLICABLE_TO_HANDOVER":
            raise CommandExecutionError("CONTRACT_CHANGE_NOT_APPLICABLE_TO_HANDOVER")
        latest_review = session.scalar(
            sa.select(CaseContractChangeApplicabilityRecord)
            .where(
                CaseContractChangeApplicabilityRecord.tenant_id == context.tenant_id,
                CaseContractChangeApplicabilityRecord.case_id == command.case_id,
                CaseContractChangeApplicabilityRecord.event_id == command.event_id,
            )
            .order_by(CaseContractChangeApplicabilityRecord.revision.desc())
            .limit(1)
        )
        if latest_review is None or latest_review.id != review.id:
            raise CommandExecutionError("CONTRACT_CHANGE_APPLICABILITY_STALE")
        latest_revision = session.scalar(
            sa.select(
                sa.func.coalesce(sa.func.max(CaseContractChangeActionRecord.revision), 0)
            ).where(
                CaseContractChangeActionRecord.tenant_id == context.tenant_id,
                CaseContractChangeActionRecord.case_id == command.case_id,
                CaseContractChangeActionRecord.event_id == command.event_id,
            )
        )
        current_revision = int(latest_revision or 0)
        if command.expected_revision != current_revision:
            raise CommandExecutionError("CONTRACT_CHANGE_ACTION_VERSION_CONFLICT")
        revision = current_revision + 1
        record = CaseContractChangeActionRecord(
            id=command.action_id,
            tenant_id=context.tenant_id,
            case_id=command.case_id,
            event_id=event.id,
            applicability_id=review.id,
            revision=revision,
            action_summary=command.action_summary.strip(),
            evidence_refs_json=list(command.evidence_refs),
            due_at=command.due_at,
            due_date_absence_reason=command.due_date_absence_reason,
            actor_id=context.actor_id,
            membership_id=context.membership_id,
            command_id=command.command_id,
            idempotency_key=command.idempotency_key,
            correlation_id=command.correlation_id,
        )
        session.add(record)
        return self._outcome(
            record=record,
            revision=revision,
            event_type="CaseContractChangeActionRecorded",
            result_code="CASE_CONTRACT_CHANGE_ACTION_RECORDED",
            payload={
                "case_id": str(command.case_id),
                "event_id": str(event.id),
                "applicability_id": str(review.id),
                "action_id": str(record.id),
                "state": "RECORDED",
            },
        )

    def _record_engagement_link(
        self, *, session: Session, command, context: CommandContext
    ) -> HandlerOutcome:
        event = session.scalar(
            sa.select(CaseContractChangeEventRecord).where(
                CaseContractChangeEventRecord.tenant_id == context.tenant_id,
                CaseContractChangeEventRecord.case_id == command.case_id,
                CaseContractChangeEventRecord.id == command.event_id,
            )
        )
        if event is None:
            raise CommandExecutionError("CONTRACT_CHANGE_EVENT_NOT_FOUND_OR_FORBIDDEN")
        snapshot = session.scalar(
            sa.select(CaseHandoverSnapshotRecord).where(
                CaseHandoverSnapshotRecord.tenant_id == context.tenant_id,
                CaseHandoverSnapshotRecord.case_id == command.case_id,
                CaseHandoverSnapshotRecord.id == event.handover_snapshot_id,
            )
        )
        if snapshot is None:
            raise CommandExecutionError("HANDOVER_NOT_FOUND_OR_FORBIDDEN")

        decision = snapshot.snapshot_json.get("decision", {})
        frozen_sources = decision.get("condition_sources", []) if isinstance(decision, dict) else []
        frozen_by_key = {
            _source_key(source): source for source in frozen_sources if isinstance(source, dict)
        }
        selected_sources = [source.model_dump(mode="json") for source in command.selected_sources]
        if command.state == "LINKED":
            for source in selected_sources:
                if frozen_by_key.get(_source_key(source)) != source:
                    raise CommandExecutionError("A1_SOURCE_NOT_IN_HANDOVER_SNAPSHOT")

        latest_revision = session.scalar(
            sa.select(
                sa.func.coalesce(sa.func.max(CaseContractChangeEngagementLinkRecord.revision), 0)
            ).where(
                CaseContractChangeEngagementLinkRecord.tenant_id == context.tenant_id,
                CaseContractChangeEngagementLinkRecord.case_id == command.case_id,
                CaseContractChangeEngagementLinkRecord.event_id == event.id,
            )
        )
        current_revision = int(latest_revision or 0)
        if command.expected_revision != current_revision:
            raise CommandExecutionError("CONTRACT_CHANGE_ENGAGEMENT_LINK_VERSION_CONFLICT")

        record = CaseContractChangeEngagementLinkRecord(
            id=command.linkage_id,
            tenant_id=context.tenant_id,
            case_id=command.case_id,
            event_id=event.id,
            handover_snapshot_id=event.handover_snapshot_id,
            revision=current_revision + 1,
            state=command.state,
            selected_sources_json=selected_sources,
            rationale=command.rationale.strip(),
            unknown_reason=command.unknown_reason.strip() if command.unknown_reason else None,
            actor_id=context.actor_id,
            membership_id=context.membership_id,
            command_id=command.command_id,
            idempotency_key=command.idempotency_key,
            correlation_id=command.correlation_id,
        )
        session.add(record)
        return self._outcome(
            record=record,
            revision=record.revision,
            event_type="CaseContractChangeEngagementLinked",
            result_code="CASE_CONTRACT_CHANGE_ENGAGEMENT_LINK_RECORDED",
            payload={
                "case_id": str(command.case_id),
                "event_id": str(event.id),
                "handover_snapshot_id": str(event.handover_snapshot_id),
                "state": record.state,
                "selected_source_count": len(selected_sources),
            },
        )

    def _record_impact_declaration(
        self, *, session: Session, command, context: CommandContext
    ) -> HandlerOutcome:
        event = session.scalar(
            sa.select(CaseContractChangeEventRecord).where(
                CaseContractChangeEventRecord.tenant_id == context.tenant_id,
                CaseContractChangeEventRecord.case_id == command.case_id,
                CaseContractChangeEventRecord.id == command.event_id,
            )
        )
        if event is None:
            raise CommandExecutionError("CONTRACT_CHANGE_EVENT_NOT_FOUND_OR_FORBIDDEN")
        linkage = session.scalar(
            sa.select(CaseContractChangeEngagementLinkRecord).where(
                CaseContractChangeEngagementLinkRecord.tenant_id == context.tenant_id,
                CaseContractChangeEngagementLinkRecord.case_id == command.case_id,
                CaseContractChangeEngagementLinkRecord.event_id == event.id,
                CaseContractChangeEngagementLinkRecord.id == command.linkage_id,
            )
        )
        if linkage is None:
            raise CommandExecutionError("C2_LINKAGE_NOT_FOUND_OR_FORBIDDEN")
        latest_linkage = session.scalar(
            sa.select(CaseContractChangeEngagementLinkRecord)
            .where(
                CaseContractChangeEngagementLinkRecord.tenant_id == context.tenant_id,
                CaseContractChangeEngagementLinkRecord.case_id == command.case_id,
                CaseContractChangeEngagementLinkRecord.event_id == event.id,
            )
            .order_by(CaseContractChangeEngagementLinkRecord.revision.desc())
            .limit(1)
        )
        if latest_linkage is None or latest_linkage.id != linkage.id or linkage.state != "LINKED":
            raise CommandExecutionError("C2_LINKAGE_NOT_CURRENT_OR_LINKED")

        source = command.source.model_dump(mode="json")
        if source not in linkage.selected_sources_json:
            raise CommandExecutionError("A1_SOURCE_NOT_SELECTED_IN_C2")

        latest_revision = session.scalar(
            sa.select(
                sa.func.coalesce(sa.func.max(CaseContractChangeImpactDeclarationRecord.revision), 0)
            ).where(
                CaseContractChangeImpactDeclarationRecord.tenant_id == context.tenant_id,
                CaseContractChangeImpactDeclarationRecord.case_id == command.case_id,
                CaseContractChangeImpactDeclarationRecord.event_id == event.id,
                CaseContractChangeImpactDeclarationRecord.linkage_id == linkage.id,
                CaseContractChangeImpactDeclarationRecord.condition_id
                == command.source.condition_id,
                CaseContractChangeImpactDeclarationRecord.impact_id == command.source.impact_id,
                CaseContractChangeImpactDeclarationRecord.impact_revision
                == command.source.impact_revision,
                CaseContractChangeImpactDeclarationRecord.axis == command.axis,
            )
        )
        current_revision = int(latest_revision or 0)
        if command.expected_revision != current_revision:
            raise CommandExecutionError("CONTRACT_CHANGE_IMPACT_VERSION_CONFLICT")

        record = CaseContractChangeImpactDeclarationRecord(
            id=command.declaration_id,
            tenant_id=context.tenant_id,
            case_id=command.case_id,
            event_id=event.id,
            linkage_id=linkage.id,
            condition_id=command.source.condition_id,
            impact_id=command.source.impact_id,
            impact_revision=command.source.impact_revision,
            source_a1_json=source,
            axis=command.axis,
            revision=current_revision + 1,
            impact_state=command.impact_state,
            impact_summary=command.impact_summary.strip() if command.impact_summary else None,
            impact_unknown_reason=(
                command.impact_unknown_reason.strip() if command.impact_unknown_reason else None
            ),
            measurement_state=command.measurement_state,
            value_as_declared=command.value_as_declared,
            currency_code=command.currency_code,
            unit=command.unit.strip() if command.unit else None,
            measurement_unknown_reason=(
                command.measurement_unknown_reason.strip()
                if command.measurement_unknown_reason
                else None
            ),
            assumptions_json=[item.strip() for item in command.assumptions],
            source_refs_json=[item.strip() for item in command.source_refs],
            evidence_refs_json=[item.strip() for item in command.evidence_refs],
            rationale=command.rationale.strip(),
            actor_id=context.actor_id,
            membership_id=context.membership_id,
            command_id=command.command_id,
            idempotency_key=command.idempotency_key,
            correlation_id=command.correlation_id,
        )
        session.add(record)
        return self._outcome(
            record=record,
            revision=record.revision,
            event_type="CaseContractChangeImpactDeclared",
            result_code="CASE_CONTRACT_CHANGE_IMPACT_DECLARED",
            payload={
                "case_id": str(command.case_id),
                "event_id": str(event.id),
                "linkage_id": str(linkage.id),
                "axis": record.axis,
                "impact_state": record.impact_state,
                "measurement_state": record.measurement_state,
            },
        )

    def _record_action_impact_relation(
        self, *, session: Session, command, context: CommandContext
    ) -> HandlerOutcome:
        action = session.scalar(
            sa.select(CaseContractChangeActionRecord).where(
                CaseContractChangeActionRecord.tenant_id == context.tenant_id,
                CaseContractChangeActionRecord.case_id == command.case_id,
                CaseContractChangeActionRecord.event_id == command.event_id,
                CaseContractChangeActionRecord.id == command.action_id,
            )
        )
        event = session.scalar(
            sa.select(CaseContractChangeEventRecord).where(
                CaseContractChangeEventRecord.tenant_id == context.tenant_id,
                CaseContractChangeEventRecord.case_id == command.case_id,
                CaseContractChangeEventRecord.id == command.event_id,
            )
        )
        if action is None or event is None:
            raise CommandExecutionError("CONTRACT_CHANGE_ACTION_NOT_FOUND_OR_FORBIDDEN")

        latest_review = session.scalar(
            sa.select(CaseContractChangeApplicabilityRecord)
            .where(
                CaseContractChangeApplicabilityRecord.tenant_id == context.tenant_id,
                CaseContractChangeApplicabilityRecord.case_id == command.case_id,
                CaseContractChangeApplicabilityRecord.event_id == command.event_id,
            )
            .order_by(
                CaseContractChangeApplicabilityRecord.revision.desc(),
                CaseContractChangeApplicabilityRecord.id.desc(),
            )
            .limit(1)
        )
        if (
            latest_review is None
            or latest_review.id != action.applicability_id
            or latest_review.decision != "APPLICABLE_TO_HANDOVER"
        ):
            raise CommandExecutionError("CONTRACT_CHANGE_ACTION_APPLICABILITY_STALE")

        current_revision = int(
            session.scalar(
                sa.select(
                    sa.func.coalesce(
                        sa.func.max(CaseContractChangeActionImpactRelationRecord.revision), 0
                    )
                ).where(
                    CaseContractChangeActionImpactRelationRecord.tenant_id == context.tenant_id,
                    CaseContractChangeActionImpactRelationRecord.case_id == command.case_id,
                    CaseContractChangeActionImpactRelationRecord.event_id == command.event_id,
                    CaseContractChangeActionImpactRelationRecord.action_id == command.action_id,
                )
            )
            or 0
        )
        if command.expected_revision != current_revision:
            raise CommandExecutionError("CONTRACT_CHANGE_ACTION_IMPACT_VERSION_CONFLICT")

        declarations = []
        if command.state == "LINKED":
            latest_linkage = session.scalar(
                sa.select(CaseContractChangeEngagementLinkRecord)
                .where(
                    CaseContractChangeEngagementLinkRecord.tenant_id == context.tenant_id,
                    CaseContractChangeEngagementLinkRecord.case_id == command.case_id,
                    CaseContractChangeEngagementLinkRecord.event_id == command.event_id,
                )
                .order_by(
                    CaseContractChangeEngagementLinkRecord.revision.desc(),
                    CaseContractChangeEngagementLinkRecord.id.desc(),
                )
                .limit(1)
            )
            if latest_linkage is None or latest_linkage.state != "LINKED":
                raise CommandExecutionError("C3_LINKAGE_NOT_CURRENT_OR_LINKED")
            declarations = list(
                session.scalars(
                    sa.select(CaseContractChangeImpactDeclarationRecord).where(
                        CaseContractChangeImpactDeclarationRecord.tenant_id == context.tenant_id,
                        CaseContractChangeImpactDeclarationRecord.case_id == command.case_id,
                        CaseContractChangeImpactDeclarationRecord.event_id == command.event_id,
                        CaseContractChangeImpactDeclarationRecord.id.in_(command.declaration_ids),
                    )
                ).all()
            )
            if len(declarations) != len(command.declaration_ids) or any(
                declaration.linkage_id != latest_linkage.id for declaration in declarations
            ):
                raise CommandExecutionError("C3_DECLARATION_NOT_FOUND_OR_STALE")
            declarations_by_id = {declaration.id: declaration for declaration in declarations}
            declarations = [declarations_by_id[item] for item in command.declaration_ids]

        record = CaseContractChangeActionImpactRelationRecord(
            id=command.relation_id,
            tenant_id=context.tenant_id,
            case_id=command.case_id,
            event_id=command.event_id,
            action_id=action.id,
            applicability_id=action.applicability_id,
            revision=current_revision + 1,
            state=command.state,
            rationale=command.rationale.strip(),
            unknown_reason=command.unknown_reason.strip() if command.unknown_reason else None,
            actor_id=context.actor_id,
            membership_id=context.membership_id,
            command_id=command.command_id,
            idempotency_key=command.idempotency_key,
            correlation_id=command.correlation_id,
        )
        session.add(record)
        session.flush()
        for position, declaration in enumerate(declarations):
            session.add(
                CaseContractChangeActionImpactLinkRecord(
                    tenant_id=context.tenant_id,
                    case_id=command.case_id,
                    event_id=command.event_id,
                    relation_id=record.id,
                    declaration_id=declaration.id,
                    position=position,
                )
            )
        return self._outcome(
            record=record,
            revision=record.revision,
            event_type="CaseContractChangeActionImpactRelated",
            result_code="CASE_CONTRACT_CHANGE_ACTION_IMPACT_RELATED",
            payload={
                "case_id": str(command.case_id),
                "event_id": str(command.event_id),
                "action_id": str(action.id),
                "relation_id": str(record.id),
                "state": record.state,
                "declaration_ids": [str(item.id) for item in declarations],
            },
        )

    @staticmethod
    def _outcome(*, record, revision: int, event_type: str, result_code: str, payload: dict):
        return HandlerOutcome(
            result_code=result_code,
            aggregate_refs=(
                {
                    "aggregate_type": event_type,
                    "aggregate_id": str(record.id),
                    "aggregate_revision": revision,
                },
            ),
            events=(
                PendingDomainEvent(
                    aggregate_type=event_type,
                    aggregate_id=record.id,
                    aggregate_revision=revision,
                    event_type=event_type,
                    payload=payload,
                ),
            ),
        )


def _source_key(source: dict[str, object]) -> tuple[object, ...]:
    return (
        source.get("condition_id"),
        source.get("requirement_id"),
        source.get("requirement_revision"),
        source.get("impact_id"),
        source.get("impact_revision"),
        source.get("profile_version_id"),
        source.get("profile_version"),
        source.get("profile_sha256"),
    )
