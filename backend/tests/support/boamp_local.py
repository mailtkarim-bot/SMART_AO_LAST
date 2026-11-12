"""Native local BOAMP path with an in-memory source and real test authentication."""

import hashlib
import json
from dataclasses import replace
from types import SimpleNamespace
from uuid import uuid4

import sqlalchemy as sa
from app.modules.market_watch.application.ports import BoampNotice
from app.modules.opportunity.application.boamp_ingestion import BoampOpportunityIngestionService
from app.modules.opportunity.application.boamp_scoring import BoampOpportunityScoringService
from app.modules.opportunity.domain.watch_profile import WatchProfileCriteria
from app.modules.opportunity.infrastructure.boamp_observation_repository import (
    BoampObservationRepository,
    ingestion_request_hash,
)
from app.modules.opportunity.infrastructure.models import (
    OpportunityWatchProfileRecord,
    OpportunityWatchProfileVersionRecord,
)
from app.modules.opportunity.infrastructure.observation_models import (
    BoampOpportunityObservationRecord,
)
from app.platform.persistence.models import TenantRecord
from app.platform.security.models import IdentityRecord, TenantMembershipRecord

from tests.api import test_collaborator_capability_api as auth
from tests.db.test_regulatory_profile_persistence import _actor


def local_boamp(session_factory, monkeypatch):
    now = auth.NOW
    tenant, identity, membership, profile = uuid4(), uuid4(), uuid4(), uuid4()
    criteria = WatchProfileCriteria(keywords=("réhabilitation",))
    snapshot = criteria.snapshot()
    digest = hashlib.sha256(
        json.dumps(snapshot, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    with session_factory.begin() as s:
        s.add(TenantRecord(id=tenant, slug="boamp-local-" + tenant.hex, lifecycle="ACTIVE"))
        s.add(
            IdentityRecord(
                id=identity,
                email_normalized=identity.hex + "@example.test",
                lifecycle="ACTIVE",
                email_verified_at=now,
            )
        )
        s.flush()
        s.add(
            TenantMembershipRecord(
                id=membership,
                tenant_id=tenant,
                identity_id=identity,
                role="PATRON_ADMIN",
                state="ACTIVE",
                activated_at=now,
                revoked_at=None,
            )
        )
        s.add(
            OpportunityWatchProfileRecord(
                id=profile,
                tenant_id=tenant,
                aggregate_revision=0,
                name="Veille synthétique",
                state="ACTIVE",
                current_version=1,
                actor_id=identity,
                command_id=uuid4(),
                idempotency_key=uuid4(),
                correlation_id=None,
            )
        )
        s.flush()
        s.add(
            OpportunityWatchProfileVersionRecord(
                id=uuid4(),
                tenant_id=tenant,
                profile_id=profile,
                version_number=1,
                name="Veille synthétique",
                criteria_json=snapshot,
                criteria_sha256=digest,
                actor_id=identity,
                command_id=uuid4(),
                idempotency_key=uuid4(),
                correlation_id=None,
            )
        )
    notice_id = "SYNTHETIC-" + uuid4().hex
    title = "Réhabilitation école synthétique"
    raw = {
        "notice_id": notice_id,
        "title": title,
        "publication_date": now.date().isoformat(),
        "response_deadline": None,
        "department_codes": ["59"],
        "market_types": ["TRAVAUX"],
        "status": "EN_COURS",
    }
    source_hash = hashlib.sha256(json.dumps(raw, sort_keys=True).encode()).hexdigest()
    notice = BoampNotice(
        notice_id=notice_id,
        title=title,
        publication_date=now.date(),
        response_deadline=None,
        department_codes=("59",),
        market_types=("TRAVAUX",),
        status="EN_COURS",
        source_contract_version="SYNTHETIC_PORT_V1",
        source_response_sha256=source_hash,
    )

    class Source:
        calls = 0

        def search(self, *, text, limit=20, offset=0):
            self.calls += 1
            return (notice,) if offset == 0 else ()

    source = Source()
    report = BoampOpportunityIngestionService(search_port=source).ingest(criteria=criteria, now=now)
    scored = tuple(
        (c, BoampOpportunityScoringService().score(candidate=c, criteria=criteria, now=now))
        for c in report.candidates
    )
    assert len(scored) == 1
    with session_factory.begin() as s:
        run = BoampObservationRepository().persist(
            session=s,
            tenant_id=tenant,
            actor_id=identity,
            profile_id=profile,
            profile_version=1,
            command_id=uuid4(),
            idempotency_key=uuid4(),
            correlation_id=None,
            request_hash=ingestion_request_hash(
                profile_id=profile,
                profile_version=1,
                pages_read=report.pages_read,
                truncated=report.truncated,
                scored_candidates=scored,
                source_mode="REPLAY",
            ),
            started_at=now,
            completed_at=now,
            pages_read=report.pages_read,
            truncated=report.truncated,
            scored_candidates=scored,
            source_mode="REPLAY",
        )
    actor = replace(
        _actor(tenant, uuid4()),
        actor_id=identity,
        identity_id=identity,
        membership_id=membership,
        session_id=uuid4(),
        authenticated_at=now,
        mfa_verified_at=now,
    )
    auth._auth_session(session_factory, actor)
    original = auth.create_app

    class NoLive:
        def search(self, **kwargs):
            raise RuntimeError("SYNTHETIC_ONLY_NO_LIVE")

    def create(**kwargs):
        kwargs["public_notice_search"] = NoLive()
        return original(**kwargs)

    monkeypatch.setattr(auth, "create_app", create)
    client, tokens = auth._client(session_factory)
    with session_factory() as s:
        observation = s.scalar(
            sa.select(BoampOpportunityObservationRecord).where(
                BoampOpportunityObservationRecord.tenant_id == tenant
            )
        )
    return SimpleNamespace(
        client=client,
        headers=auth._headers(tokens, actor),
        actor=actor,
        observation=observation,
        raw=raw,
        source_hash=source_hash,
        ingestion=run,
        source=source,
    )
