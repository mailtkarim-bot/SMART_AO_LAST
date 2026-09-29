# ruff: noqa: E501
from __future__ import annotations

from app.modules.pricing.application.contract_execution_evidence_read_handler import (
    ContractExecutionEvidenceReadService,
    ContractInstrumentSupersessionReadService,
)
from app.modules.pricing.application.contract_execution_evidence_requalification_read_handler import (
    ContractExecutionEvidenceRequalificationReadService,
)
from app.platform.security.context import ActorKind


class ContractExecutionEvidenceTimelineReadService:
    def __init__(self, *, session_factory):
        self._evidence = ContractExecutionEvidenceReadService(session_factory=session_factory)
        self._supersessions = ContractInstrumentSupersessionReadService(
            session_factory=session_factory
        )
        self._requalifications = ContractExecutionEvidenceRequalificationReadService(
            session_factory=session_factory
        )

    def list_for_case(self, *, actor, case_id):
        if actor.actor_kind is not ActorKind.PATRON_ADMIN or actor.membership_id is None:
            raise PermissionError("PATRON_REQUIRED")
        events: list[dict[str, object]] = []

        for projection in self._evidence.list_for_case(actor=actor, case_id=case_id):
            act = projection.record
            instrument = projection.contract_instrument_version
            events.append(
                {
                    "event_type": "EXECUTION_EVIDENCE",
                    "event_id": act.id,
                    "case_id": act.case_id,
                    "revision": 1,
                    "status": "RECORDED",
                    "status_origin": "HUMAN_ACT",
                    "actor_id": act.actor_id,
                    "recorded_at": act.created_at,
                    "act": {
                        "act_id": act.id,
                        "act_kind": act.act_kind,
                        "reception_outcome": projection.reception_outcome,
                        "summary": act.summary,
                        "declared_event_date": act.declared_event_date,
                        "source_refs": act.source_refs_json,
                        "evidence_refs": act.evidence_refs_json,
                        "case_dce_version_id_at_recording": act.case_dce_version_id_at_recording,
                        "current_dce_relation": projection.version_relation,
                        "contract_instrument_version_id": act.contract_instrument_version_id,
                        "current_instrument_relation": (
                            projection.contract_instrument_version_relation
                        ),
                        "contract_instrument_version": (
                            {
                                "contract_instrument_version_id": instrument.id,
                                "instrument_kind": instrument.instrument_kind,
                                "version_reference": instrument.version_reference,
                                "source_refs": instrument.source_refs_json,
                                "evidence_refs": instrument.evidence_refs_json,
                            }
                            if instrument is not None
                            else None
                        ),
                    },
                }
            )

        for projection in self._supersessions.list_for_case(actor=actor, case_id=case_id):
            record = projection.record
            events.append(
                {
                    "event_type": "INSTRUMENT_SUPERSESSION",
                    "event_id": record.id,
                    "case_id": record.case_id,
                    "revision": 1,
                    "status": "SUPERSEDED",
                    "status_origin": "PATRON_DECLARATION",
                    "actor_id": record.actor_id,
                    "recorded_at": record.created_at,
                    "supersession_id": record.id,
                    "rationale": record.rationale,
                    "replacing": {
                        "contract_instrument_version_id": projection.replacing_version.id,
                        "instrument_kind": projection.replacing_version.instrument_kind,
                        "version_reference": projection.replacing_version.version_reference,
                        "source_refs": projection.replacing_version.source_refs_json,
                        "evidence_refs": projection.replacing_version.evidence_refs_json,
                    },
                    "replaced": {
                        "contract_instrument_version_id": projection.replaced_version.id,
                        "instrument_kind": projection.replaced_version.instrument_kind,
                        "version_reference": projection.replaced_version.version_reference,
                        "source_refs": projection.replaced_version.source_refs_json,
                        "evidence_refs": projection.replaced_version.evidence_refs_json,
                    },
                }
            )

        for projection in self._requalifications.list_for_case(actor=actor, case_id=case_id):
            record = projection.record
            events.append(
                {
                    "event_type": "EVIDENCE_REQUALIFICATION",
                    "event_id": record.id,
                    "case_id": record.case_id,
                    "revision": record.revision,
                    "status": record.decision,
                    "status_origin": "PATRON_DECISION",
                    "actor_id": record.actor_id,
                    "recorded_at": record.created_at,
                    "requalification_id": record.id,
                    "act_id": projection.act.id,
                    "supersession_id": projection.supersession.id,
                    "act_kind": projection.act.act_kind,
                    "act_summary": projection.act.summary,
                    "act_source_refs": projection.act.source_refs_json,
                    "act_evidence_refs": projection.act.evidence_refs_json,
                    "resulting_contract_instrument_version_id": (
                        record.resulting_contract_instrument_version_id
                    ),
                    "resulting_instrument_kind": (
                        projection.resulting_version.instrument_kind
                        if projection.resulting_version is not None
                        else None
                    ),
                    "resulting_version_reference": (
                        projection.resulting_version.version_reference
                        if projection.resulting_version is not None
                        else None
                    ),
                    "rationale": record.rationale,
                }
            )

        return tuple(
            sorted(
                events,
                key=lambda event: (
                    event["revision"],
                    event["recorded_at"],
                    event["event_type"],
                    str(event["event_id"]),
                ),
            )
        )
