"""Received originals -> native processing -> human dossier -> actual replacement."""

from datetime import UTC, datetime
from uuid import UUID, uuid4

import sqlalchemy as sa
from app.modules.case.application.analysis_summary import AXES
from app.modules.case.infrastructure.models.analysis_assessment import AnalysisAssessmentRecord
from app.modules.dce.application.analysis import DceRcAnalysisService
from app.modules.dce.application.classification import DceDocumentClassificationService
from app.modules.dce.application.handlers import (
    RecordDceDocumentClassificationRunHandler,
    RecordDceRcAnalysisHandler,
    RecordDceRequirementMaterializationRunHandler,
)
from app.modules.dce.application.requirements import DceRequirementsService
from app.platform.events.dispatcher import CommandDispatcher

from tests.api.test_dce_authenticated_api import _headers, _seed_principal
from tests.support.l03_dce import ids, world


def process(session_factory, tenant, version):
    dispatcher = CommandDispatcher(
        session_factory=session_factory,
        handlers={
            "RecordDceDocumentClassificationRun": RecordDceDocumentClassificationRunHandler(),
            "RecordDceRcAnalysis": RecordDceRcAnalysisHandler(),
            "RecordDceRequirementMaterializationRun": (
                RecordDceRequirementMaterializationRunHandler()
            ),
        },
    )
    DceDocumentClassificationService(
        session_factory=session_factory, dispatcher=dispatcher
    ).classify(tenant_id=tenant, dce_version_id=UUID(version["dce_version_id"]))
    analyzed = DceRcAnalysisService(session_factory=session_factory, dispatcher=dispatcher).analyze(
        tenant_id=tenant, dce_version_id=UUID(version["dce_version_id"])
    )
    result = DceRequirementsService(
        session_factory=session_factory, dispatcher=dispatcher
    ).materialize(
        tenant_id=tenant,
        dce_version_id=UUID(version["dce_version_id"]),
        dce_rc_analysis_id=UUID(str(analyzed.aggregate_refs[0]["aggregate_id"])),
    )
    return result


def summary(w):
    response = w.client.get(f"/api/v1/cases/{w.case_id}/analysis-summary", headers=w.headers)
    assert response.status_code == 200, response.text
    return response.json()


def assessment(point, axis):
    return {
        **ids(),
        "assessment_id": str(uuid4()),
        "point_kind": point["kind"],
        "point_id": point["item_id"],
        "expected_revision": 0,
        "source_context_sha256": point["source_context_sha256"],
        "expected_evidence_state": "UNKNOWN",
        "residual_risk_state": "UNKNOWN",
        "unknown_reason": "Preuves et conséquences à compléter humainement.",
        "justification": "Traitement humain synthétique sur la source exacte.",
        "human_confirmed": True,
        "treatment": {
            "axis_code": axis,
            "applicability": "UNKNOWN",
            "applicability_reason": "Applicabilité au lot non encore établie.",
            "consequences": {
                "technical": None,
                "price": None,
                "delay": None,
                "cash": None,
                "contract": None,
            },
            "unknown_reason": "Aucune conséquence ou échéance certaine déduite.",
            "action": "Relire le point exact et demander la preuve attendue.",
            "responsible": "SELF",
            "due_at": None,
        },
    }


def review(w, phase, revision):
    current = summary(w)
    payload = {
        **ids(),
        "review_id": str(uuid4()),
        "expected_revision": revision,
        "dossier_sha256": current["dossier_sha256"],
        "phase": phase,
        "axes": [
            {
                "code": code,
                "state": "UNKNOWN",
                "note": "Axe relu sans présumer l’absence de risque.",
                "follow_up": "Compléter les sources et la qualification humaine.",
                "responsible": "SELF",
            }
            for code, _ in AXES
        ],
        "justification": "Revue locale des douze axes, limites conservées.",
        "human_confirmed": True,
    }
    response = w.client.post(
        f"/api/v1/cases/{w.case_id}/analysis-dossier-reviews", headers=w.headers, json=payload
    )
    assert response.status_code == 201, response.text
    replay = w.client.post(
        f"/api/v1/cases/{w.case_id}/analysis-dossier-reviews", headers=w.headers, json=payload
    )
    assert replay.status_code == 200 and replay.json()["replayed"]
    return payload


