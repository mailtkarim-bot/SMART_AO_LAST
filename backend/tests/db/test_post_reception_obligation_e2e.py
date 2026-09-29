# ruff: noqa: E501, I001
from datetime import UTC, date, datetime
from types import SimpleNamespace
from uuid import uuid4

import pytest
import sqlalchemy as sa
from sqlalchemy.orm import Session

from app.modules.pricing.application.post_reception_obligation_commands import (
    RecordPostReceptionObligationCommand,
)
from app.modules.pricing.application.contract_execution_evidence_commands import (
    RecordContractExecutionEvidenceCommand,
)
from app.modules.pricing.application.contract_execution_evidence_handler import (
    contract_execution_evidence_handlers,
)
from app.modules.pricing.application.contract_execution_evidence_read_handler import (
    ContractExecutionEvidenceReadService,
)
from app.modules.pricing.infrastructure.models.contract_execution_evidence import (
    ContractExecutionEvidenceRecord,
)
from app.modules.pricing.application.post_reception_obligation_handler import (
    post_reception_obligation_handlers,
)
from app.modules.pricing.application.post_reception_obligation_transition_commands import (
    TransitionPostReceptionObligationCommand,
)
from app.modules.pricing.application.post_reception_obligation_transition_handler import (
    post_reception_obligation_transition_handlers,
)
from app.modules.pricing.infrastructure.models.post_reception_obligation import (
    PostReceptionObligationRecord,
)
from app.modules.pricing.infrastructure.models.post_reception_obligation_transition import (
    PostReceptionObligationTransitionRecord,
)
from app.modules.pricing.application.post_reception_obligation_read_handler import (
    PostReceptionObligationReadService,
)
from app.platform.events.dispatcher import CommandContext, CommandDispatcher, CommandExecutionError
from app.platform.persistence.models import TenantRecord
from app.platform.security.context import ActorKind
from tests.db.test_regulatory_profile_persistence import _case


