from hashlib import sha256

import pytest
from app.modules.knowledge.application.rc_candidate_conflicts import project_rc_conflicts
from app.modules.knowledge.application.rc_query_intent import parse_rc_query_intent

from tests.application.test_candidate_retrieval import chunk, profile, scope, service


@pytest.mark.parametrize(
    "query,subject,lot",
    [
        ("Pour le lot 23, faut-il joindre le DC2 ?", "DC2", 23),
        ("  Pour le lot n° 24 : le formulaire DC1 doit-il être fourni ? ", "DC1", 24),
        ("Le formulaire DC2 doit-il être remis pour le lot 25 ?", "DC2", 25),
        ("Pour le lot 26, la visite de chantier est-elle obligatoire ?", "VISIT_SITE", 26),
    ],
)
def test_v9_query_extensions_keep_raw_offsets_and_legacy(query, subject, lot):
    assert parse_rc_query_intent(query).coverage != "COVERED"
    intent = parse_rc_query_intent(query, extended_forms=True)
    assert (intent.subject, intent.demand, intent.coverage, intent.scope.lot) == (
        subject,
        "OBLIGATION",
        "COVERED",
        lot,
    )
    assert intent.query_sha256 == sha256(query.encode()).hexdigest()
    assert {a.signal for a in intent.anchors} == {"SUBJECT", "DEMAND", "LOT"}
    for a in intent.anchors:
        assert query.encode()[a.start_byte : a.end_byte] == a.excerpt.encode()


@pytest.mark.parametrize(
    "query",
    [
        "Pour les lots 23 et 24, faut-il joindre le DC2 ?",
        "Pour le lot 23 ou 24, faut-il joindre le DC2 ?",
        "Pour le lot 23, faut-il joindre le DC1 et le DC2 ?",
        "Pour le lot 23, le formulaire visite doit-il être effectué ?",
        "Pour le lot 23, faut-il joindre le DC2 pour le lot 24 ?",
        "Pour le lot 23, faut-il joindre le DC2 sauf dispense ?",
    ],
)
def test_v9_never_promotes_ambiguous_queries(query):
    assert parse_rc_query_intent(query, extended_forms=True).coverage != "COVERED"


def project(text, enabled=True):
    return project_rc_conflicts(
        [chunk(text)],
        qualified_visits=True,
        independent_visit_type=True,
        independent_rc_directive=True,
        imperative_sources=enabled,
    )


@pytest.mark.parametrize(
    "text,subject,lot",
    [
        ("Pour le lot 23, fournir le formulaire DC2.", "DC2", 23),
        ("Lot 24 : joindre un mémoire technique.", "MEMOIRE_TECHNIQUE", 24),
        ("Remettre le DC1 pour le lot 25.", "DC1", 25),
        ("Lot 26 : effectuer une visite médicale.", "VISIT_MEDICAL", 26),
        ("Lot 27 : réaliser une visite de chantier.", "VISIT_SITE", 27),
    ],
)
def test_imperative_has_three_exact_source_anchors(text, subject, lot):
    assert not project(text, False).clauses
    result = project(text)
    assert len(result.clauses) == 1
    c = result.clauses[0]
    assert (c.subject, c.lot, c.value, c.kind, c.directive_signal) == (
        subject,
        lot,
        "REQUIRED",
        "ASSERTION",
        "CANDIDATE",
    )
    assert {a.signal for a in c.directive_anchors} == {"SUBJECT", "DIRECTIVE", "LOT"}
    for a in c.directive_anchors:
        assert text.encode()[a.start_byte : a.end_byte] == a.excerpt.encode()
    assert c.source_sha256 == sha256(text.encode()).hexdigest()


