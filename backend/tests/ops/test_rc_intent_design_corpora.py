"""Static design-data checks only: never call a recognizer on development or challenge."""

import json
import re
from hashlib import sha256
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
FIXTURES = ROOT / "backend/tests/fixtures/knowledge"


def test_intent_development_annotations_preserve_raw_query_and_abstention():
    data = json.loads((FIXTURES / "rc_intent_development_design_v1.json").read_text())
    assert data["synthetic"] and data["training_only"] and not data["held_out"]
    assert not data["candidate_implemented"] and not data["recognizer_executed"]
    assert len({c["id"] for c in data["cases"]}) == len(data["cases"]) == 32
    for case in data["cases"]:
        raw = case["text"].encode()
        assert case["query_sha256"] == sha256(raw).hexdigest()
        assert case["expected_answer_state"] == "UNKNOWN"
        assert case["recognizer_executed"] is False
        intent = case["expected_intent"]
        if case["expected_refusal"]:
            assert case["expected_refusal"] == "FINANCIAL_SCOPE_REFUSED"
            assert intent is None and not case["expected_anchors"]
            continue
        assert intent["coverage"] in {"COVERED", "UNSUPPORTED", "AMBIGUOUS", "UNKNOWN"}
        subjects: list[dict] = []
        demands: list[dict] = []
        lots: list[dict] = []
        for anchor in case["expected_anchors"]:
            assert 0 <= anchor["start_byte"] < anchor["end_byte"] <= len(raw)
            assert raw[anchor["start_byte"] : anchor["end_byte"]] == anchor["excerpt"].encode()
            {"SUBJECT": subjects, "DEMAND": demands, "LOT": lots}[anchor["signal"]].append(anchor)
        if intent["coverage"] == "COVERED":
            assert intent["demand"] == "OBLIGATION" and intent["subject"] != "UNKNOWN"
            assert len(subjects) == len(demands) == 1
        if intent["scope_state"] == "CANDIDATE":
            assert type(intent["lot"]) is int and intent["lot"] > 0 and len(lots) == 1
        else:
            assert intent["scope_state"] == "UNKNOWN" and intent["lot"] is None and not lots
    cases = {c["id"] for c in data["cases"]}
    for guard in data["source_guards"]:
        assert guard["query_case"] in cases and guard["expected_projection_value"] == "UNKNOWN"
        assert guard["text_sha256"] == sha256(guard["text"].encode()).hexdigest()
    assert all(g["retrieval_allowed"] is False for g in data["runtime_guards"])


def test_development_does_not_reuse_measured_queries_even_with_lot_renumbering():
    development = json.loads((FIXTURES / "rc_intent_development_design_v1.json").read_text())

    def canonical(text):
        return " ".join(re.sub(r"\b\d+\b", "NUMBER", text.casefold()).split())

    proposed = {canonical(c["text"]) for c in development["cases"]}
    assert len(proposed) == len(development["cases"])
    for name in ["rc_semantic_measurement_v1.json", "btp_rc_conditional_heldout_v18.json"]:
        measured = json.loads((FIXTURES / name).read_text())
        assert not proposed.intersection(canonical(q["text"]) for q in measured["queries"])


def test_proposed_contract_has_explicit_preobservation_gates_and_policy_reference():
    contract = json.loads((FIXTURES / "rc_intent_recognition_design_contract_v1.json").read_text())
    development = json.loads((FIXTURES / "rc_intent_development_design_v1.json").read_text())
    assert contract["status"] == "PROPOSED_PENDING_OWNER_CHOICE"
    assert contract["mechanism_choice"] is None and contract["candidate_implemented"] is False
    assert contract["recognizer_executed"] is False
    gates = contract["gates"]
    assert (
        gates["development_covered_denominator"]
        == sum(
            c["expected_intent"] is not None and c["expected_intent"]["coverage"] == "COVERED"
            for c in development["cases"]
        )
        == 16
    )
    assert gates["development_covered_minimum"] == 15
    assert gates["challenge_covered_fraction_minimum"] == 1.0
    assert gates["max_unsafe_promotions"] == gates["max_false_anchors"] == 0
    assert gates["max_invented_scopes"] == 0 and gates["answer_state"] == "UNKNOWN"
    assert gates["repetitions"] == 4 and gates["warm_repetitions"] == 3
    assert gates["interactive_p95_ms"] == 1500
    policy = contract["financial_policy"]
    assert sha256((ROOT / policy["file"]).read_bytes()).hexdigest() == policy["file_sha256"]
    assert (
        sha256((ROOT / policy["candidate_callsite_file"]).read_bytes()).hexdigest()
        == (policy["candidate_callsite_sha256"])
    )
    for case in development["cases"]:
        assert case["expected_reason"] in contract["reasons"]
        intent = case["expected_intent"]
        if intent:
            assert intent["subject"] in contract["subjects"]
            assert intent["demand"] in contract["demands"]
            assert intent["scope_state"] in contract["scope_states"]


