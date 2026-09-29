# ruff: noqa: E501, I001
from datetime import UTC, datetime
from uuid import UUID

from fastapi import APIRouter, Header, HTTPException, status
from fastapi.responses import JSONResponse

from app.interfaces.http.dependencies.auth import resolve_bearer_context
from app.interfaces.http.routes.consultations import ConsultationSecurityRuntime
from app.modules.pricing.application.contract_execution_evidence_commands import (
    DeclareContractInstrumentSupersessionCommand,
    RecordContractExecutionEvidenceCommand,
    RecordContractExecutionEvidenceRequalificationCommand,
    RecordContractInstrumentVersionCommand,
)
from app.modules.pricing.application.contract_execution_evidence_read_handler import (
    ContractExecutionEvidenceReadService,
    ContractInstrumentSupersessionReadService,
    ContractInstrumentVersionReadService,
)
from app.modules.pricing.application.contract_execution_evidence_requalification_read_handler import (
    ContractExecutionEvidenceRequalificationReadService,
)
from app.modules.pricing.application.contract_execution_evidence_timeline_read_handler import (
    ContractExecutionEvidenceTimelineReadService,
)
from app.modules.pricing.public.contract_execution_evidence_contracts import (
    ContractExecutionEvidenceResponse,
    ContractExecutionEvidenceRequalificationResponse,
    ContractExecutionEvidenceTimelineEvent,
    ContractInstrumentSupersessionResponse,
    ContractInstrumentVersionResponse,
    ContractInstrumentVersionSummary,
    DeclareContractInstrumentSupersessionRequest,
    DeclareContractInstrumentSupersessionResponse,
    RecordContractExecutionEvidenceRequest,
    RecordContractExecutionEvidenceRequalificationRequest,
    RecordContractExecutionEvidenceRequalificationResponse,
    RecordContractExecutionEvidenceResponse,
    RecordContractInstrumentVersionRequest,
    RecordContractInstrumentVersionResponse,
)
from app.platform.events.dispatcher import CommandContext, CommandDispatcher, CommandExecutionError
from app.platform.security.context import ActorKind


