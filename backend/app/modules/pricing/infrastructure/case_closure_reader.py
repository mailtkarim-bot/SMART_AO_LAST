import json
from datetime import date, datetime
from hashlib import sha256
from uuid import UUID

import sqlalchemy as sa

from app.modules.case.infrastructure.models.case import CaseRecord
from app.modules.pricing.application.case_closure_projection import financial_observations
from app.modules.pricing.infrastructure.models.contract_execution_evidence import (
    ContractExecutionEvidenceRecord,
)
from app.modules.pricing.infrastructure.models.contract_instrument_supersession import (
    ContractInstrumentSupersessionRecord,
)
from app.modules.pricing.infrastructure.models.contract_instrument_version import (
    ContractInstrumentVersionRecord,
)
from app.modules.pricing.infrastructure.models.payment_cycle_fact import PaymentCycleFactRecord
from app.modules.pricing.infrastructure.models.payment_post_reception_cycle import (
    PaymentPostReceptionCycleRecord,
)
from app.modules.pricing.infrastructure.models.post_reception_obligation import (
    PostReceptionObligationRecord,
)
from app.modules.pricing.infrastructure.models.post_reception_obligation_transition import (
    PostReceptionObligationTransitionRecord,
)


def _json_value(value):
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    if isinstance(value, UUID):
        return str(value)
    return value


def _record(row):
    return {column.name: _json_value(getattr(row, column.name)) for column in row.__table__.columns}


def fingerprint(value):
    return sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    ).hexdigest()


def case_source_identity(session, case):
    versions = list(
        session.scalars(
            sa.select(ContractInstrumentVersionRecord)
            .where(
                ContractInstrumentVersionRecord.tenant_id == case.tenant_id,
                ContractInstrumentVersionRecord.case_id == case.id,
            )
            .order_by(ContractInstrumentVersionRecord.id)
        ).all()
    )
    replacements = list(
        session.scalars(
            sa.select(ContractInstrumentSupersessionRecord)
            .where(
                ContractInstrumentSupersessionRecord.tenant_id == case.tenant_id,
                ContractInstrumentSupersessionRecord.case_id == case.id,
            )
            .order_by(ContractInstrumentSupersessionRecord.id)
        ).all()
    )
    return {
        "dce_version_id": _json_value(case.applicable_dce_version_id),
        "scope_fingerprint": case.scope_fingerprint,
        "dce_freshness": case.dce_freshness,
        "lifecycle": case.lifecycle,
        "contracts_sha256": fingerprint(
            {
                "versions": [_record(r) for r in versions],
                "replacements": [_record(r) for r in replacements],
            }
        ),
    }


def source_context_state(snapshot, current):
    if snapshot is None:
        return "UNKNOWN"
    if (
        snapshot != current
        or current["dce_freshness"] == "REVIEW_REQUIRED"
        or current["lifecycle"] != "ACTIVE"
    ):
        return "REVIEW_REQUIRED"
    return (
        "CURRENT"
        if current["dce_version_id"] and current["dce_freshness"] == "CURRENT"
        else "UNKNOWN"
    )


