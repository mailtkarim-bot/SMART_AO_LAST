"""Authenticated HTTP boundary for nominative handover."""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

from fastapi import APIRouter, Header, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field

from app.interfaces.http.dependencies.auth import resolve_bearer_context
from app.interfaces.http.routes.consultations import ConsultationSecurityRuntime
from app.platform.security.continuity import (
    ContinuityGovernanceService,
    HandoverAcceptCommand,
    HandoverRequestCommand,
)


class RequestHandoverRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    handover_id: UUID
    successor_membership_id: UUID
    assignment_ids: list[UUID] = Field(min_length=1, max_length=500)
    command_id: UUID
    idempotency_key: UUID
    rationale: str = Field(min_length=1, max_length=2_000)
    correlation_id: UUID | None = None


class AcceptHandoverRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    command_id: UUID
    reason: str = Field(min_length=1, max_length=2_000)
    correlation_id: UUID | None = None


class HandoverResponse(BaseModel):
    record_id: UUID
    state: str
    replayed: bool


def build_continuity_router(
    *,
    service: ContinuityGovernanceService,
    security_runtime: ConsultationSecurityRuntime,
) -> APIRouter:
    router = APIRouter(prefix="/api/v1/continuity/handovers", tags=["continuity"])

    @router.post("", response_model=HandoverResponse, status_code=status.HTTP_201_CREATED)
    def request_handover(
        request: RequestHandoverRequest,
        authorization: str | None = Header(default=None),
    ) -> HandoverResponse:
        actor = resolve_bearer_context(
            authorization=authorization,
            context_resolver=security_runtime.context_resolver,
        )
        try:
            result = service.request_handover(
                actor=actor,
                command=HandoverRequestCommand(
                    handover_id=request.handover_id,
                    successor_membership_id=request.successor_membership_id,
                    assignment_ids=tuple(request.assignment_ids),
                    command_id=request.command_id,
                    idempotency_key=request.idempotency_key,
                    rationale=request.rationale,
                    correlation_id=request.correlation_id,
                ),
                now=datetime.now(tz=UTC),
            )
        except PermissionError as error:
            raise _permission_error(error) from error
        except ValueError as error:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=str(error),
            ) from error
        return _response(result)

    @router.post(
        "/{handover_id}/acceptance",
        response_model=HandoverResponse,
        status_code=status.HTTP_201_CREATED,
    )
    def accept_handover(
        handover_id: UUID,
        request: AcceptHandoverRequest,
        authorization: str | None = Header(default=None),
    ) -> HandoverResponse:
        actor = resolve_bearer_context(
            authorization=authorization,
            context_resolver=security_runtime.context_resolver,
        )
        try:
            result = service.accept_handover(
                actor=actor,
                command=HandoverAcceptCommand(
                    handover_id=handover_id,
                    command_id=request.command_id,
                    reason=request.reason,
                    correlation_id=request.correlation_id,
                ),
                now=datetime.now(tz=UTC),
            )
        except PermissionError as error:
            raise _permission_error(error) from error
        except ValueError as error:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=str(error),
            ) from error
        return _response(result)

    return router


def _response(result) -> JSONResponse:
    response = HandoverResponse(
        record_id=result.record_id,
        state=result.state,
        replayed=result.replayed,
    )
    return JSONResponse(
        status_code=status.HTTP_200_OK if result.replayed else status.HTTP_201_CREATED,
        content=response.model_dump(mode="json"),
    )


def _permission_error(error: PermissionError) -> HTTPException:
    if str(error) == "NOT_FOUND_OR_FORBIDDEN":
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="NOT_FOUND_OR_FORBIDDEN",
        )
    return HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(error))
