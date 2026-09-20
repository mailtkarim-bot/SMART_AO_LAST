from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True, slots=True)
class BusinessFixture:
    recipe_id: str
    input_state: str
    action: str
    expected_refusal: str
    expected_final_state: str
    append_only_evidence: tuple[str, ...]
    business_act: str
    act_proof: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class BusinessFixtureCatalog:
    schema_version: int
    fixture_id: str
    scenarios: tuple[BusinessFixture, ...]


def load_business_fixtures(path: Path) -> BusinessFixtureCatalog:
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError("BUSINESS_FIXTURES_INVALID_JSON") from error
    return parse_business_fixtures(raw)


def parse_business_fixtures(raw: Any) -> BusinessFixtureCatalog:
    if not isinstance(raw, dict) or set(raw) != {"schema_version", "fixture_id", "scenarios"}:
        raise ValueError("BUSINESS_FIXTURES_FIELDS_INVALID")
    if raw["schema_version"] != 1 or not _text(raw["fixture_id"]):
        raise ValueError("BUSINESS_FIXTURES_HEADER_INVALID")
    scenarios = raw["scenarios"]
    if not isinstance(scenarios, list) or len(scenarios) != 9:
        raise ValueError("BUSINESS_FIXTURES_SCENARIOS_INVALID")
    parsed = tuple(_parse_fixture(item) for item in scenarios)
    if tuple(item.recipe_id for item in parsed) != tuple(f"G{index:02d}" for index in range(1, 10)):
        raise ValueError("BUSINESS_FIXTURES_IDS_INVALID")
    return BusinessFixtureCatalog(
        schema_version=1,
        fixture_id=raw["fixture_id"].strip(),
        scenarios=parsed,
    )


def _parse_fixture(raw: Any) -> BusinessFixture:
    required = {
        "recipe_id",
        "input_state",
        "action",
        "expected_refusal",
        "expected_final_state",
        "append_only_evidence",
        "business_act",
        "act_proof",
    }
    if not isinstance(raw, dict) or set(raw) != required:
        raise ValueError("BUSINESS_FIXTURE_FIELDS_INVALID")
    values = {key: _text(raw[key]) for key in required - {"append_only_evidence", "act_proof"}}
    evidence = raw["append_only_evidence"]
    if not isinstance(evidence, list) or not evidence or any(not _text(item) for item in evidence):
        raise ValueError("BUSINESS_FIXTURE_EVIDENCE_INVALID")
    act_proof = raw["act_proof"]
    if (
        not isinstance(act_proof, list)
        or not act_proof
        or any(not _text(item) for item in act_proof)
    ):
        raise ValueError("BUSINESS_FIXTURE_ACT_PROOF_INVALID")
    return BusinessFixture(
        recipe_id=values["recipe_id"],
        input_state=values["input_state"],
        action=values["action"],
        expected_refusal=values["expected_refusal"],
        expected_final_state=values["expected_final_state"],
        append_only_evidence=tuple(item.strip() for item in evidence),
        business_act=values["business_act"],
        act_proof=tuple(item.strip() for item in act_proof),
    )


def _text(value: Any) -> str:
    return value.strip() if isinstance(value, str) and value.strip() else ""
