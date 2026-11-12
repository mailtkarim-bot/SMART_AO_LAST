"""An experimental encoder identity; it confers no business eligibility."""

from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass, field
from hashlib import sha256
from math import isfinite


@dataclass(frozen=True, slots=True)
class CandidateRetrievalProfile:
    revision: str
    model_manifest_sha256: str
    runtime_manifest_sha256: str
    segment_chars: int = 1000
    overlap_chars: int = 150
    minimum_score: float = 0.85
    model_id: str = field(default="intfloat/multilingual-e5-small", init=False)
    dimension: int = field(default=384, init=False)
    max_seq_length: int = field(default=512, init=False)
    query_prefix: str = field(default="query: ", init=False)
    passage_prefix: str = field(default="passage: ", init=False)
    device: str = field(default="cpu", init=False)
    precision: str = field(default="float32", init=False)
    normalization: str = field(default="L2", init=False)
    batch_size: int = field(default=1, init=False)
    threads: int = field(default=2, init=False)
    segmentation: str = field(default="utf8-whitespace-overlap-v1", init=False)
    abstention_policy: str = field(default="experimental-floor-v1", init=False)
    review_policy: str = "rectification-signal-v1"
    sentence_transformers_version: str = field(default="5.7.0", init=False)
    transformers_version: str = field(default="5.15.1", init=False)

    tokenizers_version: str = field(default="0.22.2", init=False)
    numpy_version: str = field(default="2.5.2", init=False)
    safetensors_version: str = field(default="0.8.0", init=False)

    def __post_init__(self) -> None:
        if self.review_policy not in {
            "rectification-signal-v1",
            "rc-opposition-v2",
            "rc-query-lot-v3",
            "rc-recall-v4",
            "rc-specific-v5",
            "rc-type-proof-v6",
            "rc-subject-proof-v7",
            "rc-intent-v8",
            "rc-imperative-v9",
            "rc-conditional-v10",
        }:
            raise ValueError("unsupported candidate review policy")
        if any(
            not isinstance(v, int) or isinstance(v, bool)
            for v in (self.segment_chars, self.overlap_chars)
        ):
            raise ValueError("integer segmentation budget required")
        if not isinstance(self.minimum_score, (int, float)) or isinstance(self.minimum_score, bool):
            raise ValueError("numeric experimental floor required")
        if not re.fullmatch(r"[0-9a-f]{40}", self.revision):
            raise ValueError("full model revision required")
        if any(
            not re.fullmatch(r"[0-9a-f]{64}", value)
            for value in (self.model_manifest_sha256, self.runtime_manifest_sha256)
        ):
            raise ValueError("manifest SHA-256 required")
        if (
            not 64 <= self.segment_chars <= 1000
            or not 0 <= self.overlap_chars < self.segment_chars // 2
        ):
            raise ValueError("invalid segmentation budget")
        if not isfinite(self.minimum_score) or not 0 <= self.minimum_score <= 1:
            raise ValueError("invalid experimental score floor")

    @property
    def profile_id(self) -> str:
        data = json.dumps(asdict(self), sort_keys=True, separators=(",", ":"))
        return "candidate-e5-v1:" + sha256(data.encode()).hexdigest()