@pytest.mark.parametrize(
    "text",
    [
        "Lot 23 : ne pas fournir le DC2.",
        "Lot 23 : fournir le DC2 si demandé.",
        "Lot 23 : fournir le DC2. Sauf dispense.",
        "« Lot 23 : fournir le DC2. »",
        "Exemple : Lot 23 : fournir le DC2.",
        "Lot 23 : fournir le DC1 et le DC2.",
        "Lot 23 ou 24 : fournir le DC2.",
        "Lot 23 : fournir le DC2 pour le lot 24.",
        "Lot 23 : fournir une visite médicale.",
        "Fournir le DC2.",
    ],
)
def test_imperative_does_not_assert_unproved_source(text):
    result = project(text)
    assert not result.clauses
    assert result.unknown_regions and all(c.value == "UNKNOWN" for c in result.unknown_regions)


def test_v9_service_routes_imperative_and_preserves_v8():
    text = "Pour le lot 23, fournir le DC2."
    q = "Pour le lot 23, faut-il joindre le DC2 ?"
    retrieval, encoder = service([chunk(text)], p=profile(review_policy="rc-imperative-v9"))
    read = retrieval.retrieve(query=q, scope=scope())
    assert len(read.hits) == 1 and read.rc_projection.clauses[0].subject == "DC2"
    assert encoder.queries == [q] and read.answer_state == "UNKNOWN"
    legacy, _ = service([chunk(text)], p=profile(review_policy="rc-intent-v8"))
    assert not legacy.retrieve(query=q, scope=scope()).hits


@pytest.mark.parametrize("change", ["tenant_id", "case_id", "dce_version_id", "classification"])
def test_v9_scope_and_private_sources_never_reach_encoder(change):
    from dataclasses import replace
    from uuid import UUID

    from app.modules.knowledge.domain.retrieval import DataClassification

    value = DataClassification.FINANCIAL_PRIVATE if change == "classification" else UUID(int=99)
    doc = replace(chunk("Lot 23 : fournir le DC2."), **{change: value})
    retrieval, encoder = service([doc], p=profile(review_policy="rc-imperative-v9"))
    read = retrieval.retrieve(query="Pour le lot 23, faut-il joindre le DC2 ?", scope=scope())
    assert not read.hits and encoder.queries == encoder.passages == []


def test_v9_conditional_unknown_retry_and_changed_source():
    from math import sqrt

    docs = [chunk("Lot 23 : fournir le DC2.")]
    retrieval, encoder = service(docs, p=profile(review_policy="rc-imperative-v9"))
    encoder.query_vector = (0.84, sqrt(1 - 0.84**2)) + (0.0,) * 382
    query = "Pour le lot 23, faut-il joindre le DC2 ?"
    read = retrieval.retrieve(query=query, scope=scope())
    assert read == retrieval.retrieve(query=query, scope=scope())
    assert read.score_trace[0].decision == "RC_TYPED_RESCUE"
    encoder.after_query = docs.clear
    changed = retrieval.retrieve(query=query, scope=scope())
    assert changed.reason == "SOURCE_CHANGED" and not changed.hits


def test_v9_financial_and_multiple_demands_refuse_before_source(monkeypatch):
    from app.modules.knowledge.application.retrieval import FinancialRetrievalQueryRejected

    retrieval, encoder = service([], p=profile(review_policy="rc-imperative-v9"))
    retrieval._source.read_chunks = lambda **kw: pytest.fail("uncovered source read")
    with pytest.raises(FinancialRetrievalQueryRejected):
        retrieval.retrieve(query="Pour le lot 23, faut-il fournir la DPGF ?", scope=scope())
    read = retrieval.retrieve(
        query="Pour le lot 23, faut-il fournir le DC1 et le DC2 ?", scope=scope()
    )
    assert read.query_intent.coverage == "AMBIGUOUS" and not read.hits
    assert encoder.queries == encoder.passages == []


@pytest.mark.parametrize(
    "prefix",
    [
        "Les instructions suivantes ne sont pas applicables. ",
        "Exemple de rédaction. ",
        "Dispositions générales. ",
    ],
)
def test_imperative_does_not_cross_an_unqualified_source_preamble(prefix):
    result = project(prefix + "Lot 23 : fournir le DC2.")
    assert not result.clauses
    assert all(c.value == "UNKNOWN" for c in result.unknown_regions)
