from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

_RECIPE_ID = re.compile(r"G(?:0[1-9]|[1-4][0-9]|5[0-2])$")
_SPACE_ID = re.compile(r"(?:C(?:0[0-9]|1[0-6])|N0[1-5])$")
_EXECUTION_MODES = frozenset(
    {"LOCAL", "LOCAL_WITH_EXTERNAL_EVIDENCE", "UI_MANUAL", "EXTERNAL_DEPENDENCY"}
)


@dataclass(frozen=True, slots=True)
class RecipeScenario:
    recipe_id: str
    canonical_spaces: tuple[str, ...]
    role: str
    initial_state: str
    action: str
    refusal_expected: str
    append_only_evidence: tuple[str, ...]
    final_state: str
    execution_mode: str


@dataclass(frozen=True, slots=True)
class RecipeCatalog:
    schema_version: int
    catalog_id: str
    scenarios: tuple[RecipeScenario, ...]


def load_catalog(path: Path) -> RecipeCatalog:
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError("RECIPE_CATALOG_INVALID_JSON") from error
    return parse_catalog(raw)


def parse_catalog(raw: Any) -> RecipeCatalog:
    if not isinstance(raw, dict) or set(raw) != {"schema_version", "catalog_id", "scenarios"}:
        raise ValueError("RECIPE_CATALOG_FIELDS_INVALID")
    if raw["schema_version"] != 1 or not _non_empty(raw["catalog_id"]):
        raise ValueError("RECIPE_CATALOG_HEADER_INVALID")
    scenarios = raw["scenarios"]
    if not isinstance(scenarios, list) or len(scenarios) != 52:
        raise ValueError("RECIPE_CATALOG_SCENARIOS_INVALID")
    parsed = tuple(_parse_scenario(item) for item in scenarios)
    expected_ids = tuple(f"G{index:02d}" for index in range(1, 53))
    actual_ids = tuple(item.recipe_id for item in parsed)
    if actual_ids != expected_ids:
        raise ValueError("RECIPE_CATALOG_IDS_INVALID")
    return RecipeCatalog(
        schema_version=1,
        catalog_id=raw["catalog_id"].strip(),
        scenarios=parsed,
    )


def _parse_scenario(raw: Any) -> RecipeScenario:
    required = {
        "recipe_id",
        "canonical_spaces",
        "role",
        "initial_state",
        "action",
        "refusal_expected",
        "append_only_evidence",
        "final_state",
        "execution_mode",
    }
    if not isinstance(raw, dict) or set(raw) != required:
        raise ValueError("RECIPE_SCENARIO_FIELDS_INVALID")
    recipe_id = _non_empty(raw["recipe_id"])
    if not _RECIPE_ID.fullmatch(recipe_id):
        raise ValueError("RECIPE_SCENARIO_ID_INVALID")
    spaces = _string_tuple(raw["canonical_spaces"], "RECIPE_SCENARIO_SPACES_INVALID")
    if not spaces or any(not _SPACE_ID.fullmatch(space) for space in spaces):
        raise ValueError("RECIPE_SCENARIO_SPACES_INVALID")
    mode = _non_empty(raw["execution_mode"])
    if mode not in _EXECUTION_MODES:
        raise ValueError("RECIPE_SCENARIO_EXECUTION_MODE_INVALID")
    evidence = _string_tuple(
        raw["append_only_evidence"], "RECIPE_SCENARIO_EVIDENCE_INVALID"
    )
    if not evidence:
        raise ValueError("RECIPE_SCENARIO_EVIDENCE_INVALID")
    return RecipeScenario(
        recipe_id=recipe_id,
        canonical_spaces=spaces,
        role=_required_text(raw["role"], "RECIPE_SCENARIO_ROLE_INVALID"),
        initial_state=_required_text(
            raw["initial_state"], "RECIPE_SCENARIO_INITIAL_STATE_INVALID"
        ),
        action=_required_text(raw["action"], "RECIPE_SCENARIO_ACTION_INVALID"),
        refusal_expected=_required_text(
            raw["refusal_expected"], "RECIPE_SCENARIO_REFUSAL_INVALID"
        ),
        append_only_evidence=evidence,
        final_state=_required_text(raw["final_state"], "RECIPE_SCENARIO_FINAL_STATE_INVALID"),
        execution_mode=mode,
    )


def _non_empty(value: Any) -> str:
    return value.strip() if isinstance(value, str) and value.strip() else ""


def _required_text(value: Any, code: str) -> str:
    text = _non_empty(value)
    if not text:
        raise ValueError(code)
    return text


def _string_tuple(value: Any, code: str) -> tuple[str, ...]:
    if not isinstance(value, list) or any(not _non_empty(item) for item in value):
        raise ValueError(code)
    return tuple(item.strip() for item in value)
