import json
from hashlib import sha256
from pathlib import Path
from uuid import uuid4

import pytest
from app.modules.dce.application import analysis as a

FIXTURE = Path(__file__).parents[2] / "fixtures/rc_requirements_holdout_v1.json"
CASES = json.loads(FIXTURE.read_text())["cases"]


def source(text):
    return a.RcAnalysisSourceFragment(
        uuid4(), uuid4(), uuid4(), 1, text, sha256(text.encode()).hexdigest(), "RC"
    )


@pytest.mark.parametrize("case", CASES, ids=lambda x: x["id"])
def test_holdout_signals_have_distinct_exact_clauses_and_conservative_directives(case):
    fragment = source(case["text"])
    result = a._project_rc_requirements(sources=(fragment,))
    actual = [(x.requirement_kind, x.directive, x.excerpt.strip()) for x in result.observations]
    assert sorted(actual) == sorted(tuple(x) for x in case["expected"])
    for x in result.observations:
        assert fragment.text.encode()[x.start_byte_offset : x.end_byte_offset].decode() == x.excerpt
        assert a.is_valid_rc_observation(
            requirement_kind=x.requirement_kind,
            rule_id=x.rule_id,
            directive=x.directive,
            excerpt=x.excerpt,
        )


def test_long_matching_clause_is_refused_instead_of_losing_its_condition():
    result = a._project_rc_requirements(
        sources=(source("Si " + "contexte " * 160 + "le mémoire technique est obligatoire."),)
    )
    assert result.status == "REJECTED_LIMIT" and result.observations == ()


def test_wrapped_text_does_not_break_a_single_obligation():
    result = a._project_rc_requirements(sources=(source("Le mémoire technique est\nobligatoire."),))
    assert len(result.observations) == 1 and result.observations[0].directive == "REQUIRED_SIGNAL"


def test_historical_version_four_keeps_its_own_interpretation():
    args = dict(
        requirement_kind="RC_CONTENT_OFFER",
        rule_id="OFFER_TECHNICAL_MEMORY_V1",
        excerpt="Le candidat ne doit pas joindre le mémoire technique.",
        directive="REQUIRED_SIGNAL",
    )
    assert a.is_valid_rc_observation(**args, rule_version="4")
    assert not a.is_valid_rc_observation(**args, rule_version="5")


@pytest.mark.parametrize(
    "text",
    [
        "Lorsque le lot 2 est retenu, le mémoire technique est obligatoire.",
        "Le mémoire technique est obligatoire sous condition de sélection du lot 2.",
        "La visite de site est obligatoire à moins que le candidat dispose d’une attestation.",
    ],
)
def test_conditional_obligations_are_not_promoted(text):
    result = a._project_rc_requirements(sources=(source(text),))
    assert result.observations and all(x.directive == "UNSPECIFIED" for x in result.observations)


def test_conditional_list_context_is_refused_without_partial_certainties():
    text = (
        "Si le lot 2 est retenu :\n- Le mémoire technique est obligatoire.\n"
        "- La visite de site est obligatoire."
    )
    result = a._project_rc_requirements(sources=(source(text),))
    assert result.status == "FAILED_SAFE" and result.failure_code == "RC_LIST_CONTEXT_UNPROVEN"
    assert result.observations == () and result.source_fragments[0].text == text


@pytest.mark.parametrize("header", ["Si le lot 2\nest retenu :\n", "Si le lot 2 est retenu :\n\n"])
def test_wrapped_or_spaced_conditional_lists_are_not_certainties(header):
    result = a._project_rc_requirements(
        sources=(source(header + "- Le mémoire technique est obligatoire."),)
    )
    assert result.status == "FAILED_SAFE" and not result.observations


def test_condition_in_another_fragment_of_same_extraction_cannot_be_lost():
    from dataclasses import replace

    first = source("Si le lot 2 est retenu :")
    second = replace(
        source("- Le mémoire technique est obligatoire."),
        dce_document_id=first.dce_document_id,
        extraction_id=first.extraction_id,
        ordinal=2,
    )
    result = a._project_rc_requirements(sources=(first, second))
    assert result.status == "FAILED_SAFE" and not result.observations
    foreign = source("- Le mémoire technique est obligatoire.")
    assert a._project_rc_requirements(sources=(first, foreign)).status == "COMPLETED"


def test_numbered_conditional_list_does_not_lose_header_at_number_period():
    result = a._project_rc_requirements(
        sources=(source("Si le lot 2 est retenu :\n1. Le mémoire technique est obligatoire."),)
    )
    assert result.status == "FAILED_SAFE" and not result.observations


def test_profile_url_is_not_split_at_domain_or_query_punctuation():
    quote = "Le dépôt électronique se fait via le profil d'acheteur https://plateforme.test/depot?lot=2."
    text = quote + " Le mémoire technique est obligatoire."
    result = a._project_rc_requirements(sources=(source(text),))
    channel = next(x for x in result.observations if x.requirement_kind == "RC_RESPONSE_CHANNEL")
    assert channel.excerpt == quote
    assert a.is_valid_rc_observation(
        requirement_kind=channel.requirement_kind,
        rule_id=channel.rule_id,
        directive=channel.directive,
        excerpt=channel.excerpt,
    )


def test_url_boundaries_have_bounded_cost_without_copying_token_per_dot():
    import signal

    old_handler = signal.getsignal(signal.SIGALRM)
    old_timer = signal.getitimer(signal.ITIMER_REAL)

    def expired(*_):
        raise AssertionError("URL boundary parse exceeded budget")

    signal.signal(signal.SIGALRM, expired)
    signal.setitimer(signal.ITIMER_REAL, 2)
    try:
        text = "Profil d'acheteur https://" + "a." * 400000 + "test chemin."
        assert list(a._clause_ends_v5(text))[-1] == len(text)
    finally:
        signal.setitimer(signal.ITIMER_REAL, *old_timer)
        signal.signal(signal.SIGALRM, old_handler)


def test_independent_negation_does_not_refuse_an_unconditional_list():
    text = (
        "Le candidat ne doit pas remettre de papier. Contenu de l'offre :\n"
        "- Le mémoire technique est obligatoire."
    )
    result = a._project_rc_requirements(sources=(source(text),))
    assert result.status == "COMPLETED"
    assert len(result.observations) == 1 and result.observations[0].directive == "REQUIRED_SIGNAL"
