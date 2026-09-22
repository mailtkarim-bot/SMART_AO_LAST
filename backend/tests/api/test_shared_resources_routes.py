from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

import pytest
from app.interfaces.http.routes.shared_resources import (
    SharedResourcePreviewRequest,
    SharedResourcePreviewResponse,
    build_shared_resource_router,
)
from app.platform.security.resource_sharing import SharedResource
from fastapi import HTTPException


class FakeSharingService:
    def __init__(self) -> None:
        self.shared = SharedResource(
            share_id=uuid4(),
            resource_type="SUBMISSION_PACKAGE",
            resource_id=uuid4(),
            resource_fingerprint="a" * 64,
            purpose="Relecture du paquet.",
            classification="INTERNAL_OPERATIONAL",
            recipient_ref="client@example.test",
            starts_at=datetime(2026, 9, 20, 14, 0, tzinfo=UTC),
            expires_at=datetime(2026, 9, 20, 15, 0, tzinfo=UTC),
        )

    def read(self, *, recipient_ref: str, access_token: str, now: datetime) -> SharedResource:
        if recipient_ref != "client@example.test" or access_token != "secret-token":
            raise PermissionError("SHARE_NOT_AVAILABLE")
        return self.shared


def _endpoint(service: FakeSharingService):
    return build_shared_resource_router(service=service).routes[0].endpoint  # type: ignore[arg-type]


def test_recipient_preview_returns_exact_version_metadata_without_storage_details() -> None:
    response = _endpoint(FakeSharingService())(
        SharedResourcePreviewRequest(
            recipient_ref="client@example.test", access_token="secret-token"
        )
    )
    assert isinstance(response, SharedResourcePreviewResponse)
    assert response.resource_fingerprint == "a" * 64
    assert not hasattr(response, "access_token")
    assert not hasattr(response, "recipient_ref")


def test_recipient_preview_is_neutral_for_wrong_or_expired_share() -> None:
    with pytest.raises(HTTPException) as error:
        _endpoint(FakeSharingService())(
            SharedResourcePreviewRequest(
                recipient_ref="other@example.test", access_token="secret-token"
            )
        )
    assert error.value.status_code == 404
    assert error.value.detail == "SHARE_NOT_AVAILABLE"
