from datetime import UTC, date, datetime, timedelta
from uuid import UUID, uuid4

import pytest
import sqlalchemy as sa
from app.modules.case.infrastructure.models.case import CaseRecord
from app.modules.case.infrastructure.repositories import SqlAlchemyCaseRepository
from app.modules.dce.infrastructure.repositories import SqlAlchemyConsultationRepository
from app.modules.opportunity.application.boamp_case_creation import (
    BoampAwareCreateCaseHandler,
    BoampCaseCreationCommand,
    BoampCaseCreationService,
)
from app.modules.opportunity.application.boamp_qualification import (
    PatronBoampObservationService,
)
from app.modules.opportunity.infrastructure.boamp_qualification_repository import (
    BoampQualificationRepository,
)
from app.modules.opportunity.infrastructure.observation_models import (
    BoampOpportunityObservationRecord,
    BoampOpportunityQualificationRecord,
)
from app.platform.events.dispatcher import CommandContext, CommandDispatcher, CommandExecutionError
from app.platform.persistence.models import (
    CommandReceiptRecord,
    DomainEventRecord,
    OutboxMessageRecord,
    TenantRecord,
)
from app.platform.security.models import IdentityRecord, TenantMembershipRecord
from sqlalchemy.orm import Session, sessionmaker

pytestmark = [pytest.mark.db, pytest.mark.process]
NOW = datetime(2026, 8, 25, 12, 0, tzinfo=UTC)


@pytest.mark.parametrize(
    "decision,reason", [("REJECTED", "NOT_RELEVANT"), ("SNOOZED", "INSUFFICIENT_PUBLIC_DATA")]
)
def test_latest_human_decision_cannot_be_bypassed_by_an_older_qualification(
    database_engine, session_factory, decision, reason
):
    tenant, actor, member, observation = _seed_signal(database_engine)
    with session_factory.begin() as session:
        session.add(
            BoampOpportunityQualificationRecord(
                id=uuid4(),
                tenant_id=tenant,
                observation_id=observation,
                actor_id=actor,
                decision=decision,
                reason_code=reason,
                score_snapshot=92,
                score_version="BOAMP_PUBLIC_V1",
                command_id=uuid4(),
                idempotency_key=uuid4(),
                correlation_id=None,
                created_at=datetime.now(UTC) + timedelta(seconds=1),
            )
        )
    service = BoampCaseCreationService(
        session_factory=session_factory, dispatcher=_dispatcher(session_factory)
    )
    with pytest.raises((ValueError, CommandExecutionError)):
        service.create(
            context=_context(tenant_id=tenant, identity_id=actor, membership_id=member),
            command=_command(observation_id=observation),
            now=NOW,
        )
    with session_factory() as session:
        assert (
            session.scalar(
                sa.select(sa.func.count())
                .select_from(CaseRecord)
                .where(CaseRecord.tenant_id == tenant)
            )
            == 0
        )


def test_new_snapshot_of_same_notice_does_not_create_a_second_case(
    database_engine, session_factory
):
    tenant, actor, member, observation = _seed_signal(database_engine)
    context = _context(tenant_id=tenant, identity_id=actor, membership_id=member)
    service = BoampCaseCreationService(
        session_factory=session_factory, dispatcher=_dispatcher(session_factory)
    )
    service.create(context=context, command=_command(observation_id=observation), now=NOW)
    with session_factory.begin() as session:
        original = session.get(BoampOpportunityObservationRecord, observation)
        fields = {c.name: getattr(original, c.name) for c in original.__table__.columns}
        fields.update(
            id=uuid4(),
            fingerprint_sha256="c" * 64,
            title="Nouvelle capture synthétique du même avis",
        )
        session.add(BoampOpportunityObservationRecord(**fields))
        session.add(
            BoampOpportunityQualificationRecord(
                id=uuid4(),
                tenant_id=tenant,
                observation_id=fields["id"],
                actor_id=actor,
                decision="QUALIFIED",
                reason_code="RELEVANT_PUBLIC_SIGNAL",
                score_snapshot=92,
                score_version="BOAMP_PUBLIC_V1",
                command_id=uuid4(),
                idempotency_key=uuid4(),
                correlation_id=None,
            )
        )
    with pytest.raises(CommandExecutionError):
        service.create(context=context, command=_command(observation_id=fields["id"]), now=NOW)
    with session_factory() as session:
        assert (
            session.scalar(
                sa.select(sa.func.count())
                .select_from(CaseRecord)
                .where(CaseRecord.tenant_id == tenant)
            )
            == 1
        )


