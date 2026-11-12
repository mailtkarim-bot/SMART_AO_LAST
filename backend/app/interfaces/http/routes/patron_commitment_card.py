from datetime import UTC, datetime
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Header, HTTPException, Query, Response

from app.interfaces.http.dependencies.auth import resolve_bearer_context
from app.modules.decision.application.commitment_commands import (
    LinkConditionAssessmentCommand,
    LinkConditionAssessmentRequest,
)
from app.platform.events.dispatcher import CommandExecutionError, IdempotencyKeyReusedError


def build_patron_commitment_card_router(*, service, security_runtime):
    router = APIRouter(prefix="/api/v1/patron/cases/{case_id}", tags=["commitment-card"])

    def actor(authorization):
        return resolve_bearer_context(
            authorization=authorization, context_resolver=security_runtime.context_resolver
        )

    def denied(error):
        status = 404 if str(error) == "NOT_FOUND_OR_FORBIDDEN" else 403
        return HTTPException(
            status_code=status, detail="NOT_FOUND_OR_FORBIDDEN" if status == 404 else "FORBIDDEN"
        )

    @router.get("/commitment-card")
    def read(case_id: UUID, authorization: Annotated[str | None, Header()] = None):
        try:
            return service.read(actor=actor(authorization), case_id=case_id, now=datetime.now(UTC))
        except PermissionError as error:
            raise denied(error) from error

    @router.get("/commitment-card/history")
    def history(
        case_id: UUID,
        authorization: Annotated[str | None, Header()] = None,
        before_decision_id: Annotated[UUID | None, Query()] = None,
    ):
        try:
            return service.history(
                actor=actor(authorization),
                case_id=case_id,
                now=datetime.now(UTC),
                before_decision_id=before_decision_id,
            )
        except PermissionError as error:
            raise denied(error) from error

    @router.get("/commitment-card/decisions/{decision_id}")
    def decision(
        case_id: UUID, decision_id: UUID, authorization: Annotated[str | None, Header()] = None
    ):
        try:
            return service.history(
                actor=actor(authorization),
                case_id=case_id,
                decision_id=decision_id,
                now=datetime.now(UTC),
            )
        except PermissionError as error:
            raise denied(error) from error

    @router.post("/decisions/{decision_id}/conditions/{condition_id}/assessment-links")
    def link(
        case_id: UUID,
        decision_id: UUID,
        condition_id: UUID,
        payload: LinkConditionAssessmentRequest,
        response: Response,
        authorization: Annotated[str | None, Header()] = None,
    ):
        command = LinkConditionAssessmentCommand(
            case_id=case_id,
            decision_id=decision_id,
            condition_id=condition_id,
            **payload.model_dump(),
        )
        try:
            result = service.link(
                actor=actor(authorization), command=command, now=datetime.now(UTC)
            )
        except PermissionError as error:
            raise denied(error) from error
        except CommandExecutionError as error:
            code = str(error)
            status = (
                404
                if code == "NOT_FOUND_OR_FORBIDDEN"
                else 409
                if isinstance(error, IdempotencyKeyReusedError)
                or code.startswith("STALE_")
                or "CONFLICT" in code
                else 503
            )
            raise HTTPException(
                status_code=status,
                detail="NOT_FOUND_OR_FORBIDDEN"
                if status == 404
                else "SOURCE_OR_REVISION_CONFLICT"
                if status == 409
                else "RESULT_UNKNOWN_RETRY_IDENTICAL_INTENT",
            ) from error
        response.status_code = 200 if result.replayed else 201
        return dict(
            command_id=command.command_id,
            idempotency_key=command.idempotency_key,
            link_id=command.link_id,
            decision_id=decision_id,
            version=result.aggregate_refs[0]["aggregate_revision"],
            replayed=result.replayed,
        )

    return router
