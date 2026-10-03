"""Tenant-scoped SQLAlchemy projection for contract-change events."""

from __future__ import annotations

from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.orm import Session, sessionmaker

from app.modules.patron_action.infrastructure.models.handover import CaseHandoverSnapshotRecord
from app.modules.pricing.application.case_contract_change_queries import (
    CaseContractChangeReader,
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


class SqlAlchemyCaseContractChangeReader(CaseContractChangeReader):
    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self._session_factory = session_factory

    def list_for_case(self, *, tenant_id: UUID, case_id: UUID) -> tuple[dict[str, object], ...]:
        with self._session_factory() as session:
            events = tuple(
                session.scalars(
                    sa.select(CaseContractChangeEventRecord)
                    .where(
                        CaseContractChangeEventRecord.tenant_id == tenant_id,
                        CaseContractChangeEventRecord.case_id == case_id,
                    )
                    .order_by(
                        CaseContractChangeEventRecord.created_at,
                        CaseContractChangeEventRecord.id,
                    )
                    .limit(100)
                ).all()
            )
            if not events:
                return ()
            event_ids = [event.id for event in events]
            snapshots = {
                item.id: item
                for item in session.scalars(
                    sa.select(CaseHandoverSnapshotRecord).where(
                        CaseHandoverSnapshotRecord.tenant_id == tenant_id,
                        CaseHandoverSnapshotRecord.case_id == case_id,
                        CaseHandoverSnapshotRecord.id.in_(
                            {event.handover_snapshot_id for event in events}
                        ),
                    )
                ).all()
            }
            instrument_ids = {
                event.contract_instrument_version_id
                for event in events
                if event.contract_instrument_version_id is not None
            }
            reviews = tuple(
                session.scalars(
                    sa.select(CaseContractChangeApplicabilityRecord)
                    .where(
                        CaseContractChangeApplicabilityRecord.tenant_id == tenant_id,
                        CaseContractChangeApplicabilityRecord.case_id == case_id,
                        CaseContractChangeApplicabilityRecord.event_id.in_(event_ids),
                    )
                    .order_by(
                        CaseContractChangeApplicabilityRecord.created_at,
                        CaseContractChangeApplicabilityRecord.id,
                    )
                ).all()
            )
            instrument_ids.update(review.contract_instrument_version_id for review in reviews)
            instruments = (
                {
                    item.id: item
                    for item in session.scalars(
                        sa.select(ContractInstrumentVersionRecord).where(
                            ContractInstrumentVersionRecord.tenant_id == tenant_id,
                            ContractInstrumentVersionRecord.case_id == case_id,
                            ContractInstrumentVersionRecord.id.in_(instrument_ids),
                        )
                    ).all()
                }
                if instrument_ids
                else {}
            )
            actions = tuple(
                session.scalars(
                    sa.select(CaseContractChangeActionRecord)
                    .where(
                        CaseContractChangeActionRecord.tenant_id == tenant_id,
                        CaseContractChangeActionRecord.case_id == case_id,
                        CaseContractChangeActionRecord.event_id.in_(event_ids),
                    )
                    .order_by(
                        CaseContractChangeActionRecord.created_at,
                        CaseContractChangeActionRecord.id,
                    )
                ).all()
            )
            engagement_links = tuple(
                session.scalars(
                    sa.select(CaseContractChangeEngagementLinkRecord)
                    .where(
                        CaseContractChangeEngagementLinkRecord.tenant_id == tenant_id,
                        CaseContractChangeEngagementLinkRecord.case_id == case_id,
                        CaseContractChangeEngagementLinkRecord.event_id.in_(event_ids),
                    )
                    .order_by(
                        CaseContractChangeEngagementLinkRecord.revision,
                        CaseContractChangeEngagementLinkRecord.created_at,
                        CaseContractChangeEngagementLinkRecord.id,
                    )
                ).all()
            )
            impact_declarations = tuple(
                session.scalars(
                    sa.select(CaseContractChangeImpactDeclarationRecord)
                    .where(
                        CaseContractChangeImpactDeclarationRecord.tenant_id == tenant_id,
                        CaseContractChangeImpactDeclarationRecord.case_id == case_id,
                        CaseContractChangeImpactDeclarationRecord.event_id.in_(event_ids),
                    )
                    .order_by(
                        CaseContractChangeImpactDeclarationRecord.created_at,
                        CaseContractChangeImpactDeclarationRecord.id,
                    )
                ).all()
            )
            action_impact_relations = tuple(
                session.scalars(
                    sa.select(CaseContractChangeActionImpactRelationRecord)
                    .where(
                        CaseContractChangeActionImpactRelationRecord.tenant_id == tenant_id,
                        CaseContractChangeActionImpactRelationRecord.case_id == case_id,
                        CaseContractChangeActionImpactRelationRecord.event_id.in_(event_ids),
                    )
                    .order_by(
                        CaseContractChangeActionImpactRelationRecord.created_at,
                        CaseContractChangeActionImpactRelationRecord.revision,
                        CaseContractChangeActionImpactRelationRecord.id,
                    )
                ).all()
            )
            action_impact_links = tuple(
                session.scalars(
                    sa.select(CaseContractChangeActionImpactLinkRecord)
                    .where(
                        CaseContractChangeActionImpactLinkRecord.tenant_id == tenant_id,
                        CaseContractChangeActionImpactLinkRecord.case_id == case_id,
                        CaseContractChangeActionImpactLinkRecord.event_id.in_(event_ids),
                    )
                    .order_by(
                        CaseContractChangeActionImpactLinkRecord.relation_id,
                        CaseContractChangeActionImpactLinkRecord.position,
                    )
                ).all()
            )
            reviews_by_event: dict[UUID, list[CaseContractChangeApplicabilityRecord]] = {}
            actions_by_event: dict[UUID, list[CaseContractChangeActionRecord]] = {}
            engagement_links_by_event: dict[UUID, list[CaseContractChangeEngagementLinkRecord]] = {}
            impact_declarations_by_event: dict[
                UUID, list[CaseContractChangeImpactDeclarationRecord]
            ] = {}
            relations_by_event: dict[UUID, list[CaseContractChangeActionImpactRelationRecord]] = {}
            links_by_relation: dict[UUID, list[CaseContractChangeActionImpactLinkRecord]] = {}
            for review in reviews:
                reviews_by_event.setdefault(review.event_id, []).append(review)
            for action in actions:
                actions_by_event.setdefault(action.event_id, []).append(action)
            for link in engagement_links:
                engagement_links_by_event.setdefault(link.event_id, []).append(link)
            for declaration in impact_declarations:
                impact_declarations_by_event.setdefault(declaration.event_id, []).append(
                    declaration
                )
            for relation in action_impact_relations:
                relations_by_event.setdefault(relation.event_id, []).append(relation)
            for link in action_impact_links:
                links_by_relation.setdefault(link.relation_id, []).append(link)

            projections = []
            for event in events:
                snapshot = snapshots.get(event.handover_snapshot_id)
                history = reviews_by_event.get(event.id, [])
                latest_review = history[-1] if history else None
                award = snapshot.snapshot_json.get("award", {}) if snapshot else {}
                offer = snapshot.snapshot_json.get("offer", {}) if snapshot else {}
                decision = snapshot.snapshot_json.get("decision", {}) if snapshot else {}
                a1_sources = (
                    decision.get("condition_sources", []) if isinstance(decision, dict) else []
                )
                linkage_history = engagement_links_by_event.get(event.id, [])
                latest_linkage = linkage_history[-1] if linkage_history else None
                impact_history = impact_declarations_by_event.get(event.id, [])
                declared_version = (
                    instruments.get(event.contract_instrument_version_id)
                    if event.contract_instrument_version_id
                    else None
                )
                projections.append(
                    {
                        "event_id": str(event.id),
                        "case_id": str(case_id),
                        "handover_snapshot_id": str(event.handover_snapshot_id),
                        "outcome_id": str(snapshot.outcome_id) if snapshot else None,
                        "lot_reference": snapshot.lot_reference if snapshot else "UNKNOWN",
                        "offer_package_id": offer.get("submission_package_id"),
                        "offer_package_version": offer.get("package_version"),
                        "offer_manifest_sha256": offer.get("manifest_sha256"),
                        "change_kind": event.change_kind,
                        "issuer": event.issuer,
                        "summary": event.summary,
                        "scope_note": event.scope_note,
                        "source_refs": list(event.source_refs_json),
                        "evidence_refs": list(event.evidence_refs_json),
                        "declared_received_at": event.declared_received_at.isoformat(),
                        "declared_instrument": _instrument_projection(declared_version),
                        "applicability_state": latest_review.decision
                        if latest_review
                        else "UNKNOWN",
                        "applicability_history": [
                            {
                                "review_id": str(review.id),
                                "revision": review.revision,
                                "contract_instrument_version_id": str(
                                    review.contract_instrument_version_id
                                ),
                                "decision": review.decision,
                                "delta_state": review.delta_state,
                                "delta_note": review.delta_note,
                                "rationale": review.rationale,
                                "evidence_refs": list(review.evidence_refs_json),
                                "recorded_at": review.created_at.isoformat(),
                                "contract_instrument": _instrument_projection(
                                    instruments.get(review.contract_instrument_version_id)
                                ),
                            }
                            for review in history
                        ],
                        "actions": [
                            {
                                "action_id": str(action.id),
                                "revision": action.revision,
                                "applicability_review_id": str(action.applicability_id),
                                "summary": action.action_summary,
                                "evidence_refs": list(action.evidence_refs_json),
                                "due_at": action.due_at.isoformat() if action.due_at else None,
                                "due_date_absence_reason": action.due_date_absence_reason,
                                "state": "RECORDED",
                                "recorded_at": action.created_at.isoformat(),
                            }
                            for action in actions_by_event.get(event.id, [])
                        ],
                        "action_impact_relations": [
                            {
                                "relation_id": str(relation.id),
                                "action_id": str(relation.action_id),
                                "applicability_review_id": str(relation.applicability_id),
                                "revision": relation.revision,
                                "state": relation.state,
                                "declaration_ids": [
                                    str(link.declaration_id)
                                    for link in links_by_relation.get(relation.id, [])
                                ],
                                "rationale": relation.rationale,
                                "unknown_reason": relation.unknown_reason,
                                "projection_state": _action_impact_relation_projection_state(
                                    relation=relation,
                                    latest_review=latest_review,
                                    latest_linkage=latest_linkage,
                                    declarations_by_id={item.id: item for item in impact_history},
                                    links=links_by_relation.get(relation.id, []),
                                ),
                                "recorded_at": relation.created_at.isoformat(),
                            }
                            for relation in relations_by_event.get(event.id, [])
                        ],
                        "offer_source_locator": award.get("source_locator"),
                        "a1_engagements_state": "KNOWN" if a1_sources else "UNKNOWN",
                        "a1_engagements": a1_sources,
                        "engagement_linkage_state": latest_linkage.state
                        if latest_linkage
                        else "UNKNOWN",
                        "engagement_linkage_history": [
                            {
                                "linkage_id": str(link.id),
                                "revision": link.revision,
                                "state": link.state,
                                "selected_sources": link.selected_sources_json,
                                "rationale": link.rationale,
                                "unknown_reason": link.unknown_reason,
                                "recorded_at": link.created_at.isoformat(),
                            }
                            for link in linkage_history
                        ],
                        "impact_declarations": [
                            {
                                "declaration_id": str(item.id),
                                "linkage_id": str(item.linkage_id),
                                "source": item.source_a1_json,
                                "axis": item.axis,
                                "revision": item.revision,
                                "impact_state": item.impact_state,
                                "impact_summary": item.impact_summary,
                                "impact_unknown_reason": item.impact_unknown_reason,
                                "measurement_state": item.measurement_state,
                                "value_as_declared": item.value_as_declared,
                                "currency_code": item.currency_code,
                                "unit": item.unit,
                                "measurement_unknown_reason": item.measurement_unknown_reason,
                                "assumptions": list(item.assumptions_json),
                                "source_refs": list(item.source_refs_json),
                                "evidence_refs": list(item.evidence_refs_json),
                                "rationale": item.rationale,
                                "linkage_state": "CURRENT"
                                if latest_linkage is not None
                                and latest_linkage.id == item.linkage_id
                                and latest_linkage.state == "LINKED"
                                else "REVIEW_REQUIRED",
                                "recorded_at": item.created_at.isoformat(),
                            }
                            for item in impact_history
                        ],
                    }
                )
            return tuple(projections)


def _instrument_projection(instrument: ContractInstrumentVersionRecord | None):
    if instrument is None:
        return None
    return {
        "contract_instrument_version_id": str(instrument.id),
        "instrument_kind": instrument.instrument_kind,
        "version_reference": instrument.version_reference,
        "source_refs": list(instrument.source_refs_json),
        "evidence_refs": list(instrument.evidence_refs_json),
    }


def _action_impact_relation_projection_state(
    *, relation, latest_review, latest_linkage, declarations_by_id, links
) -> str:
    if (
        latest_review is None
        or latest_review.id != relation.applicability_id
        or latest_review.decision != "APPLICABLE_TO_HANDOVER"
    ):
        return "REVIEW_REQUIRED"
    if relation.state != "LINKED":
        return "CURRENT"
    if not links:
        return "REVIEW_REQUIRED"
    if latest_linkage is None or latest_linkage.state != "LINKED":
        return "REVIEW_REQUIRED"
    for link in links:
        declaration = declarations_by_id.get(link.declaration_id)
        if declaration is None or declaration.linkage_id != latest_linkage.id:
            return "REVIEW_REQUIRED"
    return "CURRENT"
