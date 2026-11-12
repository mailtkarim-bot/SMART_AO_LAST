"""Exact offer lineage and independent operational acts across a synthetic rectification."""

import copy
import io
import json
import os
import zipfile
from hashlib import sha256
from pathlib import Path
from typing import Any
from uuid import UUID, uuid4

import pytest
import sqlalchemy as sa
from app.modules.patron_action.infrastructure.models.handover import CaseHandoverSnapshotRecord
from app.modules.patron_action.infrastructure.models.handover_receipt import (
    CaseHandoverReceiptRecord,
)
from app.platform.persistence.models import DomainEventRecord, OutboxMessageRecord
from tests.db.test_l08_integrated_packet import (
    test_same_case_integrates_response_controls_and_native_rectification as _run,
)


def identity(correlation=True):
    values = dict(command_id=str(uuid4()), idempotency_key=str(uuid4()))
    if correlation:
        values["correlation_id"] = str(uuid4())
    return values


@pytest.mark.parametrize("technical_docx", [False, True])
def test_rectified_offer_reaches_responsable_without_inheriting_prior_handover(
    session_factory, tmp_path, monkeypatch, technical_docx, change_qualifier=None
):
    stages: list[dict[str, Any]] = []
    variant = "docx" if technical_docx else "markdown"

    def capture(factory, http, run, control, generation, w):
        root = f"/api/v1/patron/cases/{w.case_id}"
        read_url = f"/api/v1/cases/{w.case_id}/p7-handover"

        def get_view(snapshot_id=None):
            response = http.client.get(read_url, headers=http.driver_headers)
            assert response.status_code == 200, response.text
            return next(
                x
                for x in response.json()["items"]
                if snapshot_id is None or x["snapshot_id"] == snapshot_id
            )

        def counts():
            with factory() as session:
                return tuple(
                    session.scalar(sa.select(sa.func.count()).select_from(m))
                    for m in (DomainEventRecord, OutboxMessageRecord)
                )

        if generation == 1:
            outcome = str(uuid4())
            won = http.client.post(
                "/api/v1/patron/case-outcomes",
                headers=http.patron_headers,
                json={
                    **identity(),
                    "outcome_id": outcome,
                    "case_id": str(w.case_id),
                    "lot_reference": "1",
                    "outcome": "WON",
                    "source_locator": "attribution://synthetic/lot1/qualification",
                    "reservations": ["Déclaration synthétique, aucune attribution réelle."],
                },
            )
            assert won.status_code == 201, won.text
            expected_revision = 0
        else:
            outcome = stages[0]["outcome"]
            previous = get_view()
            assert previous["snapshot_id"] == stages[0]["view"]["snapshot_id"]
            assert previous["source_state"] == "REVIEW_REQUIRED"
            assert previous["receipts"] and all(
                r["scope_state"] == "HISTORICAL" for r in previous["receipts"]
            )
            expected_revision = previous["revision"]
            choices = http.client.get(root + "/p7-handover-options", headers=http.patron_headers)
            assert choices.status_code == 200, choices.text
            selected = choices.json()["items"]
            assert any(x["submission_package_id"] == str(run.candidate_id) for x in selected)
            assert all(
                x["submission_package_id"] != stages[0]["view"]["submission_package_id"]
                for x in selected
            )
            before = counts()
            stale_receipt = {**stages[0]["receipt"], **identity(), "receipt_id": str(uuid4())}
            old_receipt_path = read_url + f"/{previous['snapshot_id']}/receipts"
            refused = http.client.post(
                old_receipt_path, headers=http.driver_headers, json=stale_receipt
            )
            assert refused.status_code == 409, refused.text
            assert counts() == before

        instrument = str(uuid4())
        contract = http.client.post(
            root + "/contract-instrument-versions",
            headers=http.patron_headers,
            json={
                **identity(False),
                "contract_instrument_version_id": instrument,
                "instrument_kind": "SIGNED_CONTRACT",
                "version_reference": f"Contrat déclaré synthétique V{generation}",
                "source_refs": [f"contract://synthetic/v{generation}/candidature"],
                "evidence_refs": [f"evidence://synthetic/v{generation}/declared"],
            },
        )
        assert contract.status_code == 201, contract.text
        options = http.client.get(root + "/p7-handover/contracts", headers=http.patron_headers)
        assert options.status_code == 200, options.text
        contract_option = next(
            c for c in options.json()["items"] if c["instrument_version_id"] == instrument
        )
        if generation == 2:
            before = counts()
            stale = copy.deepcopy(stages[0]["publication"])
            stale.update(**identity(), snapshot_id=str(uuid4()))
            stale["operational_review"].update(
                expected_source_context_sha256=options.json()["source_context_sha256"],
                expected_handover_revision=expected_revision,
            )
            rejected = http.client.post(
                root + "/p7-handover", headers=http.patron_headers, json=stale
            )
            assert (
                rejected.status_code == 409
                and rejected.json()["detail"] == "HANDOVER_OFFER_VERSION_CONFLICT"
            ), rejected.text
            assert counts() == before

        point_id = str(uuid4())
        point = dict(
            point_id=point_id,
            kind="ENGAGEMENT",
            statement=f"Relire les pièces de candidature avant usage — revue V{generation}.",
            offer_excerpt="KBIS synthétique cité; validité officielle UNKNOWN.",
            offer_locator=f"Mémoire exact {run.content_sha256} — candidature",
            contract_locator=f"Contrat déclaré V{generation} — candidature",
            difference_state="UNKNOWN",
            criticality="CRITICAL",
            responsible="Responsable explicite V1" if generation == 1 else None,
            action=f"Obtenir une preuve officielle après revue V{generation}.",
            expected_evidence="Preuve attendue V1" if generation == 1 else None,
        )
        points = [point]
        for condition in options.json()["condition_options"]:
            points.append(
                dict(
                    point_id=str(uuid4()),
                    kind="CONDITION",
                    condition_id=condition["condition_id"],
                    statement=f"Condition à relire pour la seule passation V{generation}.",
                    difference_state="UNKNOWN",
                    criticality="CRITICAL",
                )
            )
        body = {
            **identity(),
            "snapshot_id": str(uuid4()),
            "outcome_id": outcome,
            "submission_package_id": str(run.candidate_id),
            "operational_review": dict(
                expected_source_context_sha256=options.json()["source_context_sha256"],
                expected_handover_revision=expected_revision,
                expected_offer_manifest_sha256=run.candidate_sha,
                contract_instrument_version_id=instrument,
                expected_contract_record_sha256=contract_option["record_sha256"],
                justification=f"Rapprochement humain synthétique explicite du pli V{generation}.",
                human_confirmed=True,
                points=points,
            ),
        }
        published = http.client.post(root + "/p7-handover", headers=http.patron_headers, json=body)
        assert published.status_code == 201, published.text
        replay = http.client.post(root + "/p7-handover", headers=http.patron_headers, json=body)
        assert replay.status_code == 200 and replay.json()["replayed"], replay.text
        view = get_view(body["snapshot_id"])
        assert view["source_state"] == "CURRENT"
        assert view["submission_package_id"] == str(run.candidate_id)
        assert view["manifest_sha256"] == control["manifest_sha256"] == run.candidate_sha
        snapshot = view["snapshot"]
        assert snapshot["offer"]["dce_version_id"] == control["dce_version_id"]
        assert snapshot["offer"]["technical_document_sha256"] == run.content_sha256
        assert snapshot["contract_comparison"]["authority_state"] == "UNKNOWN"
        assert snapshot["p7_is_order_service"] is False
        assert snapshot["offer_point_proofs"][point_id]["state"] == (
            "EXACT_DOCX_TEXT_MATCH" if technical_docx else "EXACT_BYTE_MATCH"
        )
        assert "sales_total_minor" not in json.dumps(view) and "storage_key" not in json.dumps(view)
        assert http.client.get(read_url).status_code == 401
        assert (
            http.client.get(
                read_url + f"/{body['snapshot_id']}/offer-document", headers=http.patron_headers
            ).status_code
            == 200
        )
        document = http.client.get(
            read_url + f"/{body['snapshot_id']}/offer-document", headers=http.driver_headers
        )
        assert document.status_code == 200, document.text
        with zipfile.ZipFile(io.BytesIO(run.archive)) as archive:
            assert document.content == archive.read(
                "technical-response.docx" if technical_docx else "technical-response.md"
            )
        assert sha256(document.content).hexdigest() == run.content_sha256

        receipt = {
            **identity(),
            "receipt_id": str(uuid4()),
            "expected_snapshot_revision": view["revision"],
            "expected_view_sha256": view["view_sha256"],
            "receipt_kind": "RECEIVED_WITH_GAPS",
            "note": f"Reçu de test avec inconnus et manques V{generation}.",
            "human_confirmed": True,
        }
        receipt_path = read_url + f"/{body['snapshot_id']}/receipts"
        if generation == 2:
            assert view["receipts"] == []
            missing = snapshot["operational_review"]["missing"]
            assert "RESPONSIBLE:" + point_id in missing
            assert "EXPECTED_EVIDENCE:" + point_id in missing
            assert "Responsable explicite V1" not in json.dumps(snapshot)
            assert "Preuve attendue V1" not in json.dumps(snapshot)
            before = counts()
            copied_hash = {
                **receipt,
                **identity(),
                "receipt_id": str(uuid4()),
                "expected_view_sha256": stages[0]["view"]["view_sha256"],
            }
            assert (
                http.client.post(
                    receipt_path, headers=http.driver_headers, json=copied_hash
                ).status_code
                == 409
            )
            completed = {
                **receipt,
                **identity(),
                "receipt_id": str(uuid4()),
                "receipt_kind": "RECEIVED",
            }
            assert (
                http.client.post(
                    receipt_path, headers=http.driver_headers, json=completed
                ).status_code
                == 422
            )
            assert counts() == before
        ack = http.client.post(receipt_path, headers=http.driver_headers, json=receipt)
        assert ack.status_code == 201, ack.text
        replay_ack = http.client.post(receipt_path, headers=http.driver_headers, json=receipt)
        assert replay_ack.status_code == 200 and replay_ack.json()["replayed"], replay_ack.text
        received = get_view(body["snapshot_id"])
        assert (
            len(received["receipts"]) == 1
            and received["receipts"][0]["receipt_id"] == receipt["receipt_id"]
        )
        if generation == 2:
            history = http.client.get(read_url + "/history", headers=http.driver_headers)
            assert history.status_code == 200, history.text
            old = next(
                x
                for x in history.json()["items"]
                if x["snapshot_id"] == stages[0]["view"]["snapshot_id"]
            )
            assert old["source_state"] == "HISTORICAL"
            assert old["receipts"][0]["receipt_id"] == stages[0]["receipt"]["receipt_id"]
            assert old["receipts"][0]["scope_state"] == "HISTORICAL"
        stage = dict(
            view=received,
            publication=body,
            receipt=receipt,
            outcome=outcome,
            case_id=str(w.case_id),
        )
        stages.append(stage)
        if change_qualifier is not None:
            change_qualifier(factory, http, run, control, generation, w, stage)
        if destination := os.environ.get("SMART_AO_L09_RECTIFIED_PROOF_DIR"):
            target = Path(destination) / variant / f"v{generation}"
            target.mkdir(parents=True, exist_ok=True)
            (target / "view.json").write_text(json.dumps(received, ensure_ascii=False, indent=2))
            (target / "publication.json").write_text(json.dumps(body, ensure_ascii=False, indent=2))
            (target / "receipt-intent.json").write_text(
                json.dumps(receipt, ensure_ascii=False, indent=2)
            )
            (target / "offer-document.bin").write_bytes(document.content)
            if generation == 2:
                (target / "history.json").write_text(
                    json.dumps(history.json(), ensure_ascii=False, indent=2)
                )

    _run(session_factory, tmp_path, monkeypatch, technical_docx, handover_qualifier=capture)
    assert len(stages) == 2
    assert stages[0]["view"]["snapshot_id"] != stages[1]["view"]["snapshot_id"]
    with session_factory() as session:
        for model in (CaseHandoverSnapshotRecord, CaseHandoverReceiptRecord):
            assert (
                session.scalar(
                    sa.select(sa.func.count())
                    .select_from(model)
                    .where(model.case_id == UUID(stages[1]["case_id"]))
                )
                == 2
            )
