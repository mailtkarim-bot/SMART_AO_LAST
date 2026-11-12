# ruff: noqa: E501, I001
from datetime import UTC, datetime
from typing import cast
from uuid import uuid4
from app.platform.events.dispatcher import CommandContext, CommandDispatcher, DispatchResult
from app.modules.pricing.infrastructure.local_payment_external_collector import (
    LocalPaymentExternalCollector,
)


class Dispatcher:
    def dispatch(self, *, command, context):
        return DispatchResult(
            status="SUCCEEDED",
            command_id=str(command.command_id),
            idempotency_key=str(command.idempotency_key),
            result_code="RECORDED",
            aggregate_refs=(),
            event_ids=(),
        )


def test_resilient_collection_reports_rejection_without_losing_valid_fixture():
    payloads = iter(
        (
            {"source_ref": "fixture://valid", "trigger_event": "EXTERNAL_PAYMENT_SIGNAL"},
            {"trigger_event": "EXTERNAL_PAYMENT_SIGNAL"},
        )
    )
    collector = LocalPaymentExternalCollector(
        dispatcher=cast(CommandDispatcher, Dispatcher()),
        payload_source=lambda: dict[str, object](next(payloads)),
    )
    report = collector.collect_many_resilient(
        case_id=uuid4(),
        context=CommandContext(
            tenant_id=uuid4(),
            actor_id=uuid4(),
            actor_kind="PATRON_ADMIN",
            received_at=datetime(2026, 10, 9, tzinfo=UTC),
        ),
        identities=((uuid4(), uuid4(), uuid4()), (uuid4(), uuid4(), uuid4())),
    )
    assert len(report.recorded) == 1
    assert report.rejected == ("PAYMENT_EXTERNAL_SOURCE_REQUIRED",)