def _dispatcher(session_factory: sessionmaker[Session]) -> CommandDispatcher:
    return CommandDispatcher(
        session_factory=session_factory,
        handlers={
            "CreateCase": BoampAwareCreateCaseHandler(
                repository_factory=SqlAlchemyCaseRepository,
                consultation_reader_factory=SqlAlchemyConsultationRepository,
            )
        },
    )


def _seed_signal(
    engine: sa.Engine,
    *,
    qualified: bool = True,
) -> tuple[UUID, UUID, UUID, UUID]:
    tenant_id = uuid4()
    identity_id = uuid4()
    membership_id = uuid4()
    observation_id = uuid4()
    with engine.begin() as connection:
        connection.execute(
            sa.insert(TenantRecord).values(
                id=tenant_id,
                slug=f"boamp-case-{tenant_id.hex[:12]}",
                lifecycle="ACTIVE",
            )
        )
        connection.execute(
            sa.insert(IdentityRecord).values(
                id=identity_id,
                email_normalized=f"patron-{identity_id.hex[:12]}@example.test",
                lifecycle="ACTIVE",
                email_verified_at=NOW,
            )
        )
        connection.execute(
            sa.insert(TenantMembershipRecord).values(
                id=membership_id,
                tenant_id=tenant_id,
                identity_id=identity_id,
                role="PATRON_ADMIN",
                state="ACTIVE",
                activated_at=NOW,
                revoked_at=None,
            )
        )
        connection.execute(
            sa.insert(BoampOpportunityObservationRecord).values(
                id=observation_id,
                tenant_id=tenant_id,
                source="BOAMP",
                source_notice_id=f"A-{observation_id.hex[:12]}",
                fingerprint_sha256="a" * 64,
                title="Réhabilitation école publique",
                publication_date=date(2026, 8, 20),
                response_deadline=NOW + timedelta(days=14),
                department_codes=["59"],
                market_types=["TRAVAUX"],
                source_status="EN_COURS",
                score_version="BOAMP_PUBLIC_V1",
                score=92,
                score_explanation_json={"public_relevance": 92},
                score_explanation_sha256="b" * 64,
                observed_at=NOW,
            )
        )
        if qualified:
            connection.execute(
                sa.insert(BoampOpportunityQualificationRecord).values(
                    id=uuid4(),
                    tenant_id=tenant_id,
                    observation_id=observation_id,
                    actor_id=identity_id,
                    decision="QUALIFIED",
                    reason_code="RELEVANT_PUBLIC_SIGNAL",
                    score_snapshot=92,
                    score_version="BOAMP_PUBLIC_V1",
                    command_id=uuid4(),
                    idempotency_key=uuid4(),
                    correlation_id=None,
                )
            )
    return tenant_id, identity_id, membership_id, observation_id


def _context(*, tenant_id: UUID, identity_id: UUID, membership_id: UUID) -> CommandContext:
    return CommandContext(
        tenant_id=tenant_id,
        actor_id=identity_id,
        actor_kind="PATRON_ADMIN",
        received_at=NOW,
        identity_id=identity_id,
        membership_id=membership_id,
        session_id=uuid4(),
        correlation_id=uuid4(),
    )


def _command(
    *, observation_id: UUID, idempotency_key: UUID | None = None
) -> BoampCaseCreationCommand:
    return BoampCaseCreationCommand(
        observation_id=observation_id,
        command_id=uuid4(),
        idempotency_key=idempotency_key or uuid4(),
        correlation_id=uuid4(),
    )


