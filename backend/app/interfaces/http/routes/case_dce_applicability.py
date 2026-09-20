"""SEC-01 guarded transport for linking an admitted DCE version to one Case."""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

from fastapi import APIRouter, Header, HTTPException, status
from fastapi.responses import JSONResponse

from app.interfaces.http.dependencies.auth import resolve_bearer_context
from app.interfaces.http.routes.consultations import ConsultationSecurityRuntime
from app.modules.case.application.commands import LinkCaseDceVersionCommand
from app.modules.case.public.contracts import (
    LinkCaseDceVersionRequest,
    LinkCaseDceVersionResponse,
)
from app.platform.events.dispatcher import (
    CommandContext,
    CommandExecutionError,
    IdempotencyKeyReusedError,
)
from app.platform.security.authorization import AuthorizationRequest, AuthorizationResource
from app.platform.security.capabilities import Capability
from app.platform.security.context import DataClassification


def build_case_dce_applicability_router(
    *, runtime, security_runtime: ConsultationSecurityRuntime
) -> APIRouter:
    router = APIRouter(prefix="/api/v1/cases", tags=["cases"])

    @router.post(
        "/{case_id}/dce-applicability",
        response_model=LinkCaseDceVersionResponse,
        status_code=status.HTTP_201_CREATED,
    )
    def link_case_dce_version(
        case_id: UUID,
        request: LinkCaseDceVersionRequest,
        authorization: str | None = Header(default=None),
    ) -> JSONResponse:
        context = resolve_bearer_context(
            authorization=authorization,
            context_resolver=security_runtime.context_resolver,
        )
        owner_tenant_id = runtime.get_case_tenant_id(case_id=case_id)
        if owner_tenant_id is None:
            raise HTTPException(status_code=404, detail="NOT_FOUND_OR_FORBIDDEN")
        decision = security_runtime.policy.authorize(
            context=context,
            request=AuthorizationRequest(
                action=Capability.DCE_PREPARE,
                resource=AuthorizationResource(
                    resource_type="CASE_DCE_APPLICABILITY",
                    resource_id=case_id,
                    tenant_id=owner_tenant_id,
                    classification=DataClassification.INTERNAL_OPERATIONAL,
                    case_id=case_id,
                ),
                evaluated_at=datetime.now(tz=UTC),
            ),
        )
        if not decision.allowed:
            raise HTTPException(status_code=decision.http_status_code, detail=decision.code)
        try:
            result = runtime.dispatcher.dispatch(
                command=LinkCaseDceVersionCommand(case_id=case_id, **request.model_dump()),
                context=CommandContext(
                    tenant_id=str(context.tenant_id),
                    actor_id=str(context.actor_id),
                    actor_kind=context.actor_kind.value,
                    received_at=datetime.now(tz=UTC),
                    identity_id=str(context.identity_id),
                    membership_id=str(context.membership_id),
                    session_id=str(context.session_id),
                    case_id=str(case_id),
                    correlation_id=str(request.correlation_id or request.command_id),
                ),
            )
        except IdempotencyKeyReusedError as error:
            raise HTTPException(status_code=409, detail="IDEMPOTENCY_KEY_REUSED") from error
        except CommandExecutionError as error:
            raise HTTPException(status_code=422, detail="COMMAND_REJECTED") from error
        response = LinkCaseDceVersionResponse(
            command_id=result.command_id,
            idempotency_key=result.idempotency_key,
            result_code=result.result_code,
            aggregate_refs=[dict(ref) for ref in result.aggregate_refs],
            event_ids=[UUID(event_id) for event_id in result.event_ids],
            replayed=result.replayed,
        )
        return JSONResponse(
            status_code=status.HTTP_200_OK if result.replayed else status.HTTP_201_CREATED,
            content=response.model_dump(mode="json"),
        )

    return router
