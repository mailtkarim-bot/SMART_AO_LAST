from __future__ import annotations

import socket
import time
from datetime import UTC, datetime
from threading import Thread
from uuid import uuid4

import httpx
import uvicorn
from app.interfaces.http.routes.consultations import ConsultationSecurityRuntime
from app.interfaces.http.routes.patron_actions import build_patron_action_router
from app.modules.patron_action.application.order import CaseOrderService, case_order_handlers
from app.modules.patron_action.application.outcome import CaseOutcomeService, case_outcome_handlers
from app.platform.events.dispatcher import CommandDispatcher
from app.platform.persistence.models import TenantRecord
from app.platform.security.authorization import AuthorizationPolicy
from app.platform.security.capabilities import capabilities_for
from app.platform.security.context import ActorContext, ActorKind, MembershipState
from fastapi import FastAPI
from sqlalchemy.orm import Session
from tests.db.test_regulatory_profile_persistence import _case


class TokenResolver:
    def __init__(self, actors: dict[str, ActorContext]) -> None:
        self._actors = actors

    def resolve(self, *, access_token: str) -> ActorContext:
        return self._actors[access_token]


class DropP7Acknowledgement:
    """Simulate a proxy losing a successful P7 response after the DB commit."""

    def __init__(self, app) -> None:
        self._app = app

    async def __call__(self, scope, receive, send) -> None:
        headers = dict(scope.get("headers", []))
        if (
            scope.get("type") == "http"
            and scope.get("path", "").endswith("/p7")
            and headers.get(b"x-test-drop-ack") == b"1"
        ):

            async def capture(_message):
                return None

            await self._app(scope, receive, capture)
            await send(
                {
                    "type": "http.response.start",
                    "status": 502,
                    "headers": [(b"content-type", b"application/json")],
                }
            )
            await send({"type": "http.response.body", "body": b'{"detail":"ACK_INTERRUPTED"}'})
            return
        await self._app(scope, receive, send)


def _actor(*, tenant_id, actor_kind: ActorKind) -> ActorContext:
    now = datetime.now(tz=UTC)
    return ActorContext(
        actor_id=uuid4(),
        identity_id=uuid4(),
        tenant_id=tenant_id,
        membership_id=uuid4(),
        actor_kind=actor_kind,
        membership_state=MembershipState.ACTIVE,
        capabilities=capabilities_for(actor_kind),
        assigned_case_ids=frozenset(),
        session_id=uuid4(),
        authenticated_at=now,
        mfa_verified_at=now,
        correlation_id=uuid4(),
    )


