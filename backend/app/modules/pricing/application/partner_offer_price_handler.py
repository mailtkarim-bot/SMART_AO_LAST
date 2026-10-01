from dataclasses import dataclass
from datetime import date, datetime
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.orm import Session, sessionmaker

from app.modules.case.infrastructure.models.case import CaseRecord
from app.modules.partner.infrastructure.models.partner_event import CasePartnerEventRecord
from app.modules.pricing.application.partner_offer_price_commands import (
    DeclarePartnerOfferPriceCommand,
)
from app.modules.pricing.domain.partner_offer_price import build_partner_offer_price
from app.modules.pricing.infrastructure.models.partner_offer_price import (
    PartnerOfferPriceDeclarationRecord,
)
from app.platform.events.dispatcher import (
    CommandContext,
    CommandDispatcher,
    CommandExecutionError,
    CommandHandler,
    DispatchResult,
    HandlerOutcome,
    PendingDomainEvent,
)
from app.platform.security.authorization import (
    AuthorizationPolicyPort,
    AuthorizationRequest,
    AuthorizationResource,
)
from app.platform.security.capabilities import Capability
from app.platform.security.context import ActorContext, ActorKind, DataClassification


class DeclarePartnerOfferPriceHandler(CommandHandler):
    def execute(
        self,
        *,
        session: Session,
        command: DeclarePartnerOfferPriceCommand,
        context: CommandContext,
    ) -> HandlerOutcome:
        if context.actor_kind != ActorKind.PATRON_ADMIN.value or context.membership_id is None:
            raise CommandExecutionError("PRICING_PATRON_REQUIRED")

        tenant_id = UUID(str(context.tenant_id))
        case = session.scalar(
            sa.select(CaseRecord.id)
            .where(CaseRecord.tenant_id == tenant_id, CaseRecord.id == command.case_id)
            .with_for_update()
        )
        if case is None:
            raise CommandExecutionError("CASE_NOT_FOUND_OR_FORBIDDEN")
        if (
            session.scalar(
                sa.select(PartnerOfferPriceDeclarationRecord.id).where(
                    PartnerOfferPriceDeclarationRecord.id == command.declaration_id,
                )
            )
            is not None
        ):
            raise CommandExecutionError("PARTNER_OFFER_PRICE_DECLARATION_ID_REUSED")

        receipt = session.scalar(
            sa.select(CasePartnerEventRecord).where(
                CasePartnerEventRecord.tenant_id == tenant_id,
                CasePartnerEventRecord.case_id == command.case_id,
                CasePartnerEventRecord.event_id == command.receipt_event_id,
                CasePartnerEventRecord.event_type == "RECEIVED",
            )
        )
        if receipt is None:
            raise CommandExecutionError("PARTNER_RECEIPT_NOT_FOUND_OR_FORBIDDEN")

        latest_receipt_id = session.scalar(
            sa.select(CasePartnerEventRecord.event_id)
            .where(
                CasePartnerEventRecord.tenant_id == tenant_id,
                CasePartnerEventRecord.case_id == command.case_id,
                CasePartnerEventRecord.partner_id == receipt.partner_id,
                CasePartnerEventRecord.event_type == "RECEIVED",
            )
            .order_by(CasePartnerEventRecord.revision.desc())
            .limit(1)
        )
        if latest_receipt_id != receipt.event_id:
            raise CommandExecutionError("PARTNER_RECEIPT_VERSION_CONFLICT")

        current_revision = session.scalar(
            sa.select(
                sa.func.coalesce(sa.func.max(PartnerOfferPriceDeclarationRecord.revision), 0)
            ).where(
                PartnerOfferPriceDeclarationRecord.tenant_id == tenant_id,
                PartnerOfferPriceDeclarationRecord.case_id == command.case_id,
                PartnerOfferPriceDeclarationRecord.receipt_event_id == receipt.event_id,
            )
        )
        if command.expected_revision != current_revision:
            raise CommandExecutionError("PARTNER_OFFER_PRICE_VERSION_CONFLICT")

        try:
            declaration = build_partner_offer_price(
                receipt_event_id=receipt.event_id,
                amount_as_declared=command.amount_as_declared,
                currency_code=command.currency_code,
            )
        except ValueError as error:
            raise CommandExecutionError(str(error)) from error

        revision = current_revision + 1
        session.add(
            PartnerOfferPriceDeclarationRecord(
                id=command.declaration_id,
                tenant_id=tenant_id,
                case_id=command.case_id,
                receipt_event_id=receipt.event_id,
                revision=revision,
                amount_as_declared=declaration.amount_as_declared,
                currency_code=declaration.currency_code,
                actor_id=UUID(str(context.actor_id)),
                membership_id=UUID(str(context.membership_id)),
                command_id=command.command_id,
                idempotency_key=command.idempotency_key,
                correlation_id=command.correlation_id,
            )
        )
        return HandlerOutcome(
            result_code="PARTNER_OFFER_PRICE_DECLARED",
            aggregate_refs=(
                {
                    "aggregate_type": "PARTNER_OFFER_PRICE",
                    "aggregate_id": str(command.declaration_id),
                    "aggregate_revision": revision,
                },
            ),
            events=(
                PendingDomainEvent(
                    aggregate_type="PARTNER_OFFER_PRICE",
                    aggregate_id=command.declaration_id,
                    aggregate_revision=revision,
                    event_type="PARTNER_OFFER_PRICE_DECLARED",
                    payload={
                        "case_id": str(command.case_id),
                        "receipt_event_id": str(receipt.event_id),
                    },
                ),
            ),
        )


