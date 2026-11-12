from typing import Any
from uuid import uuid4

import pytest
from pydantic import ValidationError


def test_operational_context_requires_exact_view_points_and_human_act():
    from app.modules.pricing.public.operational_change_contracts import OperationalChangeContext

    body: dict[str, Any] = dict(
        expected_view_sha256="a" * 64,
        point_ids=[uuid4()],
        justification="Instruction rapprochée de l’engagement transmis.",
        human_confirmed=True,
        publish=True,
    )
    context = OperationalChangeContext.model_validate(body)
    assert context.point_ids == body["point_ids"]
    patches: list[dict[str, Any]] = [
        dict(expected_view_sha256="bad"),
        dict(point_ids=[]),
        dict(point_ids=body["point_ids"] * 2),
        dict(human_confirmed=False),
        dict(justification="Marge privée 28 %"),
    ]
    for patch in patches:
        with pytest.raises(ValidationError):
            OperationalChangeContext.model_validate({**body, **patch})


def test_private_changes_and_binary_evidence_are_never_implicitly_published():
    from app.modules.pricing.application.operational_change_projection import (
        public_change_projection,
    )

    private: dict[str, Any] = {
        "event_id": str(uuid4()),
        "summary": "Marge privée 28 %",
        "actions": [],
        "operational_context": None,
    }
    assert public_change_projection(private) is None
    published = {
        **private,
        "summary": "Accès chantier déplacé.",
        "scope_note": "Lot01",
        "operational_context": dict(
            publication_policy="HUMAN_OPERATIONAL_CHANGE_V1",
            publish=True,
            human_confirmed=True,
            points=[],
        ),
        "impact_declarations": [dict(axis="COST", value_as_declared="23800")],
        "evidence_objects": [dict(storage_key="secret-key")],
        "actions": [dict(action_id=str(uuid4()), summary="Note privée", operational_details=None)],
    }
    result = public_change_projection(published)
    assert (
        "23800" not in str(result)
        and "secret-key" not in str(result)
        and "Note privée" not in str(result)
    )
    assert result["legal_effect_state"] == "UNKNOWN"


def test_public_timeline_identifies_each_execution_act_instead_of_its_parent_action():
    from app.modules.pricing.application.operational_change_projection import (
        public_change_projection,
    )

    publication = {
        "publication_policy": "HUMAN_OPERATIONAL_CHANGE_V1",
        "publish": True,
        "human_confirmed": True,
    }
    source = {
        "event_id": "event",
        "summary": "Instruction",
        "operational_context": publication,
        "actions": [
            {"action_id": "action", "summary": "Vérifier accès", "operational_details": publication}
        ],
        "action_execution_acts": [
            {
                "act_id": act,
                "action_id": "action",
                "recorded_at": "2026-10-25T10:00:00Z",
                "operational_publication": publication,
            }
            for act in ["act1", "act2"]
        ],
    }
    result = public_change_projection(source)
    assert [
        item["record_id"]
        for item in result["operational_timeline"]
        if item["kind"] == "EXECUTION_DECLARATION"
    ] == ["act1", "act2"]


def test_legacy_event_retry_hash_is_preserved_without_operational_extension():
    from app.modules.patron_action.application.operational_handover import canonical_sha256
    from app.modules.pricing.application.case_contract_change_commands import (
        RecordCaseContractChangeEventCommand,
    )

    body: dict[str, Any] = {
        name: str(uuid4())
        for name in [
            "command_id",
            "idempotency_key",
            "correlation_id",
            "event_id",
            "case_id",
            "handover_snapshot_id",
        ]
    }
    body.update(
        change_kind="ORDER_OF_SERVICE",
        contract_instrument_version_id=None,
        issuer=None,
        summary="Instruction synthétique",
        scope_note="Lot01",
        source_refs=["instruction://1"],
        evidence_refs=["document://1"],
        declared_received_at="2026-10-25T10:00:00Z",
    )
    actual = RecordCaseContractChangeEventCommand.model_validate(body).model_dump(mode="json")
    assert actual == body and canonical_sha256(actual) == canonical_sha256(body)


def test_technical_command_failure_is_not_reported_as_a_definitive_rejection():
    from types import SimpleNamespace

    from app.interfaces.http.routes.patron_case_contract_changes import _dispatch
    from app.platform.events.dispatcher import CommandExecutionError
    from fastapi import HTTPException

    def fail(**kwargs):
        raise CommandExecutionError("command failed before commit")

    with pytest.raises(HTTPException) as error:
        _dispatch(SimpleNamespace(record=fail), object(), actor=None)
    assert error.value.status_code == 503


def test_integrity_failure_remains_a_definitive_rejection_after_rollback():
    from types import SimpleNamespace

    from app.interfaces.http.routes.patron_case_contract_changes import _dispatch
    from app.platform.events.dispatcher import CommandExecutionError
    from fastapi import HTTPException

    def fail(**kwargs):
        raise CommandExecutionError("command persistence failed before commit")

    with pytest.raises(HTTPException) as error:
        _dispatch(SimpleNamespace(record=fail), object(), actor=None)
    assert error.value.status_code == 422
