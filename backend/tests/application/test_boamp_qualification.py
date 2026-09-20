from __future__ import annotations

from datetime import UTC, datetime, timedelta
from types import SimpleNamespace
from typing import cast
from uuid import uuid4

import pytest
from app.modules.opportunity.application.boamp_qualification import (
    BoampQualificationCommand,
    PatronBoampObservationService,
    QualificationDecision,
    QualificationReason,
)
from app.modules.opportunity.infrastructure.boamp_qualification_repository import (
    BoampObservationState,
    BoampQualificationRepository,
    QualificationPersistenceResult,
)
from app.platform.events.dispatcher import CommandContext
from app.platform.security.context import ActorKind

NOW = datetime(2026, 8, 23, 12, 0, tzinfo=UTC)


class FakeRepository:
    def __init__(self, record: SimpleNamespace) -> None:
        self.record = record
        self.calls: list[dict[str, object]] = []
        self.states: dict[object, BoampObservationState] = {}

    def list_observations(self, *, session, tenant_id, limit, min_score):
        self.calls.append({"tenant_id": tenant_id, "limit": limit, "min_score": min_score})
        return (self.record,)

    def states_for_observations(self, **_kwargs):
        return self.states

    def persist_qualification(self, **kwargs):
        self.calls.append(kwargs)
        return QualificationPersistenceResult(
            qualification_id=uuid4(), event_id=uuid4(), replayed=False
        )


class FakeSession:
    def __init__(self, *values: object) -> None:
        self.values = list(values)

    def scalar(self, _statement):
        return self.values.pop(0)


def _record():
    return SimpleNamespace(
        id=uuid4(),
        source_notice_id="A-1",
        title="Réhabilitation école",
        observed_at=NOW,
        publication_date=NOW.date(),
        response_deadline=NOW,
        department_codes=["59"],
        market_types=["TRAVAUX"],
        source_status="EN_COURS",
        score_version="BOAMP_PUBLIC_V1",
        score=100,
        score_explanation_json={"score": 100},
        fingerprint_sha256="a" * 64,
    )


def test_patron_read_returns_closed_projection_and_tenant_scope() -> None:
    tenant_id = uuid4()
    repository = FakeRepository(_record())
    service = PatronBoampObservationService(
        repository=cast(BoampQualificationRepository, repository)
    )

    result = service.read(
        session=FakeSession(uuid4()),
        tenant_id=tenant_id,
        actor_id=uuid4(),
        actor_kind=ActorKind.PATRON_ADMIN.value,
        limit=10,
        min_score=80,
        now=NOW + timedelta(days=1),
    )

    assert result[0].observation_id == repository.record.id
    assert result[0].score == 100
    assert result[0].observed_at == NOW.isoformat()
    assert result[0].p0_state.value == "UNREVIEWED"
    assert result[0].p1_state.value == "NOT_OPEN"
    assert result[0].lot_scope_state.value == "UNKNOWN"
    assert result[0].lot_scope_source == "BOAMP"
    assert result[0].deadline_state.value == "EXPIRED"
    assert result[0].unknowns == ()
    assert not hasattr(result[0], "tenant_id")
    assert repository.calls == [{"tenant_id": tenant_id, "limit": 10, "min_score": 80}]


def test_patron_read_marks_missing_deadline_as_unknown() -> None:
    repository = FakeRepository(_record())
    repository.record.response_deadline = None
    service = PatronBoampObservationService(
        repository=cast(BoampQualificationRepository, repository)
    )

    result = service.read(
        session=FakeSession(uuid4()),
        tenant_id=uuid4(),
        actor_id=uuid4(),
        actor_kind=ActorKind.PATRON_ADMIN.value,
        now=NOW,
    )[0]

    assert result.deadline_state.value == "MISSING"
    assert result.unknowns == ()

    repository.states[repository.record.id] = BoampObservationState(case_id=uuid4())
    opened = service.read(
        session=FakeSession(uuid4()),
        tenant_id=uuid4(),
        actor_id=uuid4(),
        actor_kind=ActorKind.PATRON_ADMIN.value,
        now=NOW,
    )[0]
    assert {item["code"] for item in opened.unknowns} == {
        "LOT_SCOPE",
        "DCE_NOT_RECEIVED",
        "DEADLINE_MISSING",
    }


