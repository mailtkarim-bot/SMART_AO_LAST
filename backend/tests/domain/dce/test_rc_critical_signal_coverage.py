from hashlib import sha256
from uuid import uuid4

import pytest
from app.modules.dce.application.analysis import (
    ANALYZER_VERSION,
    RcAnalysisSourceFragment,
    _project_rc_requirements,
    _recording_command,
    is_valid_rc_observation,
)


def source(text: str, family: str | None = "RC") -> RcAnalysisSourceFragment:
    return RcAnalysisSourceFragment(
        uuid4(), uuid4(), uuid4(), 1, text, sha256(text.encode()).hexdigest(), family
    )


@pytest.mark.parametrize(
    ("text", "kind", "quote"),
    [
        (
            "Critères de choix. "
            + "Contexte. " * 150
            + "Critère qualité environnementale et sociale (15%). "
            + "Contexte. " * 150
            + "Critère prix (35%).",
            "RC_AWARD_CRITERION",
            "Critère qualité environnementale et sociale (15%)",
        ),
        (
            "Critères de choix. " + "Contexte. " * 150 + "Critère prix (35%).",
            "RC_AWARD_CRITERION",
            "Critère prix (35%)",
        ),
        (
            "CRITERE 1 − Prix (55%) : montant total fictif.",
            "RC_AWARD_CRITERION",
            "CRITERE 1 − Prix (55%)",
        ),
        (
            "Date limite de remise des candidatures. "
            + "Contexte. " * 150
            + "Les offres des soumissionnaires devront être remises "
            "au plus tard le 21 décembre 2034 avant 14h00.",
            "RC_SUBMISSION_DEADLINE",
            "Les offres des soumissionnaires devront être remises "
            "au plus tard le 21 décembre 2034 avant 14h00.",
        ),
        (
            "Il est précisé que la visite présente un caractère obligatoire "
            "pour la recevabilité de l’offre.",
            "RC_SITE_VISIT",
            "Il est précisé que la visite présente un caractère obligatoire "
            "pour la recevabilité de l’offre.",
        ),
        (
            "En ce qui concerne la sous-traitance. "
            + "Contexte. " * 150
            + "Lot fictif : toute sous-traitance sur le périmètre réservé est réputée interdite.",
            "CCAP_SUBCONTRACTING",
            "toute sous-traitance sur le périmètre réservé est réputée interdite.",
        ),
    ],
    ids=["rse", "price", "price_numbered", "deadline_body", "visit_clause", "subcontracting_rc"],
)
def test_critical_quote_has_its_own_typed_source_window(text: str, kind: str, quote: str) -> None:
    fragment = source(text)
    projection = _project_rc_requirements(sources=(fragment,))
    matches = [
        o for o in projection.observations if o.requirement_kind == kind and quote in o.excerpt
    ]
    assert matches
    for observation in matches:
        assert (
            fragment.text.encode()[
                observation.start_byte_offset : observation.end_byte_offset
            ].decode()
            == observation.excerpt
        )
        assert len(observation.excerpt.encode()) <= 1000
        assert is_valid_rc_observation(
            requirement_kind=kind,
            rule_id=observation.rule_id,
            directive=observation.directive,
            excerpt=observation.excerpt,
        )


def test_new_rules_are_versioned_without_reinterpreting_v3() -> None:
    fragment = source("CRITERE 2 − Prix (55%).")
    command = _recording_command(
        dce_version_id=uuid4(), projection=_project_rc_requirements(sources=(fragment,))
    )
    assert ANALYZER_VERSION == "11"
    assert command.analyzer_version == "11"
    assert command.observations
    observation = command.observations[0]
    assert observation.rule_version == "11"
    assert not is_valid_rc_observation(
        requirement_kind=observation.requirement_kind,
        rule_id=observation.rule_id,
        directive=observation.directive,
        excerpt=observation.excerpt,
        rule_version="3",
    )


@pytest.mark.parametrize("family", [None, "UNKNOWN", "ANNEX"])
def test_rc_subcontracting_rule_does_not_promote_unclassified_sources(family: str | None) -> None:
    result = _project_rc_requirements(
        sources=(source("Toute sous-traitance est interdite.", family),)
    )
    assert not any(o.requirement_kind == "CCAP_SUBCONTRACTING" for o in result.observations)


@pytest.mark.parametrize("reverse", [False, True])
def test_each_repeated_visit_keeps_its_own_directive(reverse: bool) -> None:
    clauses = [
        "La visite présente un caractère facultatif pour le lot A.",
        "La visite présente un caractère obligatoire pour le lot B.",
    ]
    expected = ["OPTIONAL_SIGNAL", "REQUIRED_SIGNAL"]
    if reverse:
        clauses.reverse()
        expected.reverse()
    result = _project_rc_requirements(sources=(source(" ".join(clauses)),))
    matches = [o for o in result.observations if o.rule_id == "SITE_VISIT_CHARACTER_V4"]
    assert [o.directive for o in matches] == expected
    assert matches[0].end_byte_offset <= matches[1].start_byte_offset


def test_negative_visit_does_not_become_an_obligation() -> None:
    result = _project_rc_requirements(
        sources=(source("La visite présente un caractère non obligatoire pour la recevabilité."),)
    )
    assert result.observations[0].directive == "UNSPECIFIED"


def test_clause_window_does_not_rescan_an_entire_large_fragment(monkeypatch) -> None:
    from app.modules.dce.application import analysis

    text = "Contexte. " * 10000 + "La visite présente un caractère obligatoire."
    start = text.index("visite")
    scanned_lengths = []
    finditer = analysis.re.finditer

    def bounded_finditer(pattern, candidate):
        scanned_lengths.append(len(candidate))
        return finditer(pattern, candidate)

    with monkeypatch.context() as patch:
        patch.setattr(analysis.re, "finditer", bounded_finditer)
        low, high, excerpt = analysis._bounded_excerpt(
            text=text, match_start=start, match_end=start + len("visite"), clause_only=True
        )
    assert text.encode()[low:high].decode() == excerpt
    assert excerpt.strip() == "La visite présente un caractère obligatoire."
    assert max(scanned_lengths) <= 1002
