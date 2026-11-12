"""Closed operational read: publication is explicit, private files are never copied."""

from copy import deepcopy

from app.modules.pricing.public.operational_change_contracts import POLICY


def published(value):
    return (
        isinstance(value, dict)
        and value.get("publication_policy") == POLICY
        and value.get("publish") is True
        and value.get("human_confirmed") is True
    )


def fields(value, names):
    return {name: deepcopy(value[name]) for name in names if name in value}


def public_change_projection(event):
    context = event.get("operational_context")
    if not published(context):
        return None
    result = fields(
        event,
        (
            "event_id",
            "case_id",
            "handover_snapshot_id",
            "lot_reference",
            "offer_manifest_sha256",
            "change_kind",
            "issuer",
            "summary",
            "scope_note",
            "source_refs",
            "evidence_refs",
            "declared_received_at",
            "source_state",
            "source_reasons",
            "operational_timeline",
        ),
    )
    result.update(
        current_operational_context=deepcopy(event.get("current_operational_context"))
        if published(event.get("current_operational_context"))
        else None,
        operational_context=deepcopy(context),
        legal_effect_state="UNKNOWN",
        financial_content="NOT_INCLUDED",
        private_files="NOT_INCLUDED",
    )
    result["applicability_history"] = [
        fields(
            review,
            (
                "review_id",
                "revision",
                "decision",
                "delta_state",
                "delta_note",
                "source_state",
                "recorded_at",
                "contract_instrument_version_id",
                "operational_review",
            ),
        )
        for review in event.get("applicability_history", [])
        if published(review.get("operational_review"))
    ]
    public_actions = [
        action
        for action in event.get("actions", [])
        if published(action.get("operational_details"))
    ]
    result["actions"] = [
        fields(
            action,
            (
                "action_id",
                "revision",
                "applicability_review_id",
                "summary",
                "due_at",
                "due_date_absence_reason",
                "recorded_at",
                "operational_details",
                "source_state",
            ),
        )
        for action in public_actions
    ]
    ids = {action["action_id"] for action in public_actions}
    result["action_execution_acts"] = [
        {
            **fields(
                act,
                (
                    "act_id",
                    "action_id",
                    "revision",
                    "declared_state",
                    "declared_summary",
                    "unknown_reason",
                    "evidence_refs",
                    "recorded_at",
                    "operational_publication",
                    "source_state",
                ),
            ),
            "evidence_retrieval_state": "UNKNOWN",
            "external_confirmation_state": "UNKNOWN",
        }
        for act in event.get("action_execution_acts", [])
        if act.get("action_id") in ids and published(act.get("operational_publication"))
    ]
    # The private timeline may contain financial act text; rebuild only from published records.
    entries = [
        dict(
            kind="CHANGE_RECORDED",
            recorded_at=event.get("recorded_at", event.get("declared_received_at")),
            record_id=event["event_id"],
            summary=event["summary"],
        )
    ]
    for kind, key in [
        ("APPLICABILITY", "applicability_history"),
        ("ACTION", "actions"),
        ("EXECUTION_DECLARATION", "action_execution_acts"),
    ]:
        for item in result[key]:
            entries.append(
                dict(
                    kind=kind,
                    recorded_at=item.get("recorded_at"),
                    record_id=item.get(
                        {
                            "APPLICABILITY": "review_id",
                            "ACTION": "action_id",
                            "EXECUTION_DECLARATION": "act_id",
                        }[kind]
                    ),
                    source_state=item.get("source_state", result.get("source_state", "UNKNOWN")),
                )
            )
    result["operational_timeline"] = sorted(
        entries, key=lambda x: (x.get("recorded_at") or "", x.get("record_id") or "")
    )
    return result