def test_received_dce_has_twelve_axes_and_new_human_acts_after_rectification(
    database_engine, session_factory, tmp_path
):
    now = datetime.now(tz=UTC)
    w = world(database_engine, session_factory, tmp_path, now=now)
    v1 = w.admit(1)
    w.link(v1)
    process(session_factory, w.tenant, v1)
    first = summary(w)
    assert len(first["axes"]) == 12 and first["analysis_complete"] is False
    assert first["coverage"]["unread_documents"] >= 2
    points = [(a["code"], p) for a in first["axes"] for p in a["items"]]
    assert points, "No native sourced point materialized"
    assert any(not a["items"] and a["status"] == "NON_EVALUATED" for a in first["axes"])
    old = []
    for axis, point in points:
        assert point["source_state"] == "CURRENT_SOURCE"
        assert point["source_anchor"]["dce_version_id"] == v1["dce_version_id"]
        assert point["source_excerpt_state"] == "EXACT_SOURCE"
        payload = assessment(point, axis)
        old.append(payload)
        response = w.client.post(
            f"/api/v1/cases/{w.case_id}/analysis-assessments", headers=w.headers, json=payload
        )
        assert response.status_code == 201, response.text
        replay = w.client.post(
            f"/api/v1/cases/{w.case_id}/analysis-assessments", headers=w.headers, json=payload
        )
        assert replay.status_code == 200 and replay.json()["replayed"]
    review(w, "PREPARED", 0)
    review(w, "REVIEWED", 1)
    reviewed = summary(w)
    assert reviewed["dossier_review"]["phase"] == "REVIEWED"
    assert reviewed["analysis_complete"] is False
    v2 = w.admit(2, v1)
    invalid = summary(w)
    assert invalid["source_context_state"] != "CURRENT"
    assert invalid["dossier_review"]["state"] == "REVIEW_REQUIRED"
    assert all(p["source_state"] != "CURRENT_SOURCE" for a in invalid["axes"] for p in a["items"])
    stale = {**old[0], **ids(), "assessment_id": str(uuid4()), "expected_revision": 1}
    refused = w.client.post(
        f"/api/v1/cases/{w.case_id}/analysis-assessments", headers=w.headers, json=stale
    )
    assert refused.status_code == 409, refused.text
    w.link(v2, expected=3)
    process(session_factory, w.tenant, v2)
    second = summary(w)
    new_points = [(a["code"], p) for a in second["axes"] for p in a["items"]]
    assert new_points
    assert {p["item_id"] for _, p in points}.isdisjoint({p["item_id"] for _, p in new_points})
    assert all(p["human_assessment"] is None for _, p in new_points)
    for axis, point in new_points:
        response = w.client.post(
            f"/api/v1/cases/{w.case_id}/analysis-assessments",
            headers=w.headers,
            json=assessment(point, axis),
        )
        assert response.status_code == 201, response.text
    review(w, "PREPARED", 2)
    review(w, "REVIEWED", 3)
    final = summary(w)
    assert final["dossier_review"]["revision"] == 4 and final["analysis_complete"] is False
    with session_factory() as s:
        assert s.scalar(
            sa.select(sa.func.count())
            .select_from(AnalysisAssessmentRecord)
            .where(AnalysisAssessmentRecord.tenant_id == w.tenant)
        ) == len(points) + len(new_points)
    history = w.client.get(f"/api/v1/cases/{w.case_id}/analysis-dossier-history", headers=w.headers)
    assert history.status_code == 200, history.text
    assert v1["dce_version_id"] in history.text and v2["dce_version_id"] in history.text
    _, foreign_identity, foreign_session = _seed_principal(database_engine, now=now)
    foreign = _headers(w.tokens, identity_id=foreign_identity, session_id=foreign_session)
    assert (
        w.client.get(f"/api/v1/cases/{w.case_id}/analysis-summary", headers=foreign).status_code
        == 404
    )
    _, collab_identity, collab_session = _seed_principal(
        database_engine, role="COLLABORATEUR", tenant_id=w.tenant, now=now
    )
    collaborator = _headers(w.tokens, identity_id=collab_identity, session_id=collab_session)
    assert (
        w.client.post(
            f"/api/v1/cases/{w.case_id}/analysis-assessments", headers=collaborator, json=old[0]
        ).status_code
        == 403
    )
    w.client.close()
