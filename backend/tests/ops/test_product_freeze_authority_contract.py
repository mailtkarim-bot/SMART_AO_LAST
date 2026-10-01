import hashlib
import json
import re
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
DOCS_ROOT = REPOSITORY_ROOT / "docs"
ACTIVE_FREEZE = (
    DOCS_ROOT
    / "Actifs"
    / "01_Cahiers_des_charges"
    / "SMART_AO_Cahier_Directeur_Produit_Metier_OWNER_FREEZE_v3.1.md"
)
ARCHIVED_V04 = (
    DOCS_ROOT
    / "Archive"
    / "01_Cahiers_remplaces"
    / "Produit_metier"
    / "SMART_AO_Cahier_Directeur_Produit_Metier_OWNER_CONSOLIDATED_v0.4.md"
)
ARCHIVED_V1 = (
    DOCS_ROOT
    / "Archive"
    / "01_Cahiers_remplaces"
    / "Produit_metier"
    / "SMART_AO_Cahier_Directeur_Produit_Metier_OWNER_FREEZE_v1.0.md"
)
OLD_FILENAME = "SMART_AO_Cahier_Directeur_Produit_Metier_OWNER_CONSOLIDATED_v0.4.md"
ACTIVE_FILENAME = "SMART_AO_Cahier_Directeur_Produit_Metier_OWNER_FREEZE_v3.1.md"


def _active_document_text() -> str:
    return "\n".join(
        path.read_text(encoding="utf-8")
        for path in (
            DOCS_ROOT / "README_DOCUMENTATION.md",
            DOCS_ROOT / "Actifs" / "00_INDEX_DOCUMENTATION_ACTIVE.md",
        )
    )


def test_product_freeze_is_the_only_active_product_authority() -> None:
    assert ACTIVE_FREEZE.is_file()
    assert ARCHIVED_V04.is_file()
    assert ARCHIVED_V1.is_file()
    assert not (DOCS_ROOT / "Actifs" / "01_Cahiers_des_charges" / OLD_FILENAME).exists()

    active_text = _active_document_text()
    assert ACTIVE_FILENAME in active_text
    assert OLD_FILENAME not in active_text


def test_product_freeze_and_traceability_contract_are_active() -> None:
    freeze_text = ACTIVE_FREEZE.read_text(encoding="utf-8")
    matrix = (
        DOCS_ROOT
        / "Actifs"
        / "00_Pilotage_et_audits"
        / "SMART_AO_REALIGNEMENT_V3_1_DECISIONS_ET_TRACABILITE_2026-09-30.md"
    )
    assert "AUTORITÉ PRODUIT/MÉTIER ACTIVE" in freeze_text
    assert "Promotion" in freeze_text
    archived_filename = "SMART_AO_Cahier_Directeur_Produit_Metier_OWNER_FREEZE_v2.0.md"
    assert not (DOCS_ROOT / "Actifs" / "01_Cahiers_des_charges" / archived_filename).exists()
    assert (
        DOCS_ROOT
        / "Archive"
        / "01_Cahiers_remplaces"
        / "Produit_metier"
        / archived_filename
    ).is_file()
    assert list((DOCS_ROOT / "Actifs" / "01_Cahiers_des_charges").glob("*OWNER_FREEZE*.md")) == [
        ACTIVE_FREEZE
    ]
    assert matrix.is_file()
    assert "PF31-05" in matrix.read_text(encoding="utf-8")
    assert "PARTIAL" in matrix.read_text(encoding="utf-8")


def _normalize_relocated_archive_link(line: str) -> str:
    archived_files = (
        "SMART_AO_Univers_documentaire_metier_v1.0.md",
        "SMART_AO_Cahier_des_charges_Metier_v1.0.md",
    )
    for filename in archived_files:
        line = re.sub(
            rf"\]\([^)]*({re.escape(filename)})(#[^)]*)?\)",
            r"](__ARCHIVED_PRODUCT__/\1\2)",
            line,
        )
    return line


def test_integral_specs_preserve_every_source_chapter_and_body_line() -> None:
    manifest_path = (
        DOCS_ROOT
        / "Actifs"
        / "00_Pilotage_et_audits"
        / "SMART_AO_CDC_INTEGRAL_V3_1_COVERAGE_2026-09-30.json"
    )
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert len(manifest["sources"]) == 5
    for entry in manifest["sources"]:
        source_bytes = (REPOSITORY_ROOT / entry["source"]).read_bytes()
        assert hashlib.sha256(source_bytes).hexdigest() == entry["source_sha256"]
        original = source_bytes.decode().splitlines()
        if entry["scope"] == "complete v3 delta before inherited part":
            boundary = next(
                i for i, line in enumerate(original) if line.startswith("# PARTIE II —")
            )
            original = original[:boundary]
        expected = "\n".join(original).rstrip().splitlines()
        active = (REPOSITORY_ROOT / entry["target"]).read_text(encoding="utf-8")
        marker = entry["marker"]
        assert active.count(f"<!-- BEGIN {marker} -->") == 1
        body = active.split(f"<!-- BEGIN {marker} -->\n", 1)[1]
        body = body.split(f"\n<!-- END {marker} -->", 1)[0]
        actual = [line for line in body.splitlines() if not line.startswith('<a id="')]
        prefix = entry["prefix"]
        restored = [
            re.sub(rf"^#{{1,6}} {prefix}-[0-9]{{3}} — ", "# ", line)
            for line in actual
        ]
        normalized = [_normalize_relocated_archive_link(line) for line in expected]
        restored = [_normalize_relocated_archive_link(line) for line in restored]
        normalized = [re.sub(r"^#{1,6} ", "# ", line) for line in normalized]
        assert restored == normalized, entry["source"]
        ids = re.findall(r'<a id="([^" ]+)"></a>', active)
        assert len(ids) == len(set(ids)), entry["target"]


def test_local_agent_entrypoints_follow_one_current_coding_plan() -> None:
    plan_path = (
        DOCS_ROOT
        / "Actifs"
        / "00_Pilotage_et_audits"
        / "SMART_AO_PLAN_GLOBAL_CONCEPTION_REALISATION_CHECKLIST_v0.1.md"
    )
    plan = plan_path.read_text(encoding="utf-8")
    active_lines = [line for line in plan.splitlines() if line.startswith("- [>] ")]
    assert len(active_lines) == 1
    next_step = next(
        line.removeprefix("**Prochaine étape unique :** ")
        for line in plan.splitlines()
        if line.startswith("**Prochaine étape unique :** ")
    )
    assert active_lines[0] == "- [>] " + next_step
    assert "## Reprise immédiate" in plan
    assert "## Séquence de codage active V3.1" in plan
    readme = (REPOSITORY_ROOT / "README.md").read_text(encoding="utf-8")
    agent = (REPOSITORY_ROOT / "AGENTS.md").read_text(encoding="utf-8")
    for filename in (
        ACTIVE_FILENAME,
        "SMART_AO_CAHIER_DIRECTEUR_METIER_MASTER_v3.1.md",
        "SMART_AO_CAHIER_TECHNIQUE_EXECUTION_v3.1.md",
    ):
        assert filename in readme
        assert filename in agent
    for link in re.findall(r"\]\(([^)]+)\)", readme):
        if not link.startswith(("http://", "https://", "#")):
            assert (REPOSITORY_ROOT / link.split("#", 1)[0]).exists(), link
    todo = (REPOSITORY_ROOT / "todo.md").read_text(encoding="utf-8")
    assert "pas source de vérité opérationnelle actuelle" in todo
    assert plan_path.name in todo
