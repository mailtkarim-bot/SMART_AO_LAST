"""Patron-only HTTP surface for sourced changes linked to B1 handovers."""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

from fastapi import APIRouter, Header, HTTPException, status
from fastapi.responses import JSONResponse

from app.interfaces.http.dependencies.auth import resolve_bearer_context as _resolve_context
from app.interfaces.http.routes.consultations import ConsultationSecurityRuntime
from app.modules.pricing.application.case_contract_change import CaseContractChangeService
from app.modules.pricing.application.case_contract_change_commands import (
    RecordCaseContractChangeActionCommand,
    RecordCaseContractChangeApplicabilityCommand,
    RecordCaseContractChangeEventCommand,
)
from app.modules.pricing.public.case_contract_change_contracts import (
    CaseContractChangeEventListResponse,
    ContractChangeActionResponse,
    ContractChangeApplicabilityResponse,
    ContractChangeEventResponse,
    ContractChangeInstrumentResponse,
    RecordCaseContractChangeActionRequest,
    RecordCaseContractChangeApplicabilityRequest,
    RecordCaseContractChangeEventRequest,
    RecordCaseContractChangeResponse,
)
from app.platform.events.dispatcher import CommandExecutionError


def build_patron_case_contract_change_router(
    *, service: CaseContractChangeService, security_runtime: ConsultationSecurityRuntime
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
            events=[
                ContractChangeEventResponse(
                    **{
                        **event,
                        "declared_instrument": (
                            ContractChangeInstrumentResponse.model_validate(
                                event["declared_instrument"]
                            )
                            if event["declared_instrument"]
                            else None
                        ),
                        "applicability_history": [
                            ContractChangeApplicabilityResponse(
                                **{
                                    **review,
                                    "contract_instrument": (
                                        ContractChangeInstrumentResponse.model_validate(
                                            review["contract_instrument"]
                                        )
                                        if review["contract_instrument"]
                                        else None
                                    ),
                                }
                            )
                            for review in event["applicability_history"]
                        ],
                        "actions": [
                            ContractChangeActionResponse.model_validate(action)
                            for action in event["actions"]
                        ],
                    }
                )
                for event in events
            ],
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

    return router


def _actor(authorization: str | None, security_runtime: ConsultationSecurityRuntime):
    return _resolve_context(
        authorization=authorization, context_resolver=security_runtime.context_resolver
    )


def _record(service, command, *, actor):
    try:
        result = service.record(actor=actor, command=command, now=datetime.now(tz=UTC))
    except PermissionError as error:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="FORBIDDEN") from error
    except CommandExecutionError as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=str(error)
        ) from error
    response = RecordCaseContractChangeResponse(
        status=result.status, result_code=result.result_code, replayed=result.replayed
    )
    return JSONResponse(
        status_code=status.HTTP_200_OK if result.replayed else status.HTTP_201_CREATED,
        content=response.model_dump(mode="json"),
    )
