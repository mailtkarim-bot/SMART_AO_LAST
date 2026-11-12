"""No change, impact, or action is implicitly inherited by another offer's handover."""

import copy
import json
import os
from pathlib import Path
from typing import Any
from uuid import UUID, uuid4

import pytest
import sqlalchemy as sa
from app.modules.pricing.infrastructure.models.case_contract_change import (
    CaseContractChangeActionRecord,
    CaseContractChangeApplicabilityRecord,
    CaseContractChangeEventRecord,
)
from app.platform.persistence.models import DomainEventRecord, OutboxMessageRecord
from tests.db.test_l09_rectified_handover import (
    test_rectified_offer_reaches_responsable_without_inheriting_prior_handover as _run,
)


def identity():
    return dict(command_id=str(uuid4()), idempotency_key=str(uuid4()), correlation_id=str(uuid4()))


@pytest.mark.parametrize("technical_docx", [False, True])
def test_changes_require_explicit_current_v2_sources_and_never_transfer_v1_acts(
    session_factory,
    tmp_path,
    monkeypatch,
    technical_docx,
    closure_qualifier=None,
    handover_runner=None,
):
    stages: list[dict[str, Any]] = []
    variant = "docx" if technical_docx else "markdown"

    def qualify(factory, http, run, control, generation, w, handover):
        case = str(w.case_id)
        root = f"/api/v1/patron/cases/{case}/contract-change-events"
        public_url = f"/api/v1/cases/{case}/contract-change-events"
        view = handover["view"]
        snapshot = view["snapshot"]
        point = snapshot["operational_review"]["points"][0]["point_id"]
        instrument = snapshot["contract_comparison"]["instrument_version_id"]
        context = dict(
            expected_view_sha256=view["view_sha256"],
            point_ids=[point],
            justification=f"Instruction synthétique rapprochée de la passation V{generation}.",
            human_confirmed=True,
            publish=True,
        )

        def counts():
            with factory() as session:
                return tuple(
                    session.scalar(sa.select(sa.func.count()).select_from(m))
                    for m in (DomainEventRecord, OutboxMessageRecord)
                )

        def post(path, body, *, replay=False):
            response = http.client.post(path, headers=http.patron_headers, json=body)
            assert response.status_code == 201, response.text
            if replay:
                repeated = http.client.post(path, headers=http.patron_headers, json=body)
                assert repeated.status_code == 200 and repeated.json()["replayed"], repeated.text
            return response.json()

        def public():
            response = http.client.get(public_url, headers=http.driver_headers)
            assert response.status_code == 200, response.text
            return response.json()

        if generation == 2:
            old = next(x for x in public()["events"] if x["event_id"] == stages[0]["event"])
            assert old["source_state"] == "REVIEW_REQUIRED"
            assert old["actions"][0]["source_state"] == "REVIEW_REQUIRED"
            before = counts()
            stale_event = copy.deepcopy(stages[0]["event_body"])
            stale_event.update(**identity(), event_id=str(uuid4()))
            stale_event["operational_context"]["expected_view_sha256"] = view["view_sha256"]
            denied = http.client.post(root, headers=http.patron_headers, json=stale_event)
            assert denied.status_code == 409, denied.text
            cross_review = copy.deepcopy(stages[0]["review_body"])
            cross_review.update(
                **identity(),
                review_id=str(uuid4()),
                expected_revision=1,
                handover_snapshot_id=view["snapshot_id"],
                contract_instrument_version_id=instrument,
                operational_review=context,
            )
            refused = http.client.post(
                root + f"/{stages[0]['event']}/applicability",
                headers=http.patron_headers,
                json=cross_review,
            )
            assert (
                refused.status_code == 422
                and refused.json()["detail"] == "HANDOVER_REQUALIFICATION_SCOPE_MISMATCH"
            ), refused.text
            stale_action = copy.deepcopy(stages[0]["action_body"])
            stale_action.update(**identity(), action_id=str(uuid4()), expected_revision=1)
            refused = http.client.post(
                root + f"/{stages[0]['event']}/actions",
                headers=http.patron_headers,
                json=stale_action,
            )
            assert refused.status_code == 409, refused.text
            assert counts() == before

        event, review, action = map(str, (uuid4(), uuid4(), uuid4()))
        source = f"change://synthetic/lot1/v{generation}"
        event_body = {
            **identity(),
            "event_id": event,
            "handover_snapshot_id": view["snapshot_id"],
            "change_kind": "CHANGE_REQUEST",
            "contract_instrument_version_id": instrument,
            "issuer": "MOA synthétique",
            "summary": f"Demande déclarée de contrôle V{generation}.",
            "scope_note": "Lot 1 uniquement, portée juridique UNKNOWN.",
            "source_refs": [source],
            "evidence_refs": [f"evidence://synthetic/v{generation}"],
            "declared_received_at": w.now.isoformat(),
            "operational_context": context,
        }
        # Reject wrong point/current view before the successful, fresh intent.
        wrong_point = copy.deepcopy(event_body)
        wrong_point.update(**identity(), event_id=str(uuid4()))
        wrong_point["operational_context"]["point_ids"] = [
            stages[0]["point"] if generation == 2 else str(uuid4())
        ]
        before = counts()
        bad = http.client.post(root, headers=http.patron_headers, json=wrong_point)
        assert (
            bad.status_code == 422
            and bad.json()["detail"] == "HANDOVER_POINT_NOT_FOUND_OR_FORBIDDEN"
        ), bad.text
        assert counts() == before
        wrong_hash = copy.deepcopy(event_body)
        wrong_hash.update(**identity(), event_id=str(uuid4()))
        wrong_hash["operational_context"]["expected_view_sha256"] = (
            stages[0]["event_body"]["operational_context"]["expected_view_sha256"]
            if generation == 2
            else "0" * 64
        )
        before = counts()
        refused_hash = http.client.post(root, headers=http.patron_headers, json=wrong_hash)
        assert (
            refused_hash.status_code == 409
            and refused_hash.json()["detail"] == "OPERATIONAL_CHANGE_SOURCE_CONFLICT"
        ), refused_hash.text
        assert counts() == before
        post(root, event_body, replay=True)
        row = next(x for x in public()["events"] if x["event_id"] == event)
        assert row["applicability_history"] == [] and row["actions"] == []
        assert row["source_state"] == "CURRENT" and row["legal_effect_state"] == "UNKNOWN"
        assert row["operational_context"]["handover_snapshot_id"] == view["snapshot_id"]
        assert (
            row["operational_context"]["offer_manifest_sha256"]
            == run.candidate_sha
            == control["manifest_sha256"]
        )
        assert [p["point_id"] for p in row["operational_context"]["points"]] == [point]
        review_body = {
            **identity(),
            "review_id": review,
            "handover_snapshot_id": view["snapshot_id"],
            "contract_instrument_version_id": instrument,
            "expected_revision": 0,
            "decision": "APPLICABLE_TO_HANDOVER",
            "delta_state": "DECLARED",
            "delta_note": (
                f"Contrôle opérationnel supplémentaire déclaré V{generation}; "
                "conséquences non établies UNKNOWN."
            ),
            "rationale": "Rapprochement humain de test, aucune applicabilité juridique déduite.",
            "evidence_refs": [source],
            "operational_review": context,
        }
        before = counts()
        early_action = {
            **identity(),
            "action_id": str(uuid4()),
            "applicability_review_id": str(uuid4()),
            "expected_revision": 0,
            "action_summary": "Action sans revue à refuser.",
            "evidence_refs": [source],
            "due_date_absence_reason": "Date inconnue.",
        }
        refused = http.client.post(
            root + f"/{event}/actions", headers=http.patron_headers, json=early_action
        )
        assert refused.status_code == 422, refused.text
        assert counts() == before
        post(root + f"/{event}/applicability", review_body, replay=True)
        action_body = {
            **identity(),
            "action_id": action,
            "applicability_review_id": review,
            "expected_revision": 0,
            "action_summary": f"Préparer le contrôle déclaré V{generation}.",
            "evidence_refs": [source],
            "due_date_absence_reason": "Date non déterminée dans cet essai.",
            "operational_details": dict(
                human_confirmed=True,
                publish=True,
                justification=f"Action publiée explicitement V{generation}.",
                responsible="Responsable déclaré V1" if generation == 1 else None,
                expected_evidence="Preuve attendue V1" if generation == 1 else None,
            ),
        }
        post(root + f"/{event}/actions", action_body, replay=True)
        relation = {
            **identity(),
            "relation_id": str(uuid4()),
            "expected_revision": 0,
            "state": "UNKNOWN",
            "rationale": "Relation économique à qualifier séparément.",
            "unknown_reason": "Aucun impact chiffré déduit du point de passation.",
        }
        post(root + f"/{event}/actions/{action}/impact-links", relation, replay=True)
        private = http.client.get(root, headers=http.patron_headers)
        assert private.status_code == 200, private.text
        private_row = next(x for x in private.json()["events"] if x["event_id"] == event)
        assert private_row["impact_declarations"] == []
        own_relations = [
            x for x in private_row["action_impact_relations"] if x["action_id"] == action
        ]
        assert len(own_relations) == 1 and own_relations[0]["state"] == "UNKNOWN"
        assert own_relations[0]["declaration_ids"] == []

        after = public()
        row = next(x for x in after["events"] if x["event_id"] == event)
        assert row["source_state"] == "CURRENT" and row["actions"][0]["source_state"] == "CURRENT"
        assert row["current_operational_context"]["handover_snapshot_id"] == view["snapshot_id"]
        assert row["applicability_history"][0]["delta_state"] == "DECLARED"
        assert (
            row["applicability_history"][0]["operational_review"]["offer_manifest_sha256"]
            == run.candidate_sha
        )
        assert (
            row["financial_content"] == row["private_files"] == "NOT_INCLUDED"
            and row["legal_effect_state"] == "UNKNOWN"
        )
        encoded = json.dumps(after, ensure_ascii=False)
        for forbidden in (
            "storage_key",
            "sales_total_minor",
            "impact_declarations",
            "financial_snapshot",
        ):
            assert forbidden not in encoded
        assert http.client.get(public_url).status_code == 401
        assert http.client.get(root, headers=http.driver_headers).status_code == 403
        assert {x["kind"] for x in row["operational_timeline"]} >= {
            "CHANGE_RECORDED",
            "APPLICABILITY",
            "ACTION",
        }
        if generation == 2:
            assert row["actions"][0]["operational_details"]["responsible"] is None
            assert row["actions"][0]["operational_details"]["expected_evidence"] is None
            assert "Responsable déclaré V1" not in json.dumps(row, ensure_ascii=False)
            assert "Preuve attendue V1" not in json.dumps(row, ensure_ascii=False)
            old = next(x for x in after["events"] if x["event_id"] == stages[0]["event"])
            assert old["handover_snapshot_id"] == stages[0]["snapshot"]
            assert old["source_state"] == old["actions"][0]["source_state"] == "REVIEW_REQUIRED"
            assert old["actions"][0]["action_id"] == stages[0]["action"]
        stages.append(
            dict(
                event=event,
                case_id=case,
                point=point,
                action=action,
                snapshot=view["snapshot_id"],
                event_body=event_body,
                review_body=review_body,
                action_body=action_body,
            )
        )
        if closure_qualifier is not None and generation == 2:
            closure_qualifier(factory, http, w, stages, handover)
        if destination := os.environ.get("SMART_AO_L10_V2_PROOF_DIR"):
            target = Path(destination) / variant / f"v{generation}"
            target.mkdir(parents=True, exist_ok=True)
            for name, value in [
                ("operational.json", after),
                ("private.json", private.json()),
                ("event-intent.json", event_body),
                ("review-intent.json", review_body),
                ("action-intent.json", action_body),
                ("impact-intent.json", relation),
            ]:
                (target / name).write_text(json.dumps(value, ensure_ascii=False, indent=2))

    runner = handover_runner or _run
    runner(session_factory, tmp_path, monkeypatch, technical_docx, change_qualifier=qualify)
    assert len(stages) == 2 and stages[0]["event"] != stages[1]["event"]
    assert (
        stages[0]["action"] != stages[1]["action"]
        and stages[0]["snapshot"] != stages[1]["snapshot"]
    )
    with session_factory() as session:
        for model in (
            CaseContractChangeEventRecord,
            CaseContractChangeApplicabilityRecord,
            CaseContractChangeActionRecord,
        ):
            assert (
                session.scalar(
                    sa.select(sa.func.count())
                    .select_from(model)
                    .where(model.case_id == UUID(stages[1]["case_id"]))
                )
                == 2
            )
