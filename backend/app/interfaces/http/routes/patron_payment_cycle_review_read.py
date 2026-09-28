# ruff: noqa: E501, E701
from uuid import UUID

from fastapi import APIRouter, Header, HTTPException, status

from app.interfaces.http.dependencies.auth import resolve_bearer_context
from app.interfaces.http.routes.consultations import ConsultationSecurityRuntime
from app.modules.pricing.application.payment_cycle_review_read_handler import PaymentCycleReviewReadService
from app.modules.pricing.public.payment_cycle_review_contracts import PaymentCycleReviewReadResponse


def build_patron_payment_cycle_review_read_router(*, service: PaymentCycleReviewReadService, security_runtime: ConsultationSecurityRuntime) -> APIRouter:
    router = APIRouter(prefix="/api/v1/patron", tags=["patron-payment-cycle-review-read"])
    @router.get("/payment-cycles/{cycle_id}/reviews", response_model=list[PaymentCycleReviewReadResponse])
    def reviews(cycle_id: UUID, authorization: str | None = Header(default=None)):
        actor = resolve_bearer_context(authorization=authorization, context_resolver=security_runtime.context_resolver)
        try: rows = service.list_for_cycle(actor=actor, cycle_id=cycle_id)
        except PermissionError as error: raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="FORBIDDEN") from error
        return [PaymentCycleReviewReadResponse(review_id=row.id, cycle_id=row.cycle_id, reviewer_id=row.reviewer_id, decision=row.decision, rationale=row.rationale, created_at=row.created_at) for row in rows]
    return router
