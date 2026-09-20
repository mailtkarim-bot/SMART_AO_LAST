from __future__ import annotations

import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path
from uuid import UUID, uuid4

import pytest
from app.bootstrap.application import AppRuntime, create_app
from app.interfaces.http.routes.authentication import AuthenticationHttpRuntime
from app.modules.membership.application.collab_info_blockers import (
    CollaboratorInfoBlockerService,
    collaborator_info_blocker_handlers,
)
from app.modules.membership.application.collab_info_blockers_commands import (
    DeclareTaskBlockerCommand,
)
from app.modules.membership.application.collab_work_task import (
    CollaboratorWorkTaskService,
    collaborator_work_task_handlers,
)
from app.modules.membership.application.collab_work_task_commands import (
    CreateTaskFromRequirementCommand,
)
from app.modules.membership.infrastructure.collab_info_blockers_reader import (
    SqlAlchemyCollaboratorInfoBlockerReader,
)
from app.modules.membership.infrastructure.collab_work_task_reader import (
    SqlAlchemyCollaboratorWorkTaskReader,
)
from app.modules.opportunity.application.boamp_case_creation import BoampCaseCreationService
from app.platform.events.dispatcher import CommandDispatcher
from app.platform.security.authentication import AuthenticationService
from app.platform.security.authorization import AuthorizationPolicy
from app.platform.security.models import AuthSessionRecord, IdentityRecord, TenantMembershipRecord
from app.platform.security.tokens import JwtAccessTokenCodec
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "application"))
from test_collab_work_task import _seed  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "process"))
import test_boamp_case_creation_persistence as _boamp_test_helpers  # noqa: E402

NOW = datetime(2026, 8, 17, 12, 0, tzinfo=UTC)


class _Clock:
    def now(self) -> datetime:
        return NOW


class _UnusedPasswordVerifier:
    def verify(self, *, password_hash: str, password: str) -> bool:
        return False


class _UnusedTokenGenerator:
    def generate(self) -> str:
        return "unused-refresh-token"


def _client(session_factory) -> tuple[TestClient, JwtAccessTokenCodec]:
    clock = _Clock()
    tokens = JwtAccessTokenCodec(
        signing_key="test-only-signing-key-at-least-32-bytes",
        issuer="smart-ao-test",
        audience="smart-ao-web",
        clock=clock,
    )
    auth_runtime = AuthenticationHttpRuntime.create(
        authentication_service=AuthenticationService(
            session_factory=session_factory,
            password_verifier=_UnusedPasswordVerifier(),
            token_generator=_UnusedTokenGenerator(),
            clock=clock,
        ),
        session_factory=session_factory,
        access_tokens=tokens,
        csrf_token_generator=_UnusedTokenGenerator(),
        clock=clock,
    )
    return (
        TestClient(
            create_app(
                runtime=AppRuntime.create(session_factory=session_factory),
                authentication_runtime=auth_runtime,
            ),
            base_url="https://smart-ao.test",
        ),
        tokens,
    )


