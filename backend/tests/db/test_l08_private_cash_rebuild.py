"""Published-price replacement rebuilds a packet while private cash stays private."""

import json
from io import BytesIO
from uuid import uuid4
from zipfile import ZipFile

from tests.db import test_l08_pricing_response_continuity as recipe


def packet_with_private_cash(session_factory, tmp_path, monkeypatch, handover_qualifier=None):
    state = {}
    private = []
    controls = {}

    def read_cash(http, w):
        root = f"/api/v1/patron/cases/{w.case_id}/cash-schedule"
        response = http.client.get(root, headers=http.patron_headers)
        assert response.status_code == 200, response.text
        assert response.headers["cache-control"] == "no-store"
        return root, response.json()

    def declare(http, w, report, phase):
        root, view = read_cash(http, w)
        source = next(
            s
            for s in view["sources"]
            if s["id"].startswith("LINE:")
            and s["direction"] == "OUTFLOW"
            and s["financial_report"]["report_id"] == report
        )
        marker = f"PRIVATE_CASH_NO_EXPORT_{phase}_{uuid4().hex}"
        revision_id = str(uuid4())
        flow_id = str(uuid4())
        private.extend([marker, revision_id, flow_id])
        payload = dict(
            case_id=str(w.case_id),
            command_id=str(uuid4()),
            idempotency_key=str(uuid4()),
            revision_id=revision_id,
            expected_revision=view["revision"],
            expected_view_sha256=view["view_sha256"],
            human_confirmed=True,
            justification=marker,
            declaration=dict(
                period_start="2026-11-01",
                period_end="2026-11-30",
                status="ACTIVE",
                assumptions=marker,
                openings=[
                    dict(
                        currency_code=source["currency_code"],
                        amount_minor=314159265,
                        source_refs=[f"opening://{marker}"],
                    )
                ],
                flows=[
                    dict(
                        flow_id=flow_id,
                        direction=source["direction"],
                        currency_code=source["currency_code"],
                        amount_minor=source["amount_minor"],
                        declared_date="2026-11-21",
                        source_refs=source["source_refs"],
                        native_source_id=source["id"],
                    )
                ],
            ),
        )
        first = http.client.post(root, headers=http.patron_headers, json=payload)
        assert first.status_code == 201, first.text
        replay = http.client.post(root, headers=http.patron_headers, json=payload)
        assert replay.status_code == 200 and replay.json()["replayed"]
        result = read_cash(http, w)[1]
        assert result["current"]["id"] == revision_id
        assert (
            result["current"]["source_snapshot"]["source_details"][source["id"]][
                "financial_report"
            ]["report_id"]
            == report
        )
        assert result["current"]["projection"]["settlement_state"] == "UNKNOWN"
        assert http.client.get(root, headers=http.driver_headers).status_code == 403
        return result

    def private_absent(control, archive):
        value = json.dumps(control, ensure_ascii=False)
        assert "314159265" not in value
        for secret in private:
            assert secret not in value
        for key in ['"cash_schedule"', '"source_details"', '"closing_minor"', '"openings"']:
            assert key not in value
        with ZipFile(BytesIO(archive)) as bundle:
            for name in bundle.namelist():
                content = bundle.read(name)
                for secret in private:
                    assert secret.encode() not in content, (secret, name)
                assert b"314159265" not in content, name
            manifest = json.loads(bundle.read("manifest.json"))
            assert "financial_amounts" in manifest["exclusions"]
            assert all(e["kind"] != "CASH_SCHEDULE" for e in manifest["entries"])

    def first_or_last(factory, http, packet, control, phase, w):
        controls[str(phase)] = control
        state["native_http"] = http
        state["case_id"] = str(w.case_id)
        state.setdefault("candidates", {})[str(phase)] = str(packet.candidate_id)
        if phase == 1:
            old_report = control["pricing_reference"]["referenced"]["report_id"]
            state["old_cash"] = declare(http, w, old_report, 1)
            state["old_sha"] = control["manifest_sha256"]
            state["old_p5"] = control["p5_authorization_id"]
            state["old_reviews"] = control["patron_review_ids"]
            export = http.client.get(
                f"/api/v1/patron/submission-packages/{packet.candidate_id}/export",
                headers=http.patron_headers,
            )
            assert export.status_code == 200
            state["old_archive"] = export.content
            refreshed = http.client.get(
                f"/api/v1/patron/submission-packages/{packet.candidate_id}/final-control",
                headers=http.patron_headers,
            )
            assert refreshed.status_code == 200
            private_absent(refreshed.json(), export.content)
        else:
            assert control["pricing_reference"]["referenced"]["report_id"] == state["new_report"]
            assert control["manifest_sha256"] != state["old_sha"]
            assert control["p5_authorization_id"] != state["old_p5"]
            assert not set(control["patron_review_ids"]) & set(state["old_reviews"])
            assert control["conformity"] == control["signature_verification"] == "UNKNOWN"
            assert any(r["response_state"] == "MISSING" for r in control["requirements"])
            assert read_cash(http, w)[1]["current"]["id"] == state["fresh_cash"]["current"]["id"]
            private_absent(control, packet.archive)
            # A later private revision must not mutate this exact authorized export.
            state["after_cash"] = declare(http, w, state["new_report"], 3)
            exported = http.client.get(
                f"/api/v1/patron/submission-packages/{packet.candidate_id}/export",
                headers=http.patron_headers,
            )
            assert exported.status_code == 200 and exported.content == packet.archive
            refreshed = http.client.get(
                f"/api/v1/patron/submission-packages/{packet.candidate_id}/final-control",
                headers=http.patron_headers,
            )
            assert refreshed.status_code == 200
            assert refreshed.json()["manifest_sha256"] == control["manifest_sha256"]
            private_absent(refreshed.json(), exported.content)
            controls[str(phase)] = refreshed.json()
            state["controls"] = controls
            state["private_values"] = list(private)
            (tmp_path / "private-cash-controls.json").write_text(
                json.dumps(
                    dict(
                        first=controls["1"],
                        rebuilt=refreshed.json(),
                        cash_revision=state["after_cash"]["revision"],
                    ),
                    indent=2,
                )
            )

        if handover_qualifier is not None:
            handover_qualifier(factory, http, packet, control, phase, w, list(private))

    def after_replacement(factory, http, w, report):
        state["new_report"] = report
        root, stale = read_cash(http, w)
        assert stale["current"]["context_state"] == "REVIEW_REQUIRED"
        assert stale["current"]["declaration"] == state["old_cash"]["current"]["declaration"]
        assert stale["current"]["projection"]["currencies"][0]["closing_minor"] is None
        state["fresh_cash"] = declare(http, w, report, 2)
        assert len(state["fresh_cash"]["history"]) == 2
        assert state["fresh_cash"]["history"][1]["id"] == state["old_cash"]["current"]["id"]
        assert state["fresh_cash"]["history"][1]["context_state"] == "REVIEW_REQUIRED"

    recipe.test_revised_prices_rebuild_a_sourced_response_packet_with_new_human_acts(
        session_factory,
        tmp_path,
        monkeypatch,
        handover_qualifier=first_or_last,
        pricing_qualifier=after_replacement,
    )
    return state


def test_rebuilt_exact_packet_excludes_private_cash_before_and_after_replacement(
    session_factory, tmp_path, monkeypatch
):
    packet_with_private_cash(session_factory, tmp_path, monkeypatch)
