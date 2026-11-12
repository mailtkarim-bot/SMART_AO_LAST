#!/usr/bin/env python3
"""Private local inventory and native projections; never a whole-DCE claim."""

import argparse
import hashlib
import json
import math
import os
import stat
import subprocess
import sys
import tempfile
import zipfile
from collections import Counter
from dataclasses import asdict
from pathlib import Path
from uuid import NAMESPACE_URL, uuid5

MEDIA = {
    ".txt": "text/plain",
    ".pdf": "application/pdf",
    ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
}


def digest(path):
    value = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def write_json(path, value):
    with os.fdopen(
        os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC | os.O_NOFOLLOW, 0o600), "w"
    ) as stream:
        os.fchmod(stream.fileno(), 0o600)
        json.dump(value, stream, ensure_ascii=False, sort_keys=True, default=str)


def project(path, media, output):
    from app.modules.dce.application.analysis import (
        RcAnalysisSourceFragment,
        _project_rc_requirements,
    )
    from app.modules.dce.application.classification import (
        ClassificationDocument,
        ClassificationFragment,
        project_dce_classification,
    )
    from app.modules.dce.application.extraction import _project_document

    source_bytes = Path(path).read_bytes()
    source_sha256 = hashlib.sha256(source_bytes).hexdigest()
    extraction = _project_document(media_type=media, source_bytes=source_bytes)
    result = {
        "source_sha256": source_sha256,
        "status": extraction.status,
        "diagnostic": extraction.failure_code,
        "fragments": [asdict(f) for f in extraction.fragments],
        "classification": None,
        "analysis": None,
    }
    if extraction.status == "COMPLETED":
        identity = uuid5(NAMESPACE_URL, source_sha256)
        fragments = tuple(
            ClassificationFragment(
                identity,
                uuid5(identity, str(f.ordinal)),
                f.ordinal,
                f.text,
                hashlib.sha256(f.text.encode()).hexdigest(),
            )
            for f in extraction.fragments
        )
        classification = project_dce_classification(
            documents=(ClassificationDocument(identity, fragments),)
        )
        family = classification.results[0].classification if classification.results else None
        analysis = _project_rc_requirements(
            sources=tuple(
                RcAnalysisSourceFragment(
                    identity,
                    f.extraction_id,
                    f.fragment_id,
                    f.ordinal,
                    f.text,
                    f.text_sha256,
                    family,
                )
                for f in fragments
            )
        )
        result["classification"] = asdict(classification)
        result["analysis"] = asdict(analysis)
    write_json(Path(output), result)


