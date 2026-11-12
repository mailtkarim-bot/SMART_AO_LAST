"""Bind a human change to exact published handover points, without a fabricated A1 source."""

from uuid import UUID

import sqlalchemy as sa

from app.modules.membership.public.text_safety import contains_forbidden_text
from app.modules.patron_action.infrastructure.models.handover import CaseHandoverSnapshotRecord
from app.modules.patron_action.infrastructure.operational_handover import (
    current_handover_view,
    lock_handover_sources,
)
from app.modules.pricing.public.operational_change_contracts import POLICY
from app.platform.events.dispatcher import CommandExecutionError


def require_publishable(*values):
    for value in values:
        texts = value if isinstance(value, (tuple, list)) else [value]
        if any(isinstance(text, str) and contains_forbidden_text(text) for text in texts):
            raise CommandExecutionError("FINANCIAL_TEXT_NOT_PUBLISHABLE")


def capture_context(session, *, tenant_id, case_id, snapshot_id, value, actor_id, now, storage):
    snapshot = session.scalar(
        sa.select(CaseHandoverSnapshotRecord).where(
            CaseHandoverSnapshotRecord.tenant_id == tenant_id,
            CaseHandoverSnapshotRecord.case_id == case_id,
            CaseHandoverSnapshotRecord.id == snapshot_id,
        )
    )
    if snapshot is None:
        raise CommandExecutionError("HANDOVER_NOT_FOUND_OR_FORBIDDEN")
    lock_handover_sources(session, snapshot)
    public, state, reasons, sha = current_handover_view(session, snapshot, storage=storage)
    if (
        state != "CURRENT"
        and not (state == "REVIEW_REQUIRED" and set(reasons) <= {"CONTRACT_LINK_UNKNOWN"})
    ) or sha != value.expected_view_sha256:
        raise CommandExecutionError("OPERATIONAL_CHANGE_SOURCE_CONFLICT")
    points = {point["point_id"]: point for point in public["operational_review"]["points"]}
    if any(
        str(point) not in points or points[str(point)]["kind"] == "UNKNOWN"
        for point in value.point_ids
    ):
        raise CommandExecutionError("HANDOVER_POINT_NOT_FOUND_OR_FORBIDDEN")
    return {
        **value.model_dump(mode="json"),
        "publication_policy": POLICY,
        "handover_snapshot_id": str(snapshot_id),
        "handover_revision": snapshot.revision,
        "offer_manifest_sha256": snapshot.manifest_sha256,
        "points": [points[str(point)] for point in value.point_ids],
        "published_by": str(actor_id),
        "recorded_at": now.isoformat(),
    }


def publication(value, context):
    return {
        **value.model_dump(mode="json"),
        "publication_policy": POLICY,
        "published_by": str(context.actor_id),
        "recorded_at": context.received_at.isoformat(),
    }


def context_state(session, *, tenant_id, case_id, context, storage, lock=False):
    if not context:
        return "UNKNOWN", ["NO_OPERATIONAL_CONTEXT"]
    snapshot = session.scalar(
        sa.select(CaseHandoverSnapshotRecord).where(
            CaseHandoverSnapshotRecord.tenant_id == tenant_id,
            CaseHandoverSnapshotRecord.case_id == case_id,
            CaseHandoverSnapshotRecord.id == UUID(context["handover_snapshot_id"]),
        )
    )
    if snapshot is None:
        return "REVIEW_REQUIRED", ["HANDOVER_SOURCE_MISSING"]
    if lock:
        lock_handover_sources(session, snapshot)
    _, state, reasons, sha = current_handover_view(session, snapshot, storage=storage)
    if sha != context["expected_view_sha256"]:
        return "REVIEW_REQUIRED", list(reasons) + ["HANDOVER_VIEW_CHANGED"]
    if context.get("declared_contract_id"):
        try:
            current = declared_contract(
                session,
                tenant_id=tenant_id,
                case_id=case_id,
                instrument_id=UUID(context["declared_contract_id"]),
            )
            if current["declared_contract_record_sha256"] != context.get(
                "declared_contract_record_sha256"
            ):
                return "REVIEW_REQUIRED", ["CONTRACT_RECORD_CHANGED"]
        except CommandExecutionError:
            return "REVIEW_REQUIRED", ["DECLARED_CONTRACT_REVIEW_REQUIRED"]
    if state != "CURRENT":
        return "REVIEW_REQUIRED", list(reasons)
    return "CURRENT", []


def declared_contract(session, *, tenant_id, case_id, instrument_id):
    from app.modules.patron_action.application.operational_handover import canonical_sha256
    from app.modules.patron_action.infrastructure.operational_handover import instrument_record
    from app.modules.pricing.infrastructure.models.contract_instrument_supersession import (
        ContractInstrumentSupersessionRecord,
    )
    from app.modules.pricing.infrastructure.models.contract_instrument_version import (
        ContractInstrumentVersionRecord,
    )

    if instrument_id is None:
        return {"declared_contract_id": None, "declared_contract_record_sha256": None}
    instrument = session.scalar(
        sa.select(ContractInstrumentVersionRecord)
        .where(
            ContractInstrumentVersionRecord.tenant_id == tenant_id,
            ContractInstrumentVersionRecord.case_id == case_id,
            ContractInstrumentVersionRecord.id == instrument_id,
        )
        .with_for_update(nowait=True)
    )
    if instrument is None:
        raise CommandExecutionError("CONTRACT_INSTRUMENT_NOT_FOUND_OR_FORBIDDEN")
    if session.scalar(
        sa.select(ContractInstrumentSupersessionRecord.id)
        .where(
            ContractInstrumentSupersessionRecord.tenant_id == tenant_id,
            ContractInstrumentSupersessionRecord.case_id == case_id,
            ContractInstrumentSupersessionRecord.replaced_contract_instrument_version_id
            == instrument_id,
        )
        .limit(1)
    ):
        raise CommandExecutionError("OPERATIONAL_CHANGE_CONTRACT_SOURCE_CONFLICT")
    return {
        "declared_contract_id": str(instrument_id),
        "declared_contract_record_sha256": canonical_sha256(instrument_record(instrument)),
    }
