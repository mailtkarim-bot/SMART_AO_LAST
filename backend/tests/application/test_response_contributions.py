from uuid import uuid4

import pytest
from app.modules.preparation.application.document_content import (
    ResponsePlanDraftItem,
    build_response_plan_draft,
)
from app.modules.preparation.public.contracts import CreateTechnicalResponseDraftRequest


def test_native_draft_request_accepts_typed_human_contributions():
    request = CreateTechnicalResponseDraftRequest.model_validate(
        dict(
            command_id=uuid4(),
            idempotency_key=uuid4(),
            draft_id=uuid4(),
            source_document_id=uuid4(),
            expected_package_revision=1,
            section_codes=["METHOD"],
            source_refs=[uuid4()],
            contributions=[
                dict(
                    requirement_id=uuid4(),
                    section_code="METHOD",
                    content="Accès maintenu sans interruption.",
                    missing="Planning horaire à confirmer",
                )
            ],
        )
    )
    assert request.contributions[0].content == "Accès maintenu sans interruption."


def test_assembly_preserves_human_text_missing_parts_and_exact_requirement():
    from app.modules.preparation.public.contracts import ResponseContribution

    requirement = uuid4()
    item = ResponsePlanDraftItem(
        requirement_id=requirement,
        section_code="METHOD",
        capability_name="Site occupé",
        capability_title="Accès",
        capability_version_number=2,
        verified_source_count=1,
    )
    contribution = ResponseContribution(
        requirement_id=requirement,
        section_code="METHOD",
        content="Pas de fermeture. Si livraison : un signaleur accompagne le véhicule.",
        missing="Horaire et responsable à confirmer",
    )
    text = build_response_plan_draft(
        plan_version=3, draft_version=1, items=(item,), contributions=(contribution,)
    )
    assert str(requirement) in text
    assert contribution.content in text
    assert contribution.missing in text
    assert "Rédaction humaine" in text and "UNKNOWN" in text
    with pytest.raises(ValueError, match="CONTRIBUTION_PLAN_MISMATCH"):
        build_response_plan_draft(
            plan_version=3,
            draft_version=1,
            items=(item,),
            contributions=(contribution.model_copy(update={"requirement_id": uuid4()}),),
        )


@pytest.mark.parametrize(
    "values",
    [
        dict(content="", missing=""),
        dict(content="Marge de 20 %", missing=""),
        dict(content="Budget financier", missing=""),
    ],
)
def test_contributions_refuse_silent_empty_or_private_financial_wording(values):
    from app.modules.preparation.public.contracts import ResponseContribution
    from pydantic import ValidationError

    with pytest.raises(ValidationError):
        ResponseContribution(requirement_id=uuid4(), section_code="METHOD", **values)


def test_native_contribution_manifest_refuses_malformed_or_changed_provenance(monkeypatch):
    import json

    from app.modules.preparation.infrastructure import contribution_sources as sources
    from app.platform.events.dispatcher import CommandExecutionError

    requirement = uuid4()
    buyer = {"requirement_id": str(requirement), "source_state": "CURRENT_SOURCE"}
    monkeypatch.setattr(
        sources, "contribution_source_snapshots", lambda *a, **k: {requirement: buyer}
    )
    content = "- Sources résolues côté serveur : " + json.dumps(
        {"buyer": buyer, "human_content_present": True, "section_code": "METHOD"}
    )
    sources.validate_contribution_sources(
        None, tenant_id=uuid4(), case_id=uuid4(), dce_version_id=uuid4(), content=content
    )
    with pytest.raises(CommandExecutionError, match="CONTRIBUTION_SOURCE_UNKNOWN"):
        sources.validate_contribution_sources(
            None,
            tenant_id=uuid4(),
            case_id=uuid4(),
            dce_version_id=uuid4(),
            content=content.replace("CURRENT_SOURCE", "UNKNOWN"),
        )
    with pytest.raises(CommandExecutionError, match="CONTRIBUTION_SOURCE_UNKNOWN"):
        sources.validate_contribution_sources(
            None,
            tenant_id=uuid4(),
            case_id=uuid4(),
            dce_version_id=uuid4(),
            content="- Sources résolues côté serveur : nope",
        )


def test_legacy_draft_command_keeps_its_pre_contributions_payload():
    from app.modules.preparation.application.review_commands import (
        CreateTechnicalResponseDraftCommand,
    )

    command = CreateTechnicalResponseDraftCommand(
        command_id=uuid4(),
        idempotency_key=uuid4(),
        draft_id=uuid4(),
        package_id=uuid4(),
        source_document_id=uuid4(),
        expected_package_revision=1,
        section_codes=["METHOD"],
        source_refs=[uuid4()],
    )
    assert "contributions" not in command.model_dump(mode="json")


def test_unknown_missing_only_manifest_cannot_authorize_later_corrected_text(monkeypatch):
    import json

    from app.modules.preparation.infrastructure import contribution_sources as sources
    from app.platform.events.dispatcher import CommandExecutionError

    requirement = uuid4()
    buyer = {"requirement_id": str(requirement), "source_state": "UNKNOWN"}

    def current(*args, **kwargs):
        if kwargs["contributions"][0].content:
            raise CommandExecutionError("CONTRIBUTION_SOURCE_UNKNOWN")
        return {requirement: buyer}

    monkeypatch.setattr(sources, "contribution_source_snapshots", current)
    text = (
        "- Sources résolues côté serveur : "
        + json.dumps({"buyer": buyer, "human_content_present": False, "section_code": "METHOD"})
        + "\nUne correction ajoute désormais une réponse."
    )
    with pytest.raises(CommandExecutionError, match="CONTRIBUTION_SOURCE_UNKNOWN"):
        sources.validate_contribution_sources(
            None, tenant_id=uuid4(), case_id=uuid4(), dce_version_id=uuid4(), content=text
        )
