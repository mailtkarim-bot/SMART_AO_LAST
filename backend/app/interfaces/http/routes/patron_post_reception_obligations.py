# ruff: noqa: E501, E701, I001
from datetime import UTC, datetime
from uuid import UUID

from fastapi import APIRouter, Header, HTTPException, status
from fastapi.responses import JSONResponse

from app.interfaces.http.dependencies.auth import resolve_bearer_context
from app.interfaces.http.routes.consultations import ConsultationSecurityRuntime
from app.modules.pricing.application.post_reception_obligation_commands import (
    RecordPostReceptionObligationCommand,
)
from app.modules.pricing.application.post_reception_obligation_transition_commands import (
    TransitionPostReceptionObligationCommand,
)
from app.modules.pricing.application.post_reception_obligation_read_handler import (
    PostReceptionObligationReadService,
)
from app.modules.pricing.public.post_reception_obligation_contracts import (
    PostReceptionObligationResponse,
    RecordPostReceptionObligationRequest,
    RecordPostReceptionObligationResponse,
    TransitionPostReceptionObligationRequest,
    TransitionPostReceptionObligationResponse,
)
from app.platform.events.dispatcher import CommandContext, CommandDispatcher, CommandExecutionError
from app.platform.security.context import ActorKind


def build_patron_post_reception_obligations_router(
    *,
    dispatcher: CommandDispatcher,
    service: PostReceptionObligationReadService,
    security_runtime: ConsultationSecurityRuntime,
) -> APIRouter:
    router = APIRouter(prefix="/api/v1/patron", tags=["patron-post-reception-obligations"])

    @router.post(
        "/cases/{case_id}/post-reception-obligations",
        response_model=RecordPostReceptionObligationResponse,
    )
    def record(
        case_id: UUID,
        request: RecordPostReceptionObligationRequest,
        authorization: str | None = Header(default=None),
    ):
        actor = resolve_bearer_context(
            authorization=authorization, context_resolver=security_runtime.context_resolver
        )
        if actor.actor_kind is not ActorKind.PATRON_ADMIN or actor.membership_id is None:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="FORBIDDEN")
        try:
            result = dispatcher.dispatch(
                command=RecordPostReceptionObligationCommand(
                    **request.model_dump(exclude={"obligation_id"}),
                    obligation_id=request.obligation_id,
                    case_id=case_id,
                ),
                context=CommandContext(
                    tenant_id=actor.tenant_id,
                    actor_id=actor.actor_id,
                    actor_kind=actor.actor_kind.value,
                    received_at=datetime.now(tz=UTC),
                    identity_id=actor.identity_id,
                    membership_id=actor.membership_id,
                    session_id=actor.session_id,
                    case_id=case_id,
                    correlation_id=actor.correlation_id,
                ),
            )
        except CommandExecutionError as error:
            error_code = str(error)
            http_status = (
                status.HTTP_409_CONFLICT
                if "ID_REUSED" in error_code
                else status.HTTP_404_NOT_FOUND
                if "NOT_FOUND" in error_code or "FORBIDDEN" in error_code
                else status.HTTP_422_UNPROCESSABLE_ENTITY
            )
            raise HTTPException(status_code=http_status, detail=error_code) from error
        return JSONResponse(
            status_code=status.HTTP_200_OK if result.replayed else status.HTTP_201_CREATED,
            content=RecordPostReceptionObligationResponse(
                command_id=UUID(result.command_id),
                idempotency_key=UUID(result.idempotency_key),
                obligation_id=request.obligation_id,
                result_code=result.result_code,
                replayed=result.replayed,
            ).model_dump(mode="json"),
        )

    @router.get(
        "/cases/{case_id}/post-reception-obligations",
        response_model=list[PostReceptionObligationResponse],
    )
    def list_for_case(case_id: UUID, authorization: str | None = Header(default=None)):
        actor = resolve_bearer_context(
            authorization=authorization, context_resolver=security_runtime.context_resolver
        )
        try:
            rows = service.list_for_case(actor=actor, case_id=case_id)
        except PermissionError as error:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="FORBIDDEN"
            ) from error
        result = []
        for projection in rows:
            row = getattr(projection, "record", projection)
            latest = getattr(projection, "latest_transition", None)
            result.append(
                PostReceptionObligationResponse(
                    obligation_id=row.id,
                    case_id=row.case_id,
                    obligation_type=row.obligation_type,
                    origin_reception_act_id=getattr(row, "origin_reception_act_id", None),
                    origin_reception_summary=getattr(projection, "origin_reception_summary", None),
                    origin_reception_outcome=getattr(
                        projection, "origin_reception_outcome", "UNKNOWN"
                    ),
                    summary=row.summary,
                    source_refs=row.source_refs_json,
                    due_date=row.due_date,
                    resource_note=row.resource_note,
                    cost_estimate_note=row.cost_estimate_note,
                    fulfillment_proof_refs=row.fulfillment_proof_refs_json,
                    sanction_ref=row.sanction_ref,
                    status=getattr(projection, "status", row.status),
                    revision=getattr(projection, "revision", 0),
                    latest_transition_id=latest.id if latest else None,
                    latest_transition_actor_id=latest.actor_id if latest else None,
                    latest_transition_at=latest.created_at if latest else None,
                    latest_transition_rationale=latest.rationale if latest else None,
                    completion_proof_refs=latest.evidence_refs_json
                    if latest and latest.resulting_status == "COMPLETED"
                    else [],
                    actor_id=row.actor_id,
                    created_at=row.created_at,
                )
            )
        return result

    @router.post(
        "/cases/{case_id}/post-reception-obligations/{obligation_id}/transitions",
        response_model=TransitionPostReceptionObligationResponse,
    )
    def transition(
        case_id: UUID,
        obligation_id: UUID,
        request: TransitionPostReceptionObligationRequest,
        authorization: str | None = Header(default=None),
    ):
        actor = resolve_bearer_context(
            authorization=authorization, context_resolver=security_runtime.context_resolver
        )
        if actor.actor_kind is not ActorKind.PATRON_ADMIN or actor.membership_id is None:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="FORBIDDEN")
        try:
            result = dispatcher.dispatch(
                command=TransitionPostReceptionObligationCommand(
                    **request.model_dump(exclude={"transition_id"}),
                    transition_id=request.transition_id,
                    obligation_id=obligation_id,
                    case_id=case_id,
                ),
                context=CommandContext(
                    tenant_id=actor.tenant_id,
                    actor_id=actor.actor_id,
                    actor_kind=actor.actor_kind.value,
                    received_at=datetime.now(tz=UTC),
                    identity_id=actor.identity_id,
                    membership_id=actor.membership_id,
                    session_id=actor.session_id,
                    case_id=case_id,
                    correlation_id=actor.correlation_id,
                ),
            )
        except CommandExecutionError as error:
            error_code = str(error)
            http_status = (
                status.HTTP_409_CONFLICT
                if "REVISION_CONFLICT" in error_code or "ID_REUSED" in error_code
                else status.HTTP_404_NOT_FOUND
                if "NOT_FOUND" in error_code or "FORBIDDEN" in error_code
                else status.HTTP_422_UNPROCESSABLE_ENTITY
            )
            raise HTTPException(status_code=http_status, detail=error_code) from error
        revision = result.aggregate_refs[0]["aggregate_revision"]
        return JSONResponse(
            status_code=status.HTTP_200_OK if result.replayed else status.HTTP_201_CREATED,
            content=TransitionPostReceptionObligationResponse(
                command_id=UUID(result.command_id),
                idempotency_key=UUID(result.idempotency_key),
                transition_id=request.transition_id,
                result_code=result.result_code,
                aggregate_revision=revision,
                replayed=result.replayed,
            ).model_dump(mode="json"),
        )

    return router
