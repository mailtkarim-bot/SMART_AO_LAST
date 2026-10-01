from datetime import UTC, datetime
from uuid import UUID

from fastapi import APIRouter, Header, HTTPException, status
from fastapi.responses import JSONResponse

from app.interfaces.http.dependencies.auth import resolve_bearer_context
from app.interfaces.http.routes.consultations import ConsultationSecurityRuntime
from app.modules.partner.application.commands import (
    DeclareCasePartnerEngagementCommand,
    RecordCasePartnerReceiptCommand,
    RecordCasePartnerRequestCommand,
)
from app.modules.partner.application.partner_handler import CasePartnerService
from app.modules.partner.public.contracts import (
    CasePartnerEventResponse,
    CasePartnerEventsResponse,
    DeclareCasePartnerEngagementRequest,
    RecordCasePartnerEventResponse,
    RecordCasePartnerReceiptRequest,
    RecordCasePartnerRequestRequest,
)
from app.platform.events.dispatcher import (
    CommandExecutionError,
    CommandInProgressError,
    IdempotencyKeyReusedError,
)


def build_case_partner_router(
    *, service: CasePartnerService, security_runtime: ConsultationSecurityRuntime
) -> APIRouter:
    router = APIRouter(prefix="/api/v1/cases", tags=["case-partners"])

    @router.get("/{case_id}/partners", response_model=CasePartnerEventsResponse)
    def list_partner_events(case_id: UUID, authorization: str | None = Header(default=None)):
        actor = resolve_bearer_context(
            authorization=authorization,
            context_resolver=security_runtime.context_resolver,
        )
        try:
            projection = service.list_for_case(
                actor=actor, case_id=case_id, now=datetime.now(tz=UTC)
            )
        except PermissionError as error:
            raise HTTPException(status_code=403, detail="FORBIDDEN") from error
        return CasePartnerEventsResponse(
            case_id=projection.case_id,
            events=[
                CasePartnerEventResponse(
                    event_id=row.record.event_id,
                    partner_id=row.record.partner_id,
                    case_id=row.record.case_id,
                    revision=row.record.revision,
                    event_type=row.record.event_type,
                    partner_kind=row.record.partner_kind,
                    partner_label=row.record.partner_label,
                    related_event_id=row.record.related_event_id,
                    source_locator=row.record.source_locator,
                    rationale=row.record.rationale,
                    valid_until=row.record.valid_until,
                    validity_at_recording=row.record.validity_at_recording,
                    validity_current=row.validity_current,
                    exclusions_state=row.record.exclusions_state,
                    exclusions=row.record.exclusions_json,
                    mandate_state=row.record.mandate_state,
                    mandate_source_locator=row.record.mandate_source_locator,
                    actor_id=row.record.actor_id,
                    recorded_at=row.record.created_at,
                )
                for row in projection.events
            ],
            can_request=projection.can_request,
            can_receive=projection.can_receive,
            can_declare_engagement=projection.can_declare_engagement,
        )

    @router.post(
        "/{case_id}/partners/requests",
        status_code=status.HTTP_201_CREATED,
        response_model=RecordCasePartnerEventResponse,
    )
    def record_partner_request(
        case_id: UUID,
        request: RecordCasePartnerRequestRequest,
        authorization: str | None = Header(default=None),
    ):
        if request.case_id != case_id:
            raise HTTPException(status_code=422, detail="PATH_BODY_MISMATCH")
        actor = resolve_bearer_context(
            authorization=authorization,
            context_resolver=security_runtime.context_resolver,
        )
        try:
            result = service.record_request(
                actor=actor,
                command=RecordCasePartnerRequestCommand(**request.model_dump()),
                now=datetime.now(tz=UTC),
            )
        except PermissionError as error:
            raise HTTPException(status_code=403, detail="FORBIDDEN") from error
        except (IdempotencyKeyReusedError, CommandInProgressError) as error:
            raise HTTPException(status_code=409, detail="IDEMPOTENCY_CONFLICT") from error
        except CommandExecutionError as error:
            raise _command_error(error) from error
        return _receipt_response(result)

    @router.post(
        "/{case_id}/partners/receipts",
        status_code=status.HTTP_201_CREATED,
        response_model=RecordCasePartnerEventResponse,
    )
    def record_partner_receipt(
        case_id: UUID,
        request: RecordCasePartnerReceiptRequest,
        authorization: str | None = Header(default=None),
    ):
        if request.case_id != case_id:
            raise HTTPException(status_code=422, detail="PATH_BODY_MISMATCH")
        actor = resolve_bearer_context(
            authorization=authorization,
            context_resolver=security_runtime.context_resolver,
        )
        try:
            result = service.record_receipt(
                actor=actor,
                command=RecordCasePartnerReceiptCommand(**request.model_dump()),
                now=datetime.now(tz=UTC),
            )
        except PermissionError as error:
            raise HTTPException(status_code=403, detail="FORBIDDEN") from error
        except (IdempotencyKeyReusedError, CommandInProgressError) as error:
            raise HTTPException(status_code=409, detail="IDEMPOTENCY_CONFLICT") from error
        except CommandExecutionError as error:
            raise _command_error(error) from error
        return _receipt_response(result)

    @router.post(
        "/{case_id}/partners/engagements",
        status_code=status.HTTP_201_CREATED,
        response_model=RecordCasePartnerEventResponse,
    )
    def declare_partner_engagement(
        case_id: UUID,
        request: DeclareCasePartnerEngagementRequest,
        authorization: str | None = Header(default=None),
    ):
        if request.case_id != case_id:
            raise HTTPException(status_code=422, detail="PATH_BODY_MISMATCH")
        actor = resolve_bearer_context(
            authorization=authorization,
            context_resolver=security_runtime.context_resolver,
        )
        try:
            result = service.declare_engagement(
                actor=actor,
                command=DeclareCasePartnerEngagementCommand(**request.model_dump()),
                now=datetime.now(tz=UTC),
            )
        except PermissionError as error:
            raise HTTPException(status_code=403, detail="FORBIDDEN") from error
        except (IdempotencyKeyReusedError, CommandInProgressError) as error:
            raise HTTPException(status_code=409, detail="IDEMPOTENCY_CONFLICT") from error
        except CommandExecutionError as error:
            raise _command_error(error) from error
        return _receipt_response(result)

    return router


