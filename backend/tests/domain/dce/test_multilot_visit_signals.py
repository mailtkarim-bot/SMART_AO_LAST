"""Development regressions from a complete synthetic multi-document dossier."""

from hashlib import sha256
from uuid import uuid4

import pytest
from app.modules.dce.application.analysis import (
    RcAnalysisSourceFragment,
    _project_rc_requirements,
    is_valid_rc_observation,
)


def project(text):
    return _project_rc_requirements(
        sources=(
            RcAnalysisSourceFragment(
                dce_document_id=uuid4(),
                extraction_id=uuid4(),
                fragment_id=uuid4(),
                ordinal=1,
                text=text,
                text_sha256=sha256(text.encode()).hexdigest(),
                document_family="RC",
            ),
        )
    )


@pytest.mark.parametrize(
    "text,directive",
    [
        ("Lot 1 : la visite de chantier est obligatoire.", "REQUIRED_SIGNAL"),
        ("Lot 2 : la visite du chantier est facultative.", "OPTIONAL_SIGNAL"),
        ("Les visites de site ne sont pas obligatoires pour le lot 2.", "UNSPECIFIED"),
        ("Si retenu, le candidat doit effectuer une visite des chantiers du lot 1.", "UNSPECIFIED"),
    ],
)
def test_explicit_construction_visits_keep_directive_and_exact_excerpt(text, directive):
    result = project(text)
    signals = [o for o in result.observations if o.requirement_kind == "RC_SITE_VISIT"]
    assert len(signals) == 1
    obs = signals[0]
    assert obs.directive == directive
    assert text.encode()[obs.start_byte_offset : obs.end_byte_offset] == obs.excerpt.encode()
    assert is_valid_rc_observation(
        requirement_kind=obs.requirement_kind,
        rule_id=obs.rule_id,
        directive=obs.directive,
        excerpt=obs.excerpt,
    )


@pytest.mark.parametrize(
    "text",
    [
        "La visite médicale est obligatoire.",
        "La visite du médecin du chantier est obligatoire.",
        "Le candidat visite notre site internet.",
    ],
)
def test_medical_or_web_visit_is_not_a_construction_visit(text):
    assert not any(o.requirement_kind == "RC_SITE_VISIT" for o in project(text).observations)


def test_new_visit_rule_cannot_reinterpret_historical_v5():
    obs = project("Lot 1 : la visite de chantier est obligatoire.").observations[0]
    assert not is_valid_rc_observation(
        requirement_kind=obs.requirement_kind,
        rule_id=obs.rule_id,
        directive=obs.directive,
        excerpt=obs.excerpt,
        rule_version="5",
    )
    assert is_valid_rc_observation(
        requirement_kind="RC_SITE_VISIT",
        rule_id="SITE_VISIT_V1",
        directive="REQUIRED_SIGNAL",
        excerpt="La visite de site est obligatoire.",
        rule_version="5",
    )


def test_website_noun_after_site_is_not_a_construction_visit():
    assert not any(
        o.requirement_kind == "RC_SITE_VISIT"
        for o in project("La visite du site internet est obligatoire.").observations
    )


@pytest.mark.parametrize("family", ["DPGF", "OTHER", "PLANNING"])
def test_price_document_or_inventory_mention_is_not_an_rc_offer_request(family):
    text = "DPGF synthétique vierge : aucune valeur économique réelle."
    result = _project_rc_requirements(
        sources=(
            RcAnalysisSourceFragment(
                uuid4(), uuid4(), uuid4(), 1, text, sha256(text.encode()).hexdigest(), family
            ),
        )
    )
    assert not result.observations


@pytest.mark.parametrize("family", ["CCAP", "CCTP", "OTHER"])
def test_explicit_offer_request_outside_rc_must_not_disappear(family):
    text = "Le mémoire technique est obligatoire pour le lot 1."
    result = _project_rc_requirements(
        sources=(
            RcAnalysisSourceFragment(
                uuid4(), uuid4(), uuid4(), 1, text, sha256(text.encode()).hexdigest(), family
            ),
        )
    )
    assert any(o.requirement_kind == "RC_CONTENT_OFFER" for o in result.observations)
