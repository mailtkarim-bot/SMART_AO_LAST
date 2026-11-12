from __future__ import annotations

import argparse
import json
import os
import platform
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path


def _run_version(command: list[str]) -> str:
    result = subprocess.run(command, check=False, capture_output=True, text=True)
    return (result.stdout or result.stderr).strip()


def _git_value(root: Path, *args: str) -> str:
    return _run_version(["git", "-C", str(root), *args])


def collect_environment(root: Path) -> dict[str, object]:
    return {
        "collected_at_utc": datetime.now(tz=UTC).isoformat(),
        "python": sys.version,
        "python_implementation": platform.python_implementation(),
        "platform": platform.platform(),
        "machine": platform.machine(),
        "pytest": _run_version([sys.executable, "-m", "pytest", "--version"]),
        "coverage": _run_version([sys.executable, "-m", "coverage", "--version"]),
        "uv": _run_version(["uv", "--version"]),
        "git_commit": _git_value(root, "rev-parse", "HEAD"),
        "git_status_porcelain": _git_value(root, "status", "--porcelain"),
        "lockfile_sha256": _sha256(root / "uv.lock"),
    }


def _sha256(path: Path) -> str:
    import hashlib

    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def shard_modules(root: Path, index: int, count: int) -> list[str]:
    if count < 1 or not 0 <= index < count:
        raise ValueError("INVALID_SHARD_INDEX")
    modules = sorted(
        str(path.relative_to(root))
        for path in (root / "backend/tests").rglob("*.py")
        if path.name.startswith("test_") or path.name.endswith("_test.py")
    )[index::count]
    if not modules:
        raise ValueError("EMPTY_TEST_SHARD")
    return modules


def validate_shards(root: Path, directory: Path, count: int, commit: str) -> list[Path]:
    if count < 1:
        raise ValueError("INVALID_SHARD_COUNT")
    if len(commit) != 40 or any(char not in "0123456789abcdef" for char in commit):
        raise ValueError("UNRESOLVED_SOURCE_COMMIT")
    expected = {f"coverage-shard-{index}" for index in range(count)}
    if {path.name for path in directory.iterdir() if path.is_dir()} != expected:
        raise ValueError("INCOMPLETE_SHARD_SET")
    data = []
    for index in range(count):
        shard = directory / f"coverage-shard-{index}"
        try:
            modules = json.loads((shard / "modules.json").read_text())
            environment = json.loads((shard / "environment.json").read_text())
            code = (shard / "pytest-exit-code.txt").read_text().strip()
            path = shard / "coverage.data"
            valid = (
                modules == shard_modules(root, index, count)
                and environment["git_commit"] == commit
                and code == "0"
                and path.is_file()
                and path.stat().st_size > 0
            )
        except (OSError, ValueError, KeyError, TypeError) as error:
            raise ValueError("INVALID_SHARD_PROOF") from error
        if not valid:
            raise ValueError("INVALID_SHARD_PROOF")
        data.append(path)
    return data


def combine_shards(root: Path, directory: Path, output: Path, count: int) -> int:
    data = validate_shards(root, directory, count, _git_value(root, "rev-parse", "HEAD"))
    output.mkdir(parents=True, exist_ok=True)
    target = f"--data-file={output / 'coverage.data'}"
    base = [sys.executable, "-m", "coverage"]
    result = subprocess.run([*base, "combine", target, "--keep", *map(str, data)], cwd=root)
    if result.returncode:
        return result.returncode
    for kind in ("json", "xml"):
        result = subprocess.run(
            [*base, kind, target, "--fail-under=0", "-o", str(output / f"coverage.{kind}")],
            cwd=root,
        )
        if result.returncode:
            return result.returncode
    # The aggregate report enforces the unchanged threshold from pyproject.toml.
    return subprocess.run([*base, "report", target], cwd=root).returncode


def main() -> int:
    parser = argparse.ArgumentParser(description="Collect local coverage diagnostics")
    parser.add_argument("--output-dir", type=Path, required=True)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--environment-only", action="store_true")
    mode.add_argument("--shard-index", type=int)
    mode.add_argument("--combine-shards", type=Path)
    parser.add_argument("--shard-count", type=int, default=4)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    environment_path = output_dir / "environment.json"
    environment_path.write_text(
        json.dumps(collect_environment(root), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    if args.environment_only:
        return 0
    if args.combine_shards is not None:
        return combine_shards(root, args.combine_shards.resolve(), output_dir, args.shard_count)
    modules = ["backend/tests"]
    environment = dict(os.environ)
    if args.shard_index is not None:
        modules = shard_modules(root, args.shard_index, args.shard_count)
        (output_dir / "modules.json").write_text(json.dumps(modules, indent=2) + "\n")
        environment["COVERAGE_FILE"] = str(output_dir / "coverage.data")
    command = [
        sys.executable,
        "-m",
        "pytest",
        *modules,
        "-q",
        "--durations=10",
        "--cov=app",
        *(
            ["--cov-report="]
            if args.shard_index is not None
            else [
                "--cov-report=term-missing",
                f"--cov-report=json:{output_dir / 'coverage.json'}",
                f"--cov-report=xml:{output_dir / 'coverage.xml'}",
            ]
        ),
        "--cov-fail-under=0",
    ]
    result = subprocess.run(command, cwd=root, env=environment, check=False)
    (output_dir / "pytest-exit-code.txt").write_text(f"{result.returncode}\n", encoding="utf-8")
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
