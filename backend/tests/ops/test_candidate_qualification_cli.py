import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]


def load(monkeypatch):
    monkeypatch.syspath_prepend(str(ROOT / "scripts"))
    spec = importlib.util.spec_from_file_location(
        "candidate_qualifier", ROOT / "scripts/qualify_candidate_retrieval.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    class Encoder:
        def __init__(self, **kwargs):
            self.profile_id = kwargs["profile"].profile_id

        def encode_passages(self, texts):
            return [(1.0,) + (0.0,) * 383 for _ in texts]

        def encode_query(self, text):
            return (1.0,) + (0.0,) * 383

    monkeypatch.setattr(module, "CpuCandidateEncoder", Encoder)
    return module


def args(tmp_path, fixture):
    return [
        "--fixture",
        str(ROOT / "backend/tests/fixtures/knowledge" / fixture),
        "--profile",
        str(ROOT / "ops/retrieval-candidate/profile-v1.json"),
        "--model-dir",
        str(tmp_path),
        "--runtime-manifest",
        str(ROOT / "ops/retrieval-candidate/runtime-v1.json"),
        "--output",
        str(tmp_path / "report.json"),
    ]


def test_cli_keeps_failed_gates_visible_and_never_admits_a_measured_candidate(
    tmp_path, monkeypatch
):
    module = load(monkeypatch)
    assert module.main(args(tmp_path, "btp_retrieval_heldout_v2.json")) == 0
    report = json.loads((tmp_path / "report.json").read_text())
    assert report["gates"]["source_scope"] and report["gates"]["unknown_answer"]
    assert not report["gates"]["abstention"] and not report["gates"]["unexpected_review_signals"]
    assert report["admitted"] is False and report["production_engine_changed"] is False


def test_cli_refuses_development_fixture_as_held_out(tmp_path, monkeypatch):
    module = load(monkeypatch)
    with pytest.raises(ValueError, match="held-out"):
        module.main(args(tmp_path, "btp_retrieval_synthetic_v1.json"))
    assert not (tmp_path / "report.json").exists()


def test_pair_score_requires_exact_pair_subject_lot_version_and_kind(monkeypatch):
    module = load(monkeypatch)
    expected = {
        "sources": ["a", "b"],
        "subject": "VISIT",
        "lot": 9,
        "version": "v",
        "kind": "OPPOSITION",
    }
    assert module.score_rc_pairs([expected], [expected]) == {"missing": [], "unexpected": []}
    wrong = {**expected, "lot": 10}
    score = module.score_rc_pairs([expected], [wrong])
    assert len(score["missing"]) == len(score["unexpected"]) == 1
    assert module.score_rc_pairs([], [expected])["unexpected"]


def test_v3_report_traces_policy_refusal_without_claiming_document_was_read(tmp_path, monkeypatch):
    module = load(monkeypatch)
    data = json.loads(
        (ROOT / "backend/tests/fixtures/knowledge/btp_rc_conflicts_heldout_v3.json").read_text()
    )
    data["documents"] = data["documents"][:2]
    ids = [d["id"] for d in data["documents"]]
    data["queries"] = [
        dict(
            id="lot",
            text="Visite du lot 13 ?",
            expected=ids,
            critical=True,
            review_required=True,
            expected_conflicts=[
                dict(
                    sources=ids,
                    subject="VISIT",
                    lot=13,
                    version=data["version_id"],
                    kind="OPPOSITION",
                )
            ],
            expected_unknown=False,
            expected_query_lot=13,
            expected_query_anchor="lot 13",
            expected_refusal=None,
        ),
        dict(
            id="dpgf-refused",
            text="DPGF du lot 13 ?",
            expected=ids,
            critical=True,
            review_required=False,
            expected_conflicts=[],
            expected_unknown=False,
            expected_query_lot=13,
            expected_query_anchor="lot 13",
            expected_refusal="FINANCIAL_SCOPE_REFUSED",
        ),
        dict(
            id="ambiguous",
            text="Visite lots 13 et 14 ?",
            expected=ids,
            critical=True,
            review_required=True,
            expected_conflicts=[],
            expected_unknown=False,
            expected_query_lot=None,
            expected_query_anchor=None,
            expected_refusal=None,
        ),
    ]
    fixture = tmp_path / "fixture.json"
    fixture.write_text(json.dumps(data))
    argv = args(tmp_path, "btp_rc_conflicts_heldout_v3.json")
    argv[argv.index("--fixture") + 1] = str(fixture)
    argv[argv.index("--profile") + 1] = str(ROOT / "ops/retrieval-candidate/profile-v3.json")
    assert module.main(argv) == 0
    report = json.loads((tmp_path / "report.json").read_text())
    assert report["non_evaluable_queries"] == ["dpgf-refused"]
    assert report["gates"]["policy_refusals_exact"] and report["gates"]["query_lot_projection"]
    assert not report["gates"]["critical_complete"]  # A refusal is not documentary coverage.
    refusal = report["states"]["dpgf-refused"]["policy_refusal"]
    assert refusal["stage"] == "BEFORE_SOURCE_AND_ENCODER"
    assert refusal["code"] == "FINANCIAL_RETRIEVAL_SCOPE_REQUIRED"
    assert report["admitted"] is False
    assert "ambiguous" not in report["review_signals_missing"]
    assert report["states"]["ambiguous"]["query_lot"]["state"] == "UNKNOWN"


def test_v4_report_preserves_rejected_scores_and_rescue_provenance(tmp_path, monkeypatch):
    from math import sqrt

    module = load(monkeypatch)
    original = module.CpuCandidateEncoder

    class LowEncoder(original):
        def encode_query(self, text):
            return (0.8, sqrt(1 - 0.8**2)) + (0.0,) * 382

    monkeypatch.setattr(module, "CpuCandidateEncoder", LowEncoder)
    data = json.loads(
        (ROOT / "backend/tests/fixtures/knowledge/btp_rc_conflicts_heldout_v3.json").read_text()
    )
    data["documents"] = data["documents"][:2]
    data["queries"] = [
        dict(
            id="generic",
            text="La visite est-elle obligatoire ?",
            expected=[d["id"] for d in data["documents"]],
            critical=True,
            review_required=True,
            expected_conflicts=[],
            expected_unknown=False,
            expected_query_lot=None,
            expected_query_anchor=None,
            expected_refusal=None,
        )
    ]
    fixture = tmp_path / "fixture.json"
    fixture.write_text(json.dumps(data))
    argv = args(tmp_path, "btp_rc_conflicts_heldout_v3.json")
    argv[argv.index("--fixture") + 1] = str(fixture)
    argv[argv.index("--profile") + 1] = str(ROOT / "ops/retrieval-candidate/profile-v4.json")
    assert module.main(argv) == 0
    report = json.loads((tmp_path / "report.json").read_text())
    trace = report["states"]["generic"]["score_trace"]
    assert len(trace) == 2 and {t["decision"] for t in trace} == {"RC_SUBJECT_RESCUE"}
    assert all(t["score"] < t["threshold"] for t in trace)
    assert report["gates"]["score_trace_valid"] and report["gates"]["query_lot_projection"]


def test_v5_report_checks_explicit_intent_and_records_dense_rejection(tmp_path, monkeypatch):
    module = load(monkeypatch)
    data = json.loads(
        (ROOT / "backend/tests/fixtures/knowledge/btp_rc_conflicts_heldout_v3.json").read_text()
    )
    data["documents"] = data["documents"][:2]
    data["queries"] = [
        dict(
            id="medical",
            text="La visite médicale est-elle obligatoire ?",
            expected=[],
            critical=False,
            review_required=False,
            expected_conflicts=[],
            expected_unknown=False,
            expected_query_lot=None,
            expected_query_anchor=None,
            expected_refusal=None,
            expected_visit_subject="VISIT_MEDICAL",
            expected_visit_anchor="visite médicale",
        )
    ]
    fixture = tmp_path / "fixture.json"
    fixture.write_text(json.dumps(data))
    argv = args(tmp_path, "btp_rc_conflicts_heldout_v3.json")
    argv[argv.index("--fixture") + 1] = str(fixture)
    argv[argv.index("--profile") + 1] = str(ROOT / "ops/retrieval-candidate/profile-v5.json")
    assert module.main(argv) == 0
    report = json.loads((tmp_path / "report.json").read_text())
    assert report["gates"]["specific_intent_exact"] and report["gates"]["specific_projection_typed"]
    assert report["gates"]["score_trace_valid"] and report["gates"]["abstention"]
    assert not report["gates"]["evidence_recall_at_5"]
    assert report["states"]["medical"]["specific_intent"]["subject"] == "VISIT_MEDICAL"
    assert all(
        e["decision"] == "SPECIFIC_MISMATCH" for e in report["states"]["medical"]["score_trace"]
    )


def test_v6_report_proves_type_independently_and_does_not_assert_condition(tmp_path, monkeypatch):
    from math import sqrt

    module = load(monkeypatch)
    original = module.CpuCandidateEncoder

    class LowEncoder(original):
        def encode_query(self, text):
            return (0.8, sqrt(1 - 0.8**2)) + (0.0,) * 382

    monkeypatch.setattr(module, "CpuCandidateEncoder", LowEncoder)
    data = json.loads(
        (ROOT / "backend/tests/fixtures/knowledge/btp_rc_specific_heldout_v6.json").read_text()
    )
    data["documents"] = data["documents"][:2]
    data["documents"][0]["text"] = "Lot 7 : la visite médicale est obligatoire sauf dispense."
    data["documents"][1]["text"] = "Lot 8 : la visite médicale est citée dans une annexe."
    data["queries"] = [
        dict(
            id="typed",
            text="La visite médicale est-elle obligatoire ?",
            expected=[data["documents"][0]["id"]],
            critical=True,
            review_required=True,
            expected_conflicts=[],
            expected_unknown=True,
            expected_query_lot=None,
            expected_query_anchor=None,
            expected_refusal=None,
            expected_visit_subject="VISIT_MEDICAL",
            expected_visit_anchor="visite médicale",
        )
    ]
    fixture = tmp_path / "fixture.json"
    fixture.write_text(json.dumps(data))
    argv = args(tmp_path, "btp_rc_specific_heldout_v6.json")
    argv[argv.index("--fixture") + 1] = str(fixture)
    argv[argv.index("--profile") + 1] = str(ROOT / "ops/retrieval-candidate/profile-v6.json")
    assert module.main(argv) == 0
    report = json.loads((tmp_path / "report.json").read_text())
    assert report["gates"]["visit_type_proof_valid"] and report["gates"]["typed_selection_proven"]
    assert report["gates"]["score_trace_valid"] and report["gates"]["rc_unknown_refusals"]
    row = report["states"]["typed"]["rc_projection"]["unknown_regions"][0]
    assert row["value"] == "UNKNOWN" and row["condition_signals"] and row["visit_type_proof"]
    assert report["states"]["typed"]["score_trace"][0]["decision"] == "RC_TYPED_RESCUE"
    assert report["admitted"] is False


def test_qualifier_accepts_explicit_source_and_encoder_without_active_wiring(tmp_path, monkeypatch):
    module = load(monkeypatch)

    class Source:
        calls = 0

        def read_chunks(self, **kwargs):
            self.calls += 1
            return ()

    class Encoder:
        profile_id = ""

        def encode_passages(self, texts):
            pytest.fail("empty SQL source must not be encoded")

        def encode_query(self, text):
            pytest.fail("empty SQL source must not be encoded")

    from app.modules.knowledge.domain.embedding_profile import CandidateRetrievalProfile

    encoder = Encoder()
    encoder.profile_id = CandidateRetrievalProfile(
        **json.loads((ROOT / "ops/retrieval-candidate/profile-v1.json").read_text())
    ).profile_id
    source = Source()
    assert (
        module.main(
            args(tmp_path, "btp_retrieval_heldout_v2.json"),
            source_override=source,
            encoder_override=encoder,
        )
        == 0
    )
    report = json.loads((tmp_path / "report.json").read_text())
    assert source.calls > 0 and all(not q["retrieved"] for q in report["metrics"]["queries"])
    assert not report["admitted"] and not report["production_engine_changed"]


@pytest.mark.parametrize(
    "url,disposable",
    [
        ("postgresql+psycopg://proof@/smartao_e5_sql?host=/socket&hostaddr=127.0.0.1", "1"),
        ("postgresql+psycopg://proof@/smartao_e5_sql?host=/socket&service=other", "1"),
        ("sqlite:///smartao_e5_sql?host=/socket", "1"),
        ("postgresql+psycopg://proof@localhost/smartao_e5_sql", "1"),
        ("postgresql+psycopg://proof@/real_database?host=/socket", "1"),
        ("postgresql+psycopg://proof@/smartao_e5_sql?host=/other", "1"),
        ("postgresql+psycopg://proof@/smartao_e5_sql?host=/socket", "0"),
    ],
)
def test_sql_benchmark_refuses_unapproved_database_before_reading_fixture(
    tmp_path, monkeypatch, url, disposable
):
    monkeypatch.syspath_prepend(str(ROOT / "scripts"))
    spec = importlib.util.spec_from_file_location(
        "sql_benchmark", ROOT / "scripts/qualify_candidate_sql.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    monkeypatch.setenv("SMART_AO_TEST_DATABASE_URL", url)
    monkeypatch.setenv("SMART_AO_TEST_DISPOSABLE_DATABASE", disposable)
    with pytest.raises(ValueError, match="dedicated disposable Unix socket"):
        module.main(args(tmp_path, "missing.json"))


def test_sql_seed_rejects_non_synthetic_or_private_fixture_before_database(monkeypatch):
    monkeypatch.syspath_prepend(str(ROOT / "scripts"))
    spec = importlib.util.spec_from_file_location(
        "sql_benchmark_seed", ROOT / "scripts/qualify_candidate_sql.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    for data in [
        dict(synthetic=False),
        dict(
            synthetic=True,
            held_out=True,
            schema_version=1,
            documents=[dict(classification="FINANCIAL_PRIVATE")],
        ),
    ]:
        with pytest.raises(ValueError, match="synthetic internal SQL fixture"):
            module.seed_fixture(data, None)


def test_sql_benchmark_refuses_libpq_environment(tmp_path, monkeypatch):
    monkeypatch.syspath_prepend(str(ROOT / "scripts"))
    spec = importlib.util.spec_from_file_location(
        "sql_env", ROOT / "scripts/qualify_candidate_sql.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    monkeypatch.setenv(
        "SMART_AO_TEST_DATABASE_URL", "postgresql+psycopg://proof@/smartao_e5_sql?host=/socket"
    )
    monkeypatch.setenv("SMART_AO_TEST_DISPOSABLE_DATABASE", "1")
    monkeypatch.setenv("PGHOSTADDR", "127.0.0.1")
    with pytest.raises(ValueError, match="dedicated disposable Unix socket"):
        module.main(args(tmp_path, "missing.json"))


def test_v7_cli_validates_generic_and_dc2_directives_as_typed_proofs(tmp_path, monkeypatch):
    module = load(monkeypatch)
    cli = args(tmp_path, "btp_e5_sql_heldout_v8.json")
    cli[cli.index("--profile") + 1] = str(ROOT / "ops/retrieval-candidate/profile-v7.json")
    assert module.main(cli) == 0
    report = json.loads((tmp_path / "report.json").read_text())
    assert report["gates"]["visit_type_proof_valid"]
    assert report["gates"]["typed_selection_proven"]
    assert all(
        p["subject"] == "DC2" for p in report["states"]["j8-dc2"]["rc_projection"]["clauses"]
    )
    assert not report["states"]["j8-hour"]["visit_type_evidence"]


def intent_dev_fixture(tmp_path):
    from uuid import UUID

    def ident(i):
        return str(UUID(int=i))

    query = "Faut-il joindre le DC2 au dossier du lot 17 ?"
    q = dict(
        id="intent-dev",
        text=query,
        expected=[ident(4)],
        critical=True,
        review_required=False,
        expected_conflicts=[],
        expected_unknown=False,
        expected_query_lot=17,
        expected_query_anchor="lot 17",
        expected_refusal=None,
        expected_visit_subject=None,
        expected_visit_anchor=None,
        expected_intent=dict(subject="DC2", demand="OBLIGATION", coverage="COVERED"),
    )
    q["expected_query_anchors"] = intent_gold_anchors(
        query, [("DEMAND", "Faut-il joindre"), ("SUBJECT", "DC2"), ("LOT", "lot 17")]
    )
    data = dict(
        schema_version=1,
        synthetic=True,
        held_out=True,
        tenant_id=ident(1),
        case_id=ident(2),
        version_id=ident(3),
        documents=[
            dict(
                id=ident(4),
                tenant_id=ident(1),
                case_id=ident(2),
                version_id=ident(3),
                classification="INTERNAL_OPERATIONAL",
                current=True,
                extraction_status="COMPLETED",
                page=1,
                family="RC",
                text="Lot 17 : le DC2 est requis.",
            )
        ],
        queries=[q],
    )
    path = tmp_path / "intent-dev.json"
    path.write_text(json.dumps(data))
    return path, data


def test_v8_cli_intent_is_sourced_and_tampered_anchors_fail(tmp_path, monkeypatch):
    module = load(monkeypatch)
    path, data = intent_dev_fixture(tmp_path)
    cli = args(tmp_path, "unused.json")
    cli[cli.index("--fixture") + 1] = str(path)
    cli[cli.index("--profile") + 1] = str(ROOT / "ops/retrieval-candidate/profile-v8.json")
    assert module.main(cli) == 0
    report = json.loads((tmp_path / "report.json").read_text())
    assert report["gates"]["rc_query_intent_valid"] and report["gates"]["rc_query_intent_exact"]
    state = report["states"]["intent-dev"]
    state["query_intent"]["anchors"][0]["start_byte"] += 1
    gates = module.score_query_intents(
        data["queries"],
        report["states"],
        {q["query_id"]: q["ranked_regions"] for q in report["metrics"]["queries"]},
    )
    assert not gates["rc_query_intent_valid"]


def test_v8_cli_requires_independent_intent_gold(tmp_path, monkeypatch):
    module = load(monkeypatch)
    path, data = intent_dev_fixture(tmp_path)
    data["queries"][0].pop("expected_intent")
    path.write_text(json.dumps(data))
    cli = args(tmp_path, "unused.json")
    cli[cli.index("--fixture") + 1] = str(path)
    cli[cli.index("--profile") + 1] = str(ROOT / "ops/retrieval-candidate/profile-v8.json")
    with pytest.raises(ValueError, match="intent gold"):
        module.main(cli)


def test_v8_validator_rejects_anchor_cutting_a_utf8_character(monkeypatch):
    from dataclasses import asdict

    from app.modules.knowledge.application.rc_query_intent import parse_rc_query_intent

    module = load(monkeypatch)
    text = "Une visite médicale est-elle nécessaire pour le lot 17 ?"
    qi = json.loads(json.dumps(asdict(parse_rc_query_intent(text))))
    q = dict(
        id="utf8",
        text=text,
        expected_intent=dict(subject="VISIT_MEDICAL", demand="OBLIGATION", coverage="COVERED"),
    )
    q["expected_query_anchors"] = intent_gold_anchors(
        text, [("SUBJECT", "visite médicale"), ("DEMAND", "nécessaire"), ("LOT", "lot 17")]
    )
    state = dict(query_intent=qi, query_lot=qi["scope"])
    assert module.score_query_intents([q], {"utf8": state}, {"utf8": []})["rc_query_intent_valid"]
    a = next(a for a in qi["anchors"] if a["signal"] == "DEMAND")
    a["start_byte"] += 2  # Second byte of é in nécessaire.
    assert not module.score_query_intents([q], {"utf8": state}, {"utf8": []})[
        "rc_query_intent_valid"
    ]


def test_v8_validator_requires_the_scope_anchor(monkeypatch):
    from dataclasses import asdict

    from app.modules.knowledge.application.rc_query_intent import parse_rc_query_intent

    module = load(monkeypatch)
    text = "Faut-il joindre le DC2 pour le lot 17 ?"
    qi = json.loads(json.dumps(asdict(parse_rc_query_intent(text))))
    q = dict(
        id="scope",
        text=text,
        expected_intent=dict(subject="DC2", demand="OBLIGATION", coverage="COVERED"),
    )
    q["expected_query_anchors"] = intent_gold_anchors(
        text, [("DEMAND", "Faut-il joindre"), ("SUBJECT", "DC2"), ("LOT", "lot 17")]
    )
    state = dict(query_intent=qi, query_lot=qi["scope"])
    assert module.score_query_intents([q], {"scope": state}, {"scope": []})["rc_query_intent_valid"]
    qi["anchors"] = [a for a in qi["anchors"] if a["signal"] != "LOT"]
    assert not module.score_query_intents([q], {"scope": state}, {"scope": []})[
        "rc_query_intent_valid"
    ]


def test_v8_validator_rejects_semantically_misbound_but_exact_words(tmp_path, monkeypatch):
    from dataclasses import asdict

    from app.modules.knowledge.application.rc_query_intent import parse_rc_query_intent

    module = load(monkeypatch)
    _, data = intent_dev_fixture(tmp_path)
    q = data["queries"][0]
    qi = json.loads(json.dumps(asdict(parse_rc_query_intent(q["text"]))))
    state = dict(query_intent=qi, query_lot=qi["scope"])
    assert module.score_query_intents([q], {q["id"]: state}, {q["id"]: []})["rc_query_intent_valid"]
    for a in qi["anchors"]:
        word = "lot" if a["signal"] == "SUBJECT" else "le" if a["signal"] == "DEMAND" else None
        if word:
            start = q["text"].index(word)
            a.update(start_byte=start, end_byte=start + len(word), excerpt=word)
    assert not module.score_query_intents([q], {q["id"]: state}, {q["id"]: []})[
        "rc_query_intent_valid"
    ]


def test_v8_uncovered_intent_cannot_keep_links(monkeypatch):
    from dataclasses import asdict

    from app.modules.knowledge.application.rc_query_intent import parse_rc_query_intent

    module = load(monkeypatch)
    text = "Quelle teinte RAL ?"
    qi = json.loads(json.dumps(asdict(parse_rc_query_intent(text))))
    q = dict(
        id="links",
        text=text,
        expected_intent=dict(subject="UNKNOWN", demand="UNKNOWN", coverage="UNKNOWN"),
        expected_query_anchors=[],
    )
    state = dict(query_intent=qi, query_lot=qi["scope"], rc_projection=dict(links=[{}]))
    assert not module.score_query_intents([q], {"links": state}, {"links": []})[
        "rc_query_intent_valid"
    ]


def intent_gold_anchors(text, terms):
    anchors = []
    for signal, excerpt in terms:
        start = text.index(excerpt)
        anchors.append(
            dict(
                signal=signal,
                start_byte=len(text[:start].encode()),
                end_byte=len(text[: start + len(excerpt)].encode()),
                excerpt=excerpt,
            )
        )
    return sorted(anchors, key=lambda a: (a["start_byte"], a["end_byte"], a["signal"]))


def test_v9_cli_requires_and_validates_independent_directive_anchors(tmp_path, monkeypatch):
    from hashlib import sha256

    module = load(monkeypatch)
    path, data = intent_dev_fixture(tmp_path)
    text = "Lot 17 : fournir le DC2."
    data["documents"][0]["text"] = text
    data["imperative_anchors"] = [
        {
            "source_fragment_id": data["documents"][0]["id"],
            "source_sha256": sha256(text.encode()).hexdigest(),
            "start_byte": 0,
            "end_byte": len(text.encode()),
            "anchors": intent_gold_anchors(
                text, [("LOT", "17"), ("DIRECTIVE", "fournir"), ("SUBJECT", "le DC2")]
            ),
        }
    ]
    path.write_text(json.dumps(data))
    cli = args(tmp_path, "unused.json")
    cli[cli.index("--fixture") + 1] = str(path)
    cli[cli.index("--profile") + 1] = str(ROOT / "ops/retrieval-candidate/profile-v9.json")
    assert module.main(cli) == 0
    report = json.loads((tmp_path / "report.json").read_text())
    assert report["gates"]["imperative_anchors_valid"]
    c = report["states"]["intent-dev"]["rc_projection"]["clauses"][0]
    assert c["directive_anchors"]
    original = c["directive_anchors"]
    c["directive_anchors"] = []
    assert not module.score_imperative_anchors(data, report["states"])
    c["directive_anchors"] = original
    c["directive_anchors"][0]["start_byte"] += 1
    assert not module.score_imperative_anchors(data, report["states"])
    data.pop("imperative_anchors")
    path.write_text(json.dumps(data))
    with pytest.raises(ValueError, match="imperative gold"):
        module.main(cli)


def conditional_dev_fixture(tmp_path):
    from hashlib import sha256

    path, data = intent_dev_fixture(tmp_path)
    text = "Lot 17 : fournir le DC2 si le candidat n'est pas dispensé."
    data["documents"][0]["text"] = text
    data["queries"][0]["expected_legacy_intent"] = dict(
        state="NONE", subject=None, start_byte=None, end_byte=None
    )
    data["queries"][0]["review_required"] = True
    data["queries"][0]["expected_unknown"] = True
    data["imperative_anchors"] = [
        dict(
            source_fragment_id=data["documents"][0]["id"],
            source_sha256=sha256(text.encode()).hexdigest(),
            start_byte=0,
            end_byte=len(text.encode()),
            anchors=intent_gold_anchors(
                text, [("LOT", "17"), ("DIRECTIVE", "fournir"), ("SUBJECT", "le DC2")]
            ),
            condition_signals=intent_gold_anchors(
                text, [("CONDITION", "si le candidat n'est pas dispensé")]
            ),
            value="UNKNOWN",
            kind="UNKNOWN",
        )
    ]
    path.write_text(json.dumps(data))
    cli = args(tmp_path, "unused.json")
    cli[cli.index("--fixture") + 1] = str(path)
    cli[cli.index("--profile") + 1] = str(ROOT / "ops/retrieval-candidate/profile-v10.json")
    return path, data, cli


def test_v10_cli_accepts_independently_anchored_unknown_condition(tmp_path, monkeypatch):
    module = load(monkeypatch)
    _, data, cli = conditional_dev_fixture(tmp_path)
    assert module.main(cli) == 0
    report = json.loads((tmp_path / "report.json").read_text())
    assert report["gates"]["imperative_anchors_valid"]
    evidence = report["states"]["intent-dev"]["rc_projection"]["unknown_regions"][0]
    assert evidence["condition_signals"] == data["imperative_anchors"][0]["condition_signals"]
    assert evidence["value"] == evidence["kind"] == "UNKNOWN"


@pytest.mark.parametrize(
    "tamper", ["missing", "shifted", "certainty", "gold_missing", "gold_shifted"]
)
def test_v10_cli_rejects_condition_proof_corruption(tmp_path, monkeypatch, tamper):
    module = load(monkeypatch)
    _, data, cli = conditional_dev_fixture(tmp_path)
    module.main(cli)
    report = json.loads((tmp_path / "report.json").read_text())
    evidence = report["states"]["intent-dev"]["rc_projection"]["unknown_regions"][0]
    if tamper == "missing":
        evidence["condition_signals"] = []
    elif tamper == "shifted":
        evidence["condition_signals"][0]["start_byte"] += 1
    elif tamper == "certainty":
        evidence["value"], evidence["kind"] = "REQUIRED", "ASSERTION"
    elif tamper == "gold_missing":
        data["imperative_anchors"][0].pop("condition_signals")
    else:
        data["imperative_anchors"][0]["condition_signals"][0]["start_byte"] += 1
    assert not module.score_imperative_anchors(data, report["states"])


def test_v10_cli_requires_explicit_legacy_contract(tmp_path, monkeypatch):
    module = load(monkeypatch)
    path, data, cli = conditional_dev_fixture(tmp_path)
    data["queries"][0].pop("expected_legacy_intent")
    path.write_text(json.dumps(data))
    with pytest.raises(ValueError, match="legacy intent gold"):
        module.main(cli)


def test_v10_hour_keeps_legacy_unknown_and_closed_unsupported(tmp_path, monkeypatch):
    module = load(monkeypatch)
    path, data, cli = conditional_dev_fixture(tmp_path)
    q = data["queries"][0]
    q.update(
        text="À quelle heure débute la visite de site pour le lot 17 ?",
        expected=[],
        expected_unknown=False,
        review_required=False,
        expected_visit_subject="UNKNOWN",
        expected_visit_anchor=None,
        expected_legacy_intent=dict(state="UNKNOWN", subject=None, start_byte=None, end_byte=None),
        expected_intent=dict(subject="VISIT_SITE", demand="DATE_TIME", coverage="UNSUPPORTED"),
    )
    q["expected_query_anchors"] = intent_gold_anchors(
        q["text"], [("DEMAND", "À quelle heure"), ("SUBJECT", "visite de site"), ("LOT", "lot 17")]
    )
    path.write_text(json.dumps(data))
    module.main(cli)
    report = json.loads((tmp_path / "report.json").read_text())
    assert report["gates"]["legacy_intent_exact"]
    assert report["gates"]["rc_query_intent_exact"]
    q["expected_legacy_intent"]["state"] = "NONE"
    path.write_text(json.dumps(data))
    module.main(cli)
    assert not json.loads((tmp_path / "report.json").read_text())["gates"]["legacy_intent_exact"]
