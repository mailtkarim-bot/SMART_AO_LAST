"""One synthetic Affair, real DCE imports, independent human capacity/cash acts."""

import json
from copy import deepcopy
from datetime import UTC, datetime
from uuid import uuid4

from tests.support.l03_dce import world


def test_received_dce_capacity_and_cash_require_fresh_acts_after_rectification(
    database_engine, session_factory, tmp_path
):
    w = world(database_engine, session_factory, tmp_path, now=datetime.now(UTC))
    first_dce = w.admit(1)
    w.link(first_dce)
    root = f"/api/v1/patron/cases/{w.case_id}"

    def read(path):
        response = w.client.get(root + path, headers=w.headers)
        assert response.status_code == 200, response.text
        assert response.headers.get("cache-control") == "no-store"
        return response.json()

    def post(path, body, status):
        response = w.client.post(root + path, headers=w.headers, json=body)
        assert response.status_code == status, response.text
        if status < 300:
            assert response.headers.get("cache-control") == "no-store"
        return response.json()

    capacity = read("/capacity")
    cash = read("/cash-schedule")
    row = dict(
        id=str(uuid4()),
        label="Pose synthétique",
        resource_type="compagnons",
        units=2,
        start="2026-11-01",
        end="2026-11-03",
        source=dict(
            reference=first_dce["dce_version_id"], revision="1", locator="Planning déclaré §2"
        ),
    )
    plan = dict(
        command_id=str(uuid4()),
        idempotency_key=str(uuid4()),
        run_id=str(uuid4()),
        expected_revision=capacity["revision"],
        context_sha256=capacity["context_sha256"],
        demands=[row],
        supplies=[dict(row, id=str(uuid4()), label="Équipe synthétique")],
        justification="Besoins et disponibilité déclarés sur la source V1.",
        human_confirmed=True,
    )
    schedule = dict(
        case_id=str(w.case_id),
        command_id=str(uuid4()),
        idempotency_key=str(uuid4()),
        revision_id=str(uuid4()),
        expected_revision=cash["revision"],
        expected_view_sha256=cash["view_sha256"],
        human_confirmed=True,
        justification="Flux synthétique déclaré, sans liquidité garantie.",
        declaration=dict(
            period_start="2026-11-01",
            period_end="2026-11-30",
            assumptions="Périmètre partiel ; disponibilité et décaissement restent des hypothèses.",
            status="ACTIVE",
            openings=[dict(currency_code="EUR", amount_minor=0, source_refs=["balance://test"])],
            flows=[
                dict(
                    flow_id=str(uuid4()),
                    direction="OUTFLOW",
                    currency_code="EUR",
                    amount_minor=100,
                    declared_date="2026-11-02",
                    source_refs=[first_dce["dce_version_id"]],
                )
            ],
        ),
    )
    for path, body in (("/capacity", plan), ("/cash-schedule", schedule)):
        post(path, body, 201)
        assert post(path, body, 200)["replayed"]
    capacity, cash = read("/capacity"), read("/cash-schedule")
    assert capacity["current"]["status"] == "OPTIMAL"
    assert read("/capacity")["coverage_state"] == "UNKNOWN"
    assert (
        read("/cash-schedule")["current"]["projection"]["currencies"][0]["closing_minor"] == "-100"
    )

    second_dce = w.admit(2, first_dce)
    w.link(second_dce, expected=3)
    revised_capacity, revised_cash = read("/capacity"), read("/cash-schedule")
    assert revised_capacity["current"] is None
    assert revised_capacity["state"] == "REVIEW_REQUIRED"
    assert revised_cash["current"]["context_state"] == "REVIEW_REQUIRED"
    assert revised_cash["current"]["projection"]["currencies"][0]["closing_minor"] is None
    for path, body, id_field in (
        ("/capacity", plan, "run_id"),
        ("/cash-schedule", schedule, "revision_id"),
    ):
        assert post(path, body, 200)["replayed"]
        stale = dict(body, command_id=str(uuid4()), idempotency_key=str(uuid4()))
        stale[id_field] = str(uuid4())
        post(path, stale, 409)

    fresh_plan = deepcopy(plan)
    fresh_plan.update(
        command_id=str(uuid4()),
        idempotency_key=str(uuid4()),
        run_id=str(uuid4()),
        expected_revision=revised_capacity["revision"],
        context_sha256=revised_capacity["context_sha256"],
        justification="Nouvelle revue V2 ; quantité du besoin non établie.",
    )
    fresh_plan["demands"][0]["units"] = None
    for source_row in fresh_plan["demands"] + fresh_plan["supplies"]:
        source_row["source"].update(reference=second_dce["dce_version_id"], revision="2")
    fresh_cash = deepcopy(schedule)
    fresh_cash.update(
        command_id=str(uuid4()),
        idempotency_key=str(uuid4()),
        revision_id=str(uuid4()),
        expected_revision=revised_cash["revision"],
        expected_view_sha256=revised_cash["view_sha256"],
        justification="Nouvelle revue V2 ; montant et date à confirmer.",
    )
    fresh_cash["declaration"]["flows"][0].update(
        amount_minor=None, declared_date=None, source_refs=[second_dce["dce_version_id"]]
    )
    for path, body in (("/capacity", fresh_plan), ("/cash-schedule", fresh_cash)):
        post(path, dict(body, human_confirmed=False), 422)
        post(path, body, 201)
        assert post(path, body, 200)["replayed"]
    final_capacity, final_cash = read("/capacity"), read("/cash-schedule")
    assert final_capacity["revision"] == final_cash["revision"] == 2
    assert final_capacity["current"]["status"] == "UNKNOWN"
    assert final_capacity["current"]["inputs"]["demands"][0]["units"] is None
    assert final_capacity["history"][0]["inputs"]["demands"][0]["units"] == 2
    assert len(final_cash["history"]) == 2
    assert final_cash["history"][1]["declaration"] == cash["current"]["declaration"]
    group = final_cash["current"]["projection"]["currencies"][0]
    assert group["closing_minor"] is None and group["missing"]
    (tmp_path / "l07-browser-projections.json").write_text(
        json.dumps(
            dict(capacity_v1=capacity, cash_v1=cash, capacity_v2=final_capacity, cash_v2=final_cash)
        )
    )
    w.client.close()
