from datetime import UTC, datetime
from uuid import uuid4

import pytest
import sqlalchemy as sa
from app.modules.case.application.regulatory_profile import RegulatoryProfileService
from app.modules.case.application.regulatory_profile_commands import RecordRegulatoryProfileCommand
from app.modules.case.application.regulatory_profile_handler import regulatory_profile_handlers
from app.modules.case.infrastructure.models.case import CaseRecord
from app.modules.case.infrastructure.models.regulatory_profile import RegulatoryProfileRecord
from app.platform.events.dispatcher import CommandDispatcher, CommandExecutionError
from app.platform.persistence.models import TenantRecord
from app.platform.security.authorization import AuthorizationPolicy
from app.platform.security.capabilities import capabilities_for
from app.platform.security.context import ActorContext, ActorKind, MembershipState
from sqlalchemy.orm import Session

NOW = datetime(2026, 9, 24, 12, 0, tzinfo=UTC)


@pytest.fixture(autouse=True)
def isolate_regulatory_profile_records(database_engine: sa.Engine) -> None:
    with database_engine.begin() as connection:
        connection.execute(sa.text("TRUNCATE TABLE tenants CASCADE"))


def _case(*, tenant_id, case_id, marker: str) -> CaseRecord:
    return CaseRecord(
        id=case_id,
        tenant_id=tenant_id,
        aggregate_revision=1,
        functional_identity_hash=marker * 64,
        title=f"Affaire {marker}",
        object_description="Profil réglementaire de test",
        business_origin="MANUAL",
        origin_reference_id=None,
        origin_rationale="Test T1",
        consultation_id=None,
        scope_kind="CUSTOM",
        scope_json={},
        scope_fingerprint=(marker[::-1] * 64),
        applicable_dce_version_id=None,
        lifecycle="ACTIVE",
        commercial_stage="ANALYSIS",
        decision_readiness="NOT_ASSESSED",
        dce_freshness="NO_DCE",
        responsibility_status="UNASSIGNED",
        stopped_reason=None,
        stopped_at=None,
        archived_reason=None,
        archived_at=None,
        created_by_actor_id=None,
        updated_by_actor_id=None,
    )


def _actor(tenant_id, case_id) -> ActorContext:
    actor_id = uuid4()
    return ActorContext(
        actor_id=actor_id,
        identity_id=actor_id,
        tenant_id=tenant_id,
        membership_id=uuid4(),
        actor_kind=ActorKind.PATRON_ADMIN,
        membership_state=MembershipState.ACTIVE,
        capabilities=capabilities_for(ActorKind.PATRON_ADMIN),
        assigned_case_ids=frozenset({case_id}),
        session_id=uuid4(),
        authenticated_at=NOW,
        mfa_verified_at=NOW,
        correlation_id=uuid4(),
    )


def test_regulatory_profile_write_is_idempotent_and_tenant_scoped(
    database_engine: sa.Engine,
    session_factory,
) -> None:
    tenant_id = uuid4()
    foreign_tenant_id = uuid4()
    case_id = uuid4()
    foreign_case_id = uuid4()
    with Session(database_engine) as session:
        session.add_all(
            [
                TenantRecord(id=tenant_id, slug=f"reg-{tenant_id.hex[:12]}", lifecycle="ACTIVE"),
                TenantRecord(
                    id=foreign_tenant_id,
                    slug=f"reg-{foreign_tenant_id.hex[:12]}",
                    lifecycle="ACTIVE",
                ),
            ]
        )
        session.flush()
        session.add_all(
            [
                _case(tenant_id=tenant_id, case_id=case_id, marker="a"),
                _case(tenant_id=foreign_tenant_id, case_id=foreign_case_id, marker="b"),
            ]
        )
        session.commit()

    actor = _actor(tenant_id, case_id)
    service = RegulatoryProfileService(
        dispatcher=CommandDispatcher(
            session_factory=session_factory,
            handlers=regulatory_profile_handlers(),
        ),
        policy=AuthorizationPolicy(),
    )
    command = RecordRegulatoryProfileCommand(
        command_id=uuid4(),
        idempotency_key=uuid4(),
        profile_id=uuid4(),
        case_id=case_id,
        profile_version=1,
        status="UNKNOWN_APPLICABILITY",
        facts={"market_kind": "PUBLIC"},
        source_refs=("dce:rc:p4",),
    )

    result = service.execute(actor=actor, command=command, now=NOW)
    replay = service.execute(actor=actor, command=command, now=NOW)

    assert result.result_code == "REGULATORY_PROFILE_RECORDED"
    assert replay.replayed is True
    with Session(database_engine) as session:
        assert session.scalar(sa.select(sa.func.count()).select_from(RegulatoryProfileRecord)) == 1

    with pytest.raises(CommandExecutionError, match="CASE_NOT_FOUND_OR_FORBIDDEN"):
        service.execute(
            actor=actor,
            command=command.model_copy(
                update={
                    "command_id": uuid4(),
                    "idempotency_key": uuid4(),
                    "profile_id": uuid4(),
                    "case_id": foreign_case_id,
                }
            ),
            now=NOW,
        )


def test_regulatory_profiles_migration_is_tenant_scoped_and_status_closed(
    database_engine: sa.Engine,
) -> None:
    inspector = sa.inspect(database_engine)
    columns = {column["name"] for column in inspector.get_columns("regulatory_profiles")}
    checks = {check["sqltext"] for check in inspector.get_check_constraints("regulatory_profiles")}
    indexes = {index["name"] for index in inspector.get_indexes("regulatory_profiles")}

    assert {
        "id",
        "tenant_id",
        "case_id",
        "profile_version",
        "status",
        "facts_json",
        "source_refs_json",
        "effective_from",
        "effective_until",
    } <= columns
    assert any("ACTIVE" in check and "FUTURE" in check for check in checks)
    assert any("profile_version" in check for check in checks)
    assert "ix_regulatory_profiles__tenant_case_version" in indexes
