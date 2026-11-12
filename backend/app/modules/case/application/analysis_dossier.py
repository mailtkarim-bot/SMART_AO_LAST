"""Human preparation/review contracts; no gate or completeness decision."""

import hashlib
import json
from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    SerializerFunctionWrapHandler,
    model_serializer,
    model_validator,
)

from app.modules.case.application.analysis_summary import AXES
from app.platform.events.command_contracts import ApplicationCommand

AxisCode = Literal[
    "COMMERCIAL",
    "CANDIDATURE",
    "TECHNICAL",
    "CONSTRUCTIBILITY",
    "CONTRACT",
    "PRICE",
    "CASH",
    "CAPACITY",
    "PARTNERS",
    "HSE",
    "DOCUMENTS",
    "RIGHTS",
]


class AnalysisConsequences(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    technical: str | None = Field(max_length=2000)
    price: str | None = Field(max_length=2000)
    delay: str | None = Field(max_length=2000)
    cash: str | None = Field(max_length=2000)
    contract: str | None = Field(max_length=2000)

    @model_validator(mode="after")
    def meaningful(self):
        if any(v is not None and not v for v in self.model_dump().values()):
            raise ValueError("EMPTY_CONSEQUENCE")
        return self


class AnalysisTreatment(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    axis_code: AxisCode
    applicability: Literal["APPLIES", "NOT_APPLICABLE", "UNKNOWN"]
    applicability_reason: str = Field(min_length=1, max_length=2000)
    consequences: AnalysisConsequences
    unknown_reason: str | None = Field(default=None, min_length=1, max_length=2000)
    action: str = Field(min_length=1, max_length=2000)
    responsible: Literal["SELF"]
    due_at: datetime | None
    hypotheses: str | None = Field(default=None, min_length=1, max_length=2000)

    @model_serializer(mode="wrap")
    def preserve_legacy_payload(self, handler: SerializerFunctionWrapHandler):
        value = handler(self)
        if self.hypotheses is None:
            value.pop("hypotheses", None)
        return value

    @model_validator(mode="after")
    def unknowns_explained(self):
        if (
            self.applicability == "UNKNOWN"
            or self.due_at is None
            or any(v is None for v in self.consequences.model_dump().values())
        ) and not self.unknown_reason:
            raise ValueError("TREATMENT_UNKNOWN_REASON_REQUIRED")
        if self.due_at is not None and self.due_at.tzinfo is None:
            raise ValueError("AWARE_DUE_AT_REQUIRED")
        return self


class DossierAxisReview(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    code: AxisCode
    state: Literal["POINTS_REVIEWED", "UNKNOWN"]
    note: str = Field(min_length=1, max_length=2000)
    follow_up: str | None = Field(default=None, min_length=1, max_length=2000)
    responsible: Literal["SELF"]

    @model_validator(mode="after")
    def unknown_action(self):
        if self.state == "UNKNOWN" and not self.follow_up:
            raise ValueError("AXIS_FOLLOW_UP_REQUIRED")
        return self


class AnalysisDossierRequest(ApplicationCommand):
    command_type = "RecordAnalysisDossier"
    review_id: UUID
    expected_revision: int = Field(ge=0)
    dossier_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    phase: Literal["PREPARED", "REVIEWED"]
    axes: list[DossierAxisReview] = Field(min_length=12, max_length=12)
    justification: str = Field(min_length=1, max_length=2000)
    human_confirmed: Literal[True]

    @model_validator(mode="after")
    def closed_axes(self):
        if {a.code for a in self.axes} != {c for c, _ in AXES}:
            raise ValueError("TWELVE_DISTINCT_AXES_REQUIRED")
        return self


class RecordAnalysisDossierCommand(AnalysisDossierRequest):
    case_id: UUID


def dossier_digest(summary):
    # Review metadata is excluded so recording an act cannot invalidate itself.
    value = {k: v for k, v in summary.items() if k not in {"dossier_review", "dossier_sha256"}}
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), default=str).encode()
    ).hexdigest()


class AnalysisDossierService:
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
            (Capability.PATRON_ACTION_READ, DataClassification.INTERNAL_OPERATIONAL),
            (Capability.DECISION_FINALIZE, DataClassification.INTERNAL_OPERATIONAL),
            (Capability.PRICING_READ, DataClassification.FINANCIAL_PRIVATE),
            (Capability.FINANCIAL_REPORT_READ, DataClassification.FINANCIAL_PRIVATE),
            (Capability.DECISION_RISK_READ, DataClassification.INTERNAL_OPERATIONAL),
            (Capability.DECISION_RISK_WRITE, DataClassification.INTERNAL_OPERATIONAL),
            (Capability.PRICING_WRITE, DataClassification.FINANCIAL_PRIVATE),
        ]:
            decision = self._policy.authorize(
                context=actor,
                request=AuthorizationRequest(
                    action=capability,
                    resource=AuthorizationResource(
                        resource_type="CASE_ANALYSIS_DOSSIER",
                        resource_id=command.review_id,
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
