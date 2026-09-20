"""SEC-01 guarded read-only Case « À résoudre » projection."""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

from fastapi import APIRouter, Header, HTTPException, status

from app.interfaces.http.dependencies.auth import resolve_bearer_context as _resolve_context
from app.interfaces.http.routes.consultations import ConsultationSecurityRuntime
from app.modules.case.public.contracts import (
    CaseEconomicCoverageResponse,
    CaseEconomicCoverageStatusResponse,
    CaseResolutionIndexResponse,
    CaseResolutionItemResponse,
)
from app.platform.security.authorization import AuthorizationRequest, AuthorizationResource
from app.platform.security.capabilities import Capability
from app.platform.security.context import ActorKind, DataClassification


def build_case_resolution_router(
    *, runtime, security_runtime: ConsultationSecurityRuntime
) -> APIRouter:
    router = APIRouter(prefix="/api/v1/cases", tags=["cases"])

    @router.get("/{case_id}/resolution", response_model=CaseResolutionIndexResponse)
    def get_case_resolution(
        case_id: UUID,
        authorization: str | None = Header(default=None),
    ) -> CaseResolutionIndexResponse:
        context = _resolve_context(
            authorization=authorization,
            context_resolver=security_runtime.context_resolver,
        )
        owner_tenant_id = runtime.get_case_tenant_id(case_id=case_id)
        if owner_tenant_id is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="NOT_FOUND_OR_FORBIDDEN",
            )
        if context.actor_kind not in {ActorKind.PATRON_ADMIN, ActorKind.COLLABORATEUR}:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="FORBIDDEN")

        action = (
            Capability.WORK_TASK_READ
            if context.actor_kind is ActorKind.COLLABORATEUR
            else Capability.CASE_DCE_READ
        )
        decision = security_runtime.policy.authorize(
            context=context,
            request=AuthorizationRequest(
                action=action,
                resource=AuthorizationResource(
                    resource_type="CASE_RESOLUTION_INDEX",
                    resource_id=case_id,
                    tenant_id=owner_tenant_id,
                    classification=DataClassification.INTERNAL_OPERATIONAL,
                    case_id=case_id,
                ),
                evaluated_at=datetime.now(tz=UTC),
            ),
        )
        if not decision.allowed:
            if decision.http_status_code == status.HTTP_404_NOT_FOUND:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="NOT_FOUND_OR_FORBIDDEN",
                )
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="FORBIDDEN")

        projection = runtime.get_case_resolution_index(
            tenant_id=context.tenant_id,
            case_id=case_id,
            membership_id=(
                context.membership_id
                if context.actor_kind is ActorKind.COLLABORATEUR
                else None
            ),
        )
        if projection is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="NOT_FOUND_OR_FORBIDDEN",
            )
        return CaseResolutionIndexResponse(
            case_id=projection.case_id,
            work_label=projection.work_label,
            coverage=projection.coverage,
            items=[
                CaseResolutionItemResponse(
                    item_id=item.item_id,
                    item_kind=item.item_kind,
                    native_state=item.native_state,
                    source_refs=list(item.source_refs),
                    resolution_owner=item.resolution_owner,
                    next_action=item.next_action,
                    due_at=item.due_at,
                    impact=item.impact,
                )
                for item in projection.items
            ],
            economic_coverage=(
                CaseEconomicCoverageResponse(
                    assumptions=CaseEconomicCoverageStatusResponse(
                        state=projection.economic_coverage.assumptions.state,
                        source_refs=list(projection.economic_coverage.assumptions.source_refs),
                        note=projection.economic_coverage.assumptions.note,
                    ),
                    quote_validity=CaseEconomicCoverageStatusResponse(
                        state=projection.economic_coverage.quote_validity.state,
                        source_refs=list(projection.economic_coverage.quote_validity.source_refs),
                        note=projection.economic_coverage.quote_validity.note,
                    ),
                    capacity=CaseEconomicCoverageStatusResponse(
                        state=projection.economic_coverage.capacity.state,
                        source_refs=list(projection.economic_coverage.capacity.source_refs),
                        note=projection.economic_coverage.capacity.note,
                    ),
                    financing=CaseEconomicCoverageStatusResponse(
                        state=projection.economic_coverage.financing.state,
                        source_refs=list(projection.economic_coverage.financing.source_refs),
                        note=projection.economic_coverage.financing.note,
                    ),
                )
                if projection.economic_coverage is not None
                else None
            ),
        )

    return router
