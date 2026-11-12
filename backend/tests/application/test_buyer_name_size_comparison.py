import pytest

from tests.application.test_buyer_file_comparison import report_for


def compare(excerpts, *, patch=None, source_state="CURRENT", kbis=True, size=50, path=None):
    from app.modules.submission.application.buyer_name_size_comparison import (
        compare_buyer_names_sizes,
    )

    report = report_for(excerpts, patch=patch, source_state=source_state, kbis=kbis)
    for f in report.files:
        if f.document_kind == "KBIS":
            f.byte_size = size
            if path is not None:
                f.archive_path = path
    return compare_buyer_names_sizes(
        files=report.files,
        requirements=report.requirements,
        dce_version_id=report.dce_version_id,
        source_state=source_state,
    )


@pytest.mark.parametrize(
    "wanted,path,state",
    [
        ("Pièce-KBIS.pdf", "annexes/Pièce-KBIS.pdf", "OBSERVED_MATCH"),
        ("Pièce-KBIS.pdf", "annexes/piece-kbis.pdf", "OBSERVED_MISMATCH"),
        ("KBIS.pdf", "annexes/kbis.pdf", "OBSERVED_MISMATCH"),
    ],
)
def test_exact_exported_basename_preserves_case_and_accents(wanted, path, state):
    row = compare([f"Le KBIS doit être nommé «{wanted}»."], path=path)[0]
    assert row.state == state and row.requested_name == wanted
    assert row.files[0].archive_path == path
    assert row.applicability == row.conformity == "UNKNOWN"
    assert row.source_anchor["source_sha256"] == "d" * 64


@pytest.mark.parametrize(
    "size,state",
    [(49, "OBSERVED_MATCH"), (50, "OBSERVED_MATCH"), (51, "OBSERVED_MISMATCH"), (None, "UNKNOWN")],
)
def test_size_limit_is_inclusive_and_unknown_is_not_zero(size, state):
    row = compare(["La taille du KBIS ne doit pas dépasser 50 octets."], size=size)[0]
    assert row.state == state and row.max_bytes == 50


def test_binary_unit_and_observed_non_compressed_file_size():
    row = compare(["La taille du KBIS ne doit pas dépasser 1 Mio."], size=1048577)[0]
    assert row.max_bytes == 1048576 and row.state == "OBSERVED_MISMATCH"


@pytest.mark.parametrize(
    "path,state",
    [("annexes/K BIS.pdf", "OBSERVED_MISMATCH"), ("annexes/KBIS.pdf", "OBSERVED_MATCH")],
)
def test_no_spaces_applies_to_exported_basenames_of_known_files(path, state):
    row = compare(["Les noms des fichiers ne doivent pas contenir d'espaces."], path=path)[0]
    assert row.state == state and row.scope == "KNOWN_DOCUMENT_FILES"


def test_global_file_size_stays_unknown_when_technical_size_is_unknown():
    row = compare(["La taille de chaque fichier ne doit pas dépasser 100 octets."])[0]
    assert row.state == "UNKNOWN" and row.reason_code == "OBSERVED_FILE_UNKNOWN"


@pytest.mark.parametrize(
    "quote",
    [
        "La taille du KBIS ne doit pas dépasser 10 Mo.",
        "La taille du KBIS ne doit pas dépasser 1,5 Mio.",
        "La taille totale du pli ne doit pas dépasser 100 octets.",
        "La taille du KBIS ne doit pas dépasser 50 octets si demandé.",
        "Le KBIS doit être nommé «KBIS.pdf» ou «Extrait.pdf».",
        "Le KBIS doit être nommé «../KBIS.pdf».",
        "Le KBIS doit être nommé «*.pdf».",
        "Le KBIS doit être nommé «KBIS.pdf»…",
    ],
)
def test_ambiguous_units_aggregate_patterns_conditions_and_truncation_stay_unknown(quote):
    assert compare([quote])[0].state == "UNKNOWN"


@pytest.mark.parametrize(
    "patch",
    [
        {"source_anchor": None},
        {"confirmation": "PENDING_HUMAN_CONFIRMATION"},
        {"lot_candidates": [1]},
        {"source_state": "UNKNOWN"},
    ],
)
def test_source_requirements_are_not_relaxed(patch):
    assert (
        compare(["La taille du KBIS ne doit pas dépasser 50 octets."], patch=patch)[0].state
        == "UNKNOWN"
    )


