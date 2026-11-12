from datetime import UTC, datetime
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Header, HTTPException, Query, Response
from pydantic import BaseModel, ConfigDict, Field

from app.interfaces.http.routes.consultations import ConsultationSecurityRuntime
from app.interfaces.http.routes.patron_pricing_import import _resolve_context
from app.modules.pricing.application.position_commands import (
    RecordPositionReviewCommand,
    RecordPositionReviewRequest,
)
from app.modules.pricing.public.position_contracts import (
    PricingPositionsResponse,
    exact_position_money,
)
from app.platform.events.dispatcher import CommandExecutionError


class PositionReviewReceipt(BaseModel):
    model_config = ConfigDict(extra="forbid")
    record_id: UUID
    position_id: UUID
    revision: int = Field(ge=1)
    command_id: UUID
    idempotency_key: UUID
    replayed: bool


def build_patron_pricing_positions_router(
    *, service, security_runtime: ConsultationSecurityRuntime
):
    router = APIRouter(
        prefix="/api/v1/patron/cases/{case_id}/pricing-import/{batch_id}/positions",
        tags=["pricing-positions"],
    )

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

    @router.get("", response_model=PricingPositionsResponse)
    def read(
        case_id: UUID,
        batch_id: UUID,
        authorization: Annotated[str | None, Header()] = None,
        offset: Annotated[int, Query(ge=0, le=10000)] = 0,
        search: Annotated[str, Query(max_length=120)] = "",
    ):
        try:
            return exact_position_money(
                service.read(
                    actor=actor(authorization),
                    case_id=case_id,
                    batch_id=batch_id,
                    now=datetime.now(UTC),
                    offset=offset,
                    search=search,
                )
            )
        except PermissionError as error:
            raise denied(error) from error

    @router.get("/{position_id}", response_model=PricingPositionsResponse)
    def read_one(
        case_id: UUID,
        batch_id: UUID,
        position_id: UUID,
        authorization: Annotated[str | None, Header()] = None,
    ):
        try:
            return exact_position_money(
                service.read(
                    actor=actor(authorization),
                    case_id=case_id,
                    batch_id=batch_id,
                    position_id=position_id,
                    now=datetime.now(UTC),
                )
            )
        except PermissionError as error:
            raise denied(error) from error

    @router.post("/{position_id}/reviews", response_model=PositionReviewReceipt, status_code=201)
    def record(
        case_id: UUID,
        batch_id: UUID,
        position_id: UUID,
        payload: RecordPositionReviewRequest,
        response: Response,
        authorization: Annotated[str | None, Header()] = None,
    ):
        command = RecordPositionReviewCommand(
            case_id=case_id, batch_id=batch_id, position_id=position_id, **payload.model_dump()
        )
        try:
            result = service.record(
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
                if "CONFLICT" in code or "IDEMPOTENCY" in code or code == "COMMAND_IN_PROGRESS"
                else 422
            )
            raise HTTPException(
                status_code=status,
                detail="NOT_FOUND_OR_FORBIDDEN"
                if status == 404
                else "POSITION_SOURCE_OR_REVISION_CONFLICT"
                if status == 409
                else "POSITION_REVIEW_REJECTED",
            ) from error
        response.status_code = 200 if result.replayed else 201
        ref = result.aggregate_refs[0]
        return PositionReviewReceipt(
            record_id=UUID(ref["aggregate_id"]),
            position_id=position_id,
            revision=ref["aggregate_revision"],
            command_id=command.command_id,
            idempotency_key=command.idempotency_key,
            replayed=result.replayed,
        )

    @router.get("/{position_id}/history")
    def history(
        case_id: UUID,
        batch_id: UUID,
        position_id: UUID,
        authorization: Annotated[str | None, Header()] = None,
        before_revision: Annotated[int | None, Query(ge=1)] = None,
    ):
        try:
            return exact_position_money(
                service.history(
                    actor=actor(authorization),
                    case_id=case_id,
                    batch_id=batch_id,
                    position_id=position_id,
                    now=datetime.now(UTC),
                    before_revision=before_revision,
                )
            )
        except PermissionError as error:
            raise denied(error) from error

    return router