def _receipt_response(result):
    response = RecordCasePartnerEventResponse(
        status="SUCCEEDED",
        result_code=result.result_code,
        aggregate_refs=list(result.aggregate_refs),
        event_ids=list(result.event_ids),
        replayed=result.replayed,
    )
    return JSONResponse(
        status_code=status.HTTP_200_OK if result.replayed else status.HTTP_201_CREATED,
        content=response.model_dump(mode="json"),
    )


def _command_error(error: CommandExecutionError) -> HTTPException:
    detail = str(error)
    if detail in {
        "CASE_NOT_FOUND_OR_FORBIDDEN",
        "PARTNER_REQUEST_NOT_FOUND_OR_FORBIDDEN",
        "PARTNER_RECEIPT_NOT_FOUND_OR_FORBIDDEN",
    }:
        return HTTPException(status_code=404, detail="NOT_FOUND_OR_FORBIDDEN")
    if detail in {
        "PARTNER_VERSION_CONFLICT",
        "PARTNER_IDENTITY_CONFLICT",
        "PARTNER_REQUEST_ALREADY_RECEIVED",
        "PARTNER_RECEIPT_VERSION_CONFLICT",
        "PARTNER_RECEIPT_ALREADY_ENGAGED",
    }:
        return HTTPException(status_code=409, detail=detail)
    return HTTPException(status_code=422, detail=detail)