def test_reserve_lifting_links_only_to_same_case_reception_with_reservations(
    database_engine, session_factory
) -> None:
    tenant_id, foreign_tenant_id, case_id, foreign_case_id, actor_id = (
        uuid4(),
        uuid4(),
        uuid4(),
        uuid4(),
        uuid4(),
    )
    with Session(database_engine) as session:
        session.add_all(
            [
                TenantRecord(id=tenant_id, slug=f"rec-{tenant_id.hex[:10]}", lifecycle="ACTIVE"),
                TenantRecord(
                    id=foreign_tenant_id,
                    slug=f"rec-{foreign_tenant_id.hex[:10]}",
                    lifecycle="ACTIVE",
                ),
            ]
        )
        session.flush()
        session.add_all(
            [
                _case(tenant_id=tenant_id, case_id=case_id, marker="r"),
                _case(tenant_id=foreign_tenant_id, case_id=foreign_case_id, marker="s"),
            ]
        )
        session.commit()

    receipt_dispatcher = CommandDispatcher(
        session_factory=session_factory, handlers=contract_execution_evidence_handlers()
    )
    obligation_dispatcher = CommandDispatcher(
        session_factory=session_factory, handlers=post_reception_obligation_handlers()
    )
    now = datetime.now(tz=UTC)

    def context(tenant, case):
        return CommandContext(
            tenant_id=tenant,
            actor_id=actor_id,
            actor_kind="PATRON_ADMIN",
            received_at=now,
            identity_id=actor_id,
            membership_id=uuid4(),
            session_id=uuid4(),
            case_id=case,
            correlation_id=uuid4(),
        )

    receipt_id = uuid4()
    receipt = RecordContractExecutionEvidenceCommand(
        command_id=uuid4(),
        idempotency_key=uuid4(),
        act_id=receipt_id,
        case_id=case_id,
        act_kind="WORK_RECEPTION",
        reception_outcome="UNDER_RESERVATIONS",
        summary="PV avec réserves sur le lot 2",
        source_refs=("ccap://clause/24",),
        evidence_refs=("document://pv-lot-2",),
    )
    receipt_dispatcher.dispatch(command=receipt, context=context(tenant_id, case_id))
    reserve = RecordPostReceptionObligationCommand(
        command_id=uuid4(),
        idempotency_key=uuid4(),
        obligation_id=uuid4(),
        case_id=case_id,
        obligation_type="RESERVES_LIFTING",
        origin_reception_act_id=receipt_id,
        summary="Lever la réserve sur le lot 2",
        source_refs=("ccap://clause/24",),
    )
    created = obligation_dispatcher.dispatch(command=reserve, context=context(tenant_id, case_id))
    replay = obligation_dispatcher.dispatch(command=reserve, context=context(tenant_id, case_id))
    assert replay.replayed
    assert created.result_code == "POST_RECEPTION_OBLIGATION_RECORDED"

    without_reservations_id = uuid4()
    without_reservations = RecordContractExecutionEvidenceCommand(
        command_id=uuid4(),
        idempotency_key=uuid4(),
        act_id=without_reservations_id,
        case_id=case_id,
        act_kind="WORK_RECEPTION",
        reception_outcome="WITHOUT_RESERVATIONS",
        summary="PV déclaré sans réserves",
        source_refs=("ccap://clause/24",),
        evidence_refs=("document://pv-final",),
    )
    receipt_dispatcher.dispatch(command=without_reservations, context=context(tenant_id, case_id))
    with pytest.raises(CommandExecutionError, match="POST_RECEPTION_RECEIPT_NOT_ELIGIBLE"):
        obligation_dispatcher.dispatch(
            command=reserve.model_copy(
                update={
                    "command_id": uuid4(),
                    "idempotency_key": uuid4(),
                    "obligation_id": uuid4(),
                    "origin_reception_act_id": without_reservations_id,
                }
            ),
            context=context(tenant_id, case_id),
        )

    foreign_receipt_id = uuid4()
    foreign_receipt = RecordContractExecutionEvidenceCommand(
        command_id=uuid4(),
        idempotency_key=uuid4(),
        act_id=foreign_receipt_id,
        case_id=foreign_case_id,
        act_kind="WORK_RECEPTION",
        reception_outcome="WITH_RESERVATIONS",
        summary="PV autre organisation",
        source_refs=("ccap://clause/24",),
        evidence_refs=("document://foreign-pv",),
    )
    receipt_dispatcher.dispatch(
        command=foreign_receipt, context=context(foreign_tenant_id, foreign_case_id)
    )
    with pytest.raises(
        CommandExecutionError, match="POST_RECEPTION_RECEIPT_NOT_FOUND_OR_FORBIDDEN"
    ):
        obligation_dispatcher.dispatch(
            command=reserve.model_copy(
                update={
                    "command_id": uuid4(),
                    "idempotency_key": uuid4(),
                    "obligation_id": uuid4(),
                    "origin_reception_act_id": foreign_receipt_id,
                }
            ),
            context=context(tenant_id, case_id),
        )

    with Session(database_engine) as session:
        old_obligation = PostReceptionObligationRecord(
            id=uuid4(),
            tenant_id=tenant_id,
            case_id=case_id,
            obligation_type="RESERVES_LIFTING",
            summary="Ancienne réserve non reliée",
            source_refs_json=["ccap://clause/20"],
            origin_reception_act_id=None,
            due_date=None,
            resource_note=None,
            cost_estimate_note=None,
            fulfillment_proof_refs_json=[],
            sanction_ref=None,
            status="REVIEW_REQUIRED",
            actor_id=actor_id,
        )
        old_obligation_id = old_obligation.id
        session.add(old_obligation)
        legacy_receipt = ContractExecutionEvidenceRecord(
            id=uuid4(),
            tenant_id=tenant_id,
            case_id=case_id,
            case_dce_version_id_at_recording=None,
            contract_instrument_version_id=None,
            act_kind="WORK_RECEPTION",
            reception_outcome=None,
            summary="Ancien PV non qualifié",
            source_refs_json=["ccap://clause/18"],
            evidence_refs_json=["document://old-pv"],
            declared_event_date=None,
            actor_id=actor_id,
        )
        legacy_receipt_id = legacy_receipt.id
        session.add(legacy_receipt)
        session.commit()
    projection = PostReceptionObligationReadService(session_factory=session_factory).list_for_case(
        actor=SimpleNamespace(
            actor_kind=ActorKind.PATRON_ADMIN, membership_id=uuid4(), tenant_id=tenant_id
        ),
        case_id=case_id,
    )
    linked = next(item for item in projection if item.record.id == reserve.obligation_id)
    legacy = next(item for item in projection if item.record.id == old_obligation_id)
    assert linked.record.origin_reception_act_id == receipt_id
    assert linked.origin_reception_summary == "PV avec réserves sur le lot 2"
    assert linked.origin_reception_outcome == "UNDER_RESERVATIONS"
    assert legacy.origin_reception_outcome == "UNKNOWN"
    assert legacy.origin_reception_summary is None
    old_receipt = next(
        item
        for item in ContractExecutionEvidenceReadService(
            session_factory=session_factory
        ).list_for_case(
            actor=SimpleNamespace(
                actor_kind=ActorKind.PATRON_ADMIN, membership_id=uuid4(), tenant_id=tenant_id
            ),
            case_id=case_id,
        )
        if item.record.id == legacy_receipt_id
    )
    assert old_receipt.reception_outcome == "UNKNOWN"
    assert not hasattr(linked, "legal_deadline")


