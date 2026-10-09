from uuid import uuid4

from app.modules.preparation.application.document_content import (
    ResponsePlanDraftItem,
    TechnicalDocumentFacts,
    build_response_plan_draft,
    build_technical_document,
)
from app.modules.preparation.application.ports import PreparationRequirementInput


def test_technical_document_is_canonical_structured_and_non_financial() -> None:
    facts = TechnicalDocumentFacts(
        case_id=uuid4(),
        dce_version_id=uuid4(),
        readiness_state="READY_WITH_WARNINGS",
        readiness_revision=3,
        document_version=2,
        requirements=(
            PreparationRequirementInput(
                requirement_id=uuid4(),
                requirement_type="SITE_VISIT",
                directive_signal="REQUIRED_SIGNAL",
                confirmation_outcome="CONFIRMED",
            ),
            PreparationRequirementInput(
                requirement_id=uuid4(),
                requirement_type="OFFER_DOCUMENT",
                directive_signal="OPTIONAL_SIGNAL",
                confirmation_outcome=None,
            ),
        ),
        blocker_codes=(),
        warning_codes=("TASK_RESULT_MISSING",),
    )

    content = build_technical_document(facts)
    repeated = build_technical_document(facts)

    assert content == repeated
    assert "## Exigences DCE confirmées" in content
    assert "SITE_VISIT" in content
    assert "PENDING_HUMAN_CONFIRMATION" in content
    assert "TASK_RESULT_MISSING" in content
    forbidden = {"prix", "marge", "trésorerie", "chiffrage", "go/no-go"}
    assert not forbidden.intersection(content.casefold())


def test_response_draft_content_is_built_from_the_exact_plan_without_source_ids() -> None:
    case_id, requirement_id, proposal_id = (uuid4() for _ in range(3))
    content = build_response_plan_draft(
        plan_version=4,
        draft_version=2,
        items=(
            ResponsePlanDraftItem(
                requirement_id=requirement_id,
                section_code="METHOD",
                capability_name="Méthodologie travaux",
                capability_title="Organisation de chantier",
                capability_version_number=3,
                verified_source_count=2,
            ),
        ),
    )

    assert "Plan de réponse — révision 4" in content
    assert "Brouillon — version 2" in content
    assert "Méthodologie travaux — Organisation de chantier (version 3)" in content
    assert "2 pièce(s) relue(s); SHA-256 recalculés et concordants" in content
    assert str(requirement_id) not in content
    assert str(proposal_id) not in content
    assert str(case_id) not in content
    forbidden = {"prix", "marge", "trésorerie", "chiffrage", "go/no-go"}
    assert not forbidden.intersection(content.casefold())
