from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
from datetime import UTC, date, datetime, timedelta
from pathlib import Path
from uuid import uuid4

import httpx
import pytest
import sqlalchemy as sa
from alembic import command
from alembic.config import Config
from app.interfaces.http.routes.patron_boamp_opportunities import _source_status
from app.modules.market_watch.infrastructure.boamp import (
    BoampReadOnlySearch,
    BoampRegistryUnavailable,
)
from app.modules.opportunity.application.boamp_ingestion import OpportunityCandidate
from app.modules.opportunity.application.boamp_qualification import (
    PatronBoampObservationService,
)
from app.modules.opportunity.application.boamp_scoring import (
    BoampOpportunityScoringService,
    ExplainableOpportunityScore,
)
from app.modules.opportunity.domain.watch_profile import WatchProfileCriteria
from app.modules.opportunity.infrastructure.boamp_observation_repository import (
    BoampObservationPersistenceConflict,
    BoampObservationRepository,
    ingestion_request_hash,
)
from app.modules.opportunity.infrastructure.boamp_qualification_repository import (
    BoampQualificationRepository,
)
from app.modules.opportunity.infrastructure.models import (
    OpportunityWatchProfileRecord,
    OpportunityWatchProfileVersionRecord,
)
from app.modules.opportunity.infrastructure.observation_models import (
    BoampIngestionObservationLinkRecord,
    BoampIngestionRunRecord,
    BoampOpportunityObservationRecord,
)
from app.platform.persistence.models import DomainEventRecord, OutboxMessageRecord, TenantRecord
from app.platform.security.models import IdentityRecord, TenantMembershipRecord
from sqlalchemy.orm import Session, sessionmaker
from tests.support.database import ALEMBIC_INI, DATABASE_URL

pytestmark = pytest.mark.db
NOW = datetime(2026, 8, 23, 12, 0, tzinfo=UTC)
_PERSIST_SCRIPT_PATH = (
    Path(__file__).resolve().parents[3] / "scripts" / "persist_boamp_opportunities.py"
)
_PERSIST_SCRIPT_SPEC = importlib.util.spec_from_file_location(
    "persist_boamp_opportunities_for_replay_test", _PERSIST_SCRIPT_PATH
)
assert _PERSIST_SCRIPT_SPEC is not None and _PERSIST_SCRIPT_SPEC.loader is not None
_PERSIST_SCRIPT = importlib.util.module_from_spec(_PERSIST_SCRIPT_SPEC)
_PERSIST_SCRIPT_SPEC.loader.exec_module(_PERSIST_SCRIPT)
_INGEST_SCRIPT_PATH = (
    Path(__file__).resolve().parents[3] / "scripts" / "ingest_boamp_opportunities.py"
)
_INGEST_SCRIPT_SPEC = importlib.util.spec_from_file_location(
    "ingest_boamp_opportunities_for_replay_test", _INGEST_SCRIPT_PATH
)
assert _INGEST_SCRIPT_SPEC is not None and _INGEST_SCRIPT_SPEC.loader is not None
_INGEST_SCRIPT = importlib.util.module_from_spec(_INGEST_SCRIPT_SPEC)
_INGEST_SCRIPT_SPEC.loader.exec_module(_INGEST_SCRIPT)


def _candidate() -> OpportunityCandidate:
    return OpportunityCandidate(
        source="BOAMP",
        source_notice_id="A-1",
        title="Réhabilitation école",
        publication_date=date(2026, 8, 20),
        response_deadline=NOW + timedelta(days=5),
        department_codes=("59",),
        market_types=("TRAVAUX",),
        source_status="EN_COURS",
    )


def _scored() -> tuple[tuple[OpportunityCandidate, ExplainableOpportunityScore], ...]:
    candidate = _candidate()
    score = BoampOpportunityScoringService().score(
        candidate=candidate,
        criteria=WatchProfileCriteria(keywords=("réhabilitation",), included_departments=("59",)),
        now=NOW,
    )
    return ((candidate, score),)


