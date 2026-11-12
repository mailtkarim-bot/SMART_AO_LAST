from dataclasses import replace
from datetime import UTC, datetime
from typing import Any, cast
from uuid import uuid4

import pytest
import sqlalchemy as sa
from app.modules.optimization.application.dated_commands import RecordDatedCapacityCommand
from app.modules.optimization.infrastructure.dated_service import (
    DatedCapacityService,
    RecordDatedCapacityHandler,
)
from app.modules.optimization.infrastructure.models import OptimizationRunRecord
from app.platform.events.dispatcher import CommandDispatcher, CommandExecutionError
from app.platform.security.authorization import AuthorizationPolicy
from tests.application.test_financial_report_draft_lines import _seed_draft


@pytest.fixture
def workflow(session_factory):
    actor, case, _, _ = _seed_draft(session_factory)
    now = datetime.now(UTC)
    actor = replace(actor, mfa_verified_at=now, authenticated_at=now)
    service = DatedCapacityService(
        session_factory=session_factory,
        dispatcher=CommandDispatcher(
            session_factory=session_factory,
            handlers={"RecordDatedCapacity": RecordDatedCapacityHandler()},
        ),
        policy=AuthorizationPolicy(),
    )
    return service, actor, case, now


def command(service, actor, case, now, **changes):
    data = dict(
        case_id=case,
        command_id=uuid4(),
        idempotency_key=uuid4(),
        run_id=uuid4(),
        expected_revision=0,
        context_sha256=service.read(actor=actor, case_id=case, now=now)["context_sha256"],
        demands=None,
        supplies=None,
        justification="Préparation synthétique",
        human_confirmed=True,
    )
    data.update(changes)
    return RecordDatedCapacityCommand(**data)


def test_missing_capacity_is_persisted_unknown_once_and_keeps_legacy_ledger(
    session_factory, workflow
):
    service, actor, case, now = workflow
    cmd = command(service, actor, case, now)
    first = service.record(actor=actor, command=cmd, now=now)
    replay = service.record(actor=actor, command=cmd, now=now)
    assert replay.replayed and replay.aggregate_refs == first.aggregate_refs
    data = service.read(actor=actor, case_id=case, now=now)
    assert data["revision"] == 1 and data["current"]["status"] == "UNKNOWN"
    assert data["current"]["state"] == "CURRENT"
    with session_factory() as session:
        assert session.scalar(sa.select(sa.func.count()).select_from(OptimizationRunRecord)) == 1


def test_stale_revision_and_context_are_rejected(workflow):
    service, actor, case, now = workflow
    cmd = command(service, actor, case, now)
    service.record(actor=actor, command=cmd, now=now)
    with pytest.raises(CommandExecutionError):
        service.record(actor=actor, command=command(service, actor, case, now), now=now)
    with pytest.raises(CommandExecutionError):
        service.record(
            actor=actor,
            command=command(
                service, actor, case, now, expected_revision=1, context_sha256="0" * 64
            ),
            now=now,
        )


def test_foreign_case_and_expired_mfa_are_refused(workflow):
    service, actor, case, now = workflow
    with pytest.raises(PermissionError):
        service.read(actor=actor, case_id=uuid4(), now=now)
    cmd = command(service, actor, case, now)
    with pytest.raises(PermissionError):
        service.record(actor=replace(actor, mfa_verified_at=None), command=cmd, now=now)


def test_new_case_scope_hides_current_plan_but_retains_history(session_factory, workflow):
    from app.modules.case.infrastructure.models.case import CaseRecord

    service, actor, case, now = workflow
    service.record(actor=actor, command=command(service, actor, case, now), now=now)
    with session_factory.begin() as session:
        row = session.get(CaseRecord, case)
        row.scope_fingerprint = "a" * 64
    data = service.read(actor=actor, case_id=case, now=now)
    assert data["current"] is None and data["state"] == "REVIEW_REQUIRED"
    assert data["history"][0]["state"] == "HISTORICAL"