def test_missing_target_is_visible_without_a_match():
    row = compare(["Le KBIS doit être nommé «KBIS.pdf»."], kbis=False)[0]
    assert (
        row.state == "OBSERVED_MISMATCH"
        and row.reason_code == "TARGET_FILE_MISSING"
        and not row.files
    )


def test_obsolete_source_cannot_produce_a_known_observation():
    assert (
        compare(
            ["La taille du KBIS ne doit pas dépasser 50 octets."], source_state="REVIEW_REQUIRED"
        )[0].state
        == "UNKNOWN"
    )


def test_unparsed_current_conflicting_instruction_neutralizes_known_observation():
    rows = compare(
        [
            "La taille du KBIS ne doit pas dépasser 50 octets.",
            "La taille du KBIS ne doit pas dépasser 20 Mo.",
        ]
    )
    assert all(r.state == "UNKNOWN" for r in rows)


def test_different_exact_names_cannot_be_arbitrated():
    rows = compare(
        ["Le KBIS doit être nommé «KBIS.pdf».", "Le KBIS doit être nommé «Extrait.pdf»."],
        path="annexes/KBIS.pdf",
    )
    assert all(r.state == "UNKNOWN" for r in rows)


def test_old_report_without_new_fields_has_unknown_default():
    report = report_for([])
    assert report.buyer_names_sizes_state == "UNKNOWN" and report.name_size_comparisons == []


def test_verified_technical_byte_size_is_projected_without_manifest_change():
    report = report_for([], technical_byte_size=32)
    assert report.files[0].byte_size == 32
    stale = report_for([], technical_byte_size=32, source_state="REVIEW_REQUIRED")
    assert stale.files[0].byte_size is None


def test_format_prefix_keeps_the_requested_name_exact():
    row = compare(["Format de fichier : Le mémoire technique doit être nommé «Mémoire.DOCX»."])[0]
    assert row.scope == "TECHNICAL_RESPONSE" and row.requested_name == "Mémoire.DOCX"
    assert row.state == "OBSERVED_MISMATCH"


def test_huge_source_limit_stays_unknown_instead_of_losing_json_integer_precision():
    row = compare(["La taille du KBIS ne doit pas dépasser 999999999999999 Mio."])[0]
    assert row.state == "UNKNOWN" and row.max_bytes is None


def test_exact_name_with_space_conflicts_with_global_no_space_instruction():
    rows = compare(
        [
            "Le KBIS doit être nommé «K BIS.pdf».",
            "Les noms des fichiers ne doivent pas contenir d'espaces.",
        ],
        path="annexes/K BIS.pdf",
    )
    assert all(
        r.state == "UNKNOWN" and r.reason_code == "CONFLICTING_SOURCE_REQUIREMENTS" for r in rows
    )


def test_native_prefix_on_a_no_space_instruction_is_supported():
    row = compare(["Format de fichier : Les noms des fichiers ne doivent pas contenir d’espaces."])[
        0
    ]
    assert row.criterion == "NO_WHITESPACE" and row.state == "OBSERVED_MATCH"


def test_partial_filename_source_does_not_create_an_inferred_full_name():
    row = compare(["Format de fichier : Le mémoire technique doit être nommé «Memoire."])[0]
    assert row.state == "UNKNOWN" and row.requested_name is None


def test_name_conflict_does_not_neutralize_an_independent_size_observation():
    rows = compare(
        [
            "Le KBIS doit être nommé «K BIS.pdf».",
            "Les noms des fichiers ne doivent pas contenir d'espaces.",
            "La taille du KBIS ne doit pas dépasser 50 octets.",
        ],
        path="annexes/K BIS.pdf",
    )
    size = next(r for r in rows if r.criterion == "MAX_BYTES")
    assert size.state == "OBSERVED_MATCH" and size.reason_code == "SIZE_WITHIN_LIMIT"


@pytest.mark.parametrize("name", ["KBIS", "KBIS.pdf"])
def test_known_name_and_size_clauses_do_not_neutralize_an_independent_format(name):
    report = report_for(
        [
            "Le KBIS doit être fourni au format PDF.",
            f"Format de fichier : Le KBIS doit être nommé «{name}».",
            "Format de fichier : La taille du KBIS ne doit pas dépasser 50 octets.",
        ]
    )
    row = next(r for r in report.format_comparisons if r.requested == "PDF")
    assert row.state == "OBSERVED_MATCH"
