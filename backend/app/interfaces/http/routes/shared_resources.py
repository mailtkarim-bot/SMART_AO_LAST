"""Neutral recipient preview for an exact, expiring shared resource."""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, ConfigDict, Field

from app.platform.security.resource_sharing import ResourceSharingService


class SharedResourcePreviewRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    recipient_ref: str = Field(min_length=1, max_length=320)
    access_token: str = Field(min_length=1, max_length=512)


class SharedResourcePreviewResponse(BaseModel):
    share_id: UUID
    resource_type: str
    resource_id: UUID
    resource_fingerprint: str
    purpose: str
    classification: str
    starts_at: datetime
    expires_at: datetime


def build_shared_resource_router(*, service: ResourceSharingService) -> APIRouter:
    router = APIRouter(prefix="/api/v1/shared-resources", tags=["shared-resources"])

    @router.post("/preview", response_model=SharedResourcePreviewResponse)
    def preview_shared_resource(
        request: SharedResourcePreviewRequest,
    ) -> SharedResourcePreviewResponse:
        try:
            shared = service.read(
                recipient_ref=request.recipient_ref,
                access_token=request.access_token,
                now=datetime.now(tz=UTC),
            )
        except PermissionError as error:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="SHARE_NOT_AVAILABLE",
            ) from error
        return SharedResourcePreviewResponse(
            share_id=shared.share_id,
            resource_type=shared.resource_type,
            resource_id=shared.resource_id,
            resource_fingerprint=shared.resource_fingerprint,
            purpose=shared.purpose,
            classification=shared.classification,
            starts_at=shared.starts_at,
            expires_at=shared.expires_at,
        )

    return router