def closure_dossier(session, tenant_id, case_id):
    case = session.scalar(
        sa.select(CaseRecord)
        .where(CaseRecord.tenant_id == tenant_id, CaseRecord.id == case_id)
        .with_for_update(read=True)
    )
    if case is None:
        return None

    def rows(model):
        return list(
            session.scalars(
                sa.select(model)
                .where(model.tenant_id == tenant_id, model.case_id == case_id)
                .order_by(model.created_at, model.id)
            ).all()
        )

    current_source = case_source_identity(session, case)
    cycles = [_record(r) for r in rows(PaymentPostReceptionCycleRecord)]
    cycles_by_id = {r["id"]: r for r in cycles}
    replacements = [_record(r) for r in rows(ContractInstrumentSupersessionRecord)]
    replaced_ids = {r["replaced_contract_instrument_version_id"] for r in replacements}
    acts = [_record(r) for r in rows(ContractExecutionEvidenceRecord)]
    for act in acts:
        act["context_state"] = source_context_state(
            (act.get("closure_review_json") or {}).get("case_source"), current_source
        )
        instrument = act.get("contract_instrument_version_id")
        act["contract_state"] = (
            "REVIEW_REQUIRED"
            if instrument in replaced_ids
            else "DECLARED"
            if instrument
            else "UNKNOWN"
        )
        if act["contract_state"] == "REVIEW_REQUIRED":
            act["context_state"] = "REVIEW_REQUIRED"
    acts_by_id = {r["id"]: r for r in acts}
    obligations = [_record(r) for r in rows(PostReceptionObligationRecord)]
    transitions = list(
        session.scalars(
            sa.select(PostReceptionObligationTransitionRecord)
            .join(
                PostReceptionObligationRecord,
                sa.and_(
                    PostReceptionObligationRecord.tenant_id
                    == PostReceptionObligationTransitionRecord.tenant_id,
                    PostReceptionObligationRecord.id
                    == PostReceptionObligationTransitionRecord.obligation_id,
                ),
            )
            .where(
                PostReceptionObligationRecord.tenant_id == tenant_id,
                PostReceptionObligationRecord.case_id == case_id,
            )
            .order_by(
                PostReceptionObligationTransitionRecord.revision,
                PostReceptionObligationTransitionRecord.id,
            )
        ).all()
    )
    for obligation in obligations:
        history = [_record(r) for r in transitions if str(r.obligation_id) == obligation["id"]]
        obligation["history"] = history
        obligation["declared_status"] = (
            history[-1]["resulting_status"] if history else obligation["status"]
        )
        review = obligation.get("closure_review_json") or {}
        obligation["responsible"] = review.get("responsible") or "UNKNOWN"
        obligation["expected_evidence"] = review.get("expected_evidence") or "UNKNOWN"
        obligation["context_state"] = source_context_state(
            review.get("case_source"), current_source
        )
        origin = acts_by_id.get(obligation.get("origin_reception_act_id"))
        obligation["origin_context_state"] = (
            origin.get("context_state", "UNKNOWN") if origin else "UNKNOWN"
        )
        if obligation["origin_context_state"] == "REVIEW_REQUIRED":
            obligation["context_state"] = "REVIEW_REQUIRED"
    facts = []
    for row in rows(PaymentCycleFactRecord):
        fact = _record(row)
        fact["fact_id"] = fact.pop("id")
        snapshot = row.source_snapshot_json
        fact["context_state"] = source_context_state(snapshot.get("case_source"), current_source)
        if snapshot.get("cycle") != cycles_by_id.get(str(row.cycle_id)):
            fact["context_state"] = "REVIEW_REQUIRED"
        fact["evidence_state"] = "REFERENCES_DECLARED_ONLY"
        facts.append(fact)
    from app.modules.patron_action.infrastructure.models.case_interview import CaseInterviewRecord
    from app.modules.patron_action.infrastructure.models.rex import CaseRexRecord
    from app.modules.patron_action.infrastructure.models.teaching_applicability import (
        CaseTeachingApplicabilityRecord,
    )
    from app.modules.pricing.infrastructure.models.case_contract_change import (
        CaseContractChangeActionRecord,
        CaseContractChangeApplicabilityRecord,
        CaseContractChangeEventRecord,
    )
    from app.modules.pricing.infrastructure.operational_change_sources import (
        context_state,
        declared_contract,
    )
    from app.platform.events.dispatcher import CommandExecutionError

    events = {row.id: row for row in rows(CaseContractChangeEventRecord)}
    reviews = rows(CaseContractChangeApplicabilityRecord)
    latest = {}
    for review in sorted(reviews, key=lambda row: row.revision):
        latest[review.event_id] = review
    actions = []
    for row in rows(CaseContractChangeActionRecord):
        action = _record(row)
        review = latest.get(row.event_id)
        event = events.get(row.event_id)
        state = "REVIEW_REQUIRED"
        if review is not None and event is not None and review.id == row.applicability_id:
            captured = review.operational_review_json or event.operational_context_json
            state, reasons = context_state(
                session, tenant_id=tenant_id, case_id=case_id, context=captured, storage=None
            )
            # A missing binary cannot suppress an independently verifiable contract replacement.
            if captured and captured.get("declared_contract_id"):
                try:
                    contract = declared_contract(
                        session,
                        tenant_id=tenant_id,
                        case_id=case_id,
                        instrument_id=UUID(captured["declared_contract_id"]),
                    )
                    if contract["declared_contract_record_sha256"] != captured.get(
                        "declared_contract_record_sha256"
                    ):
                        state, reasons = "REVIEW_REQUIRED", ["DECLARED_CONTRACT_REVIEW_REQUIRED"]
                except (CommandExecutionError, ValueError):
                    state, reasons = "REVIEW_REQUIRED", ["DECLARED_CONTRACT_REVIEW_REQUIRED"]
            # No binary reread here: missing bytes/contract alone cannot prove a stale source.
            if state == "REVIEW_REQUIRED" and set(reasons) <= {
                "OFFER_DOCUMENT_REVIEW_REQUIRED",
                "HANDOVER_VIEW_CHANGED",
                "CONTRACT_LINK_UNKNOWN",
            }:
                state = "UNKNOWN"
        action["context_state"] = state
        actions.append(action)
    from app.modules.patron_action.infrastructure.execution_rex_reader import (
        execution_reuse_context_state,
    )

    _invalidate_comparisons(acts, obligations, facts, actions)

    dossier = {
        "change_actions": actions,
        "rex": [_record(r) for r in rows(CaseRexRecord)],
        "interviews": [_record(r) for r in rows(CaseInterviewRecord)],
        "reuse_history": [
            {
                **_record(row),
                "source_case_id": str(interview.case_id),
                "context_state": execution_reuse_context_state(session, tenant_id, row),
            }
            for row, interview in session.execute(
                sa.select(CaseTeachingApplicabilityRecord, CaseInterviewRecord)
                .join(
                    CaseInterviewRecord,
                    sa.and_(
                        CaseInterviewRecord.tenant_id == CaseTeachingApplicabilityRecord.tenant_id,
                        CaseInterviewRecord.id
                        == CaseTeachingApplicabilityRecord.source_interview_id,
                    ),
                )
                .where(
                    CaseTeachingApplicabilityRecord.tenant_id == tenant_id,
                    CaseTeachingApplicabilityRecord.target_case_id == case_id,
                )
                .order_by(
                    CaseTeachingApplicabilityRecord.created_at, CaseTeachingApplicabilityRecord.id
                )
            ).all()
        ],
        "case_id": str(case_id),
        "dce_version_id": _json_value(case.applicable_dce_version_id),
        "case_source": current_source,
        "contract_versions": [_record(r) for r in rows(ContractInstrumentVersionRecord)],
        "lot_references": [str(v) for v in case.scope_json.get("lot_numbers", [])],
        "acts": acts,
        "obligations": obligations,
        "cycles": cycles,
        "facts": facts,
        "contract_replacements": replacements,
        "open_obligation_ids": [
            o["id"]
            for o in obligations
            if o["declared_status"] != "COMPLETED" or o["context_state"] == "REVIEW_REQUIRED"
        ],
        "financial_observations": financial_observations(facts),
        "legal_effect_state": "UNKNOWN",
        "external_receipt_state": "UNKNOWN",
        "completeness_state": "REVIEW_REQUIRED",
    }
    dossier["reference_options"] = [
        {
            "kind": kind,
            "record_id": entry["fact_id"] if kind == "PAYMENT_FACT" else entry["id"],
            "sha256": fingerprint(entry),
            "label": entry.get("summary")
            or entry.get("action_summary")
            or entry.get("kind")
            or "Source enregistrée",
            "context_state": entry.get("context_state", "UNKNOWN"),
        }
        for kind, entries in (
            ("ACT", acts),
            ("OBLIGATION", obligations),
            ("PAYMENT_FACT", facts),
            ("CHANGE_ACTION", actions),
        )
        for entry in entries
    ]
    dossier["dossier_sha256"] = fingerprint(dossier)
    return dossier


