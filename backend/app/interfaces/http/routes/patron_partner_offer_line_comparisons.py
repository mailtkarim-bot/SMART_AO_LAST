from datetime import UTC, datetime
from uuid import UUID

from fastapi import APIRouter, Header, HTTPException, status
from fastapi.responses import JSONResponse

from app.interfaces.http.dependencies.auth import resolve_bearer_context
from app.interfaces.http.routes.consultations import ConsultationSecurityRuntime
from app.modules.pricing.application.partner_offer_line_comparison_commands import (
    PartnerOfferLineGroupCommand,
    PartnerOfferLineMemberCommand,
    RecordPartnerOfferLineComparisonCommand,
)
from app.modules.pricing.application.partner_offer_line_comparison_handler import (
    PartnerOfferLineComparisonService,
)
from app.modules.pricing.public.partner_offer_line_comparison_contracts import (
    PartnerOfferLineComparisonListResponse,
    PartnerOfferLineComparisonResponse,
    PartnerOfferLineGroupResponse,
    PartnerOfferLineMemberResponse,
    RecordPartnerOfferLineComparisonRequest,
    RecordPartnerOfferLineComparisonResponse,
)
from app.platform.events.dispatcher import (
    CommandExecutionError,
    CommandInProgressError,
    IdempotencyKeyReusedError,
)


def build_patron_partner_offer_line_comparisons_router(
    *, service: PartnerOfferLineComparisonService, security_runtime: ConsultationSecurityRuntime
) -> APIRouter:
    router = APIRouter(
        prefix="/api/v1/patron/cases", tags=["patron-partner-offer-line-comparisons"]
    )

    @router.get(
        "/{case_id}/partner-offer-line-comparisons",
        response_model=PartnerOfferLineComparisonListResponse,
    )
    def list_comparisons(
        case_id: UUID, authorization: str | None = Header(default=None)
    ) -> PartnerOfferLineComparisonListResponse:
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
        return PartnerOfferLineComparisonListResponse(
            case_id=result.case_id,
            comparisons=[
                PartnerOfferLineComparisonResponse(
                    record_id=comparison.record_id,
                    comparison_id=comparison.comparison_id,
                    revision=comparison.revision,
                    scope_review_id=comparison.scope_review_id,
                    scope_review_revision=comparison.scope_review_revision,
                    scope_review_decision=comparison.scope_review_decision,
                    requires_reassessment=comparison.requires_reassessment,
                    actor_id=comparison.actor_id,
                    recorded_at=comparison.created_at,
                    groups=[
                        PartnerOfferLineGroupResponse(
                            group_id=group.group_id,
                            disposition=group.disposition,
                            rationale=group.rationale,
                            members=[
                                PartnerOfferLineMemberResponse(
                                    receipt_event_id=member.receipt_event_id,
                                    partner_id=member.partner_id,
                                    partner_kind=member.partner_kind,
                                    partner_label=member.partner_label,
                                    source_locator=member.source_locator,
                                    receipt_is_current=member.receipt_is_current,
                                    line_locator_state=member.line_locator_state,
                                    line_locator=member.line_locator,
                                    item_reference_state=member.item_reference_state,
                                    item_reference=member.item_reference,
                                    designation_state=member.designation_state,
                                    designation=member.designation,
                                    unit_state=member.unit_state,
                                    unit=member.unit,
                                    quantity_state=member.quantity_state,
                                    quantity=member.quantity,
                                )
                                for member in group.members
                            ],
                        )
                        for group in comparison.groups
                    ],
                )
                for comparison in result.comparisons
            ],
        )

    @router.post(
        "/{case_id}/partner-offer-line-comparisons",
        response_model=RecordPartnerOfferLineComparisonResponse,
        status_code=status.HTTP_201_CREATED,
    )
    def record_comparison(
        case_id: UUID,
        request: RecordPartnerOfferLineComparisonRequest,
        authorization: str | None = Header(default=None),
    ):
        actor = resolve_bearer_context(
            authorization=authorization,
            context_resolver=security_runtime.context_resolver,
        )
        try:
            result = service.record(
                actor=actor,
                command=RecordPartnerOfferLineComparisonCommand(
                    command_id=request.command_id,
                    idempotency_key=request.idempotency_key,
                    correlation_id=request.correlation_id,
                    record_id=request.record_id,
                    comparison_id=request.comparison_id,
                    case_id=case_id,
                    scope_review_id=request.scope_review_id,
                    expected_revision=request.expected_revision,
                    groups=tuple(
                        PartnerOfferLineGroupCommand(
                            group_id=group.group_id,
                            disposition=group.disposition,
                            rationale=group.rationale,
                            members=tuple(
                                PartnerOfferLineMemberCommand(**member.model_dump())
                                for member in group.members
                            ),
                        )
                        for group in request.groups
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
        response = RecordPartnerOfferLineComparisonResponse(
            result_code="PARTNER_OFFER_LINE_COMPARISON_RECORDED",
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
    if detail in {
        "CASE_NOT_FOUND_OR_FORBIDDEN",
        "PARTNER_RECEIPT_NOT_FOUND_OR_FORBIDDEN",
        "PARTNER_SCOPE_REVIEW_NOT_FOUND_OR_FORBIDDEN",
    }:
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NOT_FOUND_OR_FORBIDDEN")
    if detail in {
        "PARTNER_OFFER_LINE_COMPARISON_ID_REUSED",
        "PARTNER_OFFER_LINE_COMPARISON_VERSION_CONFLICT",
        "PARTNER_OFFER_LINE_SCOPE_REVIEW_CONFLICT",
        "PARTNER_OFFER_LINE_SCOPE_MEMBER_SET_CONFLICT",
        "PARTNER_OFFER_LINE_MEMBER_SET_CONFLICT",
        "PARTNER_SCOPE_REVIEW_VERSION_CONFLICT",
        "PARTNER_RECEIPT_VERSION_CONFLICT",
    }:
        return HTTPException(status_code=status.HTTP_409_CONFLICT, detail=detail)
    return HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=detail)
