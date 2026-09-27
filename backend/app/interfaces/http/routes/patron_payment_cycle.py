# ruff: noqa: E501, E701
from uuid import UUID

from fastapi import APIRouter, Header, HTTPException, status

from app.interfaces.http.dependencies.auth import resolve_bearer_context
from app.interfaces.http.routes.consultations import ConsultationSecurityRuntime
from app.modules.dce.public.contracts import PaymentCycleResponse
from app.modules.pricing.application.payment_cycle_handler import PaymentCycleReadService


def build_patron_payment_cycle_router(*, service: PaymentCycleReadService, security_runtime: ConsultationSecurityRuntime) -> APIRouter:
    router = APIRouter(prefix="/api/v1/patron", tags=["patron-payment-cycle"])
    @router.get("/cases/{case_id}/payment-post-reception-cycles", response_model=list[PaymentCycleResponse])
    def list_cycles(case_id: UUID, authorization: str | None = Header(default=None)):
        actor = resolve_bearer_context(authorization=authorization, context_resolver=security_runtime.context_resolver)
        try: rows = service.list_for_case(actor=actor, case_id=case_id)
        except PermissionError as error: raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="FORBIDDEN") from error
        return [PaymentCycleResponse(cycle_id=row.id, case_id=row.case_id, source_refs=row.source_refs_json, trigger_event=row.trigger_event, status=row.status, cash_assumption=row.cash_assumption, post_reception_cost_note=row.post_reception_cost_note) for row in rows]
    return router