def _seed(session_factory: sessionmaker[Session]):
    tenant_id, actor_id, profile_id = uuid4(), uuid4(), uuid4()
    membership_id, version_id = uuid4(), uuid4()
    with session_factory.begin() as session:
        session.add(
            TenantRecord(id=tenant_id, slug=f"tenant-{tenant_id.hex[:12]}", lifecycle="ACTIVE")
        )
        session.flush()
        session.add(
            IdentityRecord(
                id=actor_id,
                email_normalized=f"actor-{actor_id.hex[:12]}@example.test",
                lifecycle="ACTIVE",
                email_verified_at=NOW,
            )
        )
        session.add(
            TenantMembershipRecord(
                id=membership_id,
                tenant_id=tenant_id,
                identity_id=actor_id,
                role="PATRON_ADMIN",
                state="ACTIVE",
                activated_at=NOW,
                revoked_at=None,
            )
        )
        session.add(
            OpportunityWatchProfileRecord(
                id=profile_id,
                tenant_id=tenant_id,
                aggregate_revision=0,
                name="Veille BTP",
                state="ACTIVE",
                current_version=1,
                actor_id=actor_id,
                command_id=uuid4(),
                idempotency_key=uuid4(),
                correlation_id=uuid4(),
            )
        )
        session.add(
            OpportunityWatchProfileVersionRecord(
                id=version_id,
                tenant_id=tenant_id,
                profile_id=profile_id,
                version_number=1,
                name="Veille BTP",
                criteria_json=WatchProfileCriteria(keywords=("réhabilitation",)).snapshot(),
                criteria_sha256="a" * 64,
                actor_id=actor_id,
                command_id=uuid4(),
                idempotency_key=uuid4(),
                correlation_id=uuid4(),
            )
        )
    return tenant_id, actor_id, profile_id


def test_repository_persists_and_replays_with_audit(
    session_factory: sessionmaker[Session],
) -> None:
    tenant_id, actor_id, profile_id = _seed(session_factory)
    scored = _scored()
    request_hash = ingestion_request_hash(
        profile_id=profile_id,
        profile_version=1,
        pages_read=1,
        truncated=False,
        scored_candidates=scored,
    )
    command_id, idempotency_key = uuid4(), uuid4()
    repository = BoampObservationRepository()
    with session_factory.begin() as session:
        first = repository.persist(
            session=session,
            tenant_id=tenant_id,
            actor_id=actor_id,
            profile_id=profile_id,
            profile_version=1,
            command_id=command_id,
            idempotency_key=idempotency_key,
            correlation_id=uuid4(),
            request_hash=request_hash,
            started_at=NOW,
            completed_at=NOW,
            pages_read=1,
            truncated=False,
            scored_candidates=scored,
        )
    with session_factory.begin() as session:
        replay = repository.persist(
            session=session,
            tenant_id=tenant_id,
            actor_id=actor_id,
            profile_id=profile_id,
            profile_version=1,
            command_id=command_id,
            idempotency_key=idempotency_key,
            correlation_id=uuid4(),
            request_hash=request_hash,
            started_at=NOW,
            completed_at=NOW,
            pages_read=1,
            truncated=False,
            scored_candidates=scored,
        )
    assert first.replayed is False
    assert replay.replayed is True
    assert replay.run_id == first.run_id
    with session_factory() as session:
        assert session.scalar(sa.select(sa.func.count(DomainEventRecord.id))) == 1
        assert session.scalar(sa.select(sa.func.count(OutboxMessageRecord.id))) == 1


def test_repository_rejects_same_idempotency_with_different_hash(
    session_factory: sessionmaker[Session],
) -> None:
    tenant_id, actor_id, profile_id = _seed(session_factory)
    scored = _scored()
    repository = BoampObservationRepository()
    command_id, idempotency_key = uuid4(), uuid4()
    with session_factory.begin() as session:
        repository.persist(
            session=session,
            tenant_id=tenant_id,
            actor_id=actor_id,
            profile_id=profile_id,
            profile_version=1,
            command_id=command_id,
            idempotency_key=idempotency_key,
            correlation_id=None,
            request_hash="a" * 64,
            started_at=NOW,
            completed_at=NOW,
            pages_read=1,
            truncated=False,
            scored_candidates=scored,
        )
    with pytest.raises(BoampObservationPersistenceConflict), session_factory.begin() as session:
        repository.persist(
            session=session,
            tenant_id=tenant_id,
            actor_id=actor_id,
            profile_id=profile_id,
            profile_version=1,
            command_id=command_id,
            idempotency_key=idempotency_key,
            correlation_id=None,
            request_hash="b" * 64,
            started_at=NOW,
            completed_at=NOW,
            pages_read=1,
            truncated=False,
            scored_candidates=scored,
        )


