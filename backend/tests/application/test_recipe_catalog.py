from __future__ import annotations

import json
from pathlib import Path

import pytest
from app.platform.quality.recipe_catalog import load_catalog, parse_catalog

CATALOG_PATH = (
    Path(__file__).resolve().parents[2]
    / "app"
    / "platform"
    / "quality"
    / "data"
    / "g01_g52.json"
)


def test_g01_g52_catalog_materializes_every_recipe_contract() -> None:
    catalog = load_catalog(CATALOG_PATH)

    assert catalog.catalog_id == "SMART_AO_G01_G52"
    assert len(catalog.scenarios) == 52
    assert [scenario.recipe_id for scenario in catalog.scenarios] == [
        f"G{index:02d}" for index in range(1, 53)
    ]
    assert all(scenario.role for scenario in catalog.scenarios)
    assert all(scenario.initial_state for scenario in catalog.scenarios)
    assert all(scenario.refusal_expected for scenario in catalog.scenarios)
    assert all(scenario.append_only_evidence for scenario in catalog.scenarios)
    assert all(scenario.final_state for scenario in catalog.scenarios)


@pytest.mark.parametrize(
    ("mutator", "error_code"),
    [
        (lambda value: value["scenarios"].pop(), "RECIPE_CATALOG_SCENARIOS_INVALID"),
        (
            lambda value: value["scenarios"][0].update({"execution_mode": "REMOTE_GUESS"}),
            "RECIPE_SCENARIO_EXECUTION_MODE_INVALID",
        ),
        (
            lambda value: value["scenarios"][0].update({"append_only_evidence": []}),
            "RECIPE_SCENARIO_EVIDENCE_INVALID",
        ),
    ],
)
def test_g01_g52_catalog_rejects_incomplete_or_unsafe_contracts(mutator, error_code: str) -> None:
    raw = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
    mutator(raw)

    with pytest.raises(ValueError, match=error_code):
        parse_catalog(raw)
