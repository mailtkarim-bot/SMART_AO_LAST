from copy import deepcopy
from uuid import uuid4

import pytest


def test_legacy_snapshot_does_not_publish_private_condition_wording():
    from app.modules.patron_action.application.operational_handover import public_handover_snapshot

    condition = str(uuid4())
    source = {
        "case_id": str(uuid4()),
        "offer": {"manifest_sha256": "a" * 64, "financial_content": "NOT_INCLUDED"},
        "decision": {
            "open_conditions": [
                {
                    "condition_id": condition,
                    "label": "Marge privée au moins 23 %",
                    "status": "OPEN",
                    "due_at": None,
                }
            ]
        },
        "private_margin": "23%",
        "contract_comparison": {"state": "UNKNOWN"},
    }
    before = deepcopy(source)
    result = public_handover_snapshot(source)
    assert "23 %" not in str(result) and "private_margin" not in result
    assert result["decision"]["open_conditions"][0]["condition_id"] == condition
    assert result["decision"]["open_conditions"][0]["label_state"] == "UNKNOWN"
    assert source == before


def test_operational_review_requires_explicit_human_act_and_preserves_unknowns():
    from app.modules.patron_action.public.handover_contracts import HandoverOperationalReview
    from pydantic import ValidationError

    body = dict(
        expected_source_context_sha256="c" * 64,
        expected_handover_revision=0,
        expected_offer_manifest_sha256="a" * 64,
        contract_instrument_version_id=None,
        expected_contract_record_sha256=None,
        justification="Revue opérationnelle synthétique",
        human_confirmed=True,
        points=[
            dict(
                point_id=uuid4(),
                kind="EXCLUSION",
                statement="Transport non compris dans la fourniture.",
                offer_locator="Offre §3",
                contract_locator=None,
                difference_state="UNKNOWN",
                difference_note=None,
                responsible=None,
                action="Obtenir une confirmation logistique",
                expected_evidence=None,
                due_date=None,
                criticality="CRITICAL",
                condition_id=None,
            )
        ],
    )
    review = HandoverOperationalReview.model_validate(body)
    assert review.points[0].difference_state == "UNKNOWN"
    with pytest.raises(ValidationError):
        HandoverOperationalReview.model_validate({**body, "human_confirmed": False})


def test_unpublishable_point_is_visible_as_unknown_instead_of_silently_omitted():
    from app.modules.patron_action.application.operational_handover import (
        PUBLICATION_POLICY,
        public_handover_snapshot,
    )

    source = {
        "decision": {},
        "operational_review": {
            "publication_policy": PUBLICATION_POLICY,
            "human_confirmed": True,
            "points": [
                {"point_id": str(uuid4()), "kind": "ENGAGEMENT", "statement": "Marge privée 28 %"}
            ],
        },
        "contract_comparison": {"state": "HUMAN_DECLARED", "instrument_version_id": str(uuid4())},
    }
    result = public_handover_snapshot(source)
    assert "Marge privée 28 %" not in str(result)
    assert len(result["operational_review"]["points"]) == 1
    assert result["operational_review"]["completeness"] == "PARTIAL"


def test_safe_projection_can_be_read_again_without_losing_published_points():
    from app.modules.patron_action.application.operational_handover import (
        PUBLICATION_POLICY,
        public_handover_snapshot,
    )

    source = {
        "decision": {"open_conditions": []},
        "operational_review": {
            "publication_policy": PUBLICATION_POLICY,
            "human_confirmed": True,
            "points": [
                {"point_id": str(uuid4()), "kind": "EXCLUSION", "statement": "Transport exclu."}
            ],
        },
    }
    first = public_handover_snapshot(source)
    second = public_handover_snapshot(first)
    assert second["operational_review"]["points"] == first["operational_review"]["points"]


def test_receipt_requires_exact_view_and_explicit_human_confirmation():
    from app.modules.patron_action.public.handover_contracts import AcknowledgeHandoverRequest
    from pydantic import ValidationError

    data = dict(
        command_id=uuid4(),
        idempotency_key=uuid4(),
        correlation_id=uuid4(),
        receipt_id=uuid4(),
        expected_snapshot_revision=1,
        expected_view_sha256="a" * 64,
        receipt_kind="RECEIVED_WITH_GAPS",
        note="Dossier reçu; points à clarifier conservés.",
        human_confirmed=True,
    )
    assert AcknowledgeHandoverRequest.model_validate(data).receipt_kind == "RECEIVED_WITH_GAPS"
    with pytest.raises(ValidationError):
        AcknowledgeHandoverRequest.model_validate({**data, "human_confirmed": False})


def test_receipt_capability_can_be_explicitly_granted_through_native_assignment():
    from app.modules.dce.application.commands import AssignmentScopeCommand
    from app.modules.membership.public.contracts import PatronAssignmentScopeAction
    from pydantic import TypeAdapter

    value = "case.handover.receipt.write"
    command = AssignmentScopeCommand(
        command_id=uuid4(),
        idempotency_key=uuid4(),
        correlation_id=uuid4(),
        scope_actions=["case.dce.read", value],
        scope_classifications=["INTERNAL_OPERATIONAL"],
    )
    assert command.scope_actions == ["case.dce.read", value]
    assert TypeAdapter(PatronAssignmentScopeAction).validate_python(value) == value


def test_legacy_handover_payload_keeps_its_original_retry_hash():
    from app.modules.patron_action.application.handover_commands import (
        RecordCaseHandoverSnapshotCommand,
    )
    from app.modules.patron_action.application.operational_handover import canonical_sha256

    body = {
        key: str(uuid4())
        for key in [
            "command_id",
            "idempotency_key",
            "correlation_id",
            "snapshot_id",
            "case_id",
            "outcome_id",
            "submission_package_id",
        ]
    }
    command = RecordCaseHandoverSnapshotCommand.model_validate(body)
    assert command.model_dump(mode="json") == body
    assert canonical_sha256(command.model_dump(mode="json")) == canonical_sha256(body)
