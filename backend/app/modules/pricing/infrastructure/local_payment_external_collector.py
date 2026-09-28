# ruff: noqa: E501, I001
from collections.abc import Callable
from dataclasses import dataclass
from uuid import UUID
from app.modules.pricing.application.payment_external_signal_handler import build_external_payment_signal_command
from app.platform.events.dispatcher import CommandContext, CommandDispatcher, HandlerOutcome

@dataclass(frozen=True, slots=True)
class BoundedCollectionReport:
    recorded: tuple[HandlerOutcome, ...]
    rejected: tuple[str, ...]

class LocalPaymentExternalCollector:
    """Run one bounded local external payload through the real pricing dispatcher."""
    def __init__(self, *, dispatcher: CommandDispatcher, payload_source: Callable[[], dict[str, object]]):
        self._dispatcher = dispatcher
        self._payload_source = payload_source

    def collect_many(self, *, case_id: UUID, context: CommandContext, identities: tuple[tuple[UUID, UUID, UUID], ...], max_payloads: int = 8) -> tuple[HandlerOutcome, ...]:
        if not 1 <= max_payloads <= 32:
            raise ValueError("PAYMENT_EXTERNAL_COLLECTION_BUDGET_INVALID")
        if len(identities) > max_payloads:
            raise ValueError("PAYMENT_EXTERNAL_COLLECTION_BUDGET_EXCEEDED")
        results = []
        for command_id, idempotency_key, cycle_id in identities:
            results.append(self.collect(case_id=case_id, context=context, command_id=command_id, idempotency_key=idempotency_key, cycle_id=cycle_id))
        return tuple(results)

    def collect_many_resilient(self, *, case_id: UUID, context: CommandContext, identities: tuple[tuple[UUID, UUID, UUID], ...], max_payloads: int = 8) -> BoundedCollectionReport:
        if not 1 <= max_payloads <= 32:
            raise ValueError("PAYMENT_EXTERNAL_COLLECTION_BUDGET_INVALID")
        if len(identities) > max_payloads:
            raise ValueError("PAYMENT_EXTERNAL_COLLECTION_BUDGET_EXCEEDED")
        recorded, rejected = [], []
        for command_id, idempotency_key, cycle_id in identities:
            try:
                recorded.append(self.collect(case_id=case_id, context=context, command_id=command_id, idempotency_key=idempotency_key, cycle_id=cycle_id))
            except ValueError as error:
                rejected.append(str(error))
        return BoundedCollectionReport(recorded=tuple(recorded), rejected=tuple(rejected))

    def collect(self, *, case_id: UUID, context: CommandContext, command_id: UUID, idempotency_key: UUID, cycle_id: UUID) -> HandlerOutcome:
        command = build_external_payment_signal_command(case_id=case_id, payload=self._payload_source(), command_id=command_id, idempotency_key=idempotency_key, cycle_id=cycle_id)
        return self._dispatcher.dispatch(command=command, context=context)