def qualify(
    manifest,
    output_dir,
    per_document_timeout=20,
    max_file_bytes=128 * 1024 * 1024,
    max_total_bytes=2 * 1024 * 1024 * 1024,
    max_entries=10000,
    max_depth=8,
):
    if (
        not math.isfinite(per_document_timeout)
        or per_document_timeout <= 0
        or min(max_file_bytes, max_total_bytes, max_entries, max_depth) <= 0
    ):
        raise ValueError("INVALID_LIMIT")
    manifest = Path(manifest)
    raw = manifest.read_bytes()
    roots = json.loads(raw)["originals"]
    if not roots:
        raise ValueError("EMPTY_MANIFEST")
    for root in roots:
        source = Path(root["path"])
        if any(part.is_symlink() for part in (source, *source.parents)):
            raise ValueError("ROOT_SYMLINK")
        if not source.is_file() or digest(source) != root["expected_sha256"]:
            raise ValueError("HASH_MISMATCH")
        if not isinstance(root["case_alias"], str) or not root["case_alias"]:
            raise ValueError("INVALID_CASE_ALIAS")
    output = Path(output_dir).absolute()
    if any(part.is_symlink() for part in (output, *output.parents)):
        raise ValueError("OUTPUT_SYMLINK")
    if any(
        ((part / ".git").is_file() or (part / ".git" / "HEAD").is_file())
        for part in (output, *output.parents)
    ):
        raise ValueError("OUTPUT_INSIDE_GIT")
    if (output / "ledger.json").exists() or (output / "ledger.json").is_symlink():
        raise ValueError("OUTPUT_LEDGER_EXISTS")
    output.mkdir(parents=True, exist_ok=True, mode=0o700)
    os.chmod(output, 0o700)
    limits = dict(
        per_document_timeout=per_document_timeout,
        max_file_bytes=max_file_bytes,
        max_total_bytes=max_total_bytes,
        max_entries=max_entries,
        max_depth=max_depth,
    )
    version = hashlib.sha256(raw).hexdigest()
    case_versions = {}
    for case in {root["case_alias"] for root in roots}:
        canonical = sorted(
            (Path(root["path"]).name, root["expected_sha256"])
            for root in roots
            if root["case_alias"] == case
        )
        case_versions[case] = hashlib.sha256(
            json.dumps(canonical, separators=(",", ":"), ensure_ascii=False).encode()
        ).hexdigest()

    def snapshot(source, expected_hash, size_limit):
        stored = output / (expected_hash + ".source")
        if stored.exists() or stored.is_symlink():
            if stored.is_symlink() or digest(stored) != expected_hash:
                raise ValueError("SNAPSHOT_HASH_MISMATCH")
            os.chmod(stored, 0o400)
            return stored
        with tempfile.NamedTemporaryFile(dir=output, delete=False) as target:
            temporary = Path(target.name)
            try:
                copied = 0
                with os.fdopen(os.open(source, os.O_RDONLY | os.O_NOFOLLOW), "rb") as stream:
                    for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                        copied += len(chunk)
                        if copied > size_limit:
                            raise ValueError("ROOT_SIZE_LIMIT")
                        target.write(chunk)
                target.flush()
                if digest(temporary) != expected_hash:
                    raise ValueError("SNAPSHOT_HASH_MISMATCH")
                os.chmod(temporary, 0o400)
                temporary.replace(stored)
            except BaseException:
                temporary.unlink(missing_ok=True)
                raise
        return stored

    ledger, cache = [], {}
    total = 0

    def visit(path, name, locator, case, depth, forced=None):
        nonlocal total
        content_hash = digest(path) if path else None
        row = dict(
            source_ordinal=len(ledger),
            source_locator=locator,
            root_version=case_versions[case],
            case_alias=case,
            content_sha256=content_hash,
            status=forced or "PENDING",
            diagnostic=forced,
            lot_applicability="UNKNOWN",
            review_required=True,
            projection_file=None,
        )
        ledger.append(row)
        if forced:
            return
        if name.lower().endswith(".zip") or (
            Path(name).suffix.lower() not in MEDIA and zipfile.is_zipfile(path)
        ):
            row["status"] = "ARCHIVE_INVENTORIED"
            try:
                with zipfile.ZipFile(path) as archive:
                    for index, entry in enumerate(archive.infolist()):
                        child_locator = locator + [
                            {"entry_ordinal": index, "entry_name": entry.filename}
                        ]
                        reason = None
                        if entry.flag_bits & 1:
                            reason = "REJECTED_ENCRYPTED"
                        elif stat.S_ISLNK(entry.external_attr >> 16):
                            reason = "REJECTED_ZIP_SYMLINK"
                        elif entry.is_dir():
                            reason = "DIRECTORY"
                        elif (
                            depth >= max_depth
                            or len(ledger) >= max_entries
                            or entry.file_size > max_file_bytes
                            or total + entry.file_size > max_total_bytes
                        ):
                            reason = "REJECTED_LIMIT"
                        if reason:
                            visit(None, entry.filename, child_locator, case, depth + 1, reason)
                            continue
                        total += entry.file_size
                        try:
                            with tempfile.NamedTemporaryFile(dir=output, delete=False) as target:
                                temporary = Path(target.name)
                                with archive.open(entry) as stream:
                                    copied = 0
                                    for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                                        copied += len(chunk)
                                        if copied > min(entry.file_size, max_file_bytes):
                                            raise ValueError("ARCHIVE_SIZE_MISMATCH")
                                        target.write(chunk)
                            child_hash = digest(temporary)
                            stored = output / (child_hash + ".source")
                            if stored.exists() or stored.is_symlink():
                                if stored.is_symlink() or digest(stored) != child_hash:
                                    raise ValueError("SNAPSHOT_HASH_MISMATCH")
                                temporary.unlink()
                            else:
                                temporary.replace(stored)
                            os.chmod(stored, 0o400)
                            visit(stored, entry.filename, child_locator, case, depth + 1)
                        except (OSError, RuntimeError, ValueError, zipfile.BadZipFile):
                            if "temporary" in locals():
                                temporary.unlink(missing_ok=True)
                            visit(
                                None,
                                entry.filename,
                                child_locator,
                                case,
                                depth + 1,
                                "ARCHIVE_ENTRY_UNREADABLE",
                            )
            except (OSError, zipfile.BadZipFile):
                row.update(status="ARCHIVE_UNREADABLE", diagnostic="ARCHIVE_UNREADABLE")
            return
        if path.stat().st_size > max_file_bytes:
            row.update(status="REJECTED_LIMIT", diagnostic="FILE_LIMIT")
            return
        media = MEDIA.get(Path(name).suffix.lower())
        if not media:
            row.update(status="UNSUPPORTED", diagnostic="MEDIA_TYPE_UNSUPPORTED")
            return
        key = (content_hash, media)
        artifact = hashlib.sha256((content_hash + media).encode()).hexdigest() + ".projection.json"
        if key not in cache:
            destination = output / artifact
            if destination.exists():
                destination.unlink()
            child = subprocess.Popen(
                [
                    sys.executable,
                    str(Path(__file__).resolve()),
                    "--worker",
                    str(path),
                    media,
                    str(destination),
                ],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            try:
                child.wait(timeout=per_document_timeout)
                if child.returncode != 0 or not destination.exists():
                    result = dict(
                        status="FAILED_SAFE",
                        diagnostic="CHILD_FAILED",
                        fragments=[],
                        classification=None,
                        analysis=None,
                    )
                    write_json(destination, result)
                else:
                    result = json.loads(destination.read_text())
                    if result.get("source_sha256") != content_hash:
                        result = dict(
                            status="FAILED_SAFE",
                            diagnostic="WORKER_SOURCE_HASH_MISMATCH",
                            fragments=[],
                            classification=None,
                            analysis=None,
                        )
                        write_json(destination, result)
            except subprocess.TimeoutExpired:
                child.kill()
                child.wait()
                result = dict(
                    status="TIMEOUT_UNEXTRACTED",
                    diagnostic="DOCUMENT_TIMEOUT",
                    fragments=[],
                    classification=None,
                    analysis=None,
                )
                write_json(destination, result)
            cache[key] = result
        result = cache[key]
        row.update(
            status=result["status"],
            diagnostic=result["diagnostic"],
            projection_file=artifact,
            review_required=result["status"] != "COMPLETED",
        )

    for ordinal, root in enumerate(roots):
        original = Path(root["path"])
        source = snapshot(original, root["expected_sha256"], max_total_bytes)
        if not original.name.lower().endswith(".zip"):
            total += source.stat().st_size
        visit(
            source,
            original.name,
            [{"original_ordinal": ordinal, "path": root["path"]}],
            root["case_alias"],
            0,
            "REJECTED_LIMIT" if total > max_total_bytes else None,
        )
    result = dict(
        manifest_sha256=version,
        configured_limits=limits,
        ledger=ledger,
        coverage_counts=dict(Counter(row["status"] for row in ledger)),
        coverage_is_semantic=False,
        whole_dce_analysis_claim=False,
        lot_applicability="UNKNOWN",
    )
    write_json(output / "ledger.json", result)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--per-document-timeout", type=float, default=20)
    for name, default in [
        ("max-file-bytes", 128 * 1024 * 1024),
        ("max-total-bytes", 2 * 1024 * 1024 * 1024),
        ("max-entries", 10000),
        ("max-depth", 8),
    ]:
        parser.add_argument("--" + name, type=int, default=default)
    args = parser.parse_args()
    qualify(
        args.manifest,
        args.output_dir,
        args.per_document_timeout,
        args.max_file_bytes,
        args.max_total_bytes,
        args.max_entries,
        args.max_depth,
    )


if __name__ == "__main__":
    if len(sys.argv) == 5 and sys.argv[1] == "--worker":
        project(*sys.argv[2:])
    else:
        main()
