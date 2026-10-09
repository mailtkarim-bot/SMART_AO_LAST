#!/usr/bin/env python3
"""Safely extract a quarantine archive and verify restored C5 CLEAN objects."""

from __future__ import annotations

import argparse
import hashlib
import re
import shutil
import tarfile
from pathlib import Path, PurePosixPath

_SHA256_PATTERN = re.compile(r"^[a-f0-9]{64}$")


def _relative_path(value: str, *, allow_root: bool = False) -> PurePosixPath:
    path = PurePosixPath(value)
    if path.is_absolute() or ".." in path.parts:
        raise ValueError("unsafe archive path")
    parts = tuple(part for part in path.parts if part not in {"", "."})
    if not parts and allow_root:
        return PurePosixPath(".")
    if not parts:
        raise ValueError("unsafe archive path")
    return PurePosixPath(*parts)


def _read_objects_manifest(manifest_path: Path) -> list[tuple[PurePosixPath, str]]:
    objects: list[tuple[PurePosixPath, str]] = []
    for line in manifest_path.read_text(encoding="utf-8").splitlines():
        if not line:
            continue
        fields = line.split("\t")
        if len(fields) != 2 or not _SHA256_PATTERN.fullmatch(fields[1]):
            raise ValueError("invalid C5 object manifest")
        objects.append((_relative_path(fields[0]), fields[1]))
    return objects


def restore_archive(*, archive_path: Path, destination: Path, objects_manifest: Path) -> int:
    """Extract regular files into an empty isolated volume and verify CLEAN hashes."""

    if destination.is_symlink():
        raise ValueError("unsafe quarantine restore destination")
    destination.mkdir(mode=0o700, parents=True, exist_ok=True)
    if any(destination.iterdir()):
        raise ValueError("quarantine restore destination is not empty")
    destination = destination.resolve()

    seen: set[PurePosixPath] = set()
    with tarfile.open(archive_path, mode="r:gz") as archive:
        for member in archive:
            relative = _relative_path(member.name, allow_root=True)
            if relative in seen:
                raise ValueError("duplicate quarantine archive path")
            seen.add(relative)
            if relative == PurePosixPath("."):
                target = destination
            else:
                target = destination.joinpath(*relative.parts)
            if not target.resolve().is_relative_to(destination):
                raise ValueError("unsafe archive path")
            if member.isdir():
                target.mkdir(mode=0o700, parents=True, exist_ok=True)
                continue
            if not member.isfile():
                raise ValueError("unsupported quarantine archive entry")
            target.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
            source = archive.extractfile(member)
            if source is None:
                raise ValueError("invalid quarantine archive entry")
            with source, target.open("xb") as restored:
                shutil.copyfileobj(source, restored)
            target.chmod(0o600)

    objects = _read_objects_manifest(objects_manifest)
    for relative, expected_sha256 in objects:
        restored = destination.joinpath(*relative.parts)
        if restored.is_symlink() or not restored.is_file():
            raise ValueError("C5 quarantine object is missing after restore")
        actual_sha256 = hashlib.sha256(restored.read_bytes()).hexdigest()
        if actual_sha256 != expected_sha256:
            raise ValueError("C5 quarantine object SHA-256 mismatch")
    return len(objects)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--archive", type=Path, required=True)
    parser.add_argument("--destination", type=Path, required=True)
    parser.add_argument("--objects-manifest", type=Path, required=True)
    arguments = parser.parse_args()
    verified_count = restore_archive(
        archive_path=arguments.archive,
        destination=arguments.destination,
        objects_manifest=arguments.objects_manifest,
    )
    print(f"C5 quarantine restore verified {verified_count} CLEAN object SHA-256 value(s)")


if __name__ == "__main__":
    main()
