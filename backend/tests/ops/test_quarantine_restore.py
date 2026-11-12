from __future__ import annotations

import hashlib
import importlib.util
import io
import tarfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
SPEC = importlib.util.spec_from_file_location(
    "verify_quarantine_restore", ROOT / "ops" / "verify_quarantine_restore.py"
)
assert SPEC is not None and SPEC.loader is not None
RESTORE_MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(RESTORE_MODULE)
restore_archive = RESTORE_MODULE.restore_archive


def _archive(path: Path, name: str, payload: bytes) -> None:
    with tarfile.open(path, "w:gz") as archive:
        info = tarfile.TarInfo(name)
        info.size = len(payload)
        archive.addfile(info, io.BytesIO(payload))


def test_restore_archive_extracts_only_hash_verified_object(tmp_path: Path) -> None:
    archive = tmp_path / "quarantine.tar.gz"
    destination = tmp_path / "restore-volume"
    manifest = tmp_path / "objects.tsv"
    payload = b"synthetic C5 evidence object"
    storage_key = "tenant/case/object-v1.bin"
    digest = hashlib.sha256(payload).hexdigest()
    _archive(archive, storage_key, payload)
    manifest.write_text(f"{storage_key}\t{digest}\n", encoding="utf-8")

    verified_count = restore_archive(
        archive_path=archive, destination=destination, objects_manifest=manifest
    )

    assert verified_count == 1
    assert (destination / storage_key).read_bytes() == payload


def test_restore_archive_rejects_hash_mismatch(tmp_path: Path) -> None:
    archive = tmp_path / "quarantine.tar.gz"
    destination = tmp_path / "restore-volume"
    manifest = tmp_path / "objects.tsv"
    _archive(archive, "object.bin", b"altered object")
    manifest.write_text(f"object.bin\t{'0' * 64}\n", encoding="utf-8")

    with pytest.raises(ValueError, match="SHA-256 mismatch"):
        restore_archive(archive_path=archive, destination=destination, objects_manifest=manifest)


def test_restore_archive_rejects_path_traversal(tmp_path: Path) -> None:
    archive = tmp_path / "quarantine.tar.gz"
    destination = tmp_path / "restore-volume"
    manifest = tmp_path / "objects.tsv"
    _archive(archive, "../escape.bin", b"must not escape")
    manifest.write_text("", encoding="utf-8")

    with pytest.raises(ValueError, match="unsafe archive path"):
        restore_archive(archive_path=archive, destination=destination, objects_manifest=manifest)

    assert not (tmp_path / "escape.bin").exists()