def test_score_does_not_change_unreviewed_p0_state() -> None:
    repository = FakeRepository(_record())
    service = PatronBoampObservationService(
        repository=cast(BoampQualificationRepository, repository)
    )

    repository.record.score = 10
    low_score = service.read(
        session=FakeSession(uuid4()),
        tenant_id=uuid4(),
        actor_id=uuid4(),
        actor_kind=ActorKind.PATRON_ADMIN.value,
        now=NOW,
    )[0]
    repository.record.score = 100
    high_score = service.read(
        session=FakeSession(uuid4()),
        tenant_id=uuid4(),
        actor_id=uuid4(),
        actor_kind=ActorKind.PATRON_ADMIN.value,
        now=NOW,
    )[0]

    assert low_score.p0_state == high_score.p0_state
    assert low_score.p0_state.value == "UNREVIEWED"


def test_patron_read_projects_latest_qualification_and_case_state() -> None:
    repository = FakeRepository(_record())
    qualification = SimpleNamespace(
        id=uuid4(),
        decision="QUALIFIED",
        reason_code="RELEVANT_PUBLIC_SIGNAL",
        created_at=NOW,
    )
    repository.states[repository.record.id] = BoampObservationState(
        latest_qualification=qualification,
        case_id=uuid4(),
        case_created_at=NOW,
    )
    service = PatronBoampObservationService(
        repository=cast(BoampQualificationRepository, repository)
    )

    result = service.read(
        session=FakeSession(uuid4()),
        tenant_id=uuid4(),
        actor_id=uuid4(),
        actor_kind=ActorKind.PATRON_ADMIN.value,
        now=NOW - timedelta(days=1),
    )[0]

    assert result.p0_state.value == "TARGETED"
    assert result.p0_decision == QualificationDecision.QUALIFIED
    assert result.p0_reason_code == QualificationReason.RELEVANT_PUBLIC_SIGNAL
    assert result.p0_qualification_id == qualification.id
    assert result.p1_state.value == "OPEN_WITH_UNKNOWNS"
    assert result.p1_case_id == repository.states[repository.record.id].case_id
    assert result.p1_opened_at == NOW.isoformat()
    assert result.lot_scope_source == "BOAMP"
    assert {item["code"] for item in result.unknowns} == {"LOT_SCOPE", "DCE_NOT_RECEIVED"}


def test_qualification_requires_patron_and_compatible_closed_reason() -> None:
    with pytest.raises(ValueError, match="incompatible"):
        BoampQualificationCommand(
            observation_id=uuid4(),
            decision=QualificationDecision.QUALIFIED,
            reason_code=QualificationReason.NOT_RELEVANT,
            command_id=uuid4(),
            idempotency_key=uuid4(),
        ).validate()

    repository = FakeRepository(_record())
    service = PatronBoampObservationService(
        repository=cast(BoampQualificationRepository, repository)
    )
    context = CommandContext(
        tenant_id=uuid4(),
        actor_id=uuid4(),
        actor_kind=ActorKind.PATRON_ADMIN.value,
        received_at=NOW,
    )
    command = BoampQualificationCommand(
        observation_id=repository.record.id,
        decision=QualificationDecision.QUALIFIED,
        reason_code=QualificationReason.RELEVANT_PUBLIC_SIGNAL,
        command_id=uuid4(),
        idempotency_key=uuid4(),
    )

    result = service.qualify(
        session=FakeSession(uuid4(), repository.record),
        context=context,
        command=command,
        now=NOW,
    )

    assert result.replayed is False
    assert repository.calls[-1]["tenant_id"] == context.tenant_id


def test_qualification_rejects_collaborator_before_database_access() -> None:
    repository = FakeRepository(_record())
    service = PatronBoampObservationService(
        repository=cast(BoampQualificationRepository, repository)
    )
    context = CommandContext(
        tenant_id=uuid4(),
        actor_id=uuid4(),
        actor_kind=ActorKind.COLLABORATEUR.value,
        received_at=NOW,
    )

    with pytest.raises(PermissionError, match="PATRON_REQUIRED"):
        service.qualify(
            session=FakeSession(),
            context=context,
            command=BoampQualificationCommand(
                observation_id=repository.record.id,
                decision=QualificationDecision.QUALIFIED,
                reason_code=QualificationReason.RELEVANT_PUBLIC_SIGNAL,
                command_id=uuid4(),
                idempotency_key=uuid4(),
            ),
            now=NOW,
        )
