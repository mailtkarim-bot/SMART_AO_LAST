from datetime import UTC, datetime
from uuid import UUID

from fastapi import APIRouter, Header, HTTPException, status
from fastapi.responses import JSONResponse

from app.interfaces.http.dependencies.auth import resolve_bearer_context
from app.interfaces.http.routes.consultations import ConsultationSecurityRuntime
from app.modules.pricing.application.partner_offer_scope_review_commands import (
    PartnerOfferScopeReviewOfferCommand,
    RecordPartnerOfferScopeReviewCommand,
)
from app.modules.pricing.application.partner_offer_scope_review_handler import (
    PartnerOfferScopeReviewService,
)
from app.modules.pricing.public.partner_offer_scope_review_contracts import (
    PartnerOfferScopeReviewListResponse,
    PartnerOfferScopeReviewOfferResponse,
    PartnerOfferScopeReviewResponse,
    RecordPartnerOfferScopeReviewRequest,
    RecordPartnerOfferScopeReviewResponse,
)
from app.platform.events.dispatcher import (
    CommandExecutionError,
    CommandInProgressError,
    IdempotencyKeyReusedError,
)


def build_patron_partner_offer_scope_reviews_router(
    *, service: PartnerOfferScopeReviewService, security_runtime: ConsultationSecurityRuntime
) -> APIRouter:
    router = APIRouter(prefix="/api/v1/patron/cases", tags=["patron-partner-offer-scope-reviews"])

    @router.get(
        "/{case_id}/partner-offer-scope-reviews",
        response_model=PartnerOfferScopeReviewListResponse,
    )
    def list_scope_reviews(
        case_id: UUID, authorization: str | None = Header(default=None)
    ) -> PartnerOfferScopeReviewListResponse:
        actor = resolve_bearer_context(
            authorization=authorization,
            context_resolver=security_runtime.context_resolver,
        )
        try:
            result = service.list_for_case(actor=actor, case_id=case_id, now=datetime.now(tz=UTC))
        except PermissionError as error:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="FORBIDDEN"
            ) from error
        return PartnerOfferScopeReviewListResponse(
            case_id=result.case_id,
            reviews=[
                PartnerOfferScopeReviewResponse(
                    review_id=review.review_id,
                    comparison_id=review.comparison_id,
                    revision=review.revision,
                    decision=review.decision,
                    rationale=review.rationale,
                    actor_id=review.actor_id,
                    recorded_at=review.created_at,
                    requires_reassessment=any(
                        not offer.receipt_is_current for offer in review.offers
                    ),
                    offers=[
                        PartnerOfferScopeReviewOfferResponse(
                            receipt_event_id=offer.receipt_event_id,
                            partner_id=offer.partner_id,
                            partner_kind=offer.partner_kind,
                            partner_label=offer.partner_label,
                            source_locator=offer.source_locator,
                            source_rationale=offer.source_rationale,
                            validity_current=offer.validity_current,
                            exclusions_state=offer.exclusions_state,
                            exclusions=list(offer.exclusions),
                            inclusion_state=offer.inclusion_state,
                            included_scope_note=offer.included_scope_note,
                            exclusions_review_state=offer.exclusions_review_state,
                            transport_state=offer.transport_state,
                            transport_note=offer.transport_note,
                            receipt_is_current=offer.receipt_is_current,
                        )
                        for offer in review.offers
                    ],
                )
                for review in result.reviews
            ],
        )

    @router.post(
        "/{case_id}/partner-offer-scope-reviews",
        response_model=RecordPartnerOfferScopeReviewResponse,
        status_code=status.HTTP_201_CREATED,
    )
    def record_scope_review(
        case_id: UUID,
        request: RecordPartnerOfferScopeReviewRequest,
        authorization: str | None = Header(default=None),
    ):
        actor = resolve_bearer_context(
            authorization=authorization,
            context_resolver=security_runtime.context_resolver,
        )
        try:
            result = service.record(
                actor=actor,
                command=RecordPartnerOfferScopeReviewCommand(
                    command_id=request.command_id,
                    idempotency_key=request.idempotency_key,
                    correlation_id=request.correlation_id,
                    review_id=request.review_id,
                    comparison_id=request.comparison_id,
                    case_id=case_id,
                    expected_revision=request.expected_revision,
                    decision=request.decision,
                    rationale=request.rationale,
                    offers=tuple(
                        PartnerOfferScopeReviewOfferCommand(**item.model_dump())
                        for item in request.offers
                    ),
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
            raise _command_error(error) from error
        response = RecordPartnerOfferScopeReviewResponse(
            result_code="PARTNER_SCOPE_REVIEW_RECORDED",
            aggregate_refs=list(result.aggregate_refs),
            event_ids=[UUID(event_id) for event_id in result.event_ids],
            replayed=result.replayed,
        )
        return JSONResponse(
            status_code=status.HTTP_200_OK if result.replayed else status.HTTP_201_CREATED,
            content=response.model_dump(mode="json"),
        )

    return router


def _command_error(error: CommandExecutionError) -> HTTPException:
    detail = str(error)
    if detail in {"CASE_NOT_FOUND_OR_FORBIDDEN", "PARTNER_RECEIPT_NOT_FOUND_OR_FORBIDDEN"}:
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NOT_FOUND_OR_FORBIDDEN")
    if detail in {
        "PARTNER_RECEIPT_VERSION_CONFLICT",
        "PARTNER_SCOPE_REVIEW_VERSION_CONFLICT",
        "PARTNER_SCOPE_REVIEW_MEMBER_SET_CONFLICT",
        "PARTNER_SCOPE_REVIEW_ID_REUSED",
    }:
        return HTTPException(status_code=status.HTTP_409_CONFLICT, detail=detail)
    return HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=detail)
