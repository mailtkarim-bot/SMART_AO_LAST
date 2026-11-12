"""Synthetic ingestion/score/source -> real JWT P0 -> normal Case, with exact recovery."""

from uuid import uuid4

import sqlalchemy as sa
from app.modules.case.infrastructure.models.case import CaseRecord
from app.modules.opportunity.application.boamp_case_creation import BoampCaseCreationService

from tests.support.boamp_local import local_boamp


def test_synthetic_opportunity_is_qualified_then_opened_once_with_native_unknowns(
    session_factory, monkeypatch
):
    w = local_boamp(session_factory, monkeypatch)
    root = f"/api/v1/patron/boamp-opportunities/{w.observation.id}"
    before = w.client.get("/api/v1/patron/boamp-opportunities", headers=w.headers)
    assert before.status_code == 200, before.text
    assert before.headers.get("cache-control") == "no-store"
    row = next(
        x for x in before.json()["observations"] if x["observation_id"] == str(w.observation.id)
    )
    assert row["p0_state"] == "UNREVIEWED" and row["p1_state"] == "NOT_OPEN"
    assert {u["code"] for u in row["unknowns"]} >= {
        "LOT_SCOPE",
        "DCE_NOT_RECEIVED",
        "DEADLINE_MISSING",
    }
    assert row["source_captures"][0]["source_mode"] == "REPLAY"
    assert row["source_captures"][0]["source_response_sha256"] == w.source_hash
    assert row["fingerprint_sha256"] == w.observation.fingerprint_sha256

    def ids():
        return dict(command_id=str(uuid4()), idempotency_key=str(uuid4()))

    case_intent = ids()
    assert w.client.post(root + "/case", headers=w.headers, json=case_intent).status_code == 422
    qualified = w.client.post(
        root + "/qualification",
        headers=w.headers,
        json={**ids(), "decision": "QUALIFIED", "reason_code": "RELEVANT_PUBLIC_SIGNAL"},
    )
    assert qualified.status_code == 201, qualified.text
    origin = BoampCaseCreationService.create

    def lost(service, **kwargs):
        origin(service, **kwargs)
        raise sa.exc.SQLAlchemyError("Synthetic lost receipt")

    with monkeypatch.context() as p:
        p.setattr(BoampCaseCreationService, "create", lost)
        response = w.client.post(root + "/case", headers=w.headers, json=case_intent)
    assert response.status_code == 503, response.text
    retry = w.client.post(root + "/case", headers=w.headers, json=case_intent)
    assert retry.status_code == 200 and retry.json()["replayed"] is True, retry.text
    after = w.client.get("/api/v1/patron/boamp-opportunities", headers=w.headers).json()
    current = next(x for x in after["observations"] if x["observation_id"] == row["observation_id"])
    assert (
        current["p1_case_id"] == retry.json()["case_id"]
        and current["p1_state"] == "OPEN_WITH_UNKNOWNS"
    )
    assert (
        current["unknowns"] == row["unknowns"]
        and current["p0_reason_code"] == "RELEVANT_PUBLIC_SIGNAL"
    )
    from uuid import UUID

    with session_factory() as s:
        case = s.get(CaseRecord, UUID(current["p1_case_id"]))
        assert case.origin_reference_id == w.observation.id and case.tenant_id == w.actor.tenant_id
        assert str(qualified.json()["qualification_id"]) in case.origin_rationale
        assert w.observation.fingerprint_sha256 in case.origin_rationale
        assert (
            s.scalar(
                sa.select(sa.func.count())
                .select_from(CaseRecord)
                .where(CaseRecord.tenant_id == w.actor.tenant_id)
            )
            == 1
        )
    assert w.client.post(root + "/case", headers=w.headers, json=ids()).status_code == 409
    rejected = w.client.post(
        root + "/qualification",
        headers=w.headers,
        json={**ids(), "decision": "REJECTED", "reason_code": "NOT_RELEVANT"},
    )
    assert rejected.status_code == 201
    assert (
        w.client.post(root + "/case", headers=w.headers, json=case_intent).json()["replayed"]
        is True
    )
    assert w.client.post(root + "/case", headers=w.headers, json=ids()).status_code == 422
    w.client.close()