def test_qualified_signal_creates_one_case_and_replays_durably(
    database_engine: sa.Engine,
    session_factory: sessionmaker[Session],
) -> None:
    tenant_id, identity_id, membership_id, observation_id = _seed_signal(database_engine)
    service = BoampCaseCreationService(
        session_factory=session_factory,
        dispatcher=_dispatcher(session_factory),
    )
    context = _context(
        tenant_id=tenant_id,
        identity_id=identity_id,
        membership_id=membership_id,
    )
    command = _command(observation_id=observation_id)

    first = service.create(context=context, command=command, now=NOW)
    replay = service.create(context=context, command=command, now=NOW)

    assert first.status == "SUCCEEDED"
    assert first.replayed is False
    assert replay.replayed is True
    assert replay.event_ids == first.event_ids
    assert len(first.aggregate_refs) == 1
    case_id = UUID(str(first.aggregate_refs[0]["aggregate_id"]))
    with session_factory() as session:
        case = session.get(CaseRecord, case_id)
        assert case is not None
        assert case.tenant_id == tenant_id
        assert case.business_origin == "OPPORTUNITY"
        assert case.origin_reference_id == observation_id
        assert (
            session.scalar(
                sa.select(sa.func.count(CommandReceiptRecord.id)).where(
                    CommandReceiptRecord.tenant_id == tenant_id,
                    CommandReceiptRecord.idempotency_key == command.idempotency_key,
                )
            )
            == 1
        )
        assert (
            session.scalar(
                sa.select(sa.func.count(DomainEventRecord.id)).where(
                    DomainEventRecord.tenant_id == tenant_id,
                    DomainEventRecord.event_type == "CASE_CREATED",
                )
            )
            == 1
        )
        assert (
            session.scalar(
                sa.select(sa.func.count(OutboxMessageRecord.id)).where(
                    OutboxMessageRecord.tenant_id == tenant_id,
                    OutboxMessageRecord.event_id == UUID(first.event_ids[0]),
                )
            )
            == 1
        )

        projection = PatronBoampObservationService(repository=BoampQualificationRepository()).read(
            session=session,
            tenant_id=tenant_id,
            actor_id=identity_id,
            actor_kind="PATRON_ADMIN",
            now=NOW,
        )[0]
        assert projection.p0_state.value == "TARGETED"
        assert projection.p1_state.value == "OPEN_WITH_UNKNOWNS"
        assert projection.p1_case_id == case_id
        assert projection.lot_scope_state.value == "UNKNOWN"
        assert projection.lot_scope_source == "BOAMP"
        assert {unknown["code"] for unknown in projection.unknowns} == {
            "LOT_SCOPE",
            "DCE_NOT_RECEIVED",
        }


def test_case_creation_requires_a_qualified_signal(
    database_engine: sa.Engine,
    session_factory: sessionmaker[Session],
) -> None:
    tenant_id, identity_id, membership_id, observation_id = _seed_signal(
        database_engine,
        qualified=False,
    )
    service = BoampCaseCreationService(
        session_factory=session_factory,
        dispatcher=_dispatcher(session_factory),
    )

    with pytest.raises(ValueError, match="BOAMP_QUALIFICATION_REQUIRED"):
        service.create(
            context=_context(
                tenant_id=tenant_id,
                identity_id=identity_id,
                membership_id=membership_id,
            ),
            command=_command(observation_id=observation_id),
            now=NOW,
        )

    with session_factory() as session:
        assert (
            session.scalar(
                sa.select(sa.func.count(CaseRecord.id)).where(CaseRecord.tenant_id == tenant_id)
            )
            == 0
        )
        assert (
            session.scalar(
                sa.select(sa.func.count(CommandReceiptRecord.id)).where(
                    CommandReceiptRecord.tenant_id == tenant_id
                )
            )
            == 0
        )


def test_same_qualified_signal_with_new_idempotency_key_cannot_duplicate_case(
    database_engine: sa.Engine,
    session_factory: sessionmaker[Session],
) -> None:
    tenant_id, identity_id, membership_id, observation_id = _seed_signal(database_engine)
    service = BoampCaseCreationService(
        session_factory=session_factory,
        dispatcher=_dispatcher(session_factory),
    )
    context = _context(
        tenant_id=tenant_id,
        identity_id=identity_id,
        membership_id=membership_id,
    )

    first = service.create(
        context=context,
        command=_command(observation_id=observation_id),
        now=NOW,
    )
    with pytest.raises(CommandExecutionError) as failure:
        service.create(
            context=context,
            command=_command(observation_id=observation_id),
            now=NOW,
        )

    assert isinstance(failure.value.__cause__, ValueError)
    assert str(failure.value.__cause__) == "DUPLICATE_FUNCTIONAL_IDENTITY"
    with session_factory() as session:
        assert (
            session.scalar(
                sa.select(sa.func.count(CaseRecord.id)).where(CaseRecord.tenant_id == tenant_id)
            )
            == 1
        )
        assert (
            session.scalar(
                sa.select(sa.func.count(DomainEventRecord.id)).where(
                    DomainEventRecord.tenant_id == tenant_id,
                    DomainEventRecord.event_type == "CASE_CREATED",
                )
            )
            == 1
        )
        case = session.get(CaseRecord, UUID(str(first.aggregate_refs[0]["aggregate_id"])))
        assert case is not None
        assert case.business_origin == "OPPORTUNITY"
        assert case.origin_reference_id == observation_id