def test_http_result_order_p6_p7_unknown_retry_and_role_tenant_refusals(
    database_engine, session_factory
) -> None:
    tenant_id, foreign_tenant_id = uuid4(), uuid4()
    case_id, foreign_case_id = uuid4(), uuid4()
    with Session(database_engine) as session:
        session.add_all(
            [
                TenantRecord(id=tenant_id, slug=f"c12-{tenant_id.hex[:10]}", lifecycle="ACTIVE"),
                TenantRecord(
                    id=foreign_tenant_id,
                    slug=f"c12-{foreign_tenant_id.hex[:10]}",
                    lifecycle="ACTIVE",
                ),
            ]
        )
        session.flush()
        case = _case(tenant_id=tenant_id, case_id=case_id, marker="a")
        case.scope_kind = "MULTI_LOT"
        case.scope_json = {"lot_numbers": ["01", "02", "03"]}
        foreign_case = _case(tenant_id=foreign_tenant_id, case_id=foreign_case_id, marker="b")
        foreign_case.scope_kind = "SINGLE_LOT"
        foreign_case.scope_json = {"lot_numbers": ["99"]}
        session.add_all([case, foreign_case])
        session.commit()

    patron = _actor(tenant_id=tenant_id, actor_kind=ActorKind.PATRON_ADMIN)
    collaborator = _actor(tenant_id=tenant_id, actor_kind=ActorKind.COLLABORATEUR)
    foreign_patron = _actor(tenant_id=foreign_tenant_id, actor_kind=ActorKind.PATRON_ADMIN)
    resolver = TokenResolver(
        {"patron": patron, "collaborator": collaborator, "foreign": foreign_patron}
    )
    dispatcher = CommandDispatcher(
        session_factory=session_factory,
        handlers={**case_outcome_handlers(), **case_order_handlers()},
    )
    policy = AuthorizationPolicy()
    outcome_service = CaseOutcomeService(
        dispatcher=dispatcher, session_factory=session_factory, policy=policy
    )
    order_service = CaseOrderService(
        dispatcher=dispatcher, session_factory=session_factory, policy=policy
    )
    app = FastAPI()
    app.include_router(
        build_patron_action_router(
            service=object(),
            transition_service=object(),
            outcome_service=outcome_service,
            order_service=order_service,
            security_runtime=ConsultationSecurityRuntime(
                context_resolver=resolver,
                policy=policy,
            ),
        )
    )
    app.add_middleware(DropP7Acknowledgement)

    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]
    server = uvicorn.Server(
        uvicorn.Config(
            app, host="127.0.0.1", port=port, log_level="critical", access_log=False, lifespan="off"
        )
    )
    server_thread = Thread(target=server.run, daemon=True)
    server_thread.start()
    deadline = time.monotonic() + 8
    while not server.started and server_thread.is_alive() and time.monotonic() < deadline:
        time.sleep(0.01)
    assert server.started, "local HTTP test server did not start"

    base = f"http://127.0.0.1:{port}/api/v1/patron"

    def headers(token: str) -> dict[str, str]:
        return {"Authorization": f"Bearer {token}"}

    try:
        with httpx.Client(timeout=5) as client:
            outcome_ids = {lot: uuid4() for lot in ("01", "02", "03")}
            outcomes = (
                ("01", "WON", "notification://result/01", None),
                ("02", "LOST", "notification://result/02", None),
                ("03", "UNKNOWN", None, "Aucune notification reçue."),
            )
            for lot, result, source, reason in outcomes:
                response = client.post(
                    f"{base}/case-outcomes",
                    headers=headers("patron"),
                    json={
                        "command_id": str(uuid4()),
                        "idempotency_key": str(uuid4()),
                        "outcome_id": str(outcome_ids[lot]),
                        "case_id": str(case_id),
                        "lot_reference": lot,
                        "outcome": result,
                        "source_locator": source,
                        "unknown_reason": reason,
                        "reservations": [],
                    },
                )
                assert response.status_code == 201, response.text

            won_id = outcome_ids["01"]
            order_id = uuid4()
            order_response = client.post(
                f"{base}/case-orders",
                headers=headers("patron"),
                json={
                    "command_id": str(uuid4()),
                    "idempotency_key": str(uuid4()),
                    "order_id": str(order_id),
                    "outcome_id": str(won_id),
                    "case_id": str(case_id),
                    "decision": "ACCEPTED",
                    "rationale": "Commande reçue et rapprochée.",
                },
            )
            assert order_response.status_code == 201, order_response.text

            p6_id = uuid4()
            p6_response = client.post(
                f"{base}/case-orders/{order_id}/p6",
                headers=headers("patron"),
                json={
                    "command_id": str(uuid4()),
                    "idempotency_key": str(uuid4()),
                    "p6_control_id": str(p6_id),
                    "order_id": str(order_id),
                    "case_id": str(case_id),
                    "decision": "APPROVED",
                    "reservations": ["Prix final à rapprocher"],
                    "rationale": "Revue P6 du Patron.",
                },
            )
            assert p6_response.status_code == 201, p6_response.text

            p7_payload = {
                "command_id": str(uuid4()),
                "idempotency_key": str(uuid4()),
                "p7_result_id": str(uuid4()),
                "p6_control_id": str(p6_id),
                "case_id": str(case_id),
                "result": "UNKNOWN",
                "source_locator": None,
                "reason": "Retour d’exécution en attente.",
                "reservations": ["Réception à confirmer"],
            }
            p7_path = f"{base}/case-p6/{p6_id}/p7"
            interrupted = client.post(
                p7_path, headers={**headers("patron"), "X-Test-Drop-Ack": "1"}, json=p7_payload
            )
            assert interrupted.status_code == 502
            before_retry = client.get(
                f"{base}/cases/{case_id}/execution-results", headers=headers("patron")
            )
            assert before_retry.status_code == 200
            assert before_retry.json()["results"][0]["p7"]["result"] == "UNKNOWN"

            retried = client.post(p7_path, headers=headers("patron"), json=p7_payload)
            assert retried.status_code == 200
            assert retried.json()["replayed"] is True
            projected = client.get(
                f"{base}/cases/{case_id}/execution-results", headers=headers("patron")
            ).json()
            assert projected["lot_references"] == ["01", "02", "03"]
            assert [item["outcome"] for item in projected["results"]] == ["WON", "LOST", "UNKNOWN"]
            assert len([item for item in projected["results"] if item["p7"] is not None]) == 1
            assert projected["results"][0]["p7"]["reason"] == "Retour d’exécution en attente."
            assert projected["results"][0]["p6"]["reservations"] == ["Prix final à rapprocher"]

            collaborator_read = client.get(
                f"{base}/cases/{case_id}/execution-results", headers=headers("collaborator")
            )
            assert collaborator_read.status_code == 403
            foreign_read = client.get(
                f"{base}/cases/{case_id}/execution-results", headers=headers("foreign")
            )
            assert foreign_read.status_code == 403
            foreign_write = client.post(p7_path, headers=headers("foreign"), json=p7_payload)
            assert foreign_write.status_code == 422
    finally:
        server.should_exit = True
        server_thread.join(timeout=5)
