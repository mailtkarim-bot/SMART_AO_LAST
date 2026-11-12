"""Explicit human declarations; never confirmations or gate decisions."""

from __future__ import annotations

import hashlib
import json
from typing import Literal
from uuid import UUID

from pydantic import Field, SerializerFunctionWrapHandler, model_serializer, model_validator

from app.modules.case.application.analysis_dossier import AnalysisTreatment
from app.platform.events.command_contracts import ApplicationCommand


class AnalysisAssessmentRequest(ApplicationCommand):
    command_type = "RecordAnalysisAssessment"
    assessment_id: UUID
    point_kind: Literal["REQUIREMENT", "RISK"]
    point_id: UUID
    expected_revision: int = Field(ge=0)
    source_context_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    expected_evidence_state: Literal["DECLARED", "UNKNOWN"]
    expected_evidence: str | None = Field(default=None, min_length=1, max_length=2000)
    residual_risk_state: Literal["DECLARED", "UNKNOWN"]
    residual_risk: str | None = Field(default=None, min_length=1, max_length=2000)
    unknown_reason: str | None = Field(default=None, min_length=1, max_length=2000)
    justification: str = Field(min_length=1, max_length=2000)
    treatment: AnalysisTreatment | None = Field(
        default=None, exclude_if=lambda value: value is None
    )
    human_confirmed: Literal[True]

    @model_serializer(mode="wrap")
    def legacy_compatible_payload(
        self, handler: SerializerFunctionWrapHandler
    ) -> dict[str, object]:
        payload: dict[str, object] = handler(self)
        # Optional enrichment must not change hashes of pre-upgrade retry intents.
        if self.treatment is None:
            payload.pop("treatment", None)
        return payload

    @model_validator(mode="after")
    def declared_values(self):
        for state, value in [
            (self.expected_evidence_state, self.expected_evidence),
            (self.residual_risk_state, self.residual_risk),
        ]:
            if (state == "DECLARED") != (value is not None):
                raise ValueError("DECLARATION_STATE_MISMATCH")
        if (
            "UNKNOWN" in (self.expected_evidence_state, self.residual_risk_state)
            and self.unknown_reason is None
        ):
            raise ValueError("UNKNOWN_REASON_REQUIRED")
        return self


class RecordAnalysisAssessmentCommand(AnalysisAssessmentRequest):
    case_id: UUID


def source_context_digest(*, point, tenant_id, case_id, version_id, scope):
    payload = dict(
        tenant_id=tenant_id,
        case_id=case_id,
        dce_version_id=version_id,
        scope=scope,
        kind=point["kind"],
        point_id=point["item_id"],
        native_revision=point["native_revision"],
        native_state=point.get("native_state"),
        native_type=point.get("native_type"),
        source_anchor=point["source_anchor"],
        start=point["start_byte_offset"],
        end=point["end_byte_offset"],
    )
    # Preserve historical retry fingerprints outside DOCX tables.
    if point.get("table_context") is not None:
        payload["table_context"] = point["table_context"]
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str).encode()
    ).hexdigest()


class AnalysisAssessmentService:
    def __init__(self, *, dispatcher, policy):
        self._dispatcher = dispatcher
        self._policy = policy

    def execute(self, *, actor, command, now):
        from app.platform.events.dispatcher import CommandContext
        from app.platform.security.authorization import AuthorizationRequest, AuthorizationResource
        from app.platform.security.capabilities import Capability
        from app.platform.security.context import ActorKind, DataClassification

        if actor.actor_kind is not ActorKind.PATRON_ADMIN or actor.membership_id is None:
            raise PermissionError("PATRON_REQUIRED")
        for capability, classification in [
            (Capability.CASE_DCE_READ, DataClassification.INTERNAL_OPERATIONAL),
            (Capability.DECISION_RISK_READ, DataClassification.INTERNAL_OPERATIONAL),
            (Capability.DECISION_RISK_WRITE, DataClassification.INTERNAL_OPERATIONAL),
            (Capability.PRICING_WRITE, DataClassification.FINANCIAL_PRIVATE),
        ]:
            decision = self._policy.authorize(
                context=actor,
                request=AuthorizationRequest(
                    action=capability,
                    resource=AuthorizationResource(
                        resource_type="CASE_ANALYSIS_ASSESSMENT",
                        resource_id=command.assessment_id,
                        tenant_id=actor.tenant_id,
                        case_id=command.case_id,
                        classification=classification,
                    ),
                    evaluated_at=now,
                    mfa_required=True,
                ),
            )
            if not decision.allowed:
                raise PermissionError("FORBIDDEN")
        return self._dispatcher.dispatch(
            command=command,
            context=CommandContext(
                tenant_id=actor.tenant_id,
                actor_id=actor.actor_id,
                actor_kind=actor.actor_kind.value,
                membership_id=actor.membership_id,
                identity_id=actor.identity_id,
                session_id=actor.session_id,
                received_at=now,
                case_id=command.case_id,
                correlation_id=actor.correlation_id,
            ),
        )
