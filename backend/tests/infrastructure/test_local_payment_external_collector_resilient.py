# ruff: noqa: E501, I001
from uuid import uuid4
from app.modules.pricing.infrastructure.local_payment_external_collector import LocalPaymentExternalCollector

class Dispatcher:
    def dispatch(self, *, command, context): return type("Outcome", (), {"result_code": "RECORDED"})()

def test_resilient_collection_reports_rejection_without_losing_valid_fixture():
    payloads = iter(({"source_ref": "fixture://valid", "trigger_event": "EXTERNAL_PAYMENT_SIGNAL"}, {"trigger_event": "EXTERNAL_PAYMENT_SIGNAL"}))
    collector = LocalPaymentExternalCollector(dispatcher=Dispatcher(), payload_source=lambda: next(payloads))
    report = collector.collect_many_resilient(case_id=uuid4(), context=None, identities=((uuid4(), uuid4(), uuid4()), (uuid4(), uuid4(), uuid4())))
    assert len(report.recorded) == 1
    assert report.rejected == ("PAYMENT_EXTERNAL_SOURCE_REQUIRED",)
