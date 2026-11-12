from dataclasses import replace
from hashlib import sha256
from uuid import UUID

import pytest
from app.modules.knowledge.domain.retrieval import DataClassification, RetrievalChunk


def source(text, i=1, **changes):
    return replace(
        RetrievalChunk(
            chunk_id=UUID(int=i),
            source_fragment_id=UUID(int=i),
            tenant_id=UUID(int=40),
            case_id=UUID(int=41),
            dce_version_id=UUID(int=42),
            ordinal=i,
            text=text,
            locator={"page": i},
            classification=DataClassification.INTERNAL_OPERATIONAL,
        ),
        **changes,
    )


def project(*chunks):
    from app.modules.knowledge.application.rc_candidate_conflicts import project_rc_conflicts

    return project_rc_conflicts(chunks)


@pytest.mark.parametrize(
    "positive,negative,subject",
    [
        ("la visite est obligatoire", "la visite est facultative", "VISIT"),
        (
            "le mémoire technique est exigé",
            "le mémoire technique n'est pas exigé",
            "MEMOIRE_TECHNIQUE",
        ),
        ("le DC1 est requis", "aucun DC1 n'est requis", "DC1"),
        ("les variantes sont autorisées", "les variantes sont interdites", "VARIANTS"),
    ],
)
def test_opposite_clauses_have_exact_source_pair_and_unknown_applicability(
    positive, negative, subject
):
    a, b = source(f"Lot 4 : {positive}."), source(f"Lot 4 : {negative}.", 2)
    result = project(a, b)
    assert len(result.links) == 1
    link = result.links[0]
    assert link.kind == "OPPOSITION" and link.applicability == "UNKNOWN"
    assert {link.left.source_fragment_id, link.right.source_fragment_id} == {
        UUID(int=1),
        UUID(int=2),
    }
    assert link.left.subject == subject and link.left.lot == link.right.lot == 4
    for evidence in (link.left, link.right):
        original = a if evidence.source_fragment_id == a.source_fragment_id else b
        assert (
            original.text.encode()[evidence.start_byte : evidence.end_byte].decode()
            == evidence.excerpt
        )
        assert evidence.source_sha256 == sha256(original.text.encode()).hexdigest()
        assert evidence.dce_version_id == original.dce_version_id


@pytest.mark.parametrize(
    "change",
    [
        {"tenant_id": UUID(int=99)},
        {"case_id": UUID(int=99)},
        {"dce_version_id": UUID(int=99)},
        {"classification": DataClassification.FINANCIAL_PRIVATE},
        {"classification": DataClassification.PERSONAL_DATA},
    ],
)
def test_never_links_different_security_or_version_scopes(change):
    a = source("Lot 4 : la visite est obligatoire.")
    b = source("Lot 4 : la visite est facultative.", 2, **change)
    assert project(a, b).links == ()


def test_same_subject_different_lot_is_not_a_conflict():
    assert not project(
        source("Lot 4 : la visite est obligatoire."),
        source("Lot 5 : la visite est facultative.", 2),
    ).links


@pytest.mark.parametrize(
    "text",
    [
        "La visite est obligatoire.",
        "Lots 4 et 5 : la visite est obligatoire.",
        "Lot 4 : la visite est obligatoire sauf dispense.",
        "Lot 4 : la visite n'est pas non obligatoire.",
        "Lot 4 : la visite peut être obligatoire si le site est occupé.",
        "Lot 4 : la visite est obligatoire et le certificat est requis.",
        "Lot 4 : la visite est obligatoire ?",
        "Lot 4 : la visite est obligatoire",
    ],
)
def test_unproven_scope_negation_conditions_or_compound_clause_stays_unknown(text):
    result = project(source(text))
    assert not result.clauses and not result.links and result.unknown_regions


def test_negation_alone_is_not_a_contradiction_or_a_prohibition():
    result = project(source("Lot 4 : la visite n’est pas obligatoire."))
    assert len(result.clauses) == 1 and not result.links
    assert result.clauses[0].value == "NOT_REQUIRED" and result.clauses[0].kind == "NEGATION"


def test_rectification_is_separate_and_never_establishes_precedence():
    result = project(
        source("Lot 4 : la visite est obligatoire."),
        source("Rectificatif : lot 4 : la visite est facultative.", 2),
    )
    assert len(result.links) == 1 and result.links[0].kind == "RECTIFICATION_OPPOSITION"
    assert result.clauses[1].kind == "RECTIFICATION"
    assert result.links[0].applicability == "UNKNOWN"


def test_same_statement_duplicate_and_unrelated_text_do_not_create_a_pair():
    a = source("Lot 4 : la visite est obligatoire.")
    assert not project(a, a, source("Une isolation de 90 mm est prévue.", 3)).links


def test_segment_offset_and_source_digest_are_preserved():
    text = "Lot 4 : la visite est facultative."
    from app.modules.knowledge.application.rc_candidate_conflicts import project_rc_conflicts

    c = replace(source(text), locator={"page": 3})
    evidence = project_rc_conflicts([c], regions={c.chunk_id: (20, "a" * 64)}).unknown_regions[0]
    assert evidence.start_byte == 20 and evidence.end_byte == 20 + len(text.encode())
    assert evidence.source_sha256 == "a" * 64 and evidence.locator["page"] == 3


def test_projection_refuses_excessive_clauses():
    with pytest.raises(ValueError, match="budget"):
        project(source("Lot 4 : la visite est obligatoire. " * 300))


@pytest.mark.parametrize(
    "prefix", ["Si le site est occupé :\n", "Sous réserve d'accord.\n", "Sauf dispense :\n"]
)
def test_upstream_condition_never_disappears_at_line_or_sentence_boundary(prefix):
    result = project(
        source(prefix + "Lot 4 : la visite est obligatoire."),
        source("Lot 4 : la visite est facultative.", 2),
    )
    assert not result.links and result.unknown_regions


def test_partial_upstream_region_remains_unknown_across_newline():
    from app.modules.knowledge.application.rc_candidate_conflicts import project_rc_conflicts

    a = source("dispense accordée\nLot 4 : la visite est obligatoire.")
    result = project_rc_conflicts(
        [a, source("Lot 4 : la visite est facultative.", 2)], regions={a.chunk_id: (20, "a" * 64)}
    )
    assert not result.links and result.unknown_regions