@pytest.mark.api
@pytest.mark.db
@pytest.mark.security
def test_case_resolution_http_is_closed_and_assignment_scoped(session_factory) -> None:
    actor, assignment_id, case_id, requirement_id = _seed(session_factory)
    with session_factory.begin() as session:
        session.add(
            AuthSessionRecord(
                id=actor.session_id,
                tenant_id=actor.tenant_id,
                membership_id=actor.membership_id,
                identity_id=actor.identity_id,
                state="ACTIVE",
                auth_strength="MFA",
                token_version=1,
                issued_at=NOW,
                last_seen_at=NOW,
                expires_at=NOW + timedelta(hours=8),
                absolute_expires_at=NOW + timedelta(hours=12),
                mfa_verified_at=NOW,
                revoked_at=None,
                revoke_reason=None,
            )
        )

    task = CollaboratorWorkTaskService(
        reader=SqlAlchemyCollaboratorWorkTaskReader(session_factory),
        dispatcher=CommandDispatcher(
            session_factory=session_factory,
            handlers=collaborator_work_task_handlers(),
        ),
        policy=AuthorizationPolicy(),
    ).execute(
        actor=actor,
        command=CreateTaskFromRequirementCommand(
            command_id=uuid4(),
            idempotency_key=uuid4(),
            correlation_id=uuid4(),
            task_id=uuid4(),
            assignment_id=assignment_id,
            case_id=case_id,
            requirement_id=requirement_id,
            task_kind="REQUIREMENT_CHECK",
            title="Vérifier la source",
            objective="Contrôler la page de référence.",
        ),
        now=NOW,
    )
    task_id = UUID(task.aggregate_refs[0]["aggregate_id"])
    CollaboratorInfoBlockerService(
        reader=SqlAlchemyCollaboratorInfoBlockerReader(session_factory),
        dispatcher=CommandDispatcher(
            session_factory=session_factory,
            handlers=collaborator_info_blocker_handlers(),
        ),
        policy=AuthorizationPolicy(),
    ).execute(
        actor=actor,
        command=DeclareTaskBlockerCommand(
            command_id=uuid4(),
            idempotency_key=uuid4(),
            correlation_id=uuid4(),
            task_id=task_id,
            expected_revision=0,
            blocker_id=uuid4(),
            blocker_kind="MISSING_INFORMATION",
            description="La source doit être contrôlée.",
            source_locator="RC:p8",
            resolution_owner="COLLABORATEUR",
        ),
        now=NOW,
    )

    client, tokens = _client(session_factory)
    token = tokens.issue(
        identity_id=actor.identity_id,
        session_id=actor.session_id,
        token_version=1,
    )
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get(f"/api/v1/cases/{case_id}/resolution", headers=headers)

    assert response.status_code == 200
    body = response.json()
    assert body["case_id"] == str(case_id)
    assert body["coverage"] == "PARTIAL"
    assert body["economic_coverage"] is None
    assert {item["item_kind"] for item in body["items"]} == {"REQUIREMENT", "TASK_BLOCKER"}
    assert all("description" not in item for item in body["items"])
    assert all(item["due_at"] is None for item in body["items"])
    assert client.get(f"/api/v1/cases/{uuid4()}/resolution", headers=headers).status_code == 404

    password_session = uuid4()
    with session_factory.begin() as session:
        session.add(
            AuthSessionRecord(
                id=password_session,
                tenant_id=actor.tenant_id,
                membership_id=actor.membership_id,
                identity_id=actor.identity_id,
                state="ACTIVE",
                auth_strength="PASSWORD",
                token_version=1,
                issued_at=NOW,
                last_seen_at=NOW,
                expires_at=NOW + timedelta(hours=8),
                absolute_expires_at=NOW + timedelta(hours=12),
                mfa_verified_at=None,
                revoked_at=None,
                revoke_reason=None,
            )
        )
    password_token = tokens.issue(
        identity_id=actor.identity_id,
        session_id=password_session,
        token_version=1,
    )
    password_response = client.get(
        f"/api/v1/cases/{case_id}/resolution",
        headers={"Authorization": f"Bearer {password_token}"},
    )
    assert password_response.status_code == 403
    assert password_response.json()["detail"] == "STEP_UP_REQUIRED"

    patron_identity, patron_membership, patron_session = uuid4(), uuid4(), uuid4()
    unassigned_identity, unassigned_membership, unassigned_session = uuid4(), uuid4(), uuid4()
    with session_factory.begin() as session:
        session.add_all(
            [
                IdentityRecord(
                    id=patron_identity,
                    email_normalized=f"patron-{patron_identity.hex[:12]}@example.test",
                    lifecycle="ACTIVE",
                    email_verified_at=NOW,
                ),
                TenantMembershipRecord(
                    id=patron_membership,
                    tenant_id=actor.tenant_id,
                    identity_id=patron_identity,
                    role="PATRON_ADMIN",
                    state="ACTIVE",
                    activated_at=NOW,
                    revoked_at=None,
                ),
                IdentityRecord(
                    id=unassigned_identity,
                    email_normalized=f"unassigned-{unassigned_identity.hex[:12]}@example.test",
                    lifecycle="ACTIVE",
                    email_verified_at=NOW,
                ),
                TenantMembershipRecord(
                    id=unassigned_membership,
                    tenant_id=actor.tenant_id,
                    identity_id=unassigned_identity,
                    role="COLLABORATEUR",
                    state="ACTIVE",
                    activated_at=NOW,
                    revoked_at=None,
                ),
            ]
        )
        session.flush()
        session.add_all(
            [
                AuthSessionRecord(
                    id=patron_session,
                    tenant_id=actor.tenant_id,
                    membership_id=patron_membership,
                    identity_id=patron_identity,
                    state="ACTIVE",
                    auth_strength="MFA",
                    token_version=1,
                    issued_at=NOW,
                    last_seen_at=NOW,
                    expires_at=NOW + timedelta(hours=8),
                    absolute_expires_at=NOW + timedelta(hours=12),
                    mfa_verified_at=NOW,
                    revoked_at=None,
                    revoke_reason=None,
                ),
                AuthSessionRecord(
                    id=unassigned_session,
                    tenant_id=actor.tenant_id,
                    membership_id=unassigned_membership,
                    identity_id=unassigned_identity,
                    state="ACTIVE",
                    auth_strength="MFA",
                    token_version=1,
                    issued_at=NOW,
                    last_seen_at=NOW,
                    expires_at=NOW + timedelta(hours=8),
                    absolute_expires_at=NOW + timedelta(hours=12),
                    mfa_verified_at=NOW,
                    revoked_at=None,
                    revoke_reason=None,
                ),
            ]
        )

    patron_token = tokens.issue(
        identity_id=patron_identity,
        session_id=patron_session,
        token_version=1,
    )
    patron_response = client.get(
        f"/api/v1/cases/{case_id}/resolution",
        headers={"Authorization": f"Bearer {patron_token}"},
    )
    assert patron_response.status_code == 200
    patron_body = patron_response.json()
    assert {item["item_kind"] for item in patron_body["items"]} == {
        "REQUIREMENT",
        "TASK_BLOCKER",
    }
    assert patron_body["economic_coverage"]["quote_validity"]["state"] == "NOT_DEMONSTRATED"
    assert patron_body["economic_coverage"]["capacity"]["state"] == "NOT_DEMONSTRATED"
    assert patron_body["economic_coverage"]["financing"]["state"] == "NOT_DEMONSTRATED"
    assert "sales_total_minor" not in str(patron_body["economic_coverage"])

    unassigned_token = tokens.issue(
        identity_id=unassigned_identity,
        session_id=unassigned_session,
        token_version=1,
    )
    assert (
        client.get(
            f"/api/v1/cases/{case_id}/resolution",
            headers={"Authorization": f"Bearer {unassigned_token}"},
        ).status_code
        == 403
    )


