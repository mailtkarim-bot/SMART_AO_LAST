from dataclasses import asdict
from datetime import UTC, datetime
from uuid import UUID

from fastapi import APIRouter, Header, HTTPException, status
from fastapi.responses import JSONResponse

from app.interfaces.http.aggregate_refs import require_aggregate_revision
from app.interfaces.http.dependencies.auth import resolve_bearer_context as _resolve_context
from app.interfaces.http.routes.consultations import ConsultationSecurityRuntime
from app.modules.patron_action.application.commands import CreatePatronActionCommand
from app.modules.patron_action.application.order import CaseOrderService
from app.modules.patron_action.application.order_commands import (
    RecordCaseDispositionCommand,
    RecordCaseOrderCommand,
    RecordCaseP6ControlCommand,
    RecordCaseP7ResultCommand,
    RecordCaseRetentionCommand,
    RecordCaseRexCommand,
    RequestCaseExportCommand,
)
from app.modules.patron_action.application.outcome import CaseOutcomeService
from app.modules.patron_action.application.outcome_commands import RecordCaseOutcomeCommand
from app.modules.patron_action.application.service import PatronActionService
from app.modules.patron_action.application.transition_commands import TransitionPatronActionCommand
from app.modules.patron_action.application.transition_service import PatronActionTransitionService
from app.modules.patron_action.application.transmission_commands import TransmitWonOutcomeCommand
from app.modules.patron_action.public.contracts import (
    CreatePatronActionRequest,
    PatronActionCommandResponse,
    PatronActionProjectionResponse,
    PatronActionQueueResponse,
    PatronActionTransitionResponse,
    RecordCaseDispositionRequest,
    RecordCaseOrderRequest,
    RecordCaseOutcomeRequest,
    RecordCaseP6ControlRequest,
    RecordCaseP7ResultRequest,
    RecordCaseRetentionRequest,
    RecordCaseRexRequest,
    RequestCaseExportRequest,
    TransitionPatronActionRequest,
    TransmitWonOutcomeRequest,
)
from app.platform.events.dispatcher import (
    CommandExecutionError,
    CommandInProgressError,
    IdempotencyKeyReusedError,
)


