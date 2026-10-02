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
    CaseContractChangeActionRecord,
    CaseContractChangeApplicabilityRecord,
    CaseContractChangeEventRecord,
)
from app.modules.pricing.infrastructure.models.contract_instrument_version import (
    ContractInstrumentVersionRecord,
)


class SqlAlchemyCaseContractChangeReader(CaseContractChangeReader):
    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self._session_factory = session_factory

    def list_for_case(
        self, *, tenant_id: UUID, case_id: UUID
    ) -> tuple[dict[str, object], ...]:
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
            reviews_by_event: dict[UUID, list[CaseContractChangeApplicabilityRecord]] = {}
            actions_by_event: dict[UUID, list[CaseContractChangeActionRecord]] = {}
            for review in reviews:
                reviews_by_event.setdefault(review.event_id, []).append(review)
            for action in actions:
                actions_by_event.setdefault(action.event_id, []).append(action)

            projections = []
            for event in events:
                snapshot = snapshots.get(event.handover_snapshot_id)
                history = reviews_by_event.get(event.id, [])
                latest_review = history[-1] if history else None
                award = snapshot.snapshot_json.get("award", {}) if snapshot else {}
                offer = snapshot.snapshot_json.get("offer", {}) if snapshot else {}
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
                        "offer_source_locator": award.get("source_locator"),
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
