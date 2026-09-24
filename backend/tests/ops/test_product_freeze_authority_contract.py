from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
DOCS_ROOT = REPOSITORY_ROOT / "docs"
ACTIVE_FREEZE = (
    DOCS_ROOT
    / "00_REFERENCE_ACTIVE"
    / "SMART_AO_Cahier_Directeur_Produit_Metier_OWNER_FREEZE_v2.0.md"
)
ARCHIVED_V04 = (
    DOCS_ROOT
    / "_ARCHIVE"
    / "produit_metier"
    / "SMART_AO_Cahier_Directeur_Produit_Metier_OWNER_CONSOLIDATED_v0.4.md"
)
ARCHIVED_V1 = (
    DOCS_ROOT
    / "_ARCHIVE"
    / "produit_metier"
    / "SMART_AO_Cahier_Directeur_Produit_Metier_OWNER_FREEZE_v1.0.md"
)
OLD_FILENAME = "SMART_AO_Cahier_Directeur_Produit_Metier_OWNER_CONSOLIDATED_v0.4.md"
ACTIVE_FILENAME = "SMART_AO_Cahier_Directeur_Produit_Metier_OWNER_FREEZE_v2.0.md"


def _active_document_text() -> str:
    return "\n".join(
        path.read_text(encoding="utf-8")
        for path in (
            DOCS_ROOT / "README_DOCUMENTATION.md",
            DOCS_ROOT / "00_REFERENCE_ACTIVE" / "00_INDEX_REFERENCE_ACTIVE.md",
        )
    )


def test_product_freeze_is_the_only_active_product_authority() -> None:
    assert ACTIVE_FREEZE.is_file()
    assert ARCHIVED_V04.is_file()
    assert ARCHIVED_V1.is_file()
    assert not (DOCS_ROOT / "00_REFERENCE_ACTIVE" / OLD_FILENAME).exists()

    active_text = _active_document_text()
    assert ACTIVE_FILENAME in active_text
    assert OLD_FILENAME not in active_text


def test_product_freeze_and_traceability_contract_are_active() -> None:
    freeze_text = ACTIVE_FREEZE.read_text(encoding="utf-8")
    matrix = (
        DOCS_ROOT
        / "03_PRODUCT_DESIGN_WORKING"
        / "realignment_v2_audit"
        / "MASTER_V2_TRACEABILITY_MATRIX.md"
    )
    assert "PRODUCT FREEZE v2.0 — PROMU PAR LE PROPRIÉTAIRE" in freeze_text
    assert "Promotion" in freeze_text
    assert matrix.is_file()
    assert "Traçabilité du candidat Product Freeze v2" in matrix.read_text(encoding="utf-8")
    assert "READY_WITH_BLOCKERS" in matrix.read_text(encoding="utf-8")
