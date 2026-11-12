"""Two accepted texts cannot silently become one arbitrarily selected response."""

from datetime import UTC, datetime
from types import SimpleNamespace
from typing import cast
from unittest.mock import Mock
from uuid import uuid4

import pytest
from app.modules.preparation.application.transmission import PreparationTransmissionHandler
from app.modules.preparation.infrastructure.models import PreparationPackageRecord
from app.platform.events.dispatcher import CommandContext, CommandExecutionError


def test_distinct_reviewed_responses_are_refused_before_storage_or_database_write(monkeypatch):
    tenant, package_id, first, second = uuid4(), uuid4(), uuid4(), uuid4()
    package = cast(
        PreparationPackageRecord, SimpleNamespace(id=package_id, tenant_id=tenant, state="READY")
    )
    storage, session = Mock(), Mock()
    session.scalar.return_value = SimpleNamespace(state="READY")
    session.scalars.side_effect = [
        SimpleNamespace(all=lambda: [SimpleNamespace(version=1)]),
        SimpleNamespace(
            all=lambda: [SimpleNamespace(draft_id=first), SimpleNamespace(draft_id=second)]
        ),
    ]
    handler = PreparationTransmissionHandler(storage=storage)
    monkeypatch.setattr(
        handler,
        "current_c10_review_manifest",
        Mock(
            return_value=[
                {"draft_id": str(first), "content_sha256": "a" * 64},
                {"draft_id": str(second), "content_sha256": "b" * 64},
            ]
        ),
    )
    with pytest.raises(CommandExecutionError, match="RESPONSE_DRAFT_AMBIGUOUS"):
        handler._create_snapshot(
            session=session,
            package=package,
            command=SimpleNamespace(),
            context=CommandContext(
                tenant_id=tenant,
                actor_id=uuid4(),
                actor_kind="COLLABORATEUR",
                received_at=datetime.now(UTC),
            ),
        )
    storage.write.assert_not_called()
    session.add.assert_not_called()