def test_source_mode_migration_backfills_existing_runs_as_live(
    session_factory: sessionmaker[Session],
) -> None:
    tenant_id, actor_id, profile_id = _seed(session_factory)
    scored = _scored()
    repository = BoampObservationRepository()
    run_idempotency_key = uuid4()
    request_hash = ingestion_request_hash(
        profile_id=profile_id,
        profile_version=1,
        pages_read=1,
        truncated=False,
        scored_candidates=scored,
    )
    with session_factory.begin() as session:
        result = repository.persist(
            session=session,
            tenant_id=tenant_id,
            actor_id=actor_id,
            profile_id=profile_id,
            profile_version=1,
            command_id=uuid4(),
            idempotency_key=run_idempotency_key,
            correlation_id=None,
            request_hash=request_hash,
            started_at=NOW,
            completed_at=NOW,
            pages_read=1,
            truncated=False,
            scored_candidates=scored,
        )

    config = Config(str(ALEMBIC_INI))
    config.set_main_option("sqlalchemy.url", DATABASE_URL)
    command.downgrade(config, "20261003_0130")
    command.upgrade(config, "20261005_0132")

    with session_factory() as session:
        migrated_run = session.get(BoampIngestionRunRecord, result.run_id)
        migrated_link = session.scalar(
            sa.select(BoampIngestionObservationLinkRecord).where(
                BoampIngestionObservationLinkRecord.tenant_id == tenant_id,
                BoampIngestionObservationLinkRecord.ingestion_run_id == result.run_id,
            )
        )

    assert migrated_run is not None
    assert migrated_run.source_mode == "LIVE"
    assert migrated_link is not None
    assert migrated_link.source_contract_version is None
    assert migrated_link.source_response_sha256 is None


