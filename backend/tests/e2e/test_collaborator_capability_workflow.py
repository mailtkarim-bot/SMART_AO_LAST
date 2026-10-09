from __future__ import annotations

import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from threading import Barrier
from uuid import uuid4

import pytest
import sqlalchemy as sa
from app.platform.security.models import CaseCapabilityGapRecord, CaseCapabilityProposalRecord
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session, sessionmaker

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "application"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "api"))
from test_collab_capability import _seed  # noqa: E402
from test_collaborator_capability_api import (  # noqa: E402
    _auth_session,
    _client,
    _headers,
)


@pytest.mark.e2e
@pytest.mark.api
@pytest.mark.db
@pytest.mark.security
def test_end_to_end_collaborator_proposal_gap_and_read_workflow(
    session_factory: sessionmaker[Session],
) -> None:
    actor, assignment_id, case_id, requirement_id, capability_id, version_id = _seed(
        session_factory
    )
    _auth_session(session_factory, actor)
    client, tokens = _client(session_factory)
    headers = _headers(tokens, actor)
    proposal_payload = {
        "command_id": str(uuid4()),
        "idempotency_key": str(uuid4()),
        "correlation_id": str(uuid4()),
        "capability_id": str(capability_id),
        "capability_version_id": str(version_id),
        "requirement_id": str(requirement_id),
        "justification": "La qualification répond à l’exigence Case.",
        "source_locator": "RC p. 12",
    }
    proposal = client.post(
        f"/api/v1/collaborator/cases/{case_id}/capability-proposals",
        json=proposal_payload,
        headers=headers,
    )
    replay = client.post(
        f"/api/v1/collaborator/cases/{case_id}/capability-proposals",
        json=proposal_payload,
        headers=headers,
    )
    gap = client.post(
        f"/api/v1/collaborator/cases/{case_id}/capability-gaps",
        json={
            "command_id": str(uuid4()),
            "idempotency_key": str(uuid4()),
            "correlation_id": str(uuid4()),
            "assignment_id": str(assignment_id),
            "capability_id": str(capability_id),
            "requirement_id": str(requirement_id),
            "gap_kind": "EXPIRED",
            "severity": "IMPORTANT",
            "reason": "La preuve doit être renouvelée avant transmission.",
            "source_locator": "RC p. 13",
            "recommended_action": "Demander une preuve actuelle au patron.",
        },
        headers=headers,
    )
    read = client.get(
        f"/api/v1/collaborator/cases/{case_id}/capability-assessments",
        headers=headers,
    )

    assert proposal.status_code == 201, proposal.text
    assert replay.status_code == 200, replay.text
    assert replay.json()["replayed"] is True
    assert gap.status_code == 201, gap.text
    assert read.status_code == 200, read.text
    assert len(read.json()["proposals"]) == 1
    assert read.json()["proposals"][0]["validity_state"] == "CURRENT"
    assert read.json()["proposals"][0]["assignment_id"] == str(assignment_id)
    assert read.json()["gaps"][0]["gap_kind"] == "EXPIRED"
    assert "tenant_id" not in str(read.json())
    assert "price" not in str(read.json()).lower()
    assert "margin" not in str(read.json()).lower()
    with session_factory() as session:
        assert (
            session.scalar(
                sa.select(sa.func.count())
                .select_from(CaseCapabilityProposalRecord)
                .where(CaseCapabilityProposalRecord.case_id == case_id)
            )
            == 1
        )
        assert session.scalar(sa.select(sa.func.count()).select_from(CaseCapabilityGapRecord)) == 1


@pytest.mark.e2e
@pytest.mark.api
@pytest.mark.db
@pytest.mark.security
def test_concurrent_capability_proposal_double_click_is_one_append_only_act(
    session_factory: sessionmaker[Session],
) -> None:
    actor, assignment_id, case_id, requirement_id, capability_id, version_id = _seed(
        session_factory
    )
    _auth_session(session_factory, actor)
    first_client, first_tokens = _client(session_factory)
    second_client, second_tokens = _client(session_factory)
    headers = (_headers(first_tokens, actor), _headers(second_tokens, actor))
    payload = {
        "command_id": str(uuid4()),
        "idempotency_key": str(uuid4()),
        "correlation_id": str(uuid4()),
        "capability_id": str(capability_id),
        "capability_version_id": str(version_id),
        "requirement_id": str(requirement_id),
        "justification": "Je propose cette version pour l’exigence applicable.",
    }
    url = f"/api/v1/collaborator/cases/{case_id}/capability-proposals"
    barrier = Barrier(2)

    def post(client: TestClient, auth_headers: dict[str, str]):
        barrier.wait(timeout=5)
        return client.post(url, json=payload, headers=auth_headers)

    with ThreadPoolExecutor(max_workers=2) as pool:
        responses = list(
            pool.map(
                lambda args: post(*args),
                [(first_client, headers[0]), (second_client, headers[1])],
            )
        )

    assert sorted(response.status_code for response in responses) in ([200, 201], [201, 409])
    for response in responses:
        if response.status_code in (200, 201):
            assert response.json()["command_id"] == payload["command_id"]
            assert response.json()["idempotency_key"] == payload["idempotency_key"]
        else:
            assert response.json()["detail"] == "IDEMPOTENCY_CONFLICT"
    read = first_client.get(
        url.replace("capability-proposals", "capability-assessments"), headers=headers[0]
    )
    assert read.status_code == 200, read.text
    assert len(read.json()["proposals"]) == 1
    assert read.json()["proposals"][0]["assignment_id"] == str(assignment_id)
    with session_factory() as session:
        assert (
            session.scalar(
                sa.select(sa.func.count())
                .select_from(CaseCapabilityProposalRecord)
                .where(CaseCapabilityProposalRecord.case_id == case_id)
            )
            == 1
        )
