from __future__ import annotations

import hashlib
import json
from typing import Any

import pytest
from app.platform.quality.golden_corpus import main, parse_manifest


def _manifest() -> dict[str, Any]:
    return {
        "schema_version": 1,
        "corpus_id": "corpus-v1",
        "documents": [
            {
                "document_id": "dce-001",
                "filename": "rc.pdf",
                "sha256": "a" * 64,
                "media_type": "application/pdf",
                "expected_text_fragments": ["règlement de consultation"],
                "expected_labels": ["deadline"],
            }
        ],
    }


def test_manifest_parses_closed_document_contract() -> None:
    manifest = parse_manifest(_manifest())

    assert manifest.corpus_id == "corpus-v1"
    assert manifest.documents[0].filename == "rc.pdf"
    assert manifest.documents[0].expected_labels == ("deadline",)


@pytest.mark.parametrize(
    "mutator, code",
    [
        (
            lambda value: value["documents"][0].update({"filename": "../rc.pdf"}),
            "GOLDEN_DOCUMENT_FILENAME_INVALID",
        ),
        (
            lambda value: value["documents"][0].update({"sha256": "invalid"}),
            "GOLDEN_DOCUMENT_HASH_INVALID",
        ),
        (
            lambda value: value["documents"][0].update({"extra": True}),
            "GOLDEN_DOCUMENT_FIELDS_INVALID",
        ),
        (
            lambda value: value["documents"].append(value["documents"][0].copy()),
            "GOLDEN_MANIFEST_DOCUMENT_ID_DUPLICATE",
        ),
    ],
)
def test_manifest_rejects_unsafe_or_ambiguous_documents(mutator, code: str) -> None:
    manifest = _manifest()
    mutator(manifest)

    with pytest.raises(ValueError, match=code):
        parse_manifest(manifest)


def test_manifest_cli_checks_hashes_for_nonempty_manifest(tmp_path, capsys) -> None:
    payload = b"synthetic DCE bytes"
    (tmp_path / "rc.pdf").write_bytes(payload)
    raw = _manifest()
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(json.dumps(raw), encoding="utf-8")

    assert main([str(manifest_path)]) == 1
    assert "GOLDEN_DOCUMENT_HASH_MISMATCH" in capsys.readouterr().err


def test_manifest_cli_accepts_recalculated_synthetic_file_hash(tmp_path) -> None:
    payload = b"synthetic DCE bytes"
    (tmp_path / "rc.pdf").write_bytes(payload)
    raw = _manifest()
    raw["documents"][0]["sha256"] = hashlib.sha256(payload).hexdigest()
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(json.dumps(raw), encoding="utf-8")

    assert main([str(manifest_path)]) == 0


def test_manifest_cli_rejects_missing_or_symlinked_documents(tmp_path, capsys) -> None:
    raw = _manifest()
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(json.dumps(raw), encoding="utf-8")

    assert main([str(manifest_path)]) == 1
    assert "GOLDEN_DOCUMENT_FILE_UNAVAILABLE" in capsys.readouterr().err

    outside = tmp_path.parent / "outside.pdf"
    outside.write_bytes(b"synthetic external sentinel")
    (tmp_path / "rc.pdf").symlink_to(outside)
    assert main([str(manifest_path)]) == 1
    assert "GOLDEN_DOCUMENT_FILE_INVALID" in capsys.readouterr().err


def test_empty_example_manifest_remains_structural_only(tmp_path) -> None:
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(
        json.dumps({"schema_version": 1, "corpus_id": "empty-example", "documents": []}),
        encoding="utf-8",
    )

    assert main([str(manifest_path)]) == 0
