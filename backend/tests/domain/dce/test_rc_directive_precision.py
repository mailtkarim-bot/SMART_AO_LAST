from hashlib import sha256
from uuid import uuid4

import pytest
from app.modules.dce.application.analysis import (
    RcAnalysisSourceFragment,
    _project_rc_requirements,
    _recording_command,
    is_valid_rc_observation,
)
from app.modules.dce.application.handlers import _validate_rc_analysis_observations
from app.modules.dce.infrastructure.models.dce_extraction import DceDocumentExtractionFragmentRecord


def _source(text: str) -> RcAnalysisSourceFragment:
    return RcAnalysisSourceFragment(
        dce_document_id=uuid4(),
        extraction_id=uuid4(),
        fragment_id=uuid4(),
        ordinal=1,
        text=text,
        text_sha256=sha256(text.encode()).hexdigest(),
        document_family="RC",
    )


@pytest.mark.parametrize(
    "heading",
    [
        "Date limite de dépôt des plis",
        "Date et heure limites de dépôt des offres",
        "Date limite de remise des offres",
        "Heure limite de réception des offres",
    ],
)
def test_submission_deadline_heading_is_not_silently_omitted(heading: str) -> None:
    source = _source(f"{heading} : 18/08/2034 à 11h00")
    result = _project_rc_requirements(sources=(source,))
    assert any(o.requirement_kind == "RC_SUBMISSION_DEADLINE" for o in result.observations)


@pytest.mark.parametrize(
    ("text", "kind", "directive"),
    [
        (
            "Date limite de remise des offres : 18/08/2034. "
            "Question : serait-il possible de disposer d'un délai supplémentaire ?",
            "RC_SUBMISSION_DEADLINE",
            "UNSPECIFIED",
        ),
        (
            "Le mémoire technique est obligatoire. Une visite des lieux est facultative.",
            "RC_CONTENT_OFFER",
            "REQUIRED_SIGNAL",
        ),
        (
            "Le mémoire technique est obligatoire. Une visite des lieux est facultative.",
            "RC_SITE_VISIT",
            "OPTIONAL_SIGNAL",
        ),
        (
            "Le mémoire technique est obligatoire. Il est possible de poser des questions.",
            "RC_CONTENT_OFFER",
            "REQUIRED_SIGNAL",
        ),
        (
            "Le candidat peut compléter le mémoire technique par des illustrations.",
            "RC_CONTENT_OFFER",
            "UNSPECIFIED",
        ),
        (
            "Le mémoire technique est indiqué obligatoire ou facultatif selon le lot.",
            "RC_CONTENT_OFFER",
            "UNSPECIFIED",
        ),
        (
            "La visite de site n'est pas obligatoire.",
            "RC_SITE_VISIT",
            "UNSPECIFIED",
        ),
        (
            "Le mémoire technique est\nobligatoire.",
            "RC_CONTENT_OFFER",
            "REQUIRED_SIGNAL",
        ),
    ],
)
def test_directive_is_bound_to_its_clause_not_neighboring_permissions(
    text: str, kind: str, directive: str
) -> None:
    source = _source(text)
    result = _project_rc_requirements(sources=(source,))
    observation = next(o for o in result.observations if o.requirement_kind == kind)
    assert observation.directive == directive
    assert is_valid_rc_observation(
        requirement_kind=kind,
        rule_id=observation.rule_id,
        directive=directive,
        excerpt=observation.excerpt,
    )
    assert (
        source.text.encode()[observation.start_byte_offset : observation.end_byte_offset].decode()
        == observation.excerpt
    )


@pytest.mark.parametrize("version", ["1", "2"])
def test_historical_observation_is_validated_with_its_own_semantics(version: str) -> None:
    args = {
        "requirement_kind": "RC_SUBMISSION_DEADLINE",
        "rule_id": "SUBMISSION_DEADLINE_V1",
        "directive": "OPTIONAL_SIGNAL",
        "excerpt": "Date limite de remise des offres. Une prolongation est-elle possible ?",
    }
    assert is_valid_rc_observation(**args, rule_version=version)
    assert not is_valid_rc_observation(**args, rule_version="3")
    assert not is_valid_rc_observation(**args, rule_version="999")


def test_old_version_cannot_validate_a_new_deadline_pattern() -> None:
    args = {
        "requirement_kind": "RC_SUBMISSION_DEADLINE",
        "rule_id": "SUBMISSION_DEADLINE_V1",
        "directive": "UNSPECIFIED",
        "excerpt": "Date limite de dépôt des plis : 18/08/2034.",
    }
    assert not is_valid_rc_observation(**args, rule_version="2")
    assert is_valid_rc_observation(**args, rule_version="3")


@pytest.mark.parametrize(
    "text",
    [
        "La durée de validité des offres est fixée à 120 jours.",
        "Le délai de validité des offres est de 120 jours.",
        "La validité de l'offre est de 120 jours.",
    ],
)
def test_offer_validity_wording_is_not_silently_omitted(text: str) -> None:
    projection = _project_rc_requirements(sources=(_source(text),))
    assert any(o.requirement_kind == "RC_OFFER_VALIDITY" for o in projection.observations)


def test_new_validity_pattern_does_not_relabel_an_insurance_document() -> None:
    projection = _project_rc_requirements(
        sources=(_source("La durée de validité de l'attestation d'assurance est limitée."),)
    )
    assert not any(o.requirement_kind == "RC_OFFER_VALIDITY" for o in projection.observations)


def test_conditional_permission_cannot_create_a_certain_obligation() -> None:
    projection = _project_rc_requirements(
        sources=(_source("Le mémoire technique peut être exigé selon le lot."),)
    )
    observation = next(
        o for o in projection.observations if o.requirement_kind == "RC_CONTENT_OFFER"
    )
    assert observation.directive == "UNSPECIFIED"


def test_recording_rejects_mismatched_analysis_and_observation_versions() -> None:
    source = _source("Le mémoire technique est obligatoire.")
    command = _recording_command(
        dce_version_id=uuid4(), projection=_project_rc_requirements(sources=(source,))
    )
    mismatched = command.model_copy(
        update={
            "observations": [command.observations[0].model_copy(update={"rule_version": "999"})]
        }
    )
    with pytest.raises(ValueError, match="DCE_ANALYSIS_RULE_VERSION_REQUIRED"):
        _validate_rc_analysis_observations(
            command=mismatched,
            fragments_by_id={
                source.fragment_id: DceDocumentExtractionFragmentRecord(text=source.text)
            },
        )


@pytest.mark.parametrize(
    "negation", ["est non requis", "n’est pas requis", "est non exigé", "n'est pas exigé"]
)
def test_negated_requirement_is_not_made_mandatory(negation: str) -> None:
    projection = _project_rc_requirements(sources=(_source(f"Le mémoire technique {negation}."),))
    assert projection.observations[0].directive == "UNSPECIFIED"