@pytest.mark.api
@pytest.mark.db
@pytest.mark.security
def test_case_resolution_http_exposes_opportunity_unknowns_for_patron(
    database_engine,
    session_factory,
) -> None:
    tenant_id, identity_id, membership_id, observation_id = _boamp_test_helpers._seed_signal(
        database_engine
    )
    case_result = BoampCaseCreationService(
        session_factory=session_factory,
        dispatcher=_boamp_test_helpers._dispatcher(session_factory),
    ).create(
        context=_boamp_test_helpers._context(
            tenant_id=tenant_id,
            identity_id=identity_id,
            membership_id=membership_id,
        ),
        command=_boamp_test_helpers._command(
            observation_id=observation_id, idempotency_key=uuid4()
        ),
        now=NOW,
    )
    case_id = UUID(str(case_result.aggregate_refs[0]["aggregate_id"]))
    session_id = uuid4()
    with session_factory.begin() as session:
        session.add(
            AuthSessionRecord(
                id=session_id,
                tenant_id=tenant_id,
                membership_id=membership_id,
                identity_id=identity_id,
                state="ACTIVE",
                auth_strength="MFA",
                token_version=1,
                issued_at=NOW,
                last_seen_at=NOW,
                expires_at=NOW + timedelta(hours=8),
                absolute_expires_at=NOW + timedelta(hours=12),
                mfa_verified_at=NOW,
                revoked_at=None,
                revoke_reason=None,
            )
        )

    client, tokens = _client(session_factory)
    token = tokens.issue(identity_id=identity_id, session_id=session_id, token_version=1)
    response = client.get(
        f"/api/v1/cases/{case_id}/resolution",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    unknowns = [item for item in response.json()["items"] if item["item_kind"] == "UNKNOWN"]
    assert len(unknowns) == 2
    assert all(item["native_state"] == "UNKNOWN" for item in unknowns)
    assert {item["impact"] for item in unknowns} == {
        "Périmètre d’étude et de prix non démontré.",
        "Éligibilité et exigences non vérifiables.",
    }
    assert all(f"observation:{observation_id}" in item["source_refs"] for item in unknowns)
