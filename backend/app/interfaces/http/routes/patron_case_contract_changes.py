"""Patron-only HTTP surface for sourced changes linked to B1 handovers."""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

from fastapi import APIRouter, Header, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.requests import Request

from app.interfaces.http.dependencies.auth import resolve_bearer_context as _resolve_context
from app.interfaces.http.routes.consultations import ConsultationSecurityRuntime
from app.modules.pricing.application.case_contract_change import CaseContractChangeService
from app.modules.pricing.application.case_contract_change_commands import (
    PrepareCaseContractChangeEvidenceUploadCommand,
    RecordCaseContractChangeActionCommand,
    RecordCaseContractChangeActionExecutionCommand,
    RecordCaseContractChangeActionImpactRelationCommand,
    RecordCaseContractChangeApplicabilityCommand,
    RecordCaseContractChangeEngagementLinkCommand,
    RecordCaseContractChangeEventCommand,
    RecordCaseContractChangeExternalConfirmationCommand,
    RecordCaseContractChangeImpactDeclarationCommand,
)
from app.modules.pricing.application.case_contract_change_evidence_upload import (
    CaseContractChangeEvidenceUploadService,
    EvidenceUploadAlreadyClaimedError,
    EvidenceUploadRejectedError,
)
from app.modules.pricing.public.case_contract_change_contracts import (
    CaseContractChangeEventListResponse,
    CaseContractChangeEvidenceUploadResponse,
    ContractChangeEventResponse,
    PrepareCaseContractChangeEvidenceUploadRequest,
    PrepareCaseContractChangeEvidenceUploadResponse,
    RecordCaseContractChangeActionExecutionRequest,
    RecordCaseContractChangeActionImpactRelationRequest,
    RecordCaseContractChangeActionRequest,
    RecordCaseContractChangeApplicabilityRequest,
    RecordCaseContractChangeEngagementLinkRequest,
    RecordCaseContractChangeEventRequest,
    RecordCaseContractChangeExternalConfirmationRequest,
    RecordCaseContractChangeImpactDeclarationRequest,
    RecordCaseContractChangeResponse,
)
from app.platform.events.dispatcher import CommandExecutionError