class SqlAlchemyCaseClosureReader:
    def __init__(self, session_factory):
        self._session_factory = session_factory

    def read(self, *, tenant_id, case_id):
        with self._session_factory() as session:
            return closure_dossier(session, tenant_id, case_id)


def _invalidate_comparisons(acts, obligations, facts, actions):
    # Only derived read states change; captured reviews and human consent remain historical.
    entries = acts + obligations
    for _ in range(len(entries)):
        references = {
            (kind, row.get("fact_id") if kind == "PAYMENT_FACT" else row["id"]): row
            for kind, rows in (
                ("ACT", acts),
                ("OBLIGATION", obligations),
                ("PAYMENT_FACT", facts),
                ("CHANGE_ACTION", actions),
            )
            for row in rows
        }
        changed = False
        for obligation in obligations:
            origin = references.get(("ACT", obligation.get("origin_reception_act_id")))
            if origin is not None:
                obligation["origin_context_state"] = origin.get("context_state", "UNKNOWN")
                if (
                    origin.get("context_state") == "REVIEW_REQUIRED"
                    and obligation["context_state"] != "REVIEW_REQUIRED"
                ):
                    obligation["context_state"] = "REVIEW_REQUIRED"
                    changed = True
        for row in entries:
            if row["context_state"] == "REVIEW_REQUIRED":
                continue
            for comparison in (row.get("closure_review_json") or {}).get("comparisons", []):
                for side in ("expected", "actual"):
                    ref = comparison[side]
                    source = references.get((ref["kind"], ref["record_id"]))
                    if (
                        source is None
                        or source.get("context_state") == "REVIEW_REQUIRED"
                        or fingerprint(source) != ref["sha256"]
                    ):
                        row["context_state"] = "REVIEW_REQUIRED"
                        changed = True
        if not changed:
            break