def partner_offer_price_handlers() -> dict[str, CommandHandler]:
    return {
        DeclarePartnerOfferPriceCommand.command_type: DeclarePartnerOfferPriceHandler(),
    }


@dataclass(frozen=True, slots=True)
class PartnerOfferPriceDeclarationView:
    declaration_id: UUID
    revision: int
    amount_as_declared: str
    currency_code: str
    actor_id: UUID
    created_at: datetime


@dataclass(frozen=True, slots=True)
class PartnerOfferPriceView:
    receipt_event_id: UUID
    partner_id: UUID
    partner_kind: str
    partner_label: str
    partner_revision: int
    source_locator: str
    source_rationale: str
    valid_until: date | None
    validity_current: str
    exclusions_state: str
    exclusions: tuple[str, ...]
    mandate_state: str
    is_latest_receipt: bool
    declarations: tuple[PartnerOfferPriceDeclarationView, ...]


@dataclass(frozen=True, slots=True)
class PartnerOfferPriceList:
    case_id: UUID
    offers: tuple[PartnerOfferPriceView, ...]


class PartnerOfferPriceService:
    def __init__(
        self,
        *,
        dispatcher: CommandDispatcher,
        session_factory: sessionmaker[Session],
        policy: AuthorizationPolicyPort,
    ) -> None:
        self._dispatcher = dispatcher
        self._session_factory = session_factory
        self._policy = policy

    def list_for_case(
        self, *, actor: ActorContext, case_id: UUID, now: datetime
    ) -> PartnerOfferPriceList:
        self._authorize(actor=actor, case_id=case_id, action=Capability.PRICING_READ, now=now)
        with self._session_factory() as session:
            receipts = session.scalars(
                sa.select(CasePartnerEventRecord)
                .where(
                    CasePartnerEventRecord.tenant_id == actor.tenant_id,
                    CasePartnerEventRecord.case_id == case_id,
                    CasePartnerEventRecord.event_type == "RECEIVED",
                )
                .order_by(
                    CasePartnerEventRecord.created_at.asc(), CasePartnerEventRecord.event_id.asc()
                )
            ).all()
            latest_receipt_ids = session.execute(
                sa.select(
                    sa.func.max(CasePartnerEventRecord.revision),
                    CasePartnerEventRecord.partner_id,
                )
                .where(
                    CasePartnerEventRecord.tenant_id == actor.tenant_id,
                    CasePartnerEventRecord.case_id == case_id,
                    CasePartnerEventRecord.event_type == "RECEIVED",
                )
                .group_by(CasePartnerEventRecord.partner_id)
            ).all()
            latest_revision = {partner_id: revision for revision, partner_id in latest_receipt_ids}
            receipt_ids = [row.event_id for row in receipts]
            declarations = (
                session.scalars(
                    sa.select(PartnerOfferPriceDeclarationRecord)
                    .where(
                        PartnerOfferPriceDeclarationRecord.tenant_id == actor.tenant_id,
                        PartnerOfferPriceDeclarationRecord.case_id == case_id,
                        PartnerOfferPriceDeclarationRecord.receipt_event_id.in_(receipt_ids),
                    )
                    .order_by(
                        PartnerOfferPriceDeclarationRecord.receipt_event_id.asc(),
                        PartnerOfferPriceDeclarationRecord.revision.asc(),
                    )
                ).all()
                if receipt_ids
                else []
            )
            declarations_by_receipt: dict[UUID, list[PartnerOfferPriceDeclarationView]] = {}
            for row in declarations:
                declarations_by_receipt.setdefault(row.receipt_event_id, []).append(
                    PartnerOfferPriceDeclarationView(
                        declaration_id=row.id,
                        revision=row.revision,
                        amount_as_declared=row.amount_as_declared,
                        currency_code=row.currency_code,
                        actor_id=row.actor_id,
                        created_at=row.created_at,
                    )
                )
            return PartnerOfferPriceList(
                case_id=case_id,
                offers=tuple(
                    PartnerOfferPriceView(
                        receipt_event_id=row.event_id,
                        partner_id=row.partner_id,
                        partner_kind=row.partner_kind,
                        partner_label=row.partner_label,
                        partner_revision=row.revision,
                        source_locator=row.source_locator,
                        source_rationale=row.rationale,
                        valid_until=row.valid_until,
                        validity_current=(
                            "UNKNOWN"
                            if row.valid_until is None
                            else "VALID"
                            if row.valid_until >= now.date()
                            else "EXPIRED"
                        ),
                        exclusions_state=row.exclusions_state,
                        exclusions=tuple(row.exclusions_json),
                        mandate_state=row.mandate_state,
                        is_latest_receipt=row.revision == latest_revision.get(row.partner_id),
                        declarations=tuple(declarations_by_receipt.get(row.event_id, ())),
                    )
                    for row in receipts
                ),
            )

    def declare(
        self,
        *,
        actor: ActorContext,
        command: DeclarePartnerOfferPriceCommand,
        now: datetime,
    ) -> DispatchResult:
        self._authorize(
            actor=actor, case_id=command.case_id, action=Capability.PRICING_WRITE, now=now
        )
        return self._dispatcher.dispatch(
            command=command,
            context=CommandContext(
                tenant_id=actor.tenant_id,
                actor_id=actor.actor_id,
                actor_kind=actor.actor_kind.value,
                received_at=now,
                identity_id=actor.identity_id,
                membership_id=actor.membership_id,
                session_id=actor.session_id,
                case_id=command.case_id,
                correlation_id=actor.correlation_id,
            ),
        )

    def _authorize(self, *, actor: ActorContext, case_id: UUID, action: str, now: datetime):
        if actor.actor_kind is not ActorKind.PATRON_ADMIN or actor.membership_id is None:
            raise PermissionError("FINANCIAL_PRIVATE_FORBIDDEN")
        decision = self._policy.authorize(
            context=actor,
            request=AuthorizationRequest(
                action=action,
                resource=AuthorizationResource(
                    resource_type="PARTNER_OFFER_PRICE",
                    resource_id=case_id,
                    tenant_id=actor.tenant_id,
                    classification=DataClassification.FINANCIAL_PRIVATE,
                    case_id=case_id,
                ),
                evaluated_at=now,
            ),
        )
        if not decision.allowed:
            raise PermissionError(decision.code)