def test_case_creation_does_not_cross_tenant_boundary(
    database_engine: sa.Engine,
    session_factory: sessionmaker[Session],
) -> None:
    source_tenant, _identity_id, _membership_id, observation_id = _seed_signal(database_engine)
    foreign_tenant, foreign_identity, foreign_membership, _ = _seed_signal(database_engine)
    service = BoampCaseCreationService(
        session_factory=session_factory,
        dispatcher=_dispatcher(session_factory),
    )

    with pytest.raises(PermissionError, match="NOT_FOUND_OR_FORBIDDEN"):
        service.create(
            context=_context(
                tenant_id=foreign_tenant,
                identity_id=foreign_identity,
                membership_id=foreign_membership,
            ),
            command=_command(observation_id=observation_id),
            now=NOW,
        )

    with session_factory() as session:
        assert (
            session.scalar(
                sa.select(sa.func.count(CaseRecord.id)).where(
                    CaseRecord.tenant_id.in_([source_tenant, foreign_tenant])
                )
            )
            == 0
        )


def direct_case(observation, kind="CUSTOM", rationale="Origine synthétique déclarée."):
    from app.modules.case.application.commands import CreateCaseCommand

    return CreateCaseCommand(
        command_id=uuid4(),
        idempotency_key=uuid4(),
        case_id=uuid4(),
        title="Affaire synthétique",
        object_description="Périmètre à relire sur pièces.",
        scope_kind=kind,
        lot_numbers=("01",) if kind == "SINGLE_LOT" else (),
        scope_justification="Source publique et lot déclaré, aucune éligibilité présumée."
        if kind == "CUSTOM"
        else None,
        origin_kind="OPPORTUNITY",
        origin_reference_id=observation,
        origin_rationale=rationale,
    )


def test_frozen_p0_evidence_survives_maximum_origin_rationale(database_engine, session_factory):
    tenant, actor, member, observation = _seed_signal(database_engine)
    command = direct_case(observation, rationale="x" * 2000)
    _dispatcher(session_factory).dispatch(
        command=command, context=_context(tenant_id=tenant, identity_id=actor, membership_id=member)
    )
    with session_factory() as session:
        row = session.get(CaseRecord, command.case_id)
        assert "RELEVANT_PUBLIC_SIGNAL" in row.origin_rationale
        assert "a" * 64 in row.origin_rationale and str(observation) in row.origin_rationale
        assert len(row.origin_rationale) <= 2000


@pytest.mark.parametrize("first_kind", ["CUSTOM", "SINGLE_LOT"])
def test_unknown_notice_scope_does_not_prove_a_second_scope_disjoint(
    database_engine, session_factory, first_kind
):
    tenant, actor, member, observation = _seed_signal(database_engine)
    ctx = _context(tenant_id=tenant, identity_id=actor, membership_id=member)
    dispatcher = _dispatcher(session_factory)
    dispatcher.dispatch(command=direct_case(observation, first_kind), context=ctx)
    with pytest.raises(CommandExecutionError):
        dispatcher.dispatch(
            command=direct_case(observation, "SINGLE_LOT" if first_kind == "CUSTOM" else "CUSTOM"),
            context=ctx,
        )


def test_legacy_receipt_replay_is_preserved_after_later_rejection_and_revocation(
    database_engine, session_factory
):
    from typing import cast
    from uuid import NAMESPACE_URL, uuid5

    from app.modules.case.application.handlers import CreateCaseHandler

    tenant, actor, member, observation = _seed_signal(database_engine)
    ctx = _context(tenant_id=tenant, identity_id=actor, membership_id=member)
    request = _command(observation_id=observation)

    class Capture:
        def dispatch(self, *, command, context):
            self.command = command

    capture = Capture()
    BoampCaseCreationService(
        session_factory=session_factory, dispatcher=cast(CommandDispatcher, capture)
    ).create(context=ctx, command=request, now=NOW)
    legacy = capture.command.model_copy(
        update={"case_id": uuid5(NAMESPACE_URL, f"smart-ao:case:{request.idempotency_key}")}
    )
    old = CommandDispatcher(
        session_factory=session_factory,
        handlers={
            "CreateCase": CreateCaseHandler(
                repository_factory=SqlAlchemyCaseRepository,
                consultation_reader_factory=SqlAlchemyConsultationRepository,
            )
        },
    ).dispatch(command=legacy, context=ctx)
    service = BoampCaseCreationService(
        session_factory=session_factory, dispatcher=_dispatcher(session_factory)
    )
    with session_factory.begin() as s:
        s.add(
            BoampOpportunityQualificationRecord(
                id=uuid4(),
                tenant_id=tenant,
                observation_id=observation,
                actor_id=actor,
                decision="REJECTED",
                reason_code="NOT_RELEVANT",
                score_snapshot=92,
                score_version="BOAMP_PUBLIC_V1",
                command_id=uuid4(),
                idempotency_key=uuid4(),
                correlation_id=None,
                created_at=datetime.now(UTC) + timedelta(seconds=1),
            )
        )
    replay = service.create(context=ctx, command=request, now=NOW)
    assert (
        replay.replayed
        and replay.aggregate_refs == old.aggregate_refs
        and replay.event_ids == old.event_ids
    )
    with session_factory.begin() as s:
        membership = s.get(TenantMembershipRecord, member)
        membership.state = "REVOKED"
        membership.revoked_at = datetime.now(UTC)
    with pytest.raises(PermissionError):
        service.create(context=ctx, command=request, now=NOW)