def test_independent_challenge_seal_and_static_integrity_without_content_disclosure():
    protocol = json.loads(
        (FIXTURES / "rc_intent_independent_qualification_protocol_v1.json").read_text()
    )
    contract = json.loads((ROOT / protocol["contract_file"]).read_text())
    development = json.loads((ROOT / protocol["development_file"]).read_text())
    payload = (ROOT / protocol["challenge_file"]).read_bytes()

    def require(condition, label):
        if not condition:
            raise AssertionError(label)

    require(sha256(payload).hexdigest() == protocol["challenge_sha256"], "seal checksum")
    require(
        sha256((ROOT / protocol["contract_file"]).read_bytes()).hexdigest()
        == protocol["contract_sha256"],
        "contract checksum",
    )
    require(
        sha256((ROOT / protocol["development_file"]).read_bytes()).hexdigest()
        == protocol["development_sha256"],
        "development checksum",
    )
    challenge = json.loads(payload)
    require(
        challenge["sealed"] is True and challenge["held_out"] is False, "preparation seal flags"
    )
    require(challenge["recognizer_executed"] is False, "no runtime declaration")
    require(
        len(challenge["cases"]) == len({c["id"] for c in challenge["cases"]}) == 32,
        "case identities",
    )
    counts = dict.fromkeys(["COVERED", "UNSUPPORTED", "AMBIGUOUS", "UNKNOWN", "FINANCIAL"], 0)
    by_subject = dict.fromkeys([s for s in contract["subjects"] if s != "UNKNOWN"], 0)
    explicit_scopes = 0
    proposed = {
        " ".join(re.sub(r"\b\d+\b", "NUMBER", c["text"].casefold()).split())
        for c in development["cases"]
    }
    for case in challenge["cases"]:
        raw = case["text"].encode()
        require(sha256(raw).hexdigest() == case["query_sha256"], "query checksum")
        require(case["expected_answer_state"] == "UNKNOWN", "business state")
        require(case["expected_reason"] in contract["reasons"], "reason enum")
        canonical = " ".join(re.sub(r"\b\d+\b", "NUMBER", case["text"].casefold()).split())
        require(canonical not in proposed, "development overlap")
        anchors = case["expected_anchors"]
        require(
            anchors == sorted(anchors, key=lambda a: (a["start_byte"], a["end_byte"], a["signal"])),
            "anchor order",
        )
        for a in anchors:
            require(a["signal"] in {"SUBJECT", "DEMAND", "LOT"}, "signal enum")
            require(type(a["start_byte"]) is int and type(a["end_byte"]) is int, "offset types")
            require(0 <= a["start_byte"] < a["end_byte"] <= len(raw), "offset bounds")
            require(
                raw[a["start_byte"] : a["end_byte"]] == a["excerpt"].encode(), "exact raw anchor"
            )
        intent = case["expected_intent"]
        if intent is None:
            require(
                case["expected_refusal"] == "FINANCIAL_SCOPE_REFUSED" and not anchors,
                "financial refusal",
            )
            counts["FINANCIAL"] += 1
            continue
        require(
            intent["subject"] in contract["subjects"] and intent["demand"] in contract["demands"],
            "intent enums",
        )
        require(intent["coverage"] in contract["coverage"], "coverage enum")
        counts[intent["coverage"]] += 1
        if intent["scope_state"] == "CANDIDATE":
            require(type(intent["lot"]) is int, "scope type")
            require(1 <= intent["lot"] <= 999, "scope bounds")
        else:
            require(intent["scope_state"] == "UNKNOWN" and intent["lot"] is None, "unknown scope")
        if intent["coverage"] == "COVERED":
            require(
                intent["demand"] == "OBLIGATION" and intent["subject"] != "UNKNOWN",
                "covered status",
            )
            require(sum(a["signal"] == "SUBJECT" for a in anchors) == 1, "covered subject anchor")
            require(sum(a["signal"] == "DEMAND" for a in anchors) == 1, "covered demand anchor")
            require(
                sum(a["signal"] == "LOT" for a in anchors)
                == (intent["scope_state"] == "CANDIDATE"),
                "covered scope anchor",
            )
            by_subject[intent["subject"]] += 1
            explicit_scopes += intent["scope_state"] == "CANDIDATE"
    require(counts == protocol["expected_distribution"], "declared distribution")
    require(
        by_subject == protocol["covered_by_subject"] and all(v >= 2 for v in by_subject.values()),
        "subject coverage",
    )
    require(
        explicit_scopes == protocol["positive_explicit_scope_count"] >= 2, "positive scope coverage"
    )
    require(
        protocol["independence"]["coordinator_saw_challenge_text"] is False, "procedural separation"
    )
    require(protocol["independence"]["statistical_independence_claimed"] is False, "no blind claim")


def test_intent_design_files_are_refused_before_legacy_encoder(tmp_path, monkeypatch):
    import pytest
    from tests.ops.test_candidate_qualification_cli import args, load

    module = load(monkeypatch)
    monkeypatch.setattr(module, "CpuCandidateEncoder", lambda **kw: pytest.fail("encoder invoked"))
    for name in [
        "rc_intent_development_design_v1.json",
        "rc_intent_independent_challenge_v1.sealed.json",
    ]:
        with pytest.raises(ValueError, match="only synthetic held-out"):
            module.main(args(tmp_path, name))
    assert not (tmp_path / "report.json").exists()
