"""Canonical hashing for immutable, bounded enterprise method profiles."""

from __future__ import annotations

import hashlib
import json
from typing import Any


def profile_content_hash(profile: dict[str, Any]) -> str:
    """Hash the validated JSON profile using stable UTF-8 canonical JSON."""

    encoded = json.dumps(
        profile,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()
