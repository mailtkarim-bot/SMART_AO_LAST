"""Exact response selection is explicit and cannot change a legacy retry hash."""

from uuid import uuid4

from app.modules.preparation.application.transmission_commands import (
    CreatePreparationSnapshotCommand,
)


def test_snapshot_accepts_exact_selection_and_keeps_legacy_serialization():
    fields = dict(
        command_id=uuid4(),
        idempotency_key=uuid4(),
        package_id=uuid4(),
        snapshot_id=uuid4(),
        expected_package_revision=6,
    )
    legacy = CreatePreparationSnapshotCommand(**fields)
    assert "selected_response_draft" not in legacy.model_dump(mode="json")
    selection = dict(draft_id=str(uuid4()), version=2, content_sha256="a" * 64)
    command = CreatePreparationSnapshotCommand(**fields, selected_response_draft=selection)
    assert command.model_dump(mode="json")["selected_response_draft"] == selection


def test_selection_reviews_only_the_exact_current_draft():
    from hashlib import sha256
    from types import SimpleNamespace
    from typing import cast
    from unittest.mock import Mock

    from app.modules.preparation.application.transmission import PreparationTransmissionHandler
    from app.modules.preparation.infrastructure.models import PreparationPackageRecord

    content = b"# Two contributions with explicit missing information"
    digest = sha256(content).hexdigest()
    selected, other, plan_id, tenant = uuid4(), uuid4(), uuid4(), uuid4()
    plan = SimpleNamespace(
        state="SOURCES_CURRENT", plan_id=plan_id, version=2, dce_version_id=uuid4()
    )
    package = cast(
        PreparationPackageRecord,
        SimpleNamespace(id=uuid4(), dce_version_id=plan.dce_version_id, case_id=uuid4()),
    )
    drafts = [
        SimpleNamespace(
            draft_id=i,
            version=3,
            content_sha256=digest if i == selected else "b" * 64,
            response_plan_id=plan_id,
            response_plan_version=2,
            storage_key=str(i),
        )
        for i in (selected, other)
    ]
    review = SimpleNamespace(
        review_id=uuid4(),
        revision=2,
        target_draft_id=selected,
        target_draft_version=3,
        target_content_sha256=digest,
        state="ACCEPTED",
    )
    session, storage = Mock(), Mock()
    session.scalar.return_value = plan
    session.scalars.side_effect = [Mock(all=lambda: drafts), Mock(all=lambda: [review])]
    storage.read.return_value = content
    result = PreparationTransmissionHandler(storage=storage).current_c10_review_manifest(
        session=session,
        package=package,
        tenant_id=tenant,
        selected_response_draft=dict(draft_id=str(selected), version=3, content_sha256=digest),
    )
    assert result is not None
    assert [entry["draft_id"] for entry in result] == [str(selected)]
    storage.read.assert_called_once_with(storage_key=str(selected))


def test_owned_content_verifier_keeps_bad_or_missing_bytes_unknown(monkeypatch):
    from datetime import UTC, datetime
    from hashlib import sha256
    from types import SimpleNamespace
    from unittest.mock import Mock

    from app.modules.preparation.application.service import PreparationService

    storage = Mock()
    service = PreparationService(
        session_factory=Mock(), dispatcher=Mock(), policy=Mock(), storage=storage
    )
    draft = SimpleNamespace(
        draft_id=uuid4(),
        version=1,
        storage_key="owned/draft.md",
        content_sha256=sha256(b"expected").hexdigest(),
    )
    scoped = Mock(return_value=(Mock(), None, (), (draft,)))
    monkeypatch.setattr(service, "read_package", scoped)
    actor = Mock()
    package = uuid4()
    now = datetime.now(UTC)
    storage.read.return_value = b"changed"
    result = service.read_package_with_verified_drafts(actor=actor, package_id=package, now=now)
    assert result[4][(draft.draft_id, 1)] is None
    scoped.assert_called_once_with(actor=actor, package_id=package, now=now)
    storage.read.side_effect = FileNotFoundError()
    assert (
        service.read_package_with_verified_drafts(actor=actor, package_id=package, now=now)[4][
            (draft.draft_id, 1)
        ]
        is None
    )
    storage.reset_mock()
    scoped.side_effect = PermissionError("NOT_FOUND_OR_FORBIDDEN")
    import pytest

    with pytest.raises(PermissionError):
        service.read_package_with_verified_drafts(actor=actor, package_id=package, now=now)
    storage.read.assert_not_called()