def test_synthetic_replay_round_trips_without_claiming_live_freshness(
    session_factory: sessionmaker[Session],
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    response_path = (
        Path(__file__).resolve().parents[1]
        / "fixtures/opportunity/boamp_synthetic_http_response.json"
    )
    response_bytes = response_path.read_bytes()
    source_response_sha256 = hashlib.sha256(response_bytes).hexdigest()
    client = httpx.Client(
        transport=httpx.MockTransport(
            lambda request: httpx.Response(
                200,
                content=response_bytes,
                headers={"content-type": "application/json"},
            )
        )
    )
    monkeypatch.setattr(
        _INGEST_SCRIPT,
        "BoampReadOnlySearch",
        lambda **_: BoampReadOnlySearch(client=client),
    )
    staging_path = tmp_path / "synthetic-staging.json"
    try:
        ingestion_result = _INGEST_SCRIPT.main(
            [
                "--keyword",
                "réhabilitation",
                "--now",
                NOW.isoformat(),
                "--output",
                str(staging_path),
            ]
        )
    finally:
        client.close()
    assert ingestion_result == 0
    staging_text = staging_path.read_text(encoding="utf-8")
    assert "must_not_be_staged" not in staging_text
    staging_report = json.loads(staging_text)
    staged_candidate = staging_report["candidates"][0]
    assert staged_candidate["source_contract_version"] == "BOAMP_EXPLORE_V2_1_ALLOWLIST_V1"
    assert staged_candidate["source_response_sha256"] == source_response_sha256
    candidates = _PERSIST_SCRIPT._read_candidates(staging_report)
    assert len(candidates) == 1
    candidate = candidates[0]

    altered_report = copy.deepcopy(staging_report)
    altered_report["candidates"][0]["source_response_sha256"] = "0" * 64
    with pytest.raises(ValueError, match="transport provenance fingerprint"):
        _PERSIST_SCRIPT._read_candidates(altered_report)

    tenant_id, actor_id, profile_id = _seed(session_factory)
    criteria = WatchProfileCriteria(keywords=("réhabilitation",), included_departments=("59",))
    scored = tuple(
        (item, BoampOpportunityScoringService().score(candidate=item, criteria=criteria, now=NOW))
        for item in candidates
    )
    replay_hash = ingestion_request_hash(
        profile_id=profile_id,
        profile_version=1,
        pages_read=1,
        truncated=False,
        scored_candidates=scored,
        source_mode="REPLAY",
    )
    assert replay_hash != ingestion_request_hash(
        profile_id=profile_id,
        profile_version=1,
        pages_read=1,
        truncated=False,
        scored_candidates=scored,
        source_mode="LIVE",
    )
    command_id, idempotency_key = uuid4(), uuid4()
    repository = BoampObservationRepository()
    with session_factory.begin() as session:
        first = repository.persist(
            session=session,
            tenant_id=tenant_id,
            actor_id=actor_id,
            profile_id=profile_id,
            profile_version=1,
            command_id=command_id,
            idempotency_key=idempotency_key,
            correlation_id=None,
            request_hash=replay_hash,
            started_at=NOW,
            completed_at=NOW,
            pages_read=1,
            truncated=False,
            scored_candidates=scored,
            source_mode="REPLAY",
        )
    with session_factory.begin() as session:
        replay = repository.persist(
            session=session,
            tenant_id=tenant_id,
            actor_id=actor_id,
            profile_id=profile_id,
            profile_version=1,
            command_id=command_id,
            idempotency_key=idempotency_key,
            correlation_id=None,
            request_hash=replay_hash,
            started_at=NOW,
            completed_at=NOW,
            pages_read=1,
            truncated=False,
            scored_candidates=scored,
            source_mode="REPLAY",
        )

    assert first.replayed is False
    assert replay.replayed is True
    assert replay.run_id == first.run_id
    assert replay.observation_ids == first.observation_ids
    live_hash = ingestion_request_hash(
        profile_id=profile_id,
        profile_version=1,
        pages_read=1,
        truncated=False,
        scored_candidates=scored,
        source_mode="LIVE",
    )
    with (
        pytest.raises(BoampObservationPersistenceConflict, match="idempotency"),
        session_factory.begin() as session,
    ):
        repository.persist(
            session=session,
            tenant_id=tenant_id,
            actor_id=actor_id,
            profile_id=profile_id,
            profile_version=1,
            command_id=command_id,
            idempotency_key=idempotency_key,
            correlation_id=None,
            request_hash=live_hash,
            started_at=NOW,
            completed_at=NOW,
            pages_read=1,
            truncated=False,
            scored_candidates=scored,
            source_mode="LIVE",
        )

    with session_factory() as session:
        run = session.get(BoampIngestionRunRecord, first.run_id)
        observation = session.get(BoampOpportunityObservationRecord, first.observation_ids[0])
        observation_link = session.scalar(
            sa.select(BoampIngestionObservationLinkRecord).where(
                BoampIngestionObservationLinkRecord.tenant_id == tenant_id,
                BoampIngestionObservationLinkRecord.ingestion_run_id == first.run_id,
                BoampIngestionObservationLinkRecord.observation_id == first.observation_ids[0],
            )
        )
        last_success = BoampQualificationRepository().last_successful_ingestion_at(
            session=session,
            tenant_id=tenant_id,
        )

    assert run is not None and run.source_mode == "REPLAY"
    assert observation is not None
    assert observation.source_notice_id == "SYNTH-EXP02-001"
    assert observation.fingerprint_sha256 == candidate.fingerprint()
    assert observation_link is not None
    assert observation_link.source_contract_version == "BOAMP_EXPLORE_V2_1_ALLOWLIST_V1"
    assert observation_link.source_response_sha256 == source_response_sha256
    assert observation.observed_at == NOW
    assert observation.publication_date != observation.observed_at.date()
    assert observation.response_deadline != observation.observed_at
    assert last_success is None
    source_status = _source_status(
        source_search=None,
        checked_at=NOW,
        last_success_at=last_success,
    )
    assert source_status.state == "UNKNOWN"
    assert source_status.last_success_at is None
    assert source_status.manual_entry_available is True


def test_synthetic_transport_replays_share_observation_and_keep_links_on_outage(
    session_factory: sessionmaker[Session],
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    response_path = (
        Path(__file__).resolve().parents[1]
        / "fixtures/opportunity/boamp_synthetic_http_response.json"
    )
    first_response = response_path.read_bytes()
    second_payload = json.loads(first_response)
    second_payload["results"][0]["donnees"]["private_fixture_marker"] = "different-ignored-value"
    second_response = json.dumps(second_payload, ensure_ascii=False, indent=2).encode("utf-8")
    response_bodies = (first_response, second_response)
    response_hashes = tuple(hashlib.sha256(body).hexdigest() for body in response_bodies)
    assert response_hashes[0] != response_hashes[1]

    staged_candidates = []
    for index, response_bytes in enumerate(response_bodies):
        client = httpx.Client(
            transport=httpx.MockTransport(
                lambda request, body=response_bytes: httpx.Response(
                    200,
                    content=body,
                    headers={"content-type": "application/json"},
                )
            )
        )
        monkeypatch.setattr(
            _INGEST_SCRIPT,
            "BoampReadOnlySearch",
            lambda client=client, **_: BoampReadOnlySearch(client=client),
        )
        staging_path = tmp_path / f"transport-replay-{index}.json"
        try:
            result = _INGEST_SCRIPT.main(
                [
                    "--keyword",
                    "réhabilitation",
                    "--now",
                    NOW.isoformat(),
                    "--output",
                    str(staging_path),
                ]
            )
        finally:
            client.close()
        assert result == 0
        staging_text = staging_path.read_text(encoding="utf-8")
        assert "private_fixture_marker" not in staging_text
        candidates = _PERSIST_SCRIPT._read_candidates(json.loads(staging_text))
        assert len(candidates) == 1
        staged_candidates.append(candidates[0])

    first_candidate, second_candidate = staged_candidates
    assert first_candidate.fingerprint() == second_candidate.fingerprint()
    assert first_candidate.source_response_sha256 == response_hashes[0]
    assert second_candidate.source_response_sha256 == response_hashes[1]
    assert first_candidate.transport_fingerprint() != second_candidate.transport_fingerprint()

    tenant_id, actor_id, profile_id = _seed(session_factory)
    criteria = WatchProfileCriteria(keywords=("réhabilitation",), included_departments=("59",))
    score_service = BoampOpportunityScoringService()
    repository = BoampObservationRepository()
    persisted_runs = []
    request_hashes = []
    for index, candidate in enumerate(staged_candidates):
        scored = (
            (candidate, score_service.score(candidate=candidate, criteria=criteria, now=NOW)),
        )
        request_hash = ingestion_request_hash(
            profile_id=profile_id,
            profile_version=1,
            pages_read=1,
            truncated=False,
            scored_candidates=scored,
            source_mode="REPLAY",
        )
        request_hashes.append(request_hash)
        completed_at = NOW + timedelta(minutes=index)
        with session_factory.begin() as session:
            persisted_runs.append(
                repository.persist(
                    session=session,
                    tenant_id=tenant_id,
                    actor_id=actor_id,
                    profile_id=profile_id,
                    profile_version=1,
                    command_id=uuid4(),
                    idempotency_key=uuid4(),
                    correlation_id=None,
                    request_hash=request_hash,
                    started_at=completed_at,
                    completed_at=completed_at,
                    pages_read=1,
                    truncated=False,
                    scored_candidates=scored,
                    source_mode="REPLAY",
                )
            )

    assert request_hashes[0] != request_hashes[1]
    assert all(result.replayed is False for result in persisted_runs)
    assert persisted_runs[0].run_id != persisted_runs[1].run_id
    assert persisted_runs[0].observation_ids == persisted_runs[1].observation_ids

    foreign_tenant_id, foreign_actor_id, foreign_profile_id = _seed(session_factory)
    foreign_scored = (
        (
            second_candidate,
            score_service.score(candidate=second_candidate, criteria=criteria, now=NOW),
        ),
    )
    foreign_hash = ingestion_request_hash(
        profile_id=foreign_profile_id,
        profile_version=1,
        pages_read=1,
        truncated=False,
        scored_candidates=foreign_scored,
        source_mode="REPLAY",
    )
    with session_factory.begin() as session:
        foreign_run = repository.persist(
            session=session,
            tenant_id=foreign_tenant_id,
            actor_id=foreign_actor_id,
            profile_id=foreign_profile_id,
            profile_version=1,
            command_id=uuid4(),
            idempotency_key=uuid4(),
            correlation_id=None,
            request_hash=foreign_hash,
            started_at=NOW,
            completed_at=NOW,
            pages_read=1,
            truncated=False,
            scored_candidates=foreign_scored,
            source_mode="REPLAY",
        )

    with session_factory() as session:
        observations = tuple(
            session.scalars(
                sa.select(BoampOpportunityObservationRecord).where(
                    BoampOpportunityObservationRecord.tenant_id == tenant_id,
                    BoampOpportunityObservationRecord.source_notice_id == "SYNTH-EXP02-001",
                )
            )
        )
        links = tuple(
            session.scalars(
                sa.select(BoampIngestionObservationLinkRecord)
                .where(
                    BoampIngestionObservationLinkRecord.tenant_id == tenant_id,
                    BoampIngestionObservationLinkRecord.ingestion_run_id.in_(
                        [result.run_id for result in persisted_runs]
                    ),
                )
                .order_by(BoampIngestionObservationLinkRecord.ingestion_run_id)
            )
        )
        last_success = BoampQualificationRepository().last_successful_ingestion_at(
            session=session,
            tenant_id=tenant_id,
        )

    assert len(observations) == 1
    assert observations[0].fingerprint_sha256 == first_candidate.fingerprint()
    assert observations[0].observed_at == NOW
    assert len(links) == 2
    assert {link.ingestion_run_id: link.source_response_sha256 for link in links} == {
        result.run_id: response_hashes[index] for index, result in enumerate(persisted_runs)
    }
    assert last_success is None

    class UnavailableSource:
        def search(self, *, text: str, limit: int = 20, offset: int = 0):
            raise BoampRegistryUnavailable("synthetic outage")

    source_status = _source_status(
        source_search=UnavailableSource(),
        checked_at=NOW + timedelta(minutes=2),
        last_success_at=last_success,
    )
    assert source_status.state == "UNAVAILABLE"
    assert source_status.last_success_at is None
    assert source_status.manual_entry_available is True
    with session_factory() as session:
        retained_links = tuple(
            session.scalars(
                sa.select(BoampIngestionObservationLinkRecord).where(
                    BoampIngestionObservationLinkRecord.tenant_id == tenant_id,
                    BoampIngestionObservationLinkRecord.ingestion_run_id.in_(
                        [result.run_id for result in persisted_runs]
                    ),
                )
            )
        )
    assert len(retained_links) == 2

    with session_factory() as session:
        projection = PatronBoampObservationService(repository=BoampQualificationRepository()).read(
            session=session,
            tenant_id=tenant_id,
            actor_id=actor_id,
            actor_kind="PATRON_ADMIN",
            now=NOW + timedelta(minutes=2),
        )

    assert len(projection) == 1
    captures = projection[0].source_captures
    assert len(captures) == 2
    assert [capture.ingestion_run_id for capture in captures] == [
        result.run_id for result in persisted_runs
    ]
    assert foreign_run.run_id not in {capture.ingestion_run_id for capture in captures}
    assert [capture.source_mode for capture in captures] == ["REPLAY", "REPLAY"]
    assert [capture.source_response_sha256 for capture in captures] == list(response_hashes)
