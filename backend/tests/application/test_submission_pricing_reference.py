"""Bound pricing metadata is observable, without changing P5 or exporting money."""

from datetime import timedelta
from uuid import UUID, uuid4

import pytest
from app.modules.submission.application.commands import PrepareSubmissionPackageCommand

from tests.application import test_submission_package as fixtures
from tests.application.test_submission_package import services as services
from tests.db.test_regulatory_profile_persistence import _case


def test_final_control_distinguishes_bound_price_from_a_new_published_price(
    services, session_factory, monkeypatch
):
    _, submission = services
    actor, preparation, case = fixtures._prepare_generated_document(services, session_factory)
    first_report = fixtures._publish_snapshot(
        session_factory, tenant_id=actor.tenant_id, case_id=case
    )
    command = PrepareSubmissionPackageCommand(
        command_id=uuid4(),
        idempotency_key=uuid4(),
        correlation_id=uuid4(),
        preparation_package_id=preparation,
        expected_preparation_revision=3,
    )
    receipt = submission.prepare(actor=actor, command=command, now=fixtures.NOW)
    package = UUID(receipt.aggregate_refs[0]["aggregate_id"])
    first = submission.read_final_control(
        actor=actor, submission_package_id=package, now=fixtures.NOW
    ).model_dump(mode="json")
    assert first["pricing_reference"]["state"] == "CURRENT"
    assert first["pricing_reference"]["referenced"] == dict(report_id=str(first_report), revision=4)
    monkeypatch.setattr(fixtures, "NOW", fixtures.NOW + timedelta(seconds=1))
    second_report = fixtures._publish_snapshot(
        session_factory, tenant_id=actor.tenant_id, case_id=case
    )
    second = submission.read_final_control(
        actor=actor, submission_package_id=package, now=fixtures.NOW
    ).model_dump(mode="json")
    assert second["pricing_reference"]["state"] == "REVIEW_REQUIRED"
    assert second["pricing_reference"]["referenced"] == first["pricing_reference"]["referenced"]
    assert second["pricing_reference"]["latest_published"]["report_id"] == str(second_report)
    assert second["manifest_sha256"] == first["manifest_sha256"]
    assert second["p5_authorization_status"] == first["p5_authorization_status"]
    assert second["entries_without_exported_file"] == first["entries_without_exported_file"]


@pytest.mark.parametrize("mode", ["FULL", "CANDIDATURE_ONLY"])
def test_other_case_prices_do_not_change_this_reference_or_the_candidature_scope(
    services, session_factory, monkeypatch, mode
):
    _, submission = services
    actor, preparation, case = fixtures._prepare_generated_document(services, session_factory)
    own_report = fixtures._publish_snapshot(
        session_factory, tenant_id=actor.tenant_id, case_id=case
    )
    foreign_case = uuid4()
    with session_factory.begin() as session:
        session.add(_case(tenant_id=actor.tenant_id, case_id=foreign_case, marker="a"))
    monkeypatch.setattr(fixtures, "NOW", fixtures.NOW + timedelta(seconds=1))
    fixtures._publish_snapshot(session_factory, tenant_id=actor.tenant_id, case_id=foreign_case)
    command = PrepareSubmissionPackageCommand(
        command_id=uuid4(),
        idempotency_key=uuid4(),
        correlation_id=uuid4(),
        preparation_package_id=preparation,
        expected_preparation_revision=3,
        submission_mode=mode,
        candidature_only_reason="Périmètre candidature explicite."
        if mode == "CANDIDATURE_ONLY"
        else None,
    )
    prepared = submission.prepare(actor=actor, command=command, now=fixtures.NOW)
    control = submission.read_final_control(
        actor=actor,
        submission_package_id=UUID(prepared.aggregate_refs[0]["aggregate_id"]),
        now=fixtures.NOW,
    ).model_dump(mode="json")
    price = control["pricing_reference"]
    assert price["state"] == ("CURRENT" if mode == "FULL" else "NOT_APPLICABLE")
    if mode == "FULL":
        assert price["latest_published"]["report_id"] == str(own_report)
    else:
        assert price["referenced"] is price["latest_published"] is None


def test_malformed_manifest_keeps_the_controlled_integrity_refusal(
    services, session_factory, monkeypatch
):
    import hashlib
    import json
    from unittest.mock import MagicMock

    from app.modules.submission.infrastructure.models import SubmissionPackageRecord
    from app.platform.events.dispatcher import CommandExecutionError

    _, submission = services
    actor, preparation, case = fixtures._prepare_generated_document(services, session_factory)
    fixtures._publish_snapshot(session_factory, tenant_id=actor.tenant_id, case_id=case)
    prepared = submission.prepare(
        actor=actor,
        command=PrepareSubmissionPackageCommand(
            command_id=uuid4(),
            idempotency_key=uuid4(),
            correlation_id=uuid4(),
            preparation_package_id=preparation,
            expected_preparation_revision=3,
        ),
        now=fixtures.NOW,
    )
    identifier = UUID(prepared.aggregate_refs[0]["aggregate_id"])
    with session_factory() as session:
        record = session.get(SubmissionPackageRecord, identifier)
        session.expunge(record)
    record.manifest_json = dict(record.manifest_json, entries=None)
    record.manifest_sha256 = hashlib.sha256(
        json.dumps(
            record.manifest_json, ensure_ascii=False, sort_keys=True, separators=(",", ":")
        ).encode()
    ).hexdigest()
    factory = MagicMock()
    factory.begin.return_value.__enter__.return_value.scalar.side_effect = [record, None]
    monkeypatch.setattr(submission, "_session_factory", factory)
    with pytest.raises(CommandExecutionError, match="SUBMISSION_MANIFEST_INTEGRITY_FAILED"):
        submission.read_final_control(
            actor=actor, submission_package_id=identifier, now=fixtures.NOW
        )