def build_patron_contract_execution_evidence_router(
    *,
    dispatcher: CommandDispatcher,
    service: ContractExecutionEvidenceReadService,
    instrument_version_service: ContractInstrumentVersionReadService,
    supersession_service: ContractInstrumentSupersessionReadService,
    requalification_service: ContractExecutionEvidenceRequalificationReadService,
    timeline_service: ContractExecutionEvidenceTimelineReadService,
    security_runtime: ConsultationSecurityRuntime,
) -> APIRouter:
    router = APIRouter(prefix="/api/v1/patron", tags=["patron-contract-execution-evidence"])

    @router.post(
        "/cases/{case_id}/contract-execution-evidence",
        response_model=RecordContractExecutionEvidenceResponse,
    )
    def record(
        case_id: UUID,
        request: RecordContractExecutionEvidenceRequest,
        authorization: str | None = Header(default=None),
    ):
        actor = resolve_bearer_context(
            authorization=authorization, context_resolver=security_runtime.context_resolver
        )
        if actor.actor_kind is not ActorKind.PATRON_ADMIN or actor.membership_id is None:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="FORBIDDEN")
        try:
            result = dispatcher.dispatch(
                command=RecordContractExecutionEvidenceCommand(
                    **request.model_dump(exclude={"act_id"}),
                    act_id=request.act_id,
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
            content=RecordContractExecutionEvidenceResponse(
                command_id=UUID(result.command_id),
                idempotency_key=UUID(result.idempotency_key),
                act_id=request.act_id,
                result_code=result.result_code,
                replayed=result.replayed,
            ).model_dump(mode="json"),
        )

    @router.get(
        "/cases/{case_id}/contract-execution-evidence",
        response_model=list[ContractExecutionEvidenceResponse],
    )
    def list_for_case(case_id: UUID, authorization: str | None = Header(default=None)):
        actor = resolve_bearer_context(
            authorization=authorization, context_resolver=security_runtime.context_resolver
        )
        if actor.actor_kind is not ActorKind.PATRON_ADMIN or actor.membership_id is None:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="FORBIDDEN")
        try:
            rows = service.list_for_case(actor=actor, case_id=case_id)
        except PermissionError as error:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="FORBIDDEN"
            ) from error
        result = []
        for item in rows:
            row = getattr(item, "record", item)
            instrument = getattr(item, "contract_instrument_version", None)
            result.append(
                ContractExecutionEvidenceResponse(
                    act_id=row.id,
                    case_id=row.case_id,
                    act_kind=row.act_kind,
                    reception_outcome=getattr(
                        item,
                        "reception_outcome",
                        getattr(row, "reception_outcome", None) or "UNKNOWN",
                    ),
                    summary=row.summary,
                    source_refs=row.source_refs_json,
                    evidence_refs=row.evidence_refs_json,
                    declared_event_date=row.declared_event_date,
                    case_dce_version_id_at_recording=row.case_dce_version_id_at_recording,
                    version_relation=getattr(item, "version_relation", "UNKNOWN"),
                    contract_instrument_version_relation=getattr(
                        item, "contract_instrument_version_relation", "UNKNOWN"
                    ),
                    contract_instrument_version_id=row.contract_instrument_version_id,
                    contract_instrument_version=(
                        ContractInstrumentVersionSummary(
                            contract_instrument_version_id=instrument.id,
                            instrument_kind=instrument.instrument_kind,
                            version_reference=instrument.version_reference,
                            source_refs=instrument.source_refs_json,
                            evidence_refs=instrument.evidence_refs_json,
                        )
                        if instrument is not None
                        else None
                    ),
                    actor_id=row.actor_id,
                    recorded_at=row.created_at,
                )
            )
        return result

    @router.post(
        "/cases/{case_id}/contract-instrument-versions",
        response_model=RecordContractInstrumentVersionResponse,
    )
    def record_instrument_version(
        case_id: UUID,
        request: RecordContractInstrumentVersionRequest,
        authorization: str | None = Header(default=None),
    ):
        actor = resolve_bearer_context(
            authorization=authorization, context_resolver=security_runtime.context_resolver
        )
        if actor.actor_kind is not ActorKind.PATRON_ADMIN or actor.membership_id is None:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="FORBIDDEN")
        try:
            result = dispatcher.dispatch(
                command=RecordContractInstrumentVersionCommand(
                    **request.model_dump(exclude={"contract_instrument_version_id"}),
                    contract_instrument_version_id=request.contract_instrument_version_id,
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
                if "REUSED" in error_code or "ALREADY_RECORDED" in error_code
                else status.HTTP_404_NOT_FOUND
                if "NOT_FOUND" in error_code or "FORBIDDEN" in error_code
                else status.HTTP_422_UNPROCESSABLE_ENTITY
            )
            raise HTTPException(status_code=http_status, detail=error_code) from error
        return JSONResponse(
            status_code=status.HTTP_200_OK if result.replayed else status.HTTP_201_CREATED,
            content=RecordContractInstrumentVersionResponse(
                command_id=UUID(result.command_id),
                idempotency_key=UUID(result.idempotency_key),
                contract_instrument_version_id=request.contract_instrument_version_id,
                result_code=result.result_code,
                replayed=result.replayed,
            ).model_dump(mode="json"),
        )

    @router.get(
        "/cases/{case_id}/contract-instrument-versions",
        response_model=list[ContractInstrumentVersionResponse],
    )
    def list_instrument_versions(
        case_id: UUID,
        authorization: str | None = Header(default=None),
    ):
        actor = resolve_bearer_context(
            authorization=authorization, context_resolver=security_runtime.context_resolver
        )
        if actor.actor_kind is not ActorKind.PATRON_ADMIN or actor.membership_id is None:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="FORBIDDEN")
        try:
            rows = instrument_version_service.list_for_case(actor=actor, case_id=case_id)
        except PermissionError as error:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="FORBIDDEN"
            ) from error
        return [
            ContractInstrumentVersionResponse(
                contract_instrument_version_id=row.id,
                case_id=row.case_id,
                instrument_kind=row.instrument_kind,
                version_reference=row.version_reference,
                source_refs=row.source_refs_json,
                evidence_refs=row.evidence_refs_json,
                actor_id=row.actor_id,
                recorded_at=row.created_at,
            )
            for row in rows
        ]

    @router.post(
        "/cases/{case_id}/contract-instrument-supersessions",
        response_model=DeclareContractInstrumentSupersessionResponse,
    )
    def declare_supersession(
        case_id: UUID,
        request: DeclareContractInstrumentSupersessionRequest,
        authorization: str | None = Header(default=None),
    ):
        actor = resolve_bearer_context(
            authorization=authorization, context_resolver=security_runtime.context_resolver
        )
        if actor.actor_kind is not ActorKind.PATRON_ADMIN or actor.membership_id is None:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="FORBIDDEN")
        try:
            result = dispatcher.dispatch(
                command=DeclareContractInstrumentSupersessionCommand(
                    **request.model_dump(exclude={"supersession_id"}),
                    supersession_id=request.supersession_id,
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
                if "REUSED" in error_code or "ALREADY" in error_code
                else status.HTTP_404_NOT_FOUND
                if "NOT_FOUND" in error_code or "FORBIDDEN" in error_code
                else status.HTTP_422_UNPROCESSABLE_ENTITY
            )
            raise HTTPException(status_code=http_status, detail=error_code) from error
        return JSONResponse(
            status_code=status.HTTP_200_OK if result.replayed else status.HTTP_201_CREATED,
            content=DeclareContractInstrumentSupersessionResponse(
                command_id=UUID(result.command_id),
                idempotency_key=UUID(result.idempotency_key),
                supersession_id=request.supersession_id,
                result_code=result.result_code,
                replayed=result.replayed,
            ).model_dump(mode="json"),
        )

    @router.get(
        "/cases/{case_id}/contract-instrument-supersessions",
        response_model=list[ContractInstrumentSupersessionResponse],
    )
    def list_supersessions(case_id: UUID, authorization: str | None = Header(default=None)):
        actor = resolve_bearer_context(
            authorization=authorization, context_resolver=security_runtime.context_resolver
        )
        if actor.actor_kind is not ActorKind.PATRON_ADMIN or actor.membership_id is None:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="FORBIDDEN")
        try:
            rows = supersession_service.list_for_case(actor=actor, case_id=case_id)
        except PermissionError as error:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="FORBIDDEN"
            ) from error
        return [
            ContractInstrumentSupersessionResponse(
                supersession_id=item.record.id,
                case_id=item.record.case_id,
                replacing_contract_instrument_version_id=item.replacing_version.id,
                replacing_instrument_kind=item.replacing_version.instrument_kind,
                replacing_version_reference=item.replacing_version.version_reference,
                replaced_contract_instrument_version_id=item.replaced_version.id,
                replaced_instrument_kind=item.replaced_version.instrument_kind,
                replaced_version_reference=item.replaced_version.version_reference,
                rationale=item.record.rationale,
                actor_id=item.record.actor_id,
                recorded_at=item.record.created_at,
            )
            for item in rows
        ]

    @router.post(
        "/cases/{case_id}/contract-execution-evidence-requalifications",
        response_model=RecordContractExecutionEvidenceRequalificationResponse,
    )
    def record_requalification(
        case_id: UUID,
        request: RecordContractExecutionEvidenceRequalificationRequest,
        authorization: str | None = Header(default=None),
    ):
        actor = resolve_bearer_context(
            authorization=authorization, context_resolver=security_runtime.context_resolver
        )
        if actor.actor_kind is not ActorKind.PATRON_ADMIN or actor.membership_id is None:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="FORBIDDEN")
        try:
            result = dispatcher.dispatch(
                command=RecordContractExecutionEvidenceRequalificationCommand(
                    **request.model_dump(exclude={"requalification_id"}),
                    requalification_id=request.requalification_id,
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
                if "REUSED" in error_code or "REVISION_CONFLICT" in error_code
                else status.HTTP_404_NOT_FOUND
                if "NOT_FOUND" in error_code or "FORBIDDEN" in error_code
                else status.HTTP_422_UNPROCESSABLE_ENTITY
            )
            raise HTTPException(status_code=http_status, detail=error_code) from error
        return JSONResponse(
            status_code=status.HTTP_200_OK if result.replayed else status.HTTP_201_CREATED,
            content=RecordContractExecutionEvidenceRequalificationResponse(
                command_id=UUID(result.command_id),
                idempotency_key=UUID(result.idempotency_key),
                requalification_id=request.requalification_id,
                revision=request.expected_revision + 1,
                result_code=result.result_code,
                replayed=result.replayed,
            ).model_dump(mode="json"),
        )

    @router.get(
        "/cases/{case_id}/contract-execution-evidence-requalifications",
        response_model=list[ContractExecutionEvidenceRequalificationResponse],
    )
    def list_requalifications(case_id: UUID, authorization: str | None = Header(default=None)):
        actor = resolve_bearer_context(
            authorization=authorization, context_resolver=security_runtime.context_resolver
        )
        if actor.actor_kind is not ActorKind.PATRON_ADMIN or actor.membership_id is None:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="FORBIDDEN")
        try:
            rows = requalification_service.list_for_case(actor=actor, case_id=case_id)
        except PermissionError as error:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="FORBIDDEN"
            ) from error
        return [
            ContractExecutionEvidenceRequalificationResponse(
                requalification_id=item.record.id,
                case_id=item.record.case_id,
                act_id=item.act.id,
                act_kind=item.act.act_kind,
                act_summary=item.act.summary,
                supersession_id=item.supersession.id,
                review_revision=item.record.revision,
                decision=item.record.decision,
                resulting_contract_instrument_version_id=(
                    item.record.resulting_contract_instrument_version_id
                ),
                resulting_instrument_kind=(
                    item.resulting_version.instrument_kind
                    if item.resulting_version is not None
                    else None
                ),
                resulting_version_reference=(
                    item.resulting_version.version_reference
                    if item.resulting_version is not None
                    else None
                ),
                rationale=item.record.rationale,
                actor_id=item.record.actor_id,
                recorded_at=item.record.created_at,
            )
            for item in rows
        ]

    @router.get(
        "/cases/{case_id}/contract-execution-evidence-timeline",
        response_model=list[ContractExecutionEvidenceTimelineEvent],
    )
    def list_timeline(case_id: UUID, authorization: str | None = Header(default=None)):
        actor = resolve_bearer_context(
            authorization=authorization, context_resolver=security_runtime.context_resolver
        )
        if actor.actor_kind is not ActorKind.PATRON_ADMIN or actor.membership_id is None:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="FORBIDDEN")
        try:
            return timeline_service.list_for_case(actor=actor, case_id=case_id)
        except PermissionError as error:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="FORBIDDEN"
            ) from error

    return router
