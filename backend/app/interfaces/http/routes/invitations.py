"""HTTP boundary for the first nominative invitation proof."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Header, HTTPException, Response, status
from pydantic import BaseModel, ConfigDict, Field

from app.interfaces.http.dependencies.auth import resolve_bearer_context as _resolve_context
from app.interfaces.http.routes.consultations import ConsultationSecurityRuntime
from app.platform.security.invitations import (
    InvitationConflictError,
    InvitationIssueResult,
    InvitationService,
    InvitationUnavailableError,
)


class CreateInvitationRequest(BaseModel):
    email: str = Field(min_length=3, max_length=320)


class VerifyInvitationRequest(BaseModel):
    token: str = Field(min_length=1, max_length=512)


class AcceptInvitationRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    token: str = Field(min_length=1, max_length=512)
    password: str = Field(min_length=1, max_length=1024)


class InvitationIssuedResponse(BaseModel):
    invitation_id: UUID
    token: str
    expires_at: datetime


def build_invitation_router(
    *,
    service: InvitationService,
    security_runtime: ConsultationSecurityRuntime,
) -> APIRouter:
    router = APIRouter(tags=["invitations"])

    @router.post(
        "/api/v1/patron/invitations",
        status_code=status.HTTP_201_CREATED,
        response_model=InvitationIssuedResponse,
    )
    def issue_invitation(
        request: CreateInvitationRequest,
        authorization: str | None = Header(default=None),
    ) -> InvitationIssuedResponse:
        actor = _resolve_context(
            authorization=authorization,
            context_resolver=security_runtime.context_resolver,
        )
        try:
            return _response(service.issue(actor=actor, email=request.email))
        except ValueError as error:
            raise HTTPException(status_code=422, detail="INVALID_EMAIL") from error
        except InvitationConflictError as error:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="MEMBERSHIP_OR_INVITATION_EXISTS",
            ) from error
        except PermissionError as error:
            raise _forbidden(error) from error

    @router.post(
        "/api/v1/patron/invitations/{invitation_id}/reissue",
        response_model=InvitationIssuedResponse,
    )
    def reissue_invitation(
        invitation_id: UUID,
        authorization: str | None = Header(default=None),
    ) -> InvitationIssuedResponse:
        actor = _resolve_context(
            authorization=authorization,
            context_resolver=security_runtime.context_resolver,
        )
        try:
            return _response(service.reissue(actor=actor, invitation_id=invitation_id))
        except InvitationUnavailableError as error:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="NOT_FOUND_OR_FORBIDDEN",
            ) from error
        except PermissionError as error:
            raise _forbidden(error) from error

    @router.post("/api/v1/invitations/verify", status_code=status.HTTP_204_NO_CONTENT)
    def verify_invitation(request: VerifyInvitationRequest) -> Response:
        try:
            service.verify(token=request.token)
        except InvitationUnavailableError as error:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="INVITATION_UNAVAILABLE",
            ) from error
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    @router.post("/api/v1/invitations/accept", status_code=status.HTTP_204_NO_CONTENT)
    def accept_invitation(request: AcceptInvitationRequest) -> Response:
        try:
            service.accept(token=request.token, password=request.password)
        except InvitationUnavailableError as error:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="INVITATION_UNAVAILABLE",
            ) from error
        except ValueError as error:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail="INVALID_PASSWORD",
            ) from error
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    return router


def _response(result: InvitationIssueResult) -> InvitationIssuedResponse:
    return InvitationIssuedResponse(
        invitation_id=result.invitation_id,
        token=result.token,
        expires_at=result.expires_at,
    )


def _forbidden(error: PermissionError) -> HTTPException:
    detail = "STEP_UP_REQUIRED" if str(error) == "STEP_UP_REQUIRED" else "FORBIDDEN"
    return HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=detail)
