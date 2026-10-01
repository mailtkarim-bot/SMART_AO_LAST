from datetime import UTC, datetime
from uuid import UUID

from fastapi import APIRouter, Header, HTTPException, status
from fastapi.responses import JSONResponse

from app.interfaces.http.dependencies.auth import resolve_bearer_context
from app.interfaces.http.routes.consultations import ConsultationSecurityRuntime
from app.modules.pricing.application.partner_offer_price_commands import (
    DeclarePartnerOfferPriceCommand,
)
from app.modules.pricing.application.partner_offer_price_handler import (
    PartnerOfferPriceService,
)
from app.modules.pricing.public.partner_offer_price_contracts import (
    DeclarePartnerOfferPriceRequest,
    DeclarePartnerOfferPriceResponse,
    PartnerOfferPriceDeclarationResponse,
    PartnerOfferPriceListResponse,
    PartnerOfferPriceViewResponse,
)
from app.platform.events.dispatcher import (
    CommandExecutionError,
    CommandInProgressError,
    IdempotencyKeyReusedError,
)


def build_patron_partner_offer_prices_router(
    *, service: PartnerOfferPriceService, security_runtime: ConsultationSecurityRuntime
) -> APIRouter:
    router = APIRouter(prefix="/api/v1/patron/cases", tags=["patron-partner-offer-prices"])

    @router.get("/{case_id}/partner-offer-prices", response_model=PartnerOfferPriceListResponse)
    def list_offer_prices(
        case_id: UUID, authorization: str | None = Header(default=None)
    ) -> PartnerOfferPriceListResponse:
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
        return PartnerOfferPriceListResponse(
            case_id=result.case_id,
            offers=[
                PartnerOfferPriceViewResponse(
                    receipt_event_id=item.receipt_event_id,
                    partner_id=item.partner_id,
                    partner_kind=item.partner_kind,
                    partner_label=item.partner_label,
                    partner_revision=item.partner_revision,
                    source_locator=item.source_locator,
                    source_rationale=item.source_rationale,
                    valid_until=item.valid_until,
                    validity_current=item.validity_current,
                    exclusions_state=item.exclusions_state,
                    exclusions=list(item.exclusions),
                    mandate_state=item.mandate_state,
                    is_latest_receipt=item.is_latest_receipt,
                    price_state="DECLARED" if item.declarations else "UNKNOWN",
                    declarations=[
                        PartnerOfferPriceDeclarationResponse(
                            declaration_id=declaration.declaration_id,
                            revision=declaration.revision,
                            amount_as_declared=declaration.amount_as_declared,
                            currency_code=declaration.currency_code,
                            actor_id=declaration.actor_id,
                            created_at=declaration.created_at,
                        )
                        for declaration in item.declarations
                    ],
                )
                for item in result.offers
            ],
        )

    @router.post(
        "/{case_id}/partner-offer-prices/{receipt_event_id}/declarations",
        response_model=DeclarePartnerOfferPriceResponse,
        status_code=status.HTTP_201_CREATED,
    )
    def declare_offer_price(
        case_id: UUID,
        receipt_event_id: UUID,
        request: DeclarePartnerOfferPriceRequest,
        authorization: str | None = Header(default=None),
    ):
        actor = resolve_bearer_context(
            authorization=authorization,
            context_resolver=security_runtime.context_resolver,
        )
        try:
            result = service.declare(
                actor=actor,
                command=DeclarePartnerOfferPriceCommand(
                    command_id=request.command_id,
                    idempotency_key=request.idempotency_key,
                    correlation_id=request.correlation_id,
                    declaration_id=request.declaration_id,
                    case_id=case_id,
                    receipt_event_id=receipt_event_id,
                    expected_revision=request.expected_revision,
                    amount_as_declared=request.amount_as_declared,
                    currency_code=request.currency_code,
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
        response = DeclarePartnerOfferPriceResponse(
            result_code="PARTNER_OFFER_PRICE_DECLARED",
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
        "PARTNER_OFFER_PRICE_VERSION_CONFLICT",
        "PARTNER_OFFER_PRICE_DECLARATION_ID_REUSED",
    }:
        return HTTPException(status_code=status.HTTP_409_CONFLICT, detail=detail)
    return HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=detail)