def test_post_reception_obligation_is_tenant_scoped_append_only_and_idempotent(
    database_engine, session_factory
) -> None:
    tenant_id, foreign_tenant_id, case_id, foreign_case_id, actor_id = (
        uuid4(),
        uuid4(),
        uuid4(),
        uuid4(),
        uuid4(),
    )
    with Session(database_engine) as session:
        session.add_all(
            [
                TenantRecord(id=tenant_id, slug=f"opr-{tenant_id.hex[:10]}", lifecycle="ACTIVE"),
                TenantRecord(
                    id=foreign_tenant_id,
                    slug=f"opr-{foreign_tenant_id.hex[:10]}",
                    lifecycle="ACTIVE",
                ),
            ]
        )
        session.flush()
        session.add_all(
            [
                _case(tenant_id=tenant_id, case_id=case_id, marker="e"),
                _case(tenant_id=foreign_tenant_id, case_id=foreign_case_id, marker="f"),
            ]
        )
        session.commit()
    command = RecordPostReceptionObligationCommand(
        command_id=uuid4(),
        idempotency_key=uuid4(),
        obligation_id=uuid4(),
        case_id=case_id,
        obligation_type="DOE_DIUO",
        summary="Remettre le DOE final",
        source_refs=("ccap://clause/12",),
        due_date=date(2027, 3, 31),
        cost_estimate_note="À chiffrer par le Patron",
        sanction_ref="ccap://clause/18",
    )
    dispatcher = CommandDispatcher(
        session_factory=session_factory, handlers=post_reception_obligation_handlers()
    )
    context = CommandContext(
        tenant_id=tenant_id,
        actor_id=actor_id,
        actor_kind="PATRON_ADMIN",
        received_at=datetime.now(tz=UTC),
        identity_id=actor_id,
        membership_id=uuid4(),
        session_id=uuid4(),
        case_id=case_id,
        correlation_id=uuid4(),
    )
    result = dispatcher.dispatch(command=command, context=context)
    replay = dispatcher.dispatch(command=command, context=context)
    assert result.result_code == "POST_RECEPTION_OBLIGATION_RECORDED"
    assert replay.replayed is True
    transition_dispatcher = CommandDispatcher(
        session_factory=session_factory, handlers=post_reception_obligation_transition_handlers()
    )
    missing_proof = TransitionPostReceptionObligationCommand(
        command_id=uuid4(),
        idempotency_key=uuid4(),
        transition_id=uuid4(),
        obligation_id=command.obligation_id,
        case_id=case_id,
        expected_revision=0,
        resulting_status="COMPLETED",
        rationale="Tentative sans preuve",
        evidence_refs=(),
    )
    with pytest.raises(CommandExecutionError, match="POST_RECEPTION_COMPLETION_PROOF_REQUIRED"):
        transition_dispatcher.dispatch(command=missing_proof, context=context)
    start = TransitionPostReceptionObligationCommand(
        command_id=uuid4(),
        idempotency_key=uuid4(),
        transition_id=uuid4(),
        obligation_id=command.obligation_id,
        case_id=case_id,
        expected_revision=0,
        resulting_status="IN_PROGRESS",
        rationale="Travaux planifiés",
    )
    start_result = transition_dispatcher.dispatch(command=start, context=context)
    start_replay = transition_dispatcher.dispatch(command=start, context=context)
    assert start_result.result_code == "POST_RECEPTION_OBLIGATION_TRANSITION_RECORDED"
    assert start_replay.replayed is True
    stale = TransitionPostReceptionObligationCommand(
        command_id=uuid4(),
        idempotency_key=uuid4(),
        transition_id=uuid4(),
        obligation_id=command.obligation_id,
        case_id=case_id,
        expected_revision=0,
        resulting_status="FOLLOW_UP_REQUIRED",
        rationale="Concurrent stale action",
    )
    with pytest.raises(CommandExecutionError, match="REVISION_CONFLICT"):
        transition_dispatcher.dispatch(command=stale, context=context)
    complete = TransitionPostReceptionObligationCommand(
        command_id=uuid4(),
        idempotency_key=uuid4(),
        transition_id=uuid4(),
        obligation_id=command.obligation_id,
        case_id=case_id,
        expected_revision=1,
        resulting_status="COMPLETED",
        rationale="PV contrôlé par le Patron",
        evidence_refs=("document://pv-doe",),
    )
    transition_dispatcher.dispatch(command=complete, context=context)
    foreign_context = CommandContext(
        tenant_id=foreign_tenant_id,
        actor_id=actor_id,
        actor_kind="PATRON_ADMIN",
        received_at=datetime.now(tz=UTC),
        identity_id=actor_id,
        membership_id=uuid4(),
        session_id=uuid4(),
        case_id=case_id,
        correlation_id=uuid4(),
    )
    with pytest.raises(CommandExecutionError, match="CASE_NOT_FOUND_OR_FORBIDDEN"):
        dispatcher.dispatch(
            command=command.model_copy(
                update={"command_id": uuid4(), "idempotency_key": uuid4(), "obligation_id": uuid4()}
            ),
            context=foreign_context,
        )
    with Session(database_engine) as session:
        row = session.scalar(
            sa.select(PostReceptionObligationRecord).where(
                PostReceptionObligationRecord.tenant_id == tenant_id,
                PostReceptionObligationRecord.id == command.obligation_id,
            )
        )
        assert row is not None
        assert row.status == "REVIEW_REQUIRED"
        assert row.cost_estimate_note == "À chiffrer par le Patron"
        assert (
            session.scalar(
                sa.select(sa.func.count())
                .select_from(PostReceptionObligationRecord)
                .where(
                    PostReceptionObligationRecord.tenant_id == tenant_id,
                    PostReceptionObligationRecord.case_id == case_id,
                )
            )
            == 1
        )
        with pytest.raises(sa.exc.DBAPIError), session.begin_nested():
            session.execute(
                sa.update(PostReceptionObligationRecord)
                .where(PostReceptionObligationRecord.id == command.obligation_id)
                .values(summary="Clôturé")
            )
        projection = PostReceptionObligationReadService(
            session_factory=session_factory
        ).list_for_case(
            actor=SimpleNamespace(
                actor_kind=ActorKind.PATRON_ADMIN, membership_id=uuid4(), tenant_id=tenant_id
            ),
            case_id=case_id,
        )
        assert projection[0].status == "COMPLETED"
        assert projection[0].revision == 2
        assert projection[0].latest_transition.evidence_refs_json == ["document://pv-doe"]
        assert (
            session.scalar(
                sa.select(sa.func.count()).select_from(PostReceptionObligationTransitionRecord)
            )
            == 2
        )
    with (
        Session(database_engine) as session,
        pytest.raises(sa.exc.DBAPIError),
        session.begin_nested(),
    ):
        session.execute(
            sa.update(PostReceptionObligationTransitionRecord)
            .where(PostReceptionObligationTransitionRecord.obligation_id == command.obligation_id)
            .values(rationale="Réecriture interdite")
        )
