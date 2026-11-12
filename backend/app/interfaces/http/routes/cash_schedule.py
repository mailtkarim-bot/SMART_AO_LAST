"""Private cash declarations, sharing the existing financial authorization service."""

from datetime import UTC, datetime
from uuid import UUID

from fastapi import APIRouter, Header, HTTPException, Response
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.interfaces.http.dependencies.auth import resolve_bearer_context
from app.modules.pricing.public.cash_schedule_contracts import RecordCashScheduleCommand
from app.platform.events.dispatcher import CommandExecutionError


def build_cash_schedule_router(*, service, security_runtime):
    router = APIRouter(
        prefix="/api/v1/patron/cases/{case_id}/cash-schedule", tags=["cash-schedule"]
    )

    def actor(authorization):
        return resolve_bearer_context(
            authorization=authorization, context_resolver=security_runtime.context_resolver
        )

    def failure(error):
        code = str(error)
        if "FORBIDDEN" in code or "NOT_FOUND" in code:
            return HTTPException(404, "NOT_FOUND_OR_FORBIDDEN")
        return HTTPException(409 if "CONFLICT" in code else 422, code)

    @router.get("")
    def read(case_id: UUID, response: Response, authorization: str | None = Header(default=None)):
        response.headers["Cache-Control"] = "no-store"
        try:
            return service.read(actor=actor(authorization), case_id=case_id, now=datetime.now(UTC))
        except PermissionError as error:
            raise HTTPException(403, "FORBIDDEN") from error
        except CommandExecutionError as error:
            raise failure(error) from error
        except SQLAlchemyError as error:
            raise HTTPException(503, "RESULT_UNKNOWN") from error

    @router.post("")
    def write(
        case_id: UUID,
        body: RecordCashScheduleCommand,
        authorization: str | None = Header(default=None),
    ):
        if body.case_id != case_id:
            raise HTTPException(422, "TARGET_CASE_MISMATCH")
        try:
            result = service.record(actor=actor(authorization), command=body, now=datetime.now(UTC))
        except PermissionError as error:
            raise HTTPException(403, "FORBIDDEN") from error
        except CommandExecutionError as error:
            raise failure(error) from error
        except IntegrityError as error:
            raise HTTPException(409, "CASH_REVISION_CONFLICT") from error
        except SQLAlchemyError as error:
            raise HTTPException(503, "RESULT_UNKNOWN") from error
        return JSONResponse(
            status_code=200 if result.replayed else 201,
            headers={"Cache-Control": "no-store"},
            content=dict(
                command_id=str(result.command_id),
                idempotency_key=str(result.idempotency_key),
                revision_id=str(body.revision_id),
                result_code=result.result_code,
                replayed=result.replayed,
            ),
        )

    return router
