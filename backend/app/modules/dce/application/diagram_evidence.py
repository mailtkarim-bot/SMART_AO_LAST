"""Source-bound diagram observations; neither OCR nor pixels grant eligibility."""

import re
from dataclasses import dataclass

from app.modules.dce.application.structure_projection import (
    RegionAnchor,
    RegionToken,
    StructureScope,
    project_candidate_structure,
)


@dataclass(frozen=True, slots=True)
class ArrowheadEvidence:
    scope: StructureScope
    state: str = "UNKNOWN"
    tip: tuple[float, float] | None = None
    anchor: RegionAnchor | None = None
    detector_version: str = "axis-filled-head-150dpi-v1"
    semantic_state: str = "UNKNOWN"
    status: str = "REVIEW_REQUIRED"


@dataclass(frozen=True, slots=True)
class BranchLabelEvidence:
    raw_token: RegionToken
    reread_token: RegionToken | None
    label: str | None
    state: str
    reread_input_sha256: str | None = None
    reread_extractor_id: str | None = None
    reread_extractor_version: str | None = None
    semantic_state: str = "UNKNOWN"
    status: str = "REVIEW_REQUIRED"


def qualify_branch_label(
    *,
    expected_scope: StructureScope,
    raw_token: RegionToken,
    reread_token: RegionToken | None = None,
    reread_input_sha256: str | None = None,
    reread_extractor_id: str | None = None,
    reread_extractor_version: str | None = None,
) -> BranchLabelEvidence:
    tokens = (raw_token,) if reread_token is None else (raw_token, reread_token)
    project_candidate_structure(expected_scope=expected_scope, tokens=tokens)
    if reread_token is not None and reread_token.anchor.bbox != raw_token.anchor.bbox:
        raise ValueError("BRANCH_REREAD_REGION_MISMATCH")
    if reread_token is not None and (
        not isinstance(reread_input_sha256, str)
        or re.fullmatch(r"[0-9a-f]{64}", reread_input_sha256) is None
        or any(
            not isinstance(v, str) or not v.strip() or len(v) > 200
            for v in (reread_extractor_id, reread_extractor_version)
        )
    ):
        raise ValueError("BRANCH_REREAD_PROVENANCE_REQUIRED")
    if reread_token is None and any(
        v is not None for v in (reread_input_sha256, reread_extractor_id, reread_extractor_version)
    ):
        raise ValueError("BRANCH_REREAD_PROVENANCE_REQUIRED")
    values = [t.text.strip().upper() for t in tokens]
    recognized = {value for value in values if value in {"OUI", "NON"}}
    label = next(iter(recognized)) if len(recognized) == 1 else None
    if (
        len(values[0].split()) != 1
        or values[0] in {"ELIGIBLE", "ÉLIGIBLE"}
        or (reread_token is not None and values[1] not in {"OUI", "NON"})
    ):
        label = None
    state = (
        "UNKNOWN"
        if label is None
        else ("SOURCE_LABEL_CANDIDATE" if values[0] == label else "REREAD_LABEL_CANDIDATE")
    )
    return BranchLabelEvidence(
        raw_token,
        reread_token,
        label,
        state,
        reread_input_sha256,
        reread_extractor_id,
        reread_extractor_version,
    )
