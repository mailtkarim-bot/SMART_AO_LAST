from hashlib import sha256
from uuid import UUID

import pytest
from app.modules.knowledge.domain.retrieval import DataClassification, RetrievalChunk


def source(text):
    return RetrievalChunk(
        chunk_id=UUID(int=4),
        source_fragment_id=UUID(int=4),
        tenant_id=UUID(int=1),
        case_id=UUID(int=2),
        dce_version_id=UUID(int=3),
        ordinal=1,
        text=text,
        locator={"page": 2},
        classification=DataClassification.INTERNAL_OPERATIONAL,
    )


def project(text):
    from app.modules.knowledge.application.rc_candidate_conflicts import project_rc_conflicts

    return project_rc_conflicts([source(text)], qualified_visits=True, independent_visit_type=True)


@pytest.mark.parametrize(
    "text,signal",
    [
        ("Lot 7 : la visite médicale est obligatoire sauf dispense.", "sauf"),
        ("Si le site est occupé. Lot 7 : la visite médicale est obligatoire.", "Si"),
        ("Lot 7 : la visite médicale n’est pas obligatoire sauf décision contraire.", "sauf"),
    ],
)
def test_condition_does_not_erase_type_or_create_known_obligation(text, signal):
    result = project(text)
    assert not result.clauses and not result.links
    evidence = next(c for c in result.unknown_regions if c.visit_type_proof)
    proof = evidence.visit_type_proof
    assert proof.signal == "VISIT_MEDICAL" and evidence.directive_signal == "CANDIDATE"
    assert evidence.value == "UNKNOWN" and evidence.kind == "UNKNOWN"
    assert text.encode()[proof.start_byte : proof.end_byte].decode() == proof.excerpt
    assert evidence.source_sha256 == sha256(text.encode()).hexdigest()
    assert any(s.excerpt == signal for s in evidence.condition_signals)
    for s in evidence.condition_signals:
        assert text.encode()[s.start_byte : s.end_byte].decode() == s.excerpt


def test_type_proof_does_not_prove_an_obligation_or_admit_a_reference():
    result = project("Lot 7 : la visite médicale est citée dans une annexe.")
    evidence = result.unknown_regions[0]
    assert evidence.visit_type_proof.signal == "VISIT_MEDICAL"
    assert evidence.directive_signal == "UNKNOWN" and evidence.value == "UNKNOWN"


def test_quoted_type_is_not_a_type_proof():
    result = project("Exemple : « Début. Lot 7 : la visite médicale est obligatoire. Fin. »")
    assert not result.clauses and all(c.visit_type_proof is None for c in result.unknown_regions)


def test_unqualified_visit_does_not_acquire_a_site_type():
    result = project("Lot 7 : la visite est obligatoire.")
    assert result.clauses[0].visit_type_proof is None


def test_condition_signal_budget_is_fail_closed():
    with pytest.raises(ValueError, match="budget"):
        project("Si " * 17 + ". Lot 7 : la visite médicale est obligatoire.")


def test_independent_type_requires_exact_prefix_for_segmented_source():
    from app.modules.knowledge.application.rc_candidate_conflicts import project_rc_conflicts

    chunk = source("Fin. Lot 7 : la visite médicale est obligatoire.")
    with pytest.raises(ValueError, match="prefix required"):
        project_rc_conflicts(
            [chunk],
            regions={chunk.chunk_id: (20, "a" * 64)},
            qualified_visits=True,
            independent_visit_type=True,
        )


def test_independent_type_refuses_a_context_from_other_bytes():
    from app.modules.knowledge.application.rc_candidate_conflicts import project_rc_conflicts

    chunk = source("Lot 7 : la visite médicale est obligatoire.")
    with pytest.raises(ValueError, match="context does not match source"):
        project_rc_conflicts(
            [chunk],
            qualified_visits=True,
            independent_visit_type=True,
            source_contexts={chunk.chunk_id: chunk.text + " autre contexte"},
        )
