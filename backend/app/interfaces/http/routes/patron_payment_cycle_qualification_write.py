# ruff: noqa: E501, E701
from datetime import UTC, datetime
from uuid import UUID

from fastapi import APIRouter, Header, HTTPException, status
from fastapi.responses import JSONResponse

from app.interfaces.http.dependencies.auth import resolve_bearer_context
from app.interfaces.http.routes.consultations import ConsultationSecurityRuntime
from app.modules.pricing.application.payment_cycle_commands import (
    QualifyPaymentPostReceptionCycleCommand,
)
from app.modules.pricing.application.payment_cycle_handler import PaymentCycleWriteService
from app.modules.pricing.public.payment_cycle_contracts import (
    QualifyPaymentCycleRequest,
    RecordPaymentCycleResponse,
)
from app.platform.events.dispatcher import CommandExecutionError


def build_patron_payment_cycle_qualification_write_router(*, service: PaymentCycleWriteService, security_runtime: ConsultationSecurityRuntime) -> APIRouter:
    router = APIRouter(prefix="/api/v1/patron", tags=["patron-payment-cycle-qualification-write"])
    @router.post("/cases/{case_id}/payment-cycles/{cycle_id}/cash-assumptions", response_model=RecordPaymentCycleResponse)
    def qualify(case_id: UUID, cycle_id: UUID, request: QualifyPaymentCycleRequest, authorization: str | None = Header(default=None)):
        actor = resolve_bearer_context(authorization=authorization, context_resolver=security_runtime.context_resolver)
        try:
            result = service.execute(actor=actor, command=QualifyPaymentPostReceptionCycleCommand(**request.model_dump(), cycle_id=cycle_id, case_id=case_id), now=datetime.now(tz=UTC))
        except PermissionError as error: raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="FORBIDDEN") from error
        except CommandExecutionError as error: raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error)) from error
        return JSONResponse(status_code=status.HTTP_200_OK if result.replayed else status.HTTP_201_CREATED, content=RecordPaymentCycleResponse(command_id=UUID(result.command_id), idempotency_key=UUID(result.idempotency_key), cycle_id=cycle_id, result_code=result.result_code, replayed=result.replayed).model_dump(mode="json"))
    return router
