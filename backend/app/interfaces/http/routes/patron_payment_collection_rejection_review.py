# ruff: noqa: E501, E701, I001
from datetime import UTC, datetime
from uuid import UUID
from fastapi import APIRouter, Header, HTTPException, status
from app.interfaces.http.dependencies.auth import resolve_bearer_context
from app.interfaces.http.routes.consultations import ConsultationSecurityRuntime
from app.modules.pricing.application.payment_collection_rejection_review_commands import RecordPaymentCollectionRejectionReviewCommand
from app.modules.pricing.application.payment_collection_rejection_review_read_handler import PaymentCollectionRejectionReviewReadService
from app.modules.pricing.public.payment_collection_rejection_review_contracts import RecordPaymentCollectionRejectionReviewRequest, PaymentCollectionRejectionReviewResponse
from app.platform.events.dispatcher import CommandContext, CommandDispatcher
def build_patron_payment_collection_rejection_review_router(*, dispatcher: CommandDispatcher, service: PaymentCollectionRejectionReviewReadService, security_runtime: ConsultationSecurityRuntime) -> APIRouter:
    router = APIRouter(prefix="/api/v1/patron", tags=["patron-payment-collection-rejection-review"])
    @router.post("/cases/{case_id}/payment-collection-rejection-reviews", response_model=PaymentCollectionRejectionReviewResponse)
    def record(case_id: UUID, request: RecordPaymentCollectionRejectionReviewRequest, authorization: str | None = Header(default=None)):
        actor = resolve_bearer_context(authorization=authorization, context_resolver=security_runtime.context_resolver)
        dispatcher.dispatch(command=RecordPaymentCollectionRejectionReviewCommand(**request.model_dump(), case_id=case_id), context=CommandContext(tenant_id=actor.tenant_id, actor_id=actor.actor_id, actor_kind=actor.actor_kind.value, received_at=datetime.now(tz=UTC), identity_id=actor.identity_id, membership_id=actor.membership_id, session_id=actor.session_id, case_id=case_id, correlation_id=actor.correlation_id))
        return PaymentCollectionRejectionReviewResponse(review_id=request.review_id, case_id=case_id, reviewer_id=actor.actor_id, rejected_count=request.rejected_count, decision=request.decision, rationale=request.rationale, created_at=datetime.now(tz=UTC))
    @router.get("/cases/{case_id}/payment-collection-rejection-review", response_model=PaymentCollectionRejectionReviewResponse | None)
    def read(case_id: UUID, authorization: str | None = Header(default=None)):
        actor = resolve_bearer_context(authorization=authorization, context_resolver=security_runtime.context_resolver)
        try: row = service.latest_for_case(actor=actor, case_id=case_id)
        except PermissionError as error: raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="FORBIDDEN") from error
        return None if row is None else PaymentCollectionRejectionReviewResponse(review_id=row.id, case_id=row.case_id, reviewer_id=row.reviewer_id, rejected_count=row.rejected_count, decision=row.decision, rationale=row.rationale, created_at=row.created_at)
    return router