def build_patron_case_contract_change_router(
    *,
    service: CaseContractChangeService,
    evidence_upload_service: CaseContractChangeEvidenceUploadService,
    security_runtime: ConsultationSecurityRuntime,
) -> APIRouter:
    router = APIRouter(prefix="/api/v1/patron/cases", tags=["patron-contract-changes"])

    @router.get(
        "/{case_id}/contract-change-events", response_model=CaseContractChangeEventListResponse
    )
    def list_events(case_id: UUID, authorization: str | None = Header(default=None)):
        actor = _resolve_context(
            authorization=authorization, context_resolver=security_runtime.context_resolver
        )
        try:
            events = service.list_for_case(actor=actor, case_id=case_id, now=datetime.now(tz=UTC))
        except PermissionError as error:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="FORBIDDEN"
            ) from error
        return CaseContractChangeEventListResponse(
            case_id=case_id,
            events=[ContractChangeEventResponse.model_validate(event) for event in events],
        )

    @router.post(
        "/{case_id}/contract-change-events",
        response_model=RecordCaseContractChangeResponse,
        status_code=status.HTTP_201_CREATED,
    )
    def record_event(
        case_id: UUID,
        request: RecordCaseContractChangeEventRequest,
        authorization: str | None = Header(default=None),
    ):
        command = RecordCaseContractChangeEventCommand(**request.model_dump(), case_id=case_id)
        return _record(service, command, actor=_actor(authorization, security_runtime))

    @router.post(
        "/{case_id}/contract-change-events/{event_id}/applicability",
        response_model=RecordCaseContractChangeResponse,
        status_code=status.HTTP_201_CREATED,
    )
    def record_applicability(
        case_id: UUID,
        event_id: UUID,
        request: RecordCaseContractChangeApplicabilityRequest,
        authorization: str | None = Header(default=None),
    ):
        command = RecordCaseContractChangeApplicabilityCommand(
            **request.model_dump(), case_id=case_id, event_id=event_id
        )
        return _record(service, command, actor=_actor(authorization, security_runtime))

    @router.post(
        "/{case_id}/contract-change-events/{event_id}/actions",
        response_model=RecordCaseContractChangeResponse,
        status_code=status.HTTP_201_CREATED,
    )
    def record_action(
        case_id: UUID,
        event_id: UUID,
        request: RecordCaseContractChangeActionRequest,
        authorization: str | None = Header(default=None),
    ):
        command = RecordCaseContractChangeActionCommand(
            **request.model_dump(), case_id=case_id, event_id=event_id
        )
        return _record(service, command, actor=_actor(authorization, security_runtime))

    @router.post(
        "/{case_id}/contract-change-events/{event_id}/actions/{action_id}/impact-links",
        response_model=RecordCaseContractChangeResponse,
        status_code=status.HTTP_201_CREATED,
    )
    def record_action_impact_relation(
        case_id: UUID,
        event_id: UUID,
        action_id: UUID,
        request: RecordCaseContractChangeActionImpactRelationRequest,
        authorization: str | None = Header(default=None),
    ):
        command = RecordCaseContractChangeActionImpactRelationCommand(
            **request.model_dump(), case_id=case_id, event_id=event_id, action_id=action_id
        )
        return _record(service, command, actor=_actor(authorization, security_runtime))

    @router.post(
        "/{case_id}/contract-change-events/{event_id}/actions/{action_id}/evidence-objects",
        response_model=PrepareCaseContractChangeEvidenceUploadResponse,
        status_code=status.HTTP_201_CREATED,
    )
    def prepare_evidence_object_upload(
        case_id: UUID,
        event_id: UUID,
        action_id: UUID,
        request: PrepareCaseContractChangeEvidenceUploadRequest,
        authorization: str | None = Header(default=None),
    ):
        actor = _actor(authorization, security_runtime)
        command = PrepareCaseContractChangeEvidenceUploadCommand(
            **request.model_dump(),
            case_id=case_id,
            event_id=event_id,
            action_id=action_id,
        )
        receipt = _dispatch(service, command, actor=actor)
        upload_intent = evidence_upload_service.get_intent(
            tenant_id=actor.tenant_id,
            case_id=case_id,
            event_id=event_id,
            action_id=action_id,
            evidence_object_id=request.evidence_object_id,
        )
        if upload_intent is None:
            raise HTTPException(status_code=404, detail="NOT_FOUND_OR_FORBIDDEN")
        response = PrepareCaseContractChangeEvidenceUploadResponse(
            evidence_object_id=request.evidence_object_id,
            state=upload_intent.state,
            expires_at=upload_intent.expires_at.isoformat(),
            replayed=receipt.replayed,
        )
        return JSONResponse(
            status_code=status.HTTP_200_OK if receipt.replayed else status.HTTP_201_CREATED,
            content=response.model_dump(mode="json"),
        )

    @router.put(
        "/{case_id}/contract-change-events/{event_id}/actions/{action_id}/evidence-objects/{evidence_object_id}/content",
        response_model=CaseContractChangeEvidenceUploadResponse,
    )
    async def upload_evidence_object(
        case_id: UUID,
        event_id: UUID,
        action_id: UUID,
        evidence_object_id: UUID,
        request: Request,
        authorization: str | None = Header(default=None),
        idempotency_key: UUID | None = Header(default=None, alias="Idempotency-Key"),  # noqa: B008
    ) -> CaseContractChangeEvidenceUploadResponse:
        actor = _actor(authorization, security_runtime)
        if idempotency_key is None:
            raise HTTPException(status_code=400, detail="IDEMPOTENCY_KEY_REQUIRED")
        _reject_non_binary_content_type(request.headers.get("content-type"))
        now = datetime.now(tz=UTC)
        try:
            service.authorize_case_write(actor=actor, case_id=case_id, now=now)
        except PermissionError as error:
            raise HTTPException(status_code=403, detail="FORBIDDEN") from error
        try:
            result = await evidence_upload_service.upload(
                actor=actor,
                case_id=case_id,
                event_id=event_id,
                action_id=action_id,
                evidence_object_id=evidence_object_id,
                idempotency_key=idempotency_key,
                stream=request.stream(),
                content_length=_content_length(request.headers.get("content-length")),
                now=now,
            )
        except PermissionError as error:
            raise HTTPException(status_code=404, detail="NOT_FOUND_OR_FORBIDDEN") from error
        except EvidenceUploadAlreadyClaimedError as error:
            raise HTTPException(status_code=409, detail="UPLOAD_NOT_AWAITING") from error
        except EvidenceUploadRejectedError as error:
            raise HTTPException(status_code=error.status_code, detail="UPLOAD_REJECTED") from error
        return CaseContractChangeEvidenceUploadResponse(
            evidence_object_id=result.evidence_object_id,
            version=1,
            state="CLEAN",
            sha256=result.sha256,
            actual_byte_size=result.actual_byte_size,
            media_type=result.media_type,
        )

    @router.post(
        "/{case_id}/contract-change-events/{event_id}/actions/{action_id}/execution-acts",
        response_model=RecordCaseContractChangeResponse,
        status_code=status.HTTP_201_CREATED,
    )
    async def record_action_execution(
        case_id: UUID,
        event_id: UUID,
        action_id: UUID,
        request: RecordCaseContractChangeActionExecutionRequest,
        authorization: str | None = Header(default=None),
    ):
        actor = _actor(authorization, security_runtime)
        now = datetime.now(tz=UTC)
        try:
            service.authorize_case_write(actor=actor, case_id=case_id, now=now)
        except PermissionError as error:
            raise HTTPException(status_code=403, detail="FORBIDDEN") from error
        try:
            verified_evidence_ids = await evidence_upload_service.verify_sources(
                tenant_id=actor.tenant_id,
                case_id=case_id,
                event_id=event_id,
                action_id=action_id,
                c4_relation_id=request.c4_relation_id,
                evidence_object_ids=tuple(request.evidence_object_ids),
                evidence_kind="EXECUTION_EVIDENCE",
            )
        except PermissionError as error:
            raise HTTPException(
                status_code=422, detail="C5_EVIDENCE_SOURCE_NOT_VERIFIED"
            ) from error
        except EvidenceUploadRejectedError as error:
            raise HTTPException(
                status_code=422, detail="C5_EVIDENCE_SOURCE_NOT_VERIFIED"
            ) from error
        command = RecordCaseContractChangeActionExecutionCommand(
            **request.model_dump(),
            case_id=case_id,
            event_id=event_id,
            action_id=action_id,
            verified_evidence_object_ids=verified_evidence_ids,
        )
        return _record(service, command, actor=actor)

    @router.post(
        "/{case_id}/contract-change-events/{event_id}/actions/{action_id}/execution-acts/{act_id}/external-confirmations",
        response_model=RecordCaseContractChangeResponse,
        status_code=status.HTTP_201_CREATED,
    )
    async def record_external_confirmation(
        case_id: UUID,
        event_id: UUID,
        action_id: UUID,
        act_id: UUID,
        request: RecordCaseContractChangeExternalConfirmationRequest,
        authorization: str | None = Header(default=None),
    ):
        actor = _actor(authorization, security_runtime)
        try:
            service.authorize_case_write(actor=actor, case_id=case_id, now=datetime.now(tz=UTC))
        except PermissionError as error:
            raise HTTPException(status_code=403, detail="FORBIDDEN") from error
        try:
            verified = await evidence_upload_service.verify_sources(
                tenant_id=actor.tenant_id,
                case_id=case_id,
                event_id=event_id,
                action_id=action_id,
                c4_relation_id=request.c4_relation_id,
                evidence_object_ids=(request.evidence_object_id,),
                evidence_kind="EXTERNAL_CONFIRMATION",
            )
        except PermissionError as error:
            raise HTTPException(
                status_code=422, detail="C5_EXTERNAL_CONFIRMATION_SOURCE_NOT_VERIFIED"
            ) from error
        except EvidenceUploadRejectedError as error:
            raise HTTPException(
                status_code=422, detail="C5_EXTERNAL_CONFIRMATION_SOURCE_NOT_VERIFIED"
            ) from error
        command = RecordCaseContractChangeExternalConfirmationCommand(
            **request.model_dump(),
            case_id=case_id,
            event_id=event_id,
            action_id=action_id,
            act_id=act_id,
            verified_evidence_object_id=verified[0],
        )
        return _record(service, command, actor=actor)

    @router.post(
        "/{case_id}/contract-change-events/{event_id}/engagement-links",
        response_model=RecordCaseContractChangeResponse,
        status_code=status.HTTP_201_CREATED,
    )
    def record_engagement_link(
        case_id: UUID,
        event_id: UUID,
        request: RecordCaseContractChangeEngagementLinkRequest,
        authorization: str | None = Header(default=None),
    ):
        command = RecordCaseContractChangeEngagementLinkCommand(
            **request.model_dump(), case_id=case_id, event_id=event_id
        )
        return _record(service, command, actor=_actor(authorization, security_runtime))

    @router.post(
        "/{case_id}/contract-change-events/{event_id}/impact-declarations",
        response_model=RecordCaseContractChangeResponse,
        status_code=status.HTTP_201_CREATED,
    )
    def record_impact_declaration(
        case_id: UUID,
        event_id: UUID,
        request: RecordCaseContractChangeImpactDeclarationRequest,
        authorization: str | None = Header(default=None),
    ):
        command = RecordCaseContractChangeImpactDeclarationCommand(
            **request.model_dump(), case_id=case_id, event_id=event_id
        )
        return _record(service, command, actor=_actor(authorization, security_runtime))

    return router


