import importlib.util
from hashlib import sha256
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]


def load():
    spec = importlib.util.spec_from_file_location(
        "clause_score", ROOT / "scripts/score_rc_clauses.py"
    )
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def sample():
    first = "Lot 1 : le DC2 est requis."
    second = "Lot 1 : la DPGF est requise."
    text = first + " " + second
    gold = [
        dict(
            id="a",
            source_fragment_id="s",
            start_byte=0,
            end_byte=len(first.encode()),
            excerpt=first,
            subject="DC2",
            lot=1,
            value="REQUIRED",
            kind="ASSERTION",
        ),
        dict(
            id="b",
            source_fragment_id="s",
            start_byte=len((first + " ").encode()),
            end_byte=len(text.encode()),
            excerpt=second,
            subject="DPGF",
            lot=1,
            value="REQUIRED",
            kind="ASSERTION",
        ),
    ]
    fixture = dict(
        synthetic=True,
        held_out=True,
        documents=[dict(id="s", text=text)],
        clause_inventory=gold,
        queries=[
            dict(
                id="q",
                family="document_classic",
                expected_clause_ids=["a"],
                expected=["s"],
                expected_refusal=None,
            )
        ],
    )
    a = {k: v for k, v in gold[0].items() if k != "id"} | dict(directive_signal="CANDIDATE")
    b = {k: v for k, v in gold[1].items() if k != "id"} | dict(directive_signal="UNKNOWN")
    fixture["documents"][0].update(page=1, version_id="v")
    for e in (a, b):
        e.update(
            source_sha256=sha256(text.encode()).hexdigest(), locator={"page": 1}, dce_version_id="v"
        )
    report = dict(
        synthetic_only=True,
        held_out=True,
        fixture_sha256="h",
        admitted=False,
        states=dict(
            q=dict(rc_projection=dict(clauses=[a], unknown_regions=[]), rc_unscoped_evidence=[b])
        ),
    )
    return fixture, report


def test_context_is_not_counted_as_a_wrong_projected_assertion():
    f, r = sample()
    s = load().score_clauses(f, r, "h")
    q = s["queries"][0]
    assert q["detected_relevant"] == 1 and q["missing_clause_ids"] == []
    assert q["extra_projected_candidates"] == 0 and q["wrong_known_values"] == 0
    assert q["irrelevant_context_clauses"] == 1


def test_unknown_is_unresolved_rather_than_false_certainty():
    f, r = sample()
    r["states"]["q"]["rc_projection"]["clauses"][0].update(value="UNKNOWN", kind="UNKNOWN")
    q = load().score_clauses(f, r, "h")["queries"][0]
    assert q["unresolved_relevant"] == 1 and q["wrong_known_values"] == 0
    assert q["detected_relevant"] == 1


def test_known_value_against_gold_unknown_is_overcertainty():
    f, r = sample()
    f["clause_inventory"][0].update(value="UNKNOWN", kind="UNKNOWN")
    q = load().score_clauses(f, r, "h")["queries"][0]
    assert q["wrong_known_values"] == 1 and q["overcertainty"] == 1


def test_real_extra_projection_is_visible():
    f, r = sample()
    b = r["states"]["q"]["rc_unscoped_evidence"].pop()
    b["directive_signal"] = "CANDIDATE"
    r["states"]["q"]["rc_projection"]["clauses"].append(b)
    assert load().score_clauses(f, r, "h")["queries"][0]["extra_projected_candidates"] == 1


def test_bad_gold_anchor_and_stale_report_are_refused():
    f, r = sample()
    m = load()
    with pytest.raises(ValueError, match="fixture identity"):
        m.score_clauses(f, r, "other")
    f["clause_inventory"][0]["start_byte"] = 1
    with pytest.raises(ValueError, match="gold anchor"):
        m.score_clauses(f, r, "h")


def test_absent_candidate_is_an_omission():
    f, r = sample()
    r["states"]["q"].update(rc_projection={}, rc_unscoped_evidence=[])
    q = load().score_clauses(f, r, "h")["queries"][0]
    assert q["missing_clause_ids"] == ["a"] and q["detected_relevant"] == 0


def test_known_negation_kind_is_checked_separately_from_value():
    f, r = sample()
    f["clause_inventory"][0]["kind"] = "NEGATION"
    q = load().score_clauses(f, r, "h")["queries"][0]
    assert q["wrong_known_values"] == 0 and q["wrong_known_kinds"] == 1


def test_context_detection_is_not_projected_recall():
    f, r = sample()
    a = r["states"]["q"]["rc_projection"]["clauses"].pop()
    r["states"]["q"]["rc_unscoped_evidence"].append(a)
    q = load().score_clauses(f, r, "h")["queries"][0]
    assert q["detected_relevant"] == 1 and q["projected_relevant"] == 0


@pytest.mark.parametrize(
    "change", [{"source_sha256": None}, {"locator": {"page": 2}}, {"dce_version_id": "other"}]
)
def test_actual_evidence_requires_hash_page_and_version(change):
    f, r = sample()
    r["states"]["q"]["rc_projection"]["clauses"][0].update(change)
    with pytest.raises(ValueError, match="actual anchor"):
        load().score_clauses(f, r, "h")


def test_missing_actual_hash_is_not_inferred_from_gold():
    f, r = sample()
    r["states"]["q"]["rc_projection"]["clauses"][0].pop("source_sha256")
    with pytest.raises(ValueError, match="actual anchor"):
        load().score_clauses(f, r, "h")