def build_patron_action_router(
    *,
    service: PatronActionService,
    transition_service: PatronActionTransitionService,
    outcome_service: CaseOutcomeService | None = None,
    security_runtime: ConsultationSecurityRuntime,
    order_service: CaseOrderService | None = None,
) -> APIRouter:
    router = APIRouter(prefix="/api/v1/patron", tags=["patron-actions"])

    @router.post("/case-outcomes/{outcome_id}/transmissions", status_code=status.HTTP_201_CREATED)
    def transmit_won_outcome(
        outcome_id: UUID,
        request: TransmitWonOutcomeRequest,
        authorization: str | None = Header(default=None),
    ):
        if request.outcome_id != outcome_id:
            raise HTTPException(status_code=422, detail="PATH_BODY_MISMATCH")
        actor = _resolve_context(
            authorization=authorization, context_resolver=security_runtime.context_resolver
        )
        if outcome_service is None:
            raise HTTPException(status_code=503, detail="CASE_OUTCOME_SERVICE_UNAVAILABLE")
        try:
            result = outcome_service.transmit(
                actor=actor,
                command=TransmitWonOutcomeCommand(**request.model_dump()),
                now=datetime.now(tz=UTC),
            )
        except PermissionError as error:
            raise HTTPException(status_code=403, detail="FORBIDDEN") from error
        except CommandExecutionError as error:
            raise HTTPException(status_code=422, detail=str(error)) from error
        return JSONResponse(
            status_code=201,
            content={
                "status": "SUCCEEDED",
                "result_code": result.result_code,
                "aggregate_refs": result.aggregate_refs,
                "event_ids": result.event_ids,
            },
        )

    @router.get("/cases/{case_id}/outcomes")
    def list_case_outcomes(case_id: UUID, authorization: str | None = Header(default=None)):
        actor = _resolve_context(
            authorization=authorization, context_resolver=security_runtime.context_resolver
        )
        if outcome_service is None:
            raise HTTPException(status_code=503, detail="CASE_OUTCOME_SERVICE_UNAVAILABLE")
        try:
            rows = outcome_service.list_for_case(
                actor=actor, case_id=case_id, now=datetime.now(tz=UTC)
            )
        except PermissionError as error:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="FORBIDDEN"
            ) from error
        return {
            "case_id": str(case_id),
            "outcomes": [
                {
                    "outcome_id": str(row.id),
                    "lot_reference": row.lot_reference,
                    "outcome": row.outcome,
                    "source_locator": row.source_locator,
                    "reservations": row.reservations_json,
                    "unknown_reason": row.unknown_reason,
                    "created_at": row.created_at.isoformat(),
                }
                for row in rows
            ],
        }

    @router.post("/case-outcomes", status_code=status.HTTP_201_CREATED)
    def record_case_outcome(
        request: RecordCaseOutcomeRequest, authorization: str | None = Header(default=None)
    ):
        actor = _resolve_context(
            authorization=authorization, context_resolver=security_runtime.context_resolver
        )
        if outcome_service is None:
            raise HTTPException(status_code=503, detail="CASE_OUTCOME_SERVICE_UNAVAILABLE")
        try:
            result = outcome_service.execute(
                actor=actor,
                command=RecordCaseOutcomeCommand(**request.model_dump()),
                now=datetime.now(tz=UTC),
            )
        except PermissionError as error:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="FORBIDDEN"
            ) from error
        except CommandExecutionError as error:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=str(error)
            ) from error
        return JSONResponse(
            status_code=201,
            content={
                "status": "SUCCEEDED",
                "result_code": result.result_code,
                "aggregate_refs": result.aggregate_refs,
                "event_ids": result.event_ids,
            },
        )

    @router.post("/case-orders", status_code=status.HTTP_201_CREATED)
    def record_case_order(
        request: RecordCaseOrderRequest, authorization: str | None = Header(default=None)
    ):
        if order_service is None:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="UNAVAILABLE"
            )
        actor = _resolve_context(
            authorization=authorization, context_resolver=security_runtime.context_resolver
        )
        try:
            result = order_service.record_order(
                actor=actor,
                command=RecordCaseOrderCommand(**request.model_dump()),
                now=datetime.now(tz=UTC),
            )
        except PermissionError as error:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="FORBIDDEN"
            ) from error
        except CommandExecutionError as error:
            detail = str(error)
            code = (
                status.HTTP_409_CONFLICT
                if detail == "CASE_ORDER_ALREADY_RECORDED"
                else status.HTTP_422_UNPROCESSABLE_CONTENT
            )
            raise HTTPException(status_code=code, detail=detail) from error
        return JSONResponse(
            status_code=status.HTTP_200_OK if result.replayed else status.HTTP_201_CREATED,
            content={
                "status": "SUCCEEDED",
                "result_code": result.result_code,
                "aggregate_refs": result.aggregate_refs,
                "event_ids": result.event_ids,
                "replayed": result.replayed,
            },
        )

    @router.post("/case-orders/{order_id}/p6", status_code=status.HTTP_201_CREATED)
    def record_case_p6(
        order_id: UUID,
        request: RecordCaseP6ControlRequest,
        authorization: str | None = Header(default=None),
    ):
        if request.order_id != order_id:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail="PATH_BODY_MISMATCH"
            )
        if order_service is None:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="UNAVAILABLE"
            )
        actor = _resolve_context(
            authorization=authorization, context_resolver=security_runtime.context_resolver
        )
        try:
            result = order_service.record_p6(
                actor=actor,
                command=RecordCaseP6ControlCommand(**request.model_dump()),
                now=datetime.now(tz=UTC),
            )
        except PermissionError as error:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="FORBIDDEN"
            ) from error
        except CommandExecutionError as error:
            detail = str(error)
            code = (
                status.HTTP_409_CONFLICT
                if detail == "P6_ALREADY_RECORDED"
                else status.HTTP_422_UNPROCESSABLE_CONTENT
            )
            raise HTTPException(status_code=code, detail=detail) from error
        return JSONResponse(
            status_code=status.HTTP_200_OK if result.replayed else status.HTTP_201_CREATED,
            content={
                "status": "SUCCEEDED",
                "result_code": result.result_code,
                "aggregate_refs": result.aggregate_refs,
                "event_ids": result.event_ids,
                "replayed": result.replayed,
            },
        )

    @router.post("/case-p6/{p6_control_id}/p7", status_code=status.HTTP_201_CREATED)
    def record_case_p7(
        p6_control_id: UUID,
        request: RecordCaseP7ResultRequest,
        authorization: str | None = Header(default=None),
    ):
        if request.p6_control_id != p6_control_id:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail="PATH_BODY_MISMATCH",
            )
        if order_service is None:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="UNAVAILABLE"
            )
        actor = _resolve_context(
            authorization=authorization, context_resolver=security_runtime.context_resolver
        )
        try:
            result = order_service.record_p7(
                actor=actor,
                command=RecordCaseP7ResultCommand(**request.model_dump()),
                now=datetime.now(tz=UTC),
            )
        except PermissionError as error:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="FORBIDDEN"
            ) from error
        except CommandExecutionError as error:
            detail = str(error)
            code = (
                status.HTTP_409_CONFLICT
                if detail == "P7_ALREADY_RECORDED"
                else status.HTTP_422_UNPROCESSABLE_CONTENT
            )
            raise HTTPException(status_code=code, detail=detail) from error
        return JSONResponse(
            status_code=status.HTTP_200_OK if result.replayed else status.HTTP_201_CREATED,
            content={
                "status": "SUCCEEDED",
                "result_code": result.result_code,
                "aggregate_refs": result.aggregate_refs,
                "event_ids": result.event_ids,
                "replayed": result.replayed,
            },
        )

    @router.post("/case-p7/{p7_result_id}/rex", status_code=status.HTTP_201_CREATED)
    def record_case_rex(
        p7_result_id: UUID,
        request: RecordCaseRexRequest,
        authorization: str | None = Header(default=None),
    ):
        if request.p7_result_id != p7_result_id:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail="PATH_BODY_MISMATCH",
            )
        if order_service is None:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="UNAVAILABLE"
            )
        actor = _resolve_context(
            authorization=authorization, context_resolver=security_runtime.context_resolver
        )
        try:
            result = order_service.record_rex(
                actor=actor,
                command=RecordCaseRexCommand(**request.model_dump()),
                now=datetime.now(tz=UTC),
            )
        except PermissionError as error:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="FORBIDDEN"
            ) from error
        except CommandExecutionError as error:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=str(error)
            ) from error
        return JSONResponse(
            status_code=status.HTTP_200_OK if result.replayed else status.HTTP_201_CREATED,
            content={
                "status": "SUCCEEDED",
                "result_code": result.result_code,
                "aggregate_refs": result.aggregate_refs,
                "event_ids": result.event_ids,
                "replayed": result.replayed,
            },
        )

    @router.get("/cases/{case_id}/rex")
    def list_case_rex(case_id: UUID, authorization: str | None = Header(default=None)):
        if order_service is None:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="UNAVAILABLE"
            )
        actor = _resolve_context(
            authorization=authorization, context_resolver=security_runtime.context_resolver
        )
        try:
            rows = order_service.list_rex(actor=actor, case_id=case_id, now=datetime.now(tz=UTC))
        except PermissionError as error:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="FORBIDDEN"
            ) from error
        return {
            "case_id": str(case_id),
            "rex": [
                {
                    "rex_id": str(row.id),
                    "p7_result_id": str(row.p7_result_id),
                    "lot_reference": row.lot_reference,
                    "motif": row.motif,
                    "scope": row.scope,
                    "validation": row.validation,
                    "observation": row.observation,
                    "consequence": row.consequence,
                    "follow_up": row.follow_up,
                    "source_locator": row.source_locator,
                    "created_at": row.created_at.isoformat(),
                }
                for row in rows
            ],
        }

    @router.post("/case-dispositions", status_code=status.HTTP_201_CREATED)
    def record_case_disposition(
        request: RecordCaseDispositionRequest,
        authorization: str | None = Header(default=None),
    ):
        if order_service is None:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="UNAVAILABLE"
            )
        actor = _resolve_context(
            authorization=authorization, context_resolver=security_runtime.context_resolver
        )
        try:
            result = order_service.record_disposition(
                actor=actor,
                command=RecordCaseDispositionCommand(**request.model_dump()),
                now=datetime.now(tz=UTC),
            )
        except PermissionError as error:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="FORBIDDEN"
            ) from error
        except CommandExecutionError as error:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=str(error)
            ) from error
        return JSONResponse(
            status_code=status.HTTP_200_OK if result.replayed else status.HTTP_201_CREATED,
            content={
                "status": "SUCCEEDED",
                "result_code": result.result_code,
                "aggregate_refs": result.aggregate_refs,
                "event_ids": result.event_ids,
                "replayed": result.replayed,
            },
        )

    @router.post("/case-export-requests", status_code=status.HTTP_201_CREATED)
    def request_case_export(
        request: RequestCaseExportRequest,
        authorization: str | None = Header(default=None),
    ):
        if order_service is None:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="UNAVAILABLE"
            )
        actor = _resolve_context(
            authorization=authorization, context_resolver=security_runtime.context_resolver
        )
        try:
            result = order_service.request_export(
                actor=actor,
                command=RequestCaseExportCommand(**request.model_dump()),
                now=datetime.now(tz=UTC),
            )
        except PermissionError as error:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="FORBIDDEN"
            ) from error
        except CommandExecutionError as error:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=str(error)
            ) from error
        return JSONResponse(
            status_code=status.HTTP_200_OK if result.replayed else status.HTTP_201_CREATED,
            content={
                "status": "SUCCEEDED",
                "result_code": result.result_code,
                "aggregate_refs": result.aggregate_refs,
                "event_ids": result.event_ids,
                "replayed": result.replayed,
            },
        )

    @router.post("/case-retentions", status_code=status.HTTP_201_CREATED)
    def record_case_retention(
        request: RecordCaseRetentionRequest,
        authorization: str | None = Header(default=None),
    ):
        if order_service is None:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="UNAVAILABLE"
            )
        actor = _resolve_context(
            authorization=authorization, context_resolver=security_runtime.context_resolver
        )
        try:
            result = order_service.record_retention(
                actor=actor,
                command=RecordCaseRetentionCommand(**request.model_dump()),
                now=datetime.now(tz=UTC),
            )
        except PermissionError as error:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="FORBIDDEN"
            ) from error
        except CommandExecutionError as error:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=str(error)
            ) from error
        return JSONResponse(
            status_code=status.HTTP_200_OK if result.replayed else status.HTTP_201_CREATED,
            content={
                "status": "SUCCEEDED",
                "result_code": result.result_code,
                "aggregate_refs": result.aggregate_refs,
                "event_ids": result.event_ids,
                "replayed": result.replayed,
            },
        )

    @router.get("/actions", response_model=PatronActionQueueResponse)
    def list_actions(authorization: str | None = Header(default=None)):
        actor = _resolve_context(
            authorization=authorization,
            context_resolver=security_runtime.context_resolver,
        )
        try:
            items = service.list_open(actor=actor, now=datetime.now(tz=UTC))
        except PermissionError as error:
            if str(error) == "PATRON_REQUIRED":
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN, detail="FORBIDDEN"
                ) from error
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="FORBIDDEN"
            ) from error
        projections = [PatronActionProjectionResponse(**asdict(item)) for item in items]
        return PatronActionQueueResponse(items=projections, open_count=len(projections))

    @router.post(
        "/actions/{action_id}/transitions",
        status_code=status.HTTP_201_CREATED,
        response_model=PatronActionTransitionResponse,
    )
    def transition_action(
        action_id: UUID,
        request: TransitionPatronActionRequest,
        authorization: str | None = Header(default=None),
    ):
        actor = _resolve_context(
            authorization=authorization,
            context_resolver=security_runtime.context_resolver,
        )
        try:
            result = transition_service.execute(
                actor=actor,
                command=TransitionPatronActionCommand(
                    command_id=request.command_id,
                    idempotency_key=request.idempotency_key,
                    correlation_id=request.correlation_id,
                    transition_id=request.transition_id,
                    action_id=action_id,
                    expected_revision=request.expected_revision,
                    target_state=request.target_state,
                    reason_code=request.reason_code,
                ),
                now=datetime.now(tz=UTC),
            )
        except PermissionError as error:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="FORBIDDEN"
            ) from error
        except (IdempotencyKeyReusedError, CommandInProgressError) as error:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="IDEMPOTENCY_CONFLICT"
            ) from error
        except CommandExecutionError as error:
            detail = str(error)
            code = (
                status.HTTP_409_CONFLICT
                if detail in {"VERSION_CONFLICT", "ACTION_ALREADY_CLOSED"}
                else status.HTTP_422_UNPROCESSABLE_CONTENT
            )
            raise HTTPException(status_code=code, detail=detail) from error
        response = PatronActionTransitionResponse(
            command_id=result.command_id,
            idempotency_key=result.idempotency_key,
            result_code=result.result_code,
            aggregate_id=UUID(str(result.aggregate_refs[0]["aggregate_id"])),
            aggregate_revision=require_aggregate_revision(
                result.aggregate_refs[0]["aggregate_revision"]
            ),
            event_ids=[UUID(event_id) for event_id in result.event_ids],
            replayed=result.replayed,
        )
        return JSONResponse(
            status_code=status.HTTP_200_OK if result.replayed else status.HTTP_201_CREATED,
            content=response.model_dump(mode="json"),
        )

    @router.post(
        "/actions",
        status_code=status.HTTP_201_CREATED,
        response_model=PatronActionCommandResponse,
    )
    def create_action(
        request: CreatePatronActionRequest,
        authorization: str | None = Header(default=None),
    ):
        actor = _resolve_context(
            authorization=authorization,
            context_resolver=security_runtime.context_resolver,
        )
        try:
            result = service.execute(
                actor=actor,
                command=CreatePatronActionCommand(
                    command_id=request.command_id,
                    idempotency_key=request.idempotency_key,
                    correlation_id=request.correlation_id,
                    action_id=request.action_id,
                    case_id=request.case_id,
                    functional_key=request.functional_key,
                    action_type=request.action_type,
                    severity=request.severity,
                    title=request.title,
                    why_now=request.why_now,
                    impact=request.impact,
                    recommended_action=request.recommended_action,
                    due_at=request.due_at,
                    source_refs=request.source_refs,
                ),
                now=datetime.now(tz=UTC),
            )
        except PermissionError as error:
            detail = "PATRON_REQUIRED" if str(error) == "PATRON_REQUIRED" else "FORBIDDEN"
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=detail) from error
        except IdempotencyKeyReusedError as error:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="IDEMPOTENCY_KEY_REUSED"
            ) from error
        except CommandInProgressError as error:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="COMMAND_IN_PROGRESS"
            ) from error
        except CommandExecutionError as error:
            detail = str(error)
            code = (
                status.HTTP_409_CONFLICT
                if detail == "PATRON_ACTION_ALREADY_EXISTS"
                else status.HTTP_422_UNPROCESSABLE_CONTENT
            )
            raise HTTPException(status_code=code, detail=detail) from error
        response = PatronActionCommandResponse(
            command_id=result.command_id,
            idempotency_key=result.idempotency_key,
            result_code=result.result_code,
            aggregate_id=UUID(str(result.aggregate_refs[0]["aggregate_id"])),
            aggregate_revision=require_aggregate_revision(
                result.aggregate_refs[0]["aggregate_revision"]
            ),
            event_ids=[UUID(event_id) for event_id in result.event_ids],
            replayed=result.replayed,
        )
        return JSONResponse(
            status_code=status.HTTP_200_OK if result.replayed else status.HTTP_201_CREATED,
            content=response.model_dump(mode="json"),
        )

    return router
