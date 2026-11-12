"""Development regressions; no expected value is injected into the extractor."""

from hashlib import sha256
from uuid import uuid4

import pytest
from app.modules.dce.application.analysis import (
    ANALYZER_VERSION,
    RcAnalysisSourceFragment,
    _project_rc_requirements,
    is_valid_rc_observation,
)

TECH = "DCE_TECHNICAL_PRESCRIPTION"
TIME = "DCE_SCHEDULE_CONSTRAINT"


def observations(text, family):
    return _project_rc_requirements(
        sources=(
            RcAnalysisSourceFragment(
                uuid4(),
                uuid4(),
                uuid4(),
                1,
                text,
                sha256(text.encode()).hexdigest(),
                family,
            ),
        )
    ).observations


@pytest.mark.parametrize(
    "text,family,kind",
    [
        ("Le titulaire doit fournir les plans pour le lot 2.", "CCTP", TECH),
        ("Fournir les notes de calcul pour le lot 1.", "CCTP", TECH),
        ("Le titulaire doit remettre les fiches techniques pour le lot 2.", "CCAP", TECH),
        ("Les plans d'exécution doivent être fournis pour le lot 2.", "CCTP", TECH),
        ("Les fiches techniques doivent être remises pour le lot 1.", "CCTP", TECH),
        ("Le délai d'exécution est de 6 semaines pour le lot 7.", "PLANNING", TIME),
        ("Le délai global d'exécution est de 6 semaines.", "CCAP", TIME),
        ("Le délai d'exécution est fixé à six (6) semaines.", "CCAP", TIME),
        ("La durée des travaux est fixée à huit mois pour le lot 1.", "CCAP", TIME),
        ("Délai d’exécution : 12 jours ouvrés pour le lot 2.", "CCTP", TIME),
        ("La durée d'exécution sera de vingt-quatre semaines.", "PLANNING", TIME),
        ("Le délai d'exécution est de 1,5 mois pour le lot 2.", "PLAN", TIME),
    ],
)
def test_explicit_statement_has_exact_source_and_current_proof(text, family, kind):
    hits = [o for o in observations(text, family) if o.requirement_kind == kind]
    assert len(hits) == 1
    o = hits[0]
    assert o.excerpt == text
    assert text.encode()[o.start_byte_offset : o.end_byte_offset] == text.encode()
    assert ANALYZER_VERSION == "11"
    assert is_valid_rc_observation(
        requirement_kind=kind,
        rule_id=o.rule_id,
        excerpt=o.excerpt,
        directive=o.directive,
        rule_version="8",
    )
    assert not is_valid_rc_observation(
        requirement_kind=kind,
        rule_id=o.rule_id,
        excerpt=o.excerpt,
        directive=o.directive,
        rule_version="7",
    )


@pytest.mark.parametrize(
    "text,family,kind",
    [
        ("Le titulaire ne doit pas fournir les plans pour le lot 2.", "CCTP", TECH),
        ("Si la variante est retenue, fournir les fiches techniques pour le lot 1.", "CCTP", TECH),
        ("Les plans ne doivent pas être fournis sans validation.", "CCAP", TECH),
        ("Le délai d'exécution n'est pas de six semaines.", "PLANNING", TIME),
        ("Si le support est disponible, le délai d'exécution est de six semaines.", "CCTP", TIME),
    ],
)
def test_negation_or_condition_keeps_exact_quote_and_unspecified_directive(text, family, kind):
    hits = [o for o in observations(text, family) if o.requirement_kind == kind]
    assert len(hits) == 1 and hits[0].excerpt == text
    assert hits[0].directive == "UNSPECIFIED"


@pytest.mark.parametrize(
    "text,family",
    [
        ("Le titulaire doit fournir les plans de financement.", "CCTP"),
        ("Le titulaire doit fournir les plans comptables.", "CCTP"),
        ("Le titulaire doit fournir les plans de paiement.", "CCAP"),
        ("Les plans de financement doivent être fournis.", "CCTP"),
        ("Les plans sont disponibles dans les archives.", "CCTP"),
        ("Exemple : fournir les plans.", "CCTP"),
        ("Glossaire : délai d'exécution de six semaines.", "PLANNING"),
        ("La durée de validité des offres est de six semaines.", "CCAP"),
        ("Le délai de paiement est de six semaines.", "CCAP"),
        ("Le délai d'exécution reste inconnu.", "PLANNING"),
        ("Le délai d'exécution est de 6 semaines.", "DPGF"),
        ("Le délai d'exécution est de 6 semaines.", "RC"),
        ("Fournir les plans.", "BPU"),
    ],
)
def test_foreign_or_unproved_context_has_no_new_execution_signal(text, family):
    assert not any(o.requirement_kind in {TECH, TIME} for o in observations(text, family))


def test_historical_v7_instruction_validation_is_unchanged():
    assert is_valid_rc_observation(
        requirement_kind=TECH,
        rule_id="TECHNICAL_INSTRUCTION_V7",
        excerpt="Installer une vanne pour le lot 2.",
        directive="UNSPECIFIED",
        rule_version="7",
    )
