from uuid import UUID

from app.modules.case.infrastructure.models.case import CaseRecord
from app.modules.dce.infrastructure.models.dce_version import DceDocumentRecord, DceVersionRecord

from tests.api.test_dce_authenticated_api import _headers, _seed_principal
from tests.support.l03_dce import world


def test_native_inventory_rectification_keeps_excluded_unread_and_missing_exact(
    database_engine, session_factory, tmp_path
):
    w = world(database_engine, session_factory, tmp_path)
    v1 = w.admit(1)
    w.link(v1)
    w.link(v1, w.other_case_id)
    url = f"/api/v1/cases/{w.case_id}/dce-reading"
    first = w.client.get(url, headers=w.headers)
    assert first.status_code == 200, first.text
    before = first.json()
    assert before["coverage"]["analysis_complete"] is False
    assert before["coverage"]["inventory_completeness"] == "UNKNOWN"
    assert before["coverage"]["case_scope_kind"] == "MULTI_LOT"
    assert before["coverage"]["total_documents"] == 3
    assert before["coverage"]["unread_documents"] >= 2
    exceptions = before["coverage"]["exceptions"]
    assert {"EXCLUDED_UNSAFE", "NOT_EXTRACTED", "DECLARED_MISSING"} <= {
        e["state"] for e in exceptions
    }
    assert all(e["lot_applicability"] == "UNKNOWN" for e in exceptions)
    v2 = w.admit(2, v1)
    superseded = w.client.get(url, headers=w.headers).json()
    assert superseded["dce_freshness"] == "REVIEW_REQUIRED"
    assert superseded["dce"]["lifecycle"] == "SUPERSEDED"
    cases = w.client.get("/api/v1/cases/assigned", headers=w.headers).json()
    selected = next(c for c in cases if c["case_id"] == str(w.case_id))
    assert selected["aggregate_revision"] == 3
    assert selected["applicable_dce_version_id"] == v1["dce_version_id"]
    w.link(v2, expected=3)
    current = w.client.get(url, headers=w.headers).json()
    assert current["dce"]["dce_version_id"] == v2["dce_version_id"]
    assert current["dce_freshness"] == "CURRENT"
    assert current["coverage"]["total_documents"] == 2
    old_ids = {d["document_id"] for d in before["coverage"]["documents"]}
    new_ids = {d["document_id"] for d in current["coverage"]["documents"]}
    assert old_ids.isdisjoint(new_ids)
    missing = [e for e in current["coverage"]["exceptions"] if e["kind"] == "DECLARED_MISSING"]
    assert [e["document_family"] for e in missing] == ["AE"]
    assert current["coverage"]["analysis_complete"] is False
    assert current["coverage"]["inventory_completeness"] == "UNKNOWN"
    with session_factory() as s:
        historical = s.get(DceVersionRecord, UUID(v1["dce_version_id"]))
        other = s.get(CaseRecord, w.other_case_id)
        assert historical.lifecycle == "SUPERSEDED"
        assert (
            other.applicable_dce_version_id == historical.id
            and other.dce_freshness == "REVIEW_REQUIRED"
        )
        for doc in v1["documents"]:
            assert s.get(DceDocumentRecord, UUID(doc["document_id"])) is not None
    _, foreign_identity, foreign_session = _seed_principal(database_engine)
    foreign = _headers(w.tokens, identity_id=foreign_identity, session_id=foreign_session)
    assert w.client.get(url, headers=foreign).status_code == 404
    assert (
        w.client.get(
            f"/api/v1/dce-versions/{v2['dce_version_id']}/documents", headers=foreign
        ).status_code
        == 404
    )
    _, collab_identity, collab_session = _seed_principal(
        database_engine, role="COLLABORATEUR", tenant_id=w.tenant
    )
    collaborator = _headers(w.tokens, identity_id=collab_identity, session_id=collab_session)
    assert w.client.post("/api/v1/dce-versions", json=v2, headers=collaborator).status_code == 403
    w.client.close()
