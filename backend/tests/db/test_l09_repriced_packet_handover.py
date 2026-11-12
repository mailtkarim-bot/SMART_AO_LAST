"""Exact repriced packet to a new operational publication and Responsable receipt."""

import json
from copy import deepcopy
from hashlib import sha256
from io import BytesIO
from typing import Any
from uuid import uuid4
from zipfile import ZipFile

from tests.db.test_l08_pricing_response_continuity import (
    test_revised_prices_rebuild_a_sourced_response_packet_with_new_human_acts as _run,
)


def test_repriced_packet_reaches_responsable_with_fresh_sources_and_acts(
    session_factory, tmp_path, monkeypatch, change_qualifier=None, packet_runner=None
):
    stages: list[dict[str, Any]] = []
    outcome, instrument = str(uuid4()), str(uuid4())

    def qualify(factory, http, run, control, generation, w):
        patron = f"/api/v1/patron/cases/{w.case_id}"
        read_url = f"/api/v1/cases/{w.case_id}/p7-handover"

        def post(path, body, *, driver=False, status=201):
            response = http.client.post(
                path, headers=http.driver_headers if driver else http.patron_headers, json=body
            )
            assert response.status_code == status, response.text
            if status < 300 and (path.endswith("/p7-handover") or path.endswith("/receipts")):
                assert response.json()["command_id"] == body["command_id"]
                assert response.json()["idempotency_key"] == body["idempotency_key"]
                assert response.headers.get("cache-control") == "no-store"
            return response.json()

        def ids():
            return dict(command_id=str(uuid4()), idempotency_key=str(uuid4()))

        def view(identifier):
            response = http.client.get(read_url + f"/{identifier}", headers=http.driver_headers)
            assert response.status_code == 200, response.text
            assert response.headers.get("cache-control") == "no-store"
            return response.json()

        if generation == 1:
            post(
                "/api/v1/patron/case-outcomes",
                dict(
                    ids(),
                    correlation_id=str(uuid4()),
                    outcome_id=outcome,
                    case_id=str(w.case_id),
                    lot_reference="1",
                    outcome="WON",
                    source_locator="attribution://synthetic/lot1",
                    reservations=["Déclaration synthétique, aucune attribution réelle."],
                ),
            )
            post(
                patron + "/contract-instrument-versions",
                dict(
                    ids(),
                    contract_instrument_version_id=instrument,
                    instrument_kind="SIGNED_CONTRACT",
                    version_reference="Version déclarée synthétique",
                    source_refs=["contract://synthetic/exact"],
                    evidence_refs=["evidence://synthetic/declared"],
                ),
            )
        options = http.client.get(patron + "/p7-handover/contracts", headers=http.patron_headers)
        assert options.status_code == 200, options.text
        contracts = options.json()
        contract = next(
            row for row in contracts["items"] if row["instrument_version_id"] == instrument
        )
        with ZipFile(BytesIO(run.archive)) as bundle:
            memory = bundle.read("technical-response.md")
        text = memory.decode("utf-8")
        marker = "Pour le lot 1" if generation == 1 else "Pièce synthétique référencée"
        offset = text.index(marker)
        excerpt = text[max(0, offset - 100) : offset + len(marker) + 200]
        assert text.count(excerpt) == 1
        point_id = str(uuid4())
        point = dict(
            point_id=point_id,
            kind="ENGAGEMENT",
            statement=f"Engagement technique à relire V{generation}.",
            offer_excerpt=excerpt,
            offer_locator=f"technical-response.md:region-declaree-v{generation}",
            contract_locator="contrat-déclaré:§2",
            difference_state="UNKNOWN",
            criticality="CRITICAL",
            responsible="Responsable déclaré V1" if generation == 1 else None,
            action=f"Relire la pièce officielle pour la seule passation V{generation}.",
            expected_evidence="Preuve attendue V1" if generation == 1 else None,
        )
        points = [point] + [
            dict(
                point_id=str(uuid4()),
                kind="CONDITION",
                condition_id=condition["condition_id"],
                statement=f"Condition opérationnelle à relire V{generation}.",
                difference_state="UNKNOWN",
                criticality="CRITICAL",
            )
            for condition in contracts["condition_options"]
        ]
        publication = dict(
            ids(),
            correlation_id=str(uuid4()),
            snapshot_id=str(uuid4()),
            outcome_id=outcome,
            submission_package_id=str(run.candidate_id),
            operational_review=dict(
                expected_source_context_sha256=contracts["source_context_sha256"],
                expected_handover_revision=generation - 1,
                expected_offer_manifest_sha256=run.candidate_sha,
                contract_instrument_version_id=instrument,
                expected_contract_record_sha256=contract["record_sha256"],
                justification=f"Revue opérationnelle synthétique du pli exact V{generation}.",
                human_confirmed=True,
                points=points,
            ),
        )
        if generation == 2:
            stale = deepcopy(publication)
            stale.update(ids(), snapshot_id=str(uuid4()))
            stale["operational_review"]["expected_offer_manifest_sha256"] = stages[0][
                "manifest_sha"
            ]
            post(patron + "/p7-handover", stale, status=409)
        post(patron + "/p7-handover", publication)
        assert post(patron + "/p7-handover", publication, status=200)["replayed"]
        snapshot = view(publication["snapshot_id"])
        assert snapshot["source_state"] == "CURRENT"
        assert snapshot["submission_package_id"] == str(run.candidate_id)
        assert snapshot["manifest_sha256"] == control["manifest_sha256"] == run.candidate_sha
        public = snapshot["snapshot"]
        assert public["offer"]["technical_document_sha256"] == run.content_sha256
        assert public["offer"]["financial_content"] == "NOT_INCLUDED"
        assert public["contract_comparison"]["authority_state"] == "UNKNOWN"
        assert public["p7_is_order_service"] is False
        assert public["offer_point_proofs"][point_id]["state"] == "EXACT_BYTE_MATCH"
        serialized = json.dumps(snapshot)
        for forbidden in (
            "pricing_reference",
            "financial_snapshot_id",
            "OFFICIAL_PRICING_VERSION",
            "sales_total_minor",
            "storage_key",
        ):
            assert forbidden not in serialized
        for ref in (
            control["pricing_reference"]["referenced"],
            control["pricing_reference"]["latest_published"],
        ):
            assert ref["report_id"] not in serialized
        received_document = http.client.get(
            read_url + f"/{snapshot['snapshot_id']}/offer-document", headers=http.driver_headers
        )
        assert received_document.status_code == 200, received_document.text
        assert received_document.content == memory
        assert sha256(memory).hexdigest() == run.content_sha256
        for private_path in ("/final-control", "/export"):
            assert (
                http.client.get(
                    f"/api/v1/patron/submission-packages/{run.candidate_id}" + private_path,
                    headers=http.driver_headers,
                ).status_code
                == 403
            )
        receipt = dict(
            ids(),
            correlation_id=str(uuid4()),
            receipt_id=str(uuid4()),
            expected_snapshot_revision=snapshot["revision"],
            expected_view_sha256=snapshot["view_sha256"],
            receipt_kind="RECEIVED_WITH_GAPS",
            note=f"Dossier V{generation} reçu avec inconnus explicites.",
            human_confirmed=True,
        )
        receipt_path = read_url + f"/{snapshot['snapshot_id']}/receipts"
        assert snapshot["receipts"] == []
        if generation == 2:
            old = view(stages[0]["snapshot"]["snapshot_id"])
            assert old["source_state"] == "HISTORICAL"
            assert all(row["scope_state"] == "HISTORICAL" for row in old["receipts"])
            assert (
                "Responsable déclaré V1" not in serialized
                and "Preuve attendue V1" not in serialized
            )
            assert "RESPONSIBLE:" + point_id in public["operational_review"]["missing"]
            assert "EXPECTED_EVIDENCE:" + point_id in public["operational_review"]["missing"]
            copied = dict(
                receipt,
                **ids(),
                receipt_id=str(uuid4()),
                expected_view_sha256=stages[0]["snapshot"]["view_sha256"],
            )
            post(receipt_path, copied, driver=True, status=409)
            complete = dict(receipt, **ids(), receipt_id=str(uuid4()), receipt_kind="RECEIVED")
            post(receipt_path, complete, driver=True, status=422)
        post(receipt_path, receipt, driver=True)
        assert post(receipt_path, receipt, driver=True, status=200)["replayed"]
        final = view(snapshot["snapshot_id"])
        assert (
            len(final["receipts"]) == 1
            and final["receipts"][0]["receipt_id"] == receipt["receipt_id"]
        )
        assert final["receipts"][0]["scope_state"] == "CURRENT"
        stages.append(dict(snapshot=final, manifest_sha=run.candidate_sha))
        if change_qualifier is not None:
            change_qualifier(factory, http, run, control, generation, w, {"view": final})

    if packet_runner is None:
        _run(session_factory, tmp_path, monkeypatch, handover_qualifier=qualify)
    else:
        packet_runner(session_factory, tmp_path, monkeypatch, qualify)
    assert len(stages) == 2
    assert stages[0]["snapshot"]["snapshot_id"] != stages[1]["snapshot"]["snapshot_id"]
    assert stages[0]["manifest_sha"] != stages[1]["manifest_sha"]
    (tmp_path / "l09-repriced-handover-views.json").write_text(json.dumps(stages))