def test_native_http_dated_assignment_replay_and_revision_conflict(workflow):
    from types import SimpleNamespace

    from app.interfaces.http.routes.consultations import ConsultationSecurityRuntime
    from app.interfaces.http.routes.patron_capacity import build_patron_capacity_router
    from fastapi import FastAPI
    from fastapi.testclient import TestClient

    service, actor, case, now = workflow
    app = FastAPI()
    app.include_router(
        build_patron_capacity_router(
            service=service,
            security_runtime=ConsultationSecurityRuntime(
                context_resolver=cast(Any, SimpleNamespace(resolve=lambda **kwargs: actor)),
                policy=AuthorizationPolicy(),
            ),
        )
    )
    client = TestClient(app)
    url = f"/api/v1/patron/cases/{case}/capacity"
    headers = {"Authorization": "Bearer synthetic"}
    initial = client.get(url, headers=headers)
    assert initial.status_code == 200
    row = dict(
        id=str(uuid4()),
        label="Pose",
        resource_type="compagnons",
        units=2,
        start="2026-11-01",
        end="2026-11-03",
        source=dict(reference="Planning", revision="1", locator="L2"),
    )
    cmd = command(
        service,
        actor,
        case,
        now,
        demands=[row],
        supplies=[{**row, "id": str(uuid4()), "label": "Équipe A"}],
    )
    body = cmd.model_dump(mode="json", exclude={"case_id"})
    first = client.post(url, headers=headers, json=body)
    assert first.status_code == 201, first.text
    assert client.post(url, headers=headers, json=body).status_code == 200
    data = client.get(url, headers=headers).json()
    assert data["current"]["status"] == "OPTIMAL"
    assert data["current"]["result"]["assignments"] == [
        dict(demand_id=row["id"], supply_id=body["supplies"][0]["id"])
    ]
    assert data["coverage_state"] == "UNKNOWN"
    from app.modules.case.infrastructure.resolution_reader import SqlAlchemyCaseResolutionReader

    with service._factory() as session:
        projection = SqlAlchemyCaseResolutionReader(session).get(
            tenant_id=actor.tenant_id, case_id=case, membership_id=None
        )
        assert projection is not None
        assert projection.economic_coverage is not None
        assert projection.economic_coverage.capacity.state == "UNKNOWN"
    body["justification"] = "Intent différent même clé"
    assert client.post(url, headers=headers, json=body).status_code == 409


def test_two_concurrent_revisions_cannot_both_succeed(workflow):
    from concurrent.futures import ThreadPoolExecutor

    service, actor, case, now = workflow
    commands = [command(service, actor, case, now) for _ in range(2)]

    def execute(cmd):
        try:
            service.record(actor=actor, command=cmd, now=now)
            return "RECORDED"
        except CommandExecutionError:
            return "REFUSED"

    with ThreadPoolExecutor(max_workers=2) as pool:
        assert sorted(pool.map(execute, commands)) == ["RECORDED", "REFUSED"]
    assert service.read(actor=actor, case_id=case, now=now)["revision"] == 1


def test_foreign_tenant_and_collaborator_cannot_read_or_record(workflow):
    from app.platform.security.context import ActorKind

    service, actor, case, now = workflow
    cmd = command(service, actor, case, now)
    for foreign in (
        replace(actor, tenant_id=uuid4()),
        replace(actor, actor_kind=ActorKind.COLLABORATEUR),
    ):
        with pytest.raises(PermissionError):
            service.read(actor=foreign, case_id=case, now=now)
        with pytest.raises((PermissionError, CommandExecutionError)):
            service.record(actor=foreign, command=cmd, now=now)


def test_dated_calculation_is_append_only(session_factory, workflow):
    from sqlalchemy.exc import DBAPIError

    service, actor, case, now = workflow
    cmd = command(service, actor, case, now)
    service.record(actor=actor, command=cmd, now=now)
    for statement in (
        sa.update(OptimizationRunRecord)
        .where(OptimizationRunRecord.id == cmd.run_id)
        .values(status="OPTIMAL"),
        sa.delete(OptimizationRunRecord).where(OptimizationRunRecord.id == cmd.run_id),
    ):
        with pytest.raises(DBAPIError), session_factory.begin() as session:
            session.execute(statement)
