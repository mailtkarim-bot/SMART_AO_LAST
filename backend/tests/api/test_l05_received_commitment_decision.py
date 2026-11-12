from datetime import UTC, datetime
from uuid import uuid4

from tests.api.test_l04_received_analysis_rectification import assessment, process, review, summary
from tests.support.l03_dce import ids, world


def confirm_points(w):
    current = summary(w)
    for axis in current["axes"]:
        for point in axis["items"]:
            if point["kind"] == "REQUIREMENT":
                body = {
                    **ids(),
                    "confirmation_id": str(uuid4()),
                    "expected_confirmation_revision": point["native_revision"],
                    "outcome": "CONFIRMED",
                    "reason_code": "SOURCE_REVIEWED",
                }
                r = w.client.post(
                    f"/api/v1/dce-requirements/{point['item_id']}/confirmations",
                    headers=w.headers,
                    json=body,
                )
                assert r.status_code == 201, r.text


def treated(w):
    current = summary(w)
    for axis in current["axes"]:
        for point in axis["items"]:
            body = assessment(point, axis["code"])
            body["treatment"]["hypotheses"] = (
                "Mobilisation et preuves encore à chiffrer ; aucune valeur certaine."
            )
            response = w.client.post(
                f"/api/v1/cases/{w.case_id}/analysis-assessments", headers=w.headers, json=body
            )
            assert response.status_code == 201, response.text
    return summary(w)


def card(w):
    response = w.client.get(f"/api/v1/patron/cases/{w.case_id}/commitment-card", headers=w.headers)
    assert response.status_code == 200, response.text
    return response.json()


def decision(w, body):
    return w.client.post(
        f"/api/v1/patron/cases/{w.case_id}/decisions", headers=w.headers, json=body
    )


def freeze(w, created):
    c = card(w)
    body = {
        **ids(),
        "context_id": str(uuid4()),
        "expected_revision": created["version"],
        "rationale": "Décision locale fondée sur les points et hypothèses affichés.",
        "unknowns": ["Applicabilité, mobilisation et preuve documentaire à confirmer."],
        "references": c["references"],
    }
    response = w.client.post(
        f"/api/v1/patron/cases/{w.case_id}/decisions/{created['decision_id']}/context",
        headers=w.headers,
        json=body,
    )
    assert response.status_code == 200, response.text
    return response.json()


def test_treated_dossier_reaches_card_open_condition_and_new_native_cycle(
    database_engine, session_factory, tmp_path
):
    now = datetime.now(tz=UTC)
    w = world(database_engine, session_factory, tmp_path, now=now)
    v1 = w.admit(1)
    w.link(v1)
    process(session_factory, w.tenant, v1)
    confirm_points(w)
    treated(w)
    review(w, "PREPARED", 0)
    review(w, "REVIEWED", 1)
    first = card(w)
    assert first["analysis_complete"] is False and first["gate_effect"] == "NONE"
    assert len(first["axes"]) == 12 and first["dossier_review"]["phase"] == "REVIEWED"
    types = {r["aggregate_type"] for r in first["references"]}
    assert {"ANALYSIS_ASSESSMENT", "DCE_REQUIREMENT"} <= types
    body = {**ids(), "scope_fingerprint": first["case_scope_fingerprint"]}
    created = decision(w, body)
    assert created.status_code == 201, created.text
    created = created.json()
    frozen = freeze(w, created)
    condition = str(uuid4())
    final_body = {
        **ids(),
        "expected_revision": frozen["version"],
        "displayed_fingerprint": frozen["fingerprint"],
        "outcome": "CONDITIONAL_GO",
        "justification": "Engagement synthétique réservé à l’obtention de la preuve source exacte.",
        "conditions": [
            {
                "condition_id": condition,
                "label": "Qualifier l’applicabilité au lot et obtenir la preuve attendue.",
                "owner_actor_id": str(w.identity),
                "due_date_absence_reason": "Échéance encore inconnue.",
                "failure_consequence": "Maintenir la réserve et ne pas engager automatiquement.",
            }
        ],
    }
    url = f"/api/v1/patron/cases/{w.case_id}/decisions/{created['decision_id']}"
    finalized = w.client.post(url + "/go-no-go", headers=w.headers, json=final_body)
    assert finalized.status_code == 200, finalized.text
    first = card(w)
    act = first["points"][0]["point"]["human_assessment"]
    version = finalized.json()["version"]
    link_body = {
        **ids(),
        "link_id": str(uuid4()),
        "assessment_id": act["assessment_id"],
        "assessment_revision": act["revision"],
        "source_context_sha256": act["source_context_sha256"],
        "expected_decision_revision": version,
        "justification": "Condition reliée au traitement exact, sans la satisfaire.",
        "human_confirmed": True,
    }
    linked = w.client.post(
        url + f"/conditions/{condition}/assessment-links", headers=w.headers, json=link_body
    )
    assert linked.status_code == 201, linked.text
    retry = w.client.post(
        url + f"/conditions/{condition}/assessment-links", headers=w.headers, json=link_body
    )
    assert retry.status_code == 200 and retry.json()["replayed"]
    bound = card(w)
    assert bound["current_decision"]["conditions"][0]["status"] == "OPEN"
    assert bound["gate_effect"] == "NONE"
    v2 = w.admit(2, v1)
    w.link(v2, expected=3)
    process(session_factory, w.tenant, v2)
    confirm_points(w)
    treated(w)
    review(w, "PREPARED", 2)
    review(w, "REVIEWED", 3)
    changed = card(w)
    assert changed["current_decision"]["state"] == "REVIEW_REQUIRED"
    second_body = {**ids(), "scope_fingerprint": changed["case_scope_fingerprint"]}
    second = decision(w, second_body)
    assert second.status_code == 201, second.text
    replay = decision(w, second_body)
    assert replay.status_code == 200 and replay.json()["replayed"]
    current = card(w)
    assert current["current_decision"]["cycle_number"] == 2
    assert current["current_decision"]["outcome"] == "UNDECIDED"
    assert not current["current_decision"]["conditions"]
    frozen2 = freeze(w, second.json())
    no_go = {
        **ids(),
        "expected_revision": frozen2["version"],
        "displayed_fingerprint": frozen2["fingerprint"],
        "outcome": "NO_GO",
        "justification": "Preuves et inconnus V2 ne permettent pas un engagement certain.",
        "conditions": [],
    }
    response = w.client.post(
        f"/api/v1/patron/cases/{w.case_id}/decisions/{second.json()['decision_id']}/go-no-go",
        headers=w.headers,
        json=no_go,
    )
    assert response.status_code == 200, response.text
    final = card(w)
    assert final["current_decision"]["outcome"] == "NO_GO"
    old = next(d for d in final["history"] if d["decision_id"] == created["decision_id"])
    assert (
        old["final_justification"] == final_body["justification"]
        and old["conditions"][0]["status"] == "OPEN"
    )
    assert old["assessment_links"][0]["assessment_id"] == act["assessment_id"]
    assert final["gate_effect"] == "NONE" and final["analysis_complete"] is False
    denied = decision(w, {**ids(), "scope_fingerprint": final["case_scope_fingerprint"]})
    assert denied.status_code == 409
    w.client.close()