def _actor(authorization: str | None, security_runtime: ConsultationSecurityRuntime):
    return _resolve_context(
        authorization=authorization, context_resolver=security_runtime.context_resolver
    )


def _record(service, command, *, actor):
    result = _dispatch(service, command, actor=actor)
    response = RecordCaseContractChangeResponse(
        status=result.status, result_code=result.result_code, replayed=result.replayed
    )
    return JSONResponse(
        status_code=status.HTTP_200_OK if result.replayed else status.HTTP_201_CREATED,
        content=response.model_dump(mode="json"),
    )


def _dispatch(service, command, *, actor):
    try:
        return service.record(actor=actor, command=command, now=datetime.now(tz=UTC))
    except PermissionError as error:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="FORBIDDEN") from error
    except CommandExecutionError as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=str(error)
        ) from error


def _reject_non_binary_content_type(content_type: str | None) -> None:
    if content_type is None:
        return
    normalized = content_type.split(";", maxsplit=1)[0].casefold().strip()
    if normalized in {"application/json", "multipart/form-data"}:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="BINARY_STREAM_REQUIRED",
        )


def _content_length(value: str | None) -> int | None:
    if value is None:
        return None
    try:
        parsed = int(value)
    except ValueError as error:
        raise HTTPException(status_code=400, detail="INVALID_CONTENT_LENGTH") from error
    if parsed < 0:
        raise HTTPException(status_code=400, detail="INVALID_CONTENT_LENGTH")
    return parsed
