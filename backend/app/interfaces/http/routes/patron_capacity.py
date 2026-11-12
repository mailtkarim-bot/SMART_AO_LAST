from datetime import UTC, datetime
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Header, HTTPException, Response

from app.interfaces.http.routes.consultations import ConsultationSecurityRuntime
from app.interfaces.http.routes.patron_pricing_import import _resolve_context
from app.modules.optimization.application.dated_commands import (
    RecordDatedCapacityCommand,
    RecordDatedCapacityRequest,
)
from app.platform.events.dispatcher import CommandExecutionError, IdempotencyKeyReusedError


def build_patron_capacity_router(*, service, security_runtime: ConsultationSecurityRuntime):
    router = APIRouter(prefix="/api/v1/patron/cases/{case_id}/capacity", tags=["capacity"])

    def actor(authorization):
        return _resolve_context(
            authorization=authorization, context_resolver=security_runtime.context_resolver
        )

    def denied(error):
        return HTTPException(
            status_code=404 if str(error) == "NOT_FOUND_OR_FORBIDDEN" else 403,
            detail="NOT_FOUND_OR_FORBIDDEN"
            if str(error) == "NOT_FOUND_OR_FORBIDDEN"
            else "FORBIDDEN",
        )

    @router.get("")
    def read(
        case_id: UUID, response: Response, authorization: Annotated[str | None, Header()] = None
    ):
        response.headers["Cache-Control"] = "no-store"
        try:
            return service.read(actor=actor(authorization), case_id=case_id, now=datetime.now(UTC))
        except PermissionError as error:
            raise denied(error) from error

    @router.post("")
    def record(
        case_id: UUID,
        payload: RecordDatedCapacityRequest,
        response: Response,
        authorization: Annotated[str | None, Header()] = None,
    ):
        command = RecordDatedCapacityCommand(case_id=case_id, **payload.model_dump())
        try:
            result = service.record(
                actor=actor(authorization), command=command, now=datetime.now(UTC)
            )
        except PermissionError as error:
            raise denied(error) from error
        except IdempotencyKeyReusedError as error:
            raise HTTPException(
                status_code=409, detail="CAPACITY_SOURCE_OR_REVISION_CONFLICT"
            ) from error
        except CommandExecutionError as error:
            code = str(error)
            status = (
                404
                if code == "NOT_FOUND_OR_FORBIDDEN"
                else 409
                if ("CONFLICT" in code or "IDEMPOTENCY" in code or code == "COMMAND_IN_PROGRESS")
                else 503
            )
            raise HTTPException(
                status_code=status,
                detail="NOT_FOUND_OR_FORBIDDEN"
                if status == 404
                else "CAPACITY_SOURCE_OR_REVISION_CONFLICT"
                if status == 409
                else "CAPACITY_RESULT_UNKNOWN_RETRY_IDENTICAL_INTENT",
            ) from error
        response.status_code = 200 if result.replayed else 201
        response.headers["Cache-Control"] = "no-store"
        return dict(
            run_id=command.run_id,
            command_id=command.command_id,
            idempotency_key=command.idempotency_key,
            replayed=result.replayed,
            revision=result.aggregate_refs[0]["aggregate_revision"],
        )

    return router
