"""Synthetic V2 continuity: declared reception/reserves and expected versus collected cash."""

import json
import os
from copy import deepcopy
from pathlib import Path
from uuid import UUID, uuid4

import pytest
from tests.db.test_l10_rectified_changes import (
    test_changes_require_explicit_current_v2_sources_and_never_transfer_v1_acts as _run,
)


def ids():
    return dict(command_id=str(uuid4()), idempotency_key=str(uuid4()))


@pytest.mark.parametrize("technical_docx", [False, True])
def test_v2_changes_remain_explicit_in_closure_without_presuming_payment(
    session_factory,
    tmp_path,
    monkeypatch,
    technical_docx,
    continuity_qualifier=None,
    changes_runner=None,
):
    def qualify(factory, http, w, stages, handover):
        import sqlalchemy as sa
        from app.modules.pricing.infrastructure.case_closure_reader import _record
        from app.modules.pricing.infrastructure.models.contract_execution_evidence import (
            ContractExecutionEvidenceRecord,
        )
        from app.modules.pricing.infrastructure.models.payment_cycle_fact import (
            PaymentCycleFactRecord,
        )
        from app.modules.pricing.infrastructure.models.post_reception_obligation import (
            PostReceptionObligationRecord,
        )

        root = f"/api/v1/patron/cases/{w.case_id}/closure"

        def stored_records():
            with factory() as session:
                return [
                    [
                        _record(row)
                        for row in session.scalars(
                            sa.select(model)
                            .where(
                                model.case_id == w.case_id,
                                model.tenant_id == w.actor.tenant_id,
                            )
                            .order_by(model.id)
                        ).all()
                    ]
                    for model in (
                        ContractExecutionEvidenceRecord,
                        PostReceptionObligationRecord,
                        PaymentCycleFactRecord,
                    )
                ]

        def read():
            r = http.client.get(root, headers=http.patron_headers)
            assert r.status_code == 200, r.text
            return r.json()

        def post(path, body):
            r = http.client.post(root + path, headers=http.patron_headers, json=body)
            assert r.status_code == 201, r.text
            stored = stored_records()
            replay = http.client.post(root + path, headers=http.patron_headers, json=body)
            assert replay.status_code == 200 and replay.json()["replayed"], replay.text
            assert stored_records() == stored
            assert {k: v for k, v in r.json().items() if k != "replayed"} == {
                k: v for k, v in replay.json().items() if k != "replayed"
            }

        before = read()
        assert http.client.get(root, headers=http.driver_headers).status_code == 403
        instrument = handover["view"]["snapshot"]["contract_comparison"]["instrument_version_id"]
        reception = str(uuid4())
        review = dict(
            expected_dossier_sha256=before["dossier_sha256"],
            human_confirmed=True,
            justification="Revue synthétique des sources V2 avec manques conservés.",
            responsible=None,
            expected_evidence=None,
            acknowledged_open_obligation_ids=[],
            comparisons=[],
        )
        post(
            "/acts",
            {
                **ids(),
                "act_id": reception,
                "act_kind": "WORK_RECEPTION",
                "reception_outcome": "WITH_RESERVATIONS",
                "summary": "Réception déclarée V2 avec réserve, sans constat externe.",
                "source_refs": [f"change://synthetic/{stages[1]['event']}"],
                "evidence_refs": ["pv://synthetic/v2"],
                "contract_instrument_version_id": instrument,
                "closure_review": review,
            },
        )
        current = read()
        assert {x["id"] for x in current["change_actions"]} >= {x["action"] for x in stages}
        refs = current["reference_options"]
        action_ref = next(
            x
            for x in refs
            if x["kind"] == "CHANGE_ACTION" and x["record_id"] == stages[1]["action"]
        )
        reception_ref = next(x for x in refs if x["kind"] == "ACT" and x["record_id"] == reception)
        comparison = dict(
            expected={k: action_ref[k] for k in ("kind", "record_id", "sha256")},
            actual={k: reception_ref[k] for k in ("kind", "record_id", "sha256")},
            note="Rapprochement déclaré de l’action V2 et de la réception avec réserves.",
        )
        obligation = str(uuid4())
        post(
            "/obligations",
            {
                **ids(),
                "obligation_id": obligation,
                "obligation_type": "RESERVES_LIFTING",
                "origin_reception_act_id": reception,
                "summary": "Réserve à lever après contrôle V2.",
                "source_refs": [f"action://synthetic/{stages[1]['action']}"],
                "closure_review": {
                    **review,
                    "expected_dossier_sha256": read()["dossier_sha256"],
                    "comparisons": [comparison],
                },
            },
        )
        cycle = str(uuid4())
        post(
            "/cycles",
            {
                **ids(),
                "cycle_id": cycle,
                "source_refs": ["contract://synthetic/v2"],
                "trigger_event": "INVOICE",
                "status": "REVIEW_REQUIRED",
            },
        )
        previous = None
        created_facts = {}
        for kind, amount in [("PAYMENT_EXPECTED", 100000), ("COLLECTION_RECORDED", 60000)]:
            fact = str(uuid4())
            post(
                "/payment-facts",
                {
                    **ids(),
                    "fact_id": fact,
                    "cycle_id": cycle,
                    "kind": kind,
                    "amount_minor": amount,
                    "currency_code": "EUR",
                    "declared_date": w.now.date().isoformat(),
                    "source_refs": ["account://synthetic/v2"],
                    "evidence_refs": ["evidence://synthetic/cash"],
                    "human_confirmed": True,
                    "justification": "Déclaration de test, aucune banque connectée.",
                    "expected_dossier_sha256": read()["dossier_sha256"],
                    "compared_to_fact_id": previous,
                },
            )
            if kind == "PAYMENT_EXPECTED":
                assert read()["financial_observations"]["collection_state"] == "UNKNOWN"
            created_facts[kind] = fact
            previous = fact
        after = read()
        act = next(x for x in after["acts"] if x["id"] == reception)
        reserve = next(x for x in after["obligations"] if x["id"] == obligation)
        assert act["reception_outcome"] == "WITH_RESERVATIONS"
        assert (
            act["case_dce_version_id_at_recording"]
            == handover["view"]["snapshot"]["offer"]["dce_version_id"]
        )
        assert act["source_refs_json"] == [f"change://synthetic/{stages[1]['event']}"]
        assert reserve["origin_reception_act_id"] == reception
        assert (
            reserve["declared_status"] != "COMPLETED" and obligation in after["open_obligation_ids"]
        )
        for item in (act, reserve):
            assert item["closure_review_json"]["responsible"] is None
            assert item["closure_review_json"]["expected_evidence"] is None
        linked = reserve["closure_review_json"]["comparisons"][0]
        assert (
            linked["expected"] == comparison["expected"]
            and linked["actual"] == comparison["actual"]
        )
        for kind, amount in [("PAYMENT_EXPECTED", 100000), ("COLLECTION_RECORDED", 60000)]:
            stored = next(x for x in after["facts"] if x["fact_id"] == created_facts[kind])
            assert stored["cycle_id"] == cycle and stored["amount_minor"] == amount
        observed = next(
            x
            for x in after["financial_observations"]["comparisons"]
            if x["expected_fact_id"] == created_facts["PAYMENT_EXPECTED"]
            and x["recorded_fact_id"] == created_facts["COLLECTION_RECORDED"]
        )
        assert observed["difference_minor"] == -40000
        assert after["financial_observations"]["settlement_state"] == "UNKNOWN"
        assert any(
            x["difference_minor"] == -40000 for x in after["financial_observations"]["comparisons"]
        )
        # An updated handover invalidates the comparison without rewriting the declaration.
        from app.modules.patron_action.infrastructure.models.handover import (
            CaseHandoverSnapshotRecord,
        )

        historical_review = deepcopy(reserve["closure_review_json"])
        historical_facts = deepcopy(after["facts"])
        assert reserve["context_state"] == "CURRENT"
        assert (
            next(x for x in after["change_actions"] if x["id"] == stages[1]["action"])[
                "context_state"
            ]
            != "REVIEW_REQUIRED"
        )
        with factory.begin() as session:
            prior = session.get(CaseHandoverSnapshotRecord, UUID(handover["view"]["snapshot_id"]))
            values = {c.name: deepcopy(getattr(prior, c.name)) for c in prior.__table__.columns}
            values.update(id=uuid4(), revision=prior.revision + 1)
            for key in ("command_id", "idempotency_key", "correlation_id"):
                if key in values:
                    values[key] = uuid4()
            session.add(CaseHandoverSnapshotRecord(**values))
        invalidated = read()
        old_reserve = next(x for x in invalidated["obligations"] if x["id"] == obligation)
        assert old_reserve["context_state"] == "REVIEW_REQUIRED"
        assert old_reserve["closure_review_json"] == historical_review
        assert obligation in invalidated["open_obligation_ids"]
        assert (
            next(x for x in invalidated["change_actions"] if x["id"] == stages[1]["action"])[
                "context_state"
            ]
            == "REVIEW_REQUIRED"
        )

        fresh_reception = str(uuid4())
        fresh_body = {
            **ids(),
            "act_id": fresh_reception,
            "act_kind": "WORK_RECEPTION",
            "reception_outcome": "WITH_RESERVATIONS",
            "summary": "Nouvelle réception relue après invalidation, manques conservés.",
            "source_refs": ["pv://synthetic/requalified"],
            "evidence_refs": ["evidence://synthetic/requalified"],
            "contract_instrument_version_id": instrument,
            "closure_review": {
                **review,
                "expected_dossier_sha256": invalidated["dossier_sha256"],
                "justification": "Nouveau consentement sur les sources relues.",
            },
        }
        stale = deepcopy(fresh_body)
        stale.update(**ids(), act_id=str(uuid4()))
        stale["closure_review"]["expected_dossier_sha256"] = before["dossier_sha256"]
        response = http.client.post(root + "/acts", headers=http.patron_headers, json=stale)
        assert response.status_code == 409 and response.json()["detail"] == "CLOSURE_VIEW_CONFLICT"
        unconfirmed = deepcopy(fresh_body)
        unconfirmed.update(**ids(), act_id=str(uuid4()))
        unconfirmed["closure_review"]["human_confirmed"] = False
        assert (
            http.client.post(
                root + "/acts", headers=http.patron_headers, json=unconfirmed
            ).status_code
            == 422
        )
        assert (
            http.client.post(
                root + "/acts", headers=http.driver_headers, json=fresh_body
            ).status_code
            == 403
        )
        post("/acts", fresh_body)
        fresh_obligation = str(uuid4())
        post(
            "/obligations",
            {
                **ids(),
                "obligation_id": fresh_obligation,
                "obligation_type": "RESERVES_LIFTING",
                "origin_reception_act_id": fresh_reception,
                "summary": "Réserve nouvelle, aucune levée antérieure héritée.",
                "source_refs": ["reserve://synthetic/requalified"],
                "closure_review": {
                    **review,
                    "expected_dossier_sha256": read()["dossier_sha256"],
                    "justification": "Consentement distinct pour la nouvelle réserve.",
                },
            },
        )
        qualified = read()
        assert {obligation, fresh_obligation} <= set(qualified["open_obligation_ids"])
        assert (
            next(x for x in qualified["obligations"] if x["id"] == obligation)[
                "closure_review_json"
            ]
            == historical_review
        )
        new_reserve = next(x for x in qualified["obligations"] if x["id"] == fresh_obligation)
        assert new_reserve["declared_status"] != "COMPLETED"
        assert new_reserve["closure_review_json"]["human_confirmed"] is True
        assert new_reserve["source_refs_json"] == ["reserve://synthetic/requalified"]
        exit_body = {
            **ids(),
            "act_id": str(uuid4()),
            "act_kind": "CONTRACT_EXIT",
            "summary": "Sortie déclarée avec manques explicitement acquittés.",
            "source_refs": ["exit://synthetic/requalified"],
            "evidence_refs": ["review://synthetic/requalified"],
            "closure_review": {
                **review,
                "expected_dossier_sha256": qualified["dossier_sha256"],
                "justification": "Acquittement humain des réserves, sans conformité déduite.",
            },
        }
        response = http.client.post(root + "/acts", headers=http.patron_headers, json=exit_body)
        assert response.status_code == 422
        assert response.json()["detail"] == "OPEN_OBLIGATIONS_REQUIRE_ACKNOWLEDGEMENT"
        exit_body["closure_review"]["acknowledged_open_obligation_ids"] = qualified[
            "open_obligation_ids"
        ]
        exit_body.update(**ids(), act_id=str(uuid4()))
        post("/acts", exit_body)
        final = read()
        exit_act = next(x for x in final["acts"] if x["id"] == exit_body["act_id"])
        assert exit_act["closure_review_json"]["legal_effect_state"] == "UNKNOWN"
        for key in (
            "human_confirmed",
            "expected_dossier_sha256",
            "justification",
            "acknowledged_open_obligation_ids",
        ):
            assert exit_act["closure_review_json"][key] == exit_body["closure_review"][key]
        assert set(final["open_obligation_ids"]) == set(qualified["open_obligation_ids"])
        assert final["facts"] == historical_facts
        assert final["financial_observations"]["settlement_state"] == "UNKNOWN"
        assert final["external_receipt_state"] == final["legal_effect_state"] == "UNKNOWN"
        assert final["completeness_state"] == "REVIEW_REQUIRED"
        stored = stored_records()
        assert read() == final
        assert stored_records() == stored
        if continuity_qualifier is not None:
            continuity_qualifier(factory, http, w, final)
        if destination := os.environ.get("SMART_AO_L11_V2_PROOF_DIR"):
            p = Path(destination) / ("docx" if technical_docx else "markdown")
            p.mkdir(parents=True, exist_ok=True)
            (p / "before.json").write_text(json.dumps(before, ensure_ascii=False, indent=2))
            (p / "after.json").write_text(json.dumps(after, ensure_ascii=False, indent=2))
            for name, value in (
                ("invalidated", invalidated),
                ("requalified", qualified),
                ("final", final),
            ):
                (p / f"{name}.json").write_text(json.dumps(value, ensure_ascii=False, indent=2))
            (p / "lineage.json").write_text(
                json.dumps(
                    dict(
                        case_id=str(w.case_id),
                        v1_event=stages[0]["event"],
                        v2_event=stages[1]["event"],
                        v2_action=stages[1]["action"],
                        handover=handover["view"]["snapshot_id"],
                        reception=reception,
                        obligation=obligation,
                        cycle=cycle,
                    ),
                    indent=2,
                )
            )

    captured = []

    def capture(*args):
        captured.append(args)

    # Finish the upstream two-snapshot assertions before adding the invalidation fixture.
    runner = changes_runner or _run
    runner(session_factory, tmp_path, monkeypatch, technical_docx, closure_qualifier=capture)
    assert len(captured) == 1
    from fastapi.testclient import TestClient

    http = captured[0][1]
    # The upstream recipe closes its client; retain the exact local app and actor headers.
    with TestClient(http.client.app) as client:
        http.client = client
        qualify(*captured[0])