def test_two_snapshot_conversions_serialize_on_the_notice(database_engine, session_factory):
    from concurrent.futures import ThreadPoolExecutor

    tenant, actor, member, observation = _seed_signal(database_engine)
    with session_factory.begin() as s:
        original = s.get(BoampOpportunityObservationRecord, observation)
        fields = {c.name: getattr(original, c.name) for c in original.__table__.columns}
        fields.update(id=uuid4(), fingerprint_sha256="d" * 64)
        s.add(BoampOpportunityObservationRecord(**fields))
        s.flush()
        s.add(
            BoampOpportunityQualificationRecord(
                id=uuid4(),
                tenant_id=tenant,
                observation_id=fields["id"],
                actor_id=actor,
                decision="QUALIFIED",
                reason_code="RELEVANT_PUBLIC_SIGNAL",
                score_snapshot=92,
                score_version="BOAMP_PUBLIC_V1",
                command_id=uuid4(),
                idempotency_key=uuid4(),
                correlation_id=None,
            )
        )
    ctx = _context(tenant_id=tenant, identity_id=actor, membership_id=member)
    service = BoampCaseCreationService(
        session_factory=session_factory, dispatcher=_dispatcher(session_factory)
    )

    def create(source):
        try:
            service.create(context=ctx, command=_command(observation_id=source), now=NOW)
            return "CREATED"
        except CommandExecutionError as e:
            assert (
                isinstance(e.__cause__, ValueError)
                and str(e.__cause__) == "DUPLICATE_FUNCTIONAL_IDENTITY"
            )
            return "DUPLICATE"

    with ThreadPoolExecutor(max_workers=2) as pool:
        assert sorted(pool.map(create, [observation, fields["id"]])) == ["CREATED", "DUPLICATE"]
    with session_factory() as s:
        states = BoampQualificationRepository().states_for_observations(
            session=s, tenant_id=tenant, observation_ids=(observation, fields["id"])
        )
        assert states[observation].case_id == states[fields["id"]].case_id
        first = states[observation].latest_qualification
        second = states[fields["id"]].latest_qualification
        assert first is not None and second is not None
        assert first.observation_id == observation
        assert second.observation_id == fields["id"]


def test_generic_unverified_opportunity_refs_do_not_disclose_foreign_boamp_data(
    database_engine, session_factory
):
    tenant, actor, member, _ = _seed_signal(database_engine)
    foreign, _, _, foreign_observation = _seed_signal(database_engine)
    ctx = _context(tenant_id=tenant, identity_id=actor, membership_id=member)
    for source in (foreign_observation, uuid4()):
        command = direct_case(source)
        _dispatcher(session_factory).dispatch(command=command, context=ctx)
        with session_factory() as s:
            row = s.get(CaseRecord, command.case_id)
            assert (
                row.tenant_id == tenant and row.origin_rationale == "Origine synthétique déclarée."
            )
            assert row.title == "Affaire synthétique"


def test_optional_origin_rationale_still_freezes_p0_proof(database_engine, session_factory):
    tenant, actor, member, observation = _seed_signal(database_engine)
    command = direct_case(observation, rationale=None)
    _dispatcher(session_factory).dispatch(
        command=command, context=_context(tenant_id=tenant, identity_id=actor, membership_id=member)
    )
    with session_factory() as s:
        row = s.get(CaseRecord, command.case_id)
        assert "RELEVANT_PUBLIC_SIGNAL" in row.origin_rationale and "a" * 64 in row.origin_rationale
