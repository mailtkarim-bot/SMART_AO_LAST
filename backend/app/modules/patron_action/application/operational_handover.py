"""Closed operational handover view; private decision wording never crosses P7."""

import hashlib
import json
from contextlib import suppress
from copy import deepcopy
from uuid import UUID

from pydantic import ValidationError

from app.modules.membership.public.text_safety import contains_forbidden_text
from app.modules.patron_action.public.handover_contracts import HandoverOperationalPoint

PUBLICATION_POLICY = "HUMAN_OPERATIONAL_PUBLICATION_V1"


def canonical_sha256(value):
    return hashlib.sha256(
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def _fields(value, names):
    if not isinstance(value, dict):
        return {}
    return {key: deepcopy(value[key]) for key in names if key in value}


def public_handover_snapshot(source):
    review = source.get("operational_review", {})
    published = (
        isinstance(review, dict)
        and review.get("publication_policy") == PUBLICATION_POLICY
        and review.get("human_confirmed") is True
    )
    points = []
    unpublishable = []
    if published:
        for value in review.get("points", [])[:64]:
            try:
                points.append(
                    HandoverOperationalPoint.model_validate(value).model_dump(mode="json")
                )
            except (ValidationError, TypeError):
                point_id = "UNKNOWN"
                if isinstance(value, dict):
                    with suppress(ValueError, TypeError):
                        point_id = str(UUID(str(value.get("point_id"))))
                unpublishable.append(point_id)
                points.append(
                    {
                        "point_id": point_id,
                        "kind": "UNKNOWN",
                        "statement": "Point non publié · UNKNOWN",
                        "criticality": "UNKNOWN",
                        "condition_id": None,
                    }
                )
    labels = {
        point["condition_id"]: point["statement"]
        for point in points
        if point["kind"] == "CONDITION" and point.get("condition_id")
    }
    decision = _fields(
        source.get("decision"),
        (
            "state",
            "decision_id",
            "revision",
            "outcome",
            "context_id",
            "context_fingerprint",
            "conditions_state",
            "condition_sources",
        ),
    )
    conditions = []
    raw_conditions = source.get("decision", {}).get("open_conditions", [])
    for condition in raw_conditions:
        public = _fields(condition, ("condition_id", "status", "due_at"))
        label = labels.get(public.get("condition_id"))
        public.update(
            label=label or "Formulation opérationnelle à publier · UNKNOWN",
            label_state="HUMAN_PUBLISHED" if label else "UNKNOWN",
        )
        conditions.append(public)
    decision["open_conditions"] = conditions
    decision["condition_sources"] = [
        _fields(
            link,
            (
                "condition_id",
                "requirement_id",
                "requirement_revision",
                "impact_id",
                "impact_revision",
                "profile_version_id",
                "profile_version",
                "profile_sha256",
            ),
        )
        for link in decision.get("condition_sources", [])
    ]
    offer = _fields(
        source.get("offer"),
        (
            "submission_package_id",
            "package_version",
            "manifest_sha256",
            "dce_version_id",
            "technical_document_id",
            "technical_document_version",
            "technical_document_kind",
            "technical_document_sha256",
            "file_revalidation_state",
        ),
    )
    offer["financial_content"] = "NOT_INCLUDED"
    award = _fields(source.get("award"), ("outcome_id", "lot_reference", "recorded_at"))
    locator = source.get("award", {}).get("source_locator")
    award["source_locator"] = (
        locator if isinstance(locator, str) and not contains_forbidden_text(locator) else "UNKNOWN"
    )
    comparison = {"state": "UNKNOWN", "reason": "Rapprochement humain non enregistré."}
    if published:
        comparison = _fields(
            source.get("contract_comparison"),
            (
                "state",
                "instrument_version_id",
                "instrument_kind",
                "record_sha256",
                "file_sha256",
                "authority_state",
                "declared_reference_state",
            ),
        )
        comparison.setdefault("state", "UNKNOWN")
    missing = ["POINT_REQUIRES_REVIEW:" + point_id for point_id in unpublishable]
    if published and not points:
        missing.append("OPERATIONAL_POINTS_NOT_RECORDED")
    if not published:
        missing.append("OPERATIONAL_REVIEW_NOT_RECORDED")
    if not comparison.get("instrument_version_id"):
        missing.append("DECLARED_CONTRACT_NOT_LINKED")
    for condition in conditions:
        if condition["label_state"] == "UNKNOWN":
            missing.append("CONDITION_NOT_PUBLISHED:" + condition["condition_id"])
    for point in points:
        if point["criticality"] == "CRITICAL":
            for field in ("responsible", "offer_locator", "action", "expected_evidence"):
                if not point.get(field):
                    missing.append(field.upper() + ":" + point["point_id"])
    for point in points:
        if point["criticality"] == "CRITICAL":
            proof = source.get("offer_point_proofs", {}).get(point["point_id"], {})
            if proof.get("state") not in {"EXACT_BYTE_MATCH", "EXACT_DOCX_TEXT_MATCH"}:
                missing.append("OFFER_EXCERPT_NOT_PROVED:" + point["point_id"])
            if not point.get("contract_locator"):
                missing.append("CONTRACT_LOCATOR:" + point["point_id"])
    return {
        "schema_version": 2,
        "kind": "P7_HANDOVER_SNAPSHOT",
        "p7_is_order_service": False,
        "award": award,
        "offer": offer,
        "decision": decision,
        "contract_comparison": comparison,
        "operational_review": {
            "publication_policy": PUBLICATION_POLICY if published else None,
            "human_confirmed": published,
            "state": "HUMAN_PUBLISHED" if published else "UNKNOWN",
            "points": points,
            "justification": review.get("justification")
            if published
            and isinstance(review.get("justification"), str)
            and not contains_forbidden_text(review["justification"])
            else "UNKNOWN",
            "published_at": review.get("published_at") if published else None,
            "publisher_id": review.get("publisher_id") if published else None,
            "missing": missing,
            "completeness": "PARTIAL" if missing else "REVIEW_REQUIRED",
            "analysis_complete": False,
        },
        "source_context": _fields(
            source.get("source_context"),
            ("case_scope_fingerprint", "case_dce_version_id", "decision_id", "decision_revision"),
        ),
        "offer_point_proofs": _fields(
            source.get("offer_point_proofs"), tuple(str(point.get("point_id")) for point in points)
        ),
        "excluded": ["DONNEES_FINANCIERES_PRIVEES", "TEXTES_LIBRES_PATRON"],
    }


def review_context_sha256(*, scope_fingerprint, dce_version_id, decision_id, decision_revision):
    return canonical_sha256(
        {
            "case_scope_fingerprint": scope_fingerprint,
            "case_dce_version_id": str(dce_version_id) if dce_version_id else None,
            "decision_id": str(decision_id) if decision_id else None,
            "decision_revision": decision_revision,
        }
    )
