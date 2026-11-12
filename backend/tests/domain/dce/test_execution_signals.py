"""Development cases distinct from the historical multi-lot challenges."""

from hashlib import sha256
from uuid import uuid4

import pytest
from app.modules.dce.application.analysis import RcAnalysisSourceFragment, _project_rc_requirements


def signals(text, family):
    return _project_rc_requirements(
        sources=(
            RcAnalysisSourceFragment(
                uuid4(), uuid4(), uuid4(), 1, text, sha256(text.encode()).hexdigest(), family
            ),
        )
    ).observations


@pytest.mark.parametrize(
    "text,family,kind",
    [
        ("Lot 5 : installer des canalisations en cuivre.", "CCTP", "DCE_TECHNICAL_PRESCRIPTION"),
        ("Lot 5 : évacuer les déblais par la voie de service.", "CCTP", "DCE_LOGISTICS_CONSTRAINT"),
        (
            "Lot 9 : intervention après achèvement des fondations.",
            "PLANNING",
            "DCE_SCHEDULE_CONSTRAINT",
        ),
        (
            "Les travaux en hauteur sont interdits lorsque le vent est excessif.",
            "OTHER",
            "DCE_HSE_CONSTRAINT",
        ),
        ("Le délai de paiement est fixé à vingt jours pour le lot 5.", "CCAP", "DCE_PAYMENT_TERM"),
        (
            "Le procès-verbal de réception doit consigner les réserves.",
            "CCAP",
            "DCE_ACCEPTANCE_TERM",
        ),
    ],
)
def test_execution_statement_has_typed_exact_source(text, family, kind):
    hits = [o for o in signals(text, family) if o.requirement_kind == kind]
    assert len(hits) == 1
    o = hits[0]
    assert text.encode()[o.start_byte_offset : o.end_byte_offset] == o.excerpt.encode()


@pytest.mark.parametrize(
    "text,family",
    [
        ("La réception des offres est fixée au 2 mars.", "RC"),
        ("Installer le logiciel de lecture des prix.", "DPGF"),
        ("Le planning sera communiqué ultérieurement.", "PLANNING"),
        ("Le bureau accueille une équipe de revue documentaire.", "PLANNING"),
        ("La facture porte le mot paiement dans son titre.", "CCAP"),
    ],
)
def test_keyword_or_foreign_context_does_not_become_execution_fact(text, family):
    assert not any(o.requirement_kind.startswith("DCE_") for o in signals(text, family))


@pytest.mark.parametrize(
    "text,family,kind",
    [
        (
            "Ne pas installer de chaudière avant validation du lot 5.",
            "CCTP",
            "DCE_TECHNICAL_PRESCRIPTION",
        ),
        (
            "Si le diagnostic est absent, le retrait des matériaux amiantés est interdit.",
            "OTHER",
            "DCE_HSE_CONSTRAINT",
        ),
        (
            "Le paiement intervient après contrôle si la prestation est acceptée.",
            "CCAP",
            "DCE_PAYMENT_TERM",
        ),
    ],
)
def test_condition_and_negation_are_not_promoted_to_required(text, family, kind):
    hits = [o for o in signals(text, family) if o.requirement_kind == kind]
    assert hits and all(o.directive == "UNSPECIFIED" for o in hits)
    assert all(o.excerpt == text for o in hits)


@pytest.mark.parametrize(
    "text,family",
    [
        ("Lexique : amiante.", "OTHER"),
        ("Exemple : installer un radiateur.", "CCTP"),
    ],
)
def test_explicit_glossary_or_example_is_not_an_instruction(text, family):
    assert not any(o.requirement_kind.startswith("DCE_") for o in signals(text, family))


def test_readback_rejects_an_example_even_when_its_keyword_matches():
    from app.modules.dce.application.analysis import is_valid_rc_observation

    assert not is_valid_rc_observation(
        requirement_kind="DCE_TECHNICAL_PRESCRIPTION",
        rule_id="TECHNICAL_INSTRUCTION_V7",
        directive="UNSPECIFIED",
        excerpt="Exemple : installer un radiateur.",
    )


@pytest.mark.parametrize(
    "text,kind",
    [
        ("Les travaux doivent intervenir\naprès réception du support.", "DCE_SCHEDULE_CONSTRAINT"),
        ("La réception doit faire l’objet\nd’un procès-verbal.", "DCE_ACCEPTANCE_TERM"),
    ],
)
def test_wrapped_clause_retains_its_signal_and_original_bytes(text, kind):
    hits = [o for o in signals(text, "CCAP") if o.requirement_kind == kind]
    assert len(hits) == 1
    assert text.encode()[hits[0].start_byte_offset : hits[0].end_byte_offset] == text.encode()


@pytest.mark.parametrize(
    "text",
    [
        "Exemples : installer un radiateur.",
        "Lot 5 : exemple : installer un radiateur.",
    ],
)
def test_example_scope_is_refused_on_projection_and_readback(text):
    from app.modules.dce.application.analysis import is_valid_rc_observation

    assert not any(o.requirement_kind.startswith("DCE_") for o in signals(text, "CCTP"))
    assert not is_valid_rc_observation(
        requirement_kind="DCE_TECHNICAL_PRESCRIPTION",
        rule_id="TECHNICAL_INSTRUCTION_V7",
        directive="UNSPECIFIED",
        excerpt=text,
    )
