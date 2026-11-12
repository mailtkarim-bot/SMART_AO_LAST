"""Pinned local E5 encoder, available only to explicitly constructed candidates."""

from __future__ import annotations

import json
from collections.abc import Sequence
from hashlib import file_digest, sha256
from importlib.metadata import version
from pathlib import Path
from threading import RLock
from typing import Any

from app.modules.knowledge.domain.embedding_profile import CandidateRetrievalProfile

_ALLOWED_FILES = frozenset(
    {
        "config.json",
        "config_sentence_transformers.json",
        "modules.json",
        "sentence_bert_config.json",
        "sentencepiece.bpe.model",
        "special_tokens_map.json",
        "tokenizer.json",
        "tokenizer_config.json",
        "1_Pooling/config.json",
        "model.safetensors",
    }
)


def verify_candidate_files(
    *, profile: CandidateRetrievalProfile, model_dir: Path, runtime_manifest: Path
) -> tuple[tuple[Path, int, int, int], ...]:
    root = model_dir.resolve(strict=True)
    manifest = root / "qualification-manifest.json"
    manifest_bytes = manifest.read_bytes()
    runtime_bytes = runtime_manifest.read_bytes()
    if (
        sha256(manifest_bytes).hexdigest() != profile.model_manifest_sha256
        or sha256(runtime_bytes).hexdigest() != profile.runtime_manifest_sha256
    ):
        raise ValueError("candidate manifest identity mismatch")
    data = json.loads(manifest_bytes)
    runtime = json.loads(runtime_bytes)
    if data["repository"] != profile.model_id or data["revision"] != profile.revision:
        raise ValueError("candidate model revision mismatch")
    if runtime["torch"] != "2.13.0+cpu" or runtime["torchvision"]["version"] != "0.28.0+cpu":
        raise ValueError("candidate CPU runtime mismatch")
    files = []
    seen = set()
    for entry in data["files"]:
        name = entry["file"]
        if name not in _ALLOWED_FILES or name in seen:
            raise ValueError("candidate model file refused")
        path = (root / name).resolve(strict=True)
        if not path.is_relative_to(root) or not path.is_file():
            raise ValueError("candidate model file refused")
        seen.add(name)
        stat = path.stat()
        stamp = (stat.st_ino, stat.st_size, stat.st_mtime_ns)
        with path.open("rb") as stream:
            digest = file_digest(stream, "sha256").hexdigest()
        if (
            path.stat().st_size != entry["bytes"]
            or digest != entry["sha256"]
            or _stamp(path) != stamp
        ):
            raise ValueError("candidate model integrity mismatch")
        files.append((path, *stamp))
    if not {"config.json", "modules.json", "model.safetensors"} <= seen:
        raise ValueError("candidate model files incomplete")
    for path in root.rglob("*"):
        if path.is_symlink() or (
            path.is_file()
            and path.relative_to(root).as_posix() not in seen | {"qualification-manifest.json"}
        ):
            raise ValueError("unverified candidate model asset")
    modules = json.loads((root / "modules.json").read_text())
    expected_modules = [
        ("sentence_transformers.models.Transformer", ""),
        ("sentence_transformers.models.Pooling", "1_Pooling"),
        ("sentence_transformers.models.Normalize", "2_Normalize"),
    ]
    if [(m["type"], m.get("path")) for m in modules] != expected_modules:
        raise ValueError("unqualified model module/path")
    return tuple(files)


def _stamp(path: Path) -> tuple[int, int, int]:
    stat = path.stat()
    return stat.st_ino, stat.st_size, stat.st_mtime_ns


def _check_stamps(stamps: tuple[tuple[Path, int, int, int], ...]) -> None:
    if any(_stamp(path) != (inode, size, stamp) for path, inode, size, stamp in stamps):
        raise ValueError("candidate model files changed")


class CpuCandidateEncoder:
    def __init__(
        self, *, profile: CandidateRetrievalProfile, model_dir: Path, runtime_manifest: Path
    ) -> None:
        self._profile = profile
        self._root = model_dir.resolve(strict=True)
        self._runtime = runtime_manifest.resolve(strict=True)
        self._model: Any | None = None
        self._stamps: tuple[tuple[Path, int, int, int], ...] | None = None
        self._lock = RLock()

    @property
    def profile_id(self) -> str:
        return self._profile.profile_id

    def _load_model(self) -> Any:
        if self._model is None:
            files = verify_candidate_files(
                profile=self._profile, model_dir=self._root, runtime_manifest=self._runtime
            )
            expected = {
                "torch": "2.13.0+cpu",
                "torchvision": "0.28.0+cpu",
                "sentence-transformers": self._profile.sentence_transformers_version,
                "transformers": self._profile.transformers_version,
                "tokenizers": self._profile.tokenizers_version,
                "numpy": self._profile.numpy_version,
                "safetensors": self._profile.safetensors_version,
            }
            if any(version(name) != value for name, value in expected.items()):
                raise ValueError("unqualified installed candidate runtime")
            import torch
            from sentence_transformers import SentenceTransformer

            torch.set_num_threads(self._profile.threads)
            model = SentenceTransformer(
                str(self._root), device="cpu", local_files_only=True, trust_remote_code=False
            )
            model.max_seq_length = self._profile.max_seq_length
            if (
                model.get_sentence_embedding_dimension() != self._profile.dimension
                or next(model.parameters()).dtype != torch.float32
            ):
                raise ValueError("unqualified candidate model shape/precision")
            _check_stamps(files)
            self._stamps = files
            self._model = model
        return self._model

    def _encode(self, texts: Sequence[str], prefix: str) -> list[tuple[float, ...]]:
        if not texts:
            return []
        if any(not text.strip() for text in texts):
            raise ValueError("blank candidate text")
        with self._lock:
            if (
                sha256((self._root / "qualification-manifest.json").read_bytes()).hexdigest()
                != self._profile.model_manifest_sha256
                or sha256(self._runtime.read_bytes()).hexdigest()
                != self._profile.runtime_manifest_sha256
            ):
                raise ValueError("candidate manifest changed")
            model = self._load_model()
            if self._stamps is not None:
                _check_stamps(self._stamps)
            values = [prefix + text for text in texts]
            if any(
                len(model.tokenizer(text, truncation=False)["input_ids"])
                > self._profile.max_seq_length
                for text in values
            ):
                raise ValueError("TOKEN_TRUNCATION_REFUSED")
            encoded = model.encode(
                values,
                prompt="",
                batch_size=self._profile.batch_size,
                convert_to_numpy=True,
                normalize_embeddings=True,
                show_progress_bar=False,
            )
            if self._stamps is not None:
                _check_stamps(self._stamps)
            return [tuple(float(value) for value in row) for row in encoded]

    def encode_passages(self, texts: Sequence[str]) -> list[tuple[float, ...]]:
        return self._encode(texts, self._profile.passage_prefix)

    def encode_query(self, text: str) -> tuple[float, ...]:
        [value] = self._encode([text], self._profile.query_prefix)
        return value
