from hashlib import sha256
from uuid import uuid4

import pytest
from app.modules.dce.application.classification import (
    ClassificationDocument,
    ClassificationFragment,
    project_dce_classification,
)


def _classify(*texts: str):
    fragments = tuple(
        ClassificationFragment(
            extraction_id=uuid4(),
            fragment_id=uuid4(),
            ordinal=index,
            text=text,
            text_sha256=sha256(text.encode()).hexdigest(),
        )
        for index, text in enumerate(texts, start=1)
    )
    document = ClassificationDocument(dce_document_id=uuid4(), fragments=fragments)
    return project_dce_classification(documents=(document,)).results[0]


@pytest.mark.parametrize(
    ("heading", "references", "expected"),
    [
        ("RÈGLEMENT DE LA CONSULTATION", "Acte d'engagement DPGF annexe\n" * 30, "RC"),
        ("ACTE D'ENGAGEMENT", "Le règlement de la consultation prévoit la DPGF.\n" * 30, "AE"),
        ("CCTP", "Le CCAP et ses annexes précisent les règles.\n" * 30, "CCTP"),
    ],
)
def test_document_title_is_not_outvoted_by_references_to_other_pieces(
    heading: str, references: str, expected: str
) -> None:
    result = _classify(f"{heading}\nProjet entièrement synthétique.\n", references)
    assert result.status == "CLASSIFIED"
    assert result.classification == expected
    assert result.rule_match_count == 1
    assert len(result.evidence) == 1


def test_conflicting_explicit_titles_require_review() -> None:
    result = _classify("RÈGLEMENT DE LA CONSULTATION\nACTE D'ENGAGEMENT\n")
    assert result.status == "REVIEW_REQUIRED"
    assert result.classification is None


def test_body_reference_is_not_promoted_to_document_title() -> None:
    result = _classify(
        "Acte d'engagement à renseigner.\n"
        "Selon le règlement de la consultation, consulter les annexes.\n"
    )
    assert result.classification != "RC"


def test_title_suffix_precedes_document_list() -> None:
    result = _classify(
        "Règlement de consultation — travaux\n"
        "Composition du dossier :\nActe d’engagement\n"
        "Les pièces suivent le règlement de consultation."
    )
    assert result.status == "CLASSIFIED"
    assert result.classification == "RC"


def test_document_list_after_prose_does_not_override_title() -> None:
    result = _classify("Règlement de consultation\nComposition du dossier :\nActe d’engagement\n")
    assert result.status == "CLASSIFIED"
    assert result.classification == "RC"
