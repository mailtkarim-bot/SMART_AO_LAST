from dataclasses import replace
from types import SimpleNamespace
from uuid import UUID

import pytest
from app.modules.knowledge.domain.retrieval import (
    DataClassification,
    RetrievalChunk,
    RetrievalScope,
)


def profile(**kwargs):
    from app.modules.knowledge.domain.embedding_profile import CandidateRetrievalProfile

    return CandidateRetrievalProfile(
        revision="a" * 40,
        model_manifest_sha256="b" * 64,
        runtime_manifest_sha256="c" * 64,
        **kwargs,
    )


def scope():
    return RetrievalScope(tenant_id=UUID(int=1), case_id=UUID(int=2), dce_version_id=UUID(int=3))


def chunk(text="Une visite obligatoire est prévue pour le lot 4.", **kwargs):
    return RetrievalChunk(
        chunk_id=UUID(int=4),
        source_fragment_id=UUID(int=4),
        tenant_id=UUID(int=1),
        case_id=UUID(int=2),
        dce_version_id=UUID(int=3),
        ordinal=1,
        text=text,
        locator={"kind": "pdf_page", "page": 7},
        classification=DataClassification.INTERNAL_OPERATIONAL,
        **kwargs,
    )


class Encoder:
    def __init__(self, p):
        self.profile_id = p.profile_id
        self.passages = []
        self.queries = []
        self.after_query = lambda: None
        self.query_vector = (1.0,) + (0.0,) * 383

    def encode_passages(self, texts):
        self.passages.append(list(texts))
        return [(1.0,) + (0.0,) * 383 for _ in texts]

    def encode_query(self, query):
        self.queries.append(query)
        self.after_query()
        return self.query_vector


def service(documents, p=None):
    from app.modules.knowledge.application.candidate_retrieval import CandidateRetrievalService

    p = p or profile()
    encoder = Encoder(p)
    source = SimpleNamespace(read_chunks=lambda **kwargs: tuple(documents))
    return CandidateRetrievalService(profile=p, source=source, encoder=encoder), encoder


def test_profile_identity_includes_segmentation_and_abstention():
    p = profile()
    assert p.profile_id == profile().profile_id
    assert p.profile_id != profile(overlap_chars=100).profile_id
    assert p.profile_id != profile(minimum_score=0.9).profile_id
    with pytest.raises(ValueError):
        profile(minimum_score=float("nan"))
    with pytest.raises(ValueError):
        profile(overlap_chars=1000)


def test_segments_preserve_bytes_hash_and_overlap():
    from hashlib import sha256

    from app.modules.knowledge.application.candidate_retrieval import segment_chunks

    source = chunk("Prévoir les équipements. " * 130)
    segments = segment_chunks([source], profile())
    assert len(segments) > 1
    assert segments[0].start_byte == 0 and segments[-1].end_byte == len(source.text.encode())
    for item in segments:
        assert source.text.encode()[item.start_byte : item.end_byte].decode() == item.chunk.text
        assert item.source_sha256 == sha256(source.text.encode()).hexdigest()
        assert item.chunk.source_fragment_id == source.source_fragment_id
    assert all(b.start_byte < a.end_byte for a, b in zip(segments, segments[1:], strict=False))


@pytest.mark.parametrize(
    "change",
    [
        dict(tenant_id=UUID(int=99)),
        dict(case_id=UUID(int=99)),
        dict(dce_version_id=UUID(int=99)),
        dict(classification=DataClassification.FINANCIAL_PRIVATE),
        dict(classification=DataClassification.PERSONAL_DATA),
    ],
)
def test_foreign_private_and_obsolete_sources_never_reach_encoder(change):
    retrieval, encoder = service([replace(chunk(), **change)])
    result = retrieval.retrieve(query="Visite du lot 4 ?", scope=scope(), top_k=5)
    assert result.state == "ABSTAIN" and result.answer_state == "UNKNOWN" and not result.hits
    assert encoder.passages == encoder.queries == []


def test_separate_encodings_stable_retry_and_no_effect():
    retrieval, encoder = service([chunk()])
    first = retrieval.retrieve(query="Visite lot 4 ?", scope=scope(), top_k=5)
    second = retrieval.retrieve(query="Visite lot 4 ?", scope=scope(), top_k=5)
    assert first == second and first.state == "CANDIDATES_ONLY"
    assert first.answer_state == "UNKNOWN" and len(first.hits) == 1
    assert len(encoder.passages) == 1 and encoder.queries == ["Visite lot 4 ?"] * 2
    assert first.hits[0].source_sha256


def test_source_changed_during_query_refuses_stale_results():
    docs = [chunk()]
    retrieval, encoder = service(docs)
    encoder.after_query = lambda: docs.clear()
    result = retrieval.retrieve(query="Visite lot 4 ?", scope=scope(), top_k=5)
    assert (
        result.state == "REVIEW_REQUIRED"
        and result.reason == "SOURCE_CHANGED"
        and result.hits == ()
    )


def test_changed_content_invalidates_cached_index():
    docs = [chunk()]
    retrieval, encoder = service(docs)
    retrieval.retrieve(query="Visite lot 4 ?", scope=scope(), top_k=5)
    docs[0] = replace(docs[0], text="La visite est facultative.")
    result = retrieval.retrieve(query="Visite lot 4 ?", scope=scope(), top_k=5)
    assert len(encoder.passages) == 2
    assert result.hits[0].result.chunk.text == "La visite est facultative."


def test_abstention_never_means_proven_absence():
    retrieval, encoder = service([chunk()])
    encoder.query_vector = (0.0, 1.0) + (0.0,) * 382
    result = retrieval.retrieve(query="Garantie absente ?", scope=scope(), top_k=5)
    assert result.state == "ABSTAIN" and result.reason == "BELOW_EXPERIMENTAL_FLOOR"
    assert result.answer_state == "UNKNOWN" and not result.hits


def test_rectification_signal_is_review_not_an_applicable_answer():
    retrieval, _ = service(
        [chunk("Le rectificatif annule la date précédente et reporte la remise.")]
    )
    result = retrieval.retrieve(query="Date de remise ?", scope=scope(), top_k=5)
    assert result.state == "REVIEW_REQUIRED" and result.reason == "RECTIFICATION_SIGNAL"
    assert result.hits and result.answer_state == "UNKNOWN"


def test_profile_mismatch_and_invalid_vectors_are_refused():
    from app.modules.knowledge.application.candidate_retrieval import CandidateRetrievalService

    with pytest.raises(ValueError):
        CandidateRetrievalService(
            profile=profile(),
            source=SimpleNamespace(),
            encoder=Encoder(profile(minimum_score=0.95)),
        )
    retrieval, encoder = service([chunk()])
    encoder.query_vector = (float("nan"),) + (0.0,) * 383
    with pytest.raises(ValueError):
        retrieval.retrieve(query="Visite ?", scope=scope(), top_k=5)


def test_financial_query_is_rejected_before_source_or_model():
    from app.modules.knowledge.application.retrieval import FinancialRetrievalQueryRejected

    retrieval, encoder = service([chunk()])
    with pytest.raises(FinancialRetrievalQueryRejected):
        retrieval.retrieve(query="Quel prix et quelle marge ?", scope=scope(), top_k=5)
    assert encoder.passages == encoder.queries == []


def test_returned_locator_cannot_mutate_the_cached_proof():
    retrieval, _ = service([chunk()])
    result = retrieval.retrieve(query="Visite ?", scope=scope())
    result.hits[0].result.chunk.locator["page"] = 999
    again = retrieval.retrieve(query="Visite ?", scope=scope())
    assert again.hits[0].result.chunk.locator["page"] == 7


def test_encoder_profile_changed_during_query_is_refused():
    retrieval, encoder = service([chunk()])
    encoder.after_query = lambda: setattr(encoder, "profile_id", "other")
    with pytest.raises(ValueError):
        retrieval.retrieve(query="Visite ?", scope=scope())


def test_two_concurrent_scopes_never_exchange_hits():
    from concurrent.futures import ThreadPoolExecutor
    from threading import Barrier

    from app.modules.knowledge.application.candidate_retrieval import CandidateRetrievalService

    p = profile()
    encoder = Encoder(p)
    barrier = Barrier(2)
    a = chunk()
    b = replace(
        a,
        tenant_id=UUID(int=99),
        chunk_id=UUID(int=88),
        source_fragment_id=UUID(int=88),
        text="Autre tenant synthétique.",
    )
    encoder.after_query = lambda: barrier.wait(timeout=5)
    source = SimpleNamespace(read_chunks=lambda **kwargs: [a, b])
    retrieval = CandidateRetrievalService(profile=p, source=source, encoder=encoder)
    scopes = [scope(), replace(scope(), tenant_id=UUID(int=99))]
    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(lambda s: retrieval.retrieve(query="Visite ?", scope=s), scopes))
    assert [r.hits[0].result.chunk.source_fragment_id for r in results] == [
        a.source_fragment_id,
        b.source_fragment_id,
    ]


def test_v2_service_projects_pair_and_preserves_v1_policy():

    a = chunk("Lot 4 : la visite est obligatoire.")
    b = replace(
        a,
        chunk_id=UUID(int=5),
        source_fragment_id=UUID(int=5),
        text="Lot 4 : la visite est facultative.",
    )
    v1, _ = service([a, b])
    assert v1.retrieve(query="Visite ?", scope=scope()).state == "CANDIDATES_ONLY"
    p = profile(review_policy="rc-opposition-v2")
    assert p.profile_id != profile().profile_id
    v2, _ = service([a, b], p=p)
    result = v2.retrieve(query="Visite ?", scope=scope())
    assert result.state == "REVIEW_REQUIRED" and result.reason == "RC_OPPOSITION_SIGNAL"
    assert len(result.rc_projection.links) == 1 and result.answer_state == "UNKNOWN"
    assert set(result.review_source_ids) == {a.source_fragment_id, b.source_fragment_id}
    assert result == v2.retrieve(query="Visite ?", scope=scope())


def test_v2_ambiguous_condition_is_visible_and_no_implicit_scope_transfer():

    retrieval, _ = service(
        [chunk("Lot 4 : la visite est obligatoire sauf dispense.")],
        p=profile(review_policy="rc-opposition-v2"),
    )
    result = retrieval.retrieve(query="Visite ?", scope=scope())
    assert result.state == "REVIEW_REQUIRED" and result.reason == "RC_UNPROVEN_CLAUSE"
    assert result.rc_projection.unknown_regions and not result.rc_projection.links


@pytest.mark.parametrize(
    "subject,positive,negative,wanted,other",
    [
        ("visite", "la visite est obligatoire", "la visite est facultative", 14, 13),
        ("variantes", "les variantes sont autorisées", "les variantes sont interdites", 32, 31),
    ],
)
def test_v3_never_promotes_other_lot_pairs_but_keeps_raw_sources(
    subject, positive, negative, wanted, other
):
    docs = [
        chunk(f"Lot {other} : {positive}."),
        replace(
            chunk(f"Lot {other} : {negative}."),
            chunk_id=UUID(int=5),
            source_fragment_id=UUID(int=5),
        ),
        replace(
            chunk(f"Lot {wanted} : {negative}."),
            chunk_id=UUID(int=6),
            source_fragment_id=UUID(int=6),
        ),
    ]
    retrieval, _ = service(docs, p=profile(review_policy="rc-query-lot-v3"))
    result = retrieval.retrieve(query=f"{subject} du lot {wanted} ?", scope=scope())
    assert result.query_lot.lot == wanted and result.state == "CANDIDATES_ONLY"
    assert not result.rc_projection.links and len(result.rc_unscoped_evidence) == 2
    assert len(result.hits) == 3 and {c.lot for c in result.rc_projection.clauses} == {wanted}
    assert result == retrieval.retrieve(query=f"{subject} du lot {wanted} ?", scope=scope())


@pytest.mark.parametrize(
    "query", ["Visite ?", "Visite lots 4 et 5 ?", "Sans le lot 4, visite ?", "Lot 4—7 : visite ?"]
)
def test_v3_unknown_query_scope_does_not_select_a_pair(query):
    docs = [
        chunk("Lot 4 : la visite est obligatoire."),
        replace(
            chunk("Lot 4 : la visite est facultative."),
            chunk_id=UUID(int=5),
            source_fragment_id=UUID(int=5),
        ),
    ]
    retrieval, _ = service(docs, p=profile(review_policy="rc-query-lot-v3"))
    result = retrieval.retrieve(query=query, scope=scope())
    assert result.query_lot.state == "UNKNOWN" and result.answer_state == "UNKNOWN"
    assert result.reason == "RC_QUERY_LOT_UNKNOWN" and result.state == "REVIEW_REQUIRED"
    assert (
        not result.rc_projection.links
        and len(result.rc_unscoped_evidence) == 2
        and len(result.hits) == 2
    )


@pytest.mark.parametrize(
    "policy", ["rc-query-lot-v3", "rc-recall-v4", "rc-specific-v5", "rc-type-proof-v6"]
)
def test_v3_dpgf_refusal_happens_before_source_and_encoder(policy):
    from app.modules.knowledge.application.retrieval import FinancialRetrievalQueryRejected

    retrieval, encoder = service([], p=profile(review_policy=policy))

    def forbidden(**kwargs):
        pytest.fail("financial query reached source")

    retrieval._source.read_chunks = forbidden
    with pytest.raises(FinancialRetrievalQueryRejected, match="FINANCIAL_RETRIEVAL_SCOPE_REQUIRED"):
        retrieval.retrieve(query="La DPGF est-elle requise pour le lot 4 ?", scope=scope())
    assert not encoder.passages and not encoder.queries


def test_v4_rescues_negative_visit_clause_without_changing_dense_floor_or_scope():
    from math import sqrt

    p = profile(review_policy="rc-recall-v4")
    retrieval, encoder = service([chunk("Lot 7 : la visite n’est pas exigée.")], p=p)
    encoder.query_vector = (0.8347, sqrt(1 - 0.8347**2)) + (0.0,) * 382
    result = retrieval.retrieve(query="La visite est-elle obligatoire ?", scope=scope())
    assert len(result.hits) == 1 and result.hits[0].result.score < p.minimum_score
    assert result.score_trace[0].decision == "RC_SUBJECT_RESCUE"
    assert result.score_trace[0].threshold == 0.85
    assert result.query_lot.state == "UNKNOWN" and result.reason == "RC_QUERY_LOT_UNKNOWN"
    assert not result.rc_projection.links and result.answer_state == "UNKNOWN"
    assert result == retrieval.retrieve(query="La visite est-elle obligatoire ?", scope=scope())


def test_v4_does_not_rescue_medical_visit_or_unproven_clause():
    from math import sqrt

    retrieval, encoder = service(
        [
            chunk("La visite médicale est obligatoire."),
            replace(
                chunk("Lot 7 : la visite est obligatoire sauf dispense."),
                chunk_id=UUID(int=5),
                source_fragment_id=UUID(int=5),
            ),
        ],
        p=profile(review_policy="rc-recall-v4"),
    )
    encoder.query_vector = (0.8, sqrt(1 - 0.8**2)) + (0.0,) * 382
    result = retrieval.retrieve(query="La visite est-elle obligatoire ?", scope=scope())
    assert result.state == "ABSTAIN" and not result.hits and len(result.score_trace) == 2
    assert {e.decision for e in result.score_trace} == {"BELOW_FLOOR"}


def test_v4_keeps_dense_hits_first_and_traces_budget_rejection():
    docs = [
        chunk("Lot 7 : la visite est obligatoire."),
        replace(
            chunk("Lot 8 : la visite est facultative."),
            chunk_id=UUID(int=5),
            source_fragment_id=UUID(int=5),
        ),
    ]
    retrieval, _ = service(docs, p=profile(review_policy="rc-recall-v4"))
    result = retrieval.retrieve(query="La visite est-elle obligatoire ?", scope=scope(), top_k=1)
    assert len(result.hits) == 1 and len(result.score_trace) == 2
    assert [e.decision for e in result.score_trace] == ["DENSE_FLOOR", "TOP_K_LIMIT"]


@pytest.mark.parametrize(
    "change",
    [
        dict(tenant_id=UUID(int=99)),
        dict(case_id=UUID(int=99)),
        dict(dce_version_id=UUID(int=99)),
        dict(classification=DataClassification.FINANCIAL_PRIVATE),
        dict(classification=DataClassification.PERSONAL_DATA),
    ],
)
@pytest.mark.parametrize("policy", ["rc-recall-v4", "rc-specific-v5", "rc-type-proof-v6"])
def test_v4_no_trace_or_encoding_for_foreign_or_private_source(change, policy):
    retrieval, encoder = service([replace(chunk(), **change)], p=profile(review_policy=policy))
    result = retrieval.retrieve(query="La visite est-elle obligatoire ?", scope=scope())
    assert (
        not result.hits and not result.score_trace and not encoder.passages and not encoder.queries
    )


@pytest.mark.parametrize("policy", ["rc-recall-v4", "rc-specific-v5", "rc-type-proof-v6"])
def test_v4_changed_source_returns_no_scores_or_rescued_results(policy):
    docs = [chunk()]
    retrieval, encoder = service(docs, p=profile(review_policy=policy))
    encoder.after_query = lambda: docs.clear()
    result = retrieval.retrieve(query="La visite est-elle obligatoire ?", scope=scope())
    assert result.reason == "SOURCE_CHANGED" and not result.hits and not result.score_trace


@pytest.mark.parametrize("segment,overlap,words", [(100, 10, 18), (1000, 150, 190)])
def test_v4_rescue_never_loses_condition_before_segment(segment, overlap, words):
    from math import sqrt

    text = "Si le site est occupé, " + "texte " * words + ". Lot 7 : la visite est obligatoire."
    retrieval, encoder = service(
        [chunk(text)],
        p=profile(review_policy="rc-recall-v4", segment_chars=segment, overlap_chars=overlap),
    )
    encoder.query_vector = (0.8, sqrt(1 - 0.8**2)) + (0.0,) * 382
    result = retrieval.retrieve(query="La visite est-elle obligatoire ?", scope=scope())
    assert not result.hits and not any(
        t.decision == "RC_SUBJECT_RESCUE" for t in result.score_trace
    )


@pytest.mark.parametrize(
    "source_text",
    [
        "Lot 7 : la visite est obligatoire.",
        "Lot 7 : la visite de chantier est obligatoire.",
        "Le dossier médical est disponible. Lot 7 : la visite est obligatoire.",
        "Lot 7 : la visite médicale est obligatoire sauf dispense.",
        "Le texte cite « visite médicale obligatoire » dans une annexe.",
    ],
)
def test_v5_medical_question_never_accepts_unproven_or_other_kind_dense_hit(source_text):
    retrieval, _ = service([chunk(source_text)], p=profile(review_policy="rc-specific-v5"))
    result = retrieval.retrieve(query="La visite médicale est-elle obligatoire ?", scope=scope())
    assert result.state == "ABSTAIN" and result.answer_state == "UNKNOWN" and not result.hits
    assert result.specific_intent.subject == "VISIT_MEDICAL"
    assert result.score_trace[0].decision in {"SPECIFIC_MISMATCH", "SPECIFIC_UNPROVEN"}


@pytest.mark.parametrize(
    "text",
    [
        "Lot 7 : la visite médicale est obligatoire.",
        "Lot 7 : la visite médicale n’est pas obligatoire.",
        "La visite médicale est obligatoire.",
    ],
)
@pytest.mark.parametrize("policy", ["rc-specific-v5", "rc-type-proof-v6"])
def test_v5_medical_evidence_preserves_negation_and_unknown_applicability(text, policy):
    retrieval, _ = service([chunk(text)], p=profile(review_policy=policy))
    result = retrieval.retrieve(query="La visite médicale est-elle obligatoire ?", scope=scope())
    assert len(result.hits) == 1 and result.answer_state == "UNKNOWN"
    assert result.query_lot.state == "UNKNOWN" and not result.rc_projection.links
    assert result == retrieval.retrieve(
        query="La visite médicale est-elle obligatoire ?", scope=scope()
    )


@pytest.mark.parametrize("policy", ["rc-specific-v5", "rc-type-proof-v6"])
def test_v5_site_question_rejects_medical_and_preserves_generic_v4_rescue(policy):
    from math import sqrt

    docs = [
        chunk("Lot 7 : la visite médicale est obligatoire."),
        replace(
            chunk("Lot 8 : la visite de chantier est obligatoire."),
            chunk_id=UUID(int=5),
            source_fragment_id=UUID(int=5),
        ),
    ]
    retrieval, encoder = service(docs, p=profile(review_policy=policy))
    result = retrieval.retrieve(query="La visite de chantier est-elle obligatoire ?", scope=scope())
    assert len(result.hits) == 1 and result.hits[0].result.chunk.source_fragment_id == UUID(int=5)
    retrieval, encoder = service(
        [chunk("Lot 7 : la visite n’est pas exigée.")], p=profile(review_policy=policy)
    )
    encoder.query_vector = (0.8, sqrt(1 - 0.8**2)) + (0.0,) * 382
    result = retrieval.retrieve(query="La visite est-elle obligatoire ?", scope=scope())
    assert len(result.hits) == 1 and result.score_trace[0].decision == "RC_SUBJECT_RESCUE"


@pytest.mark.parametrize("policy", ["rc-specific-v5", "rc-type-proof-v6"])
def test_v5_does_not_promote_other_visit_kind_pairs_inside_matching_fragment(policy):
    text = (
        "Lot 7 : la visite médicale est obligatoire. "
        "Lot 7 : la visite de chantier est obligatoire. "
        "Lot 7 : la visite de chantier est facultative."
    )
    retrieval, _ = service([chunk(text)], p=profile(review_policy=policy))
    result = retrieval.retrieve(
        query="La visite médicale est-elle obligatoire pour le lot 7 ?", scope=scope()
    )
    assert len(result.hits) == 1 and not result.rc_projection.links
    assert {e.subject for e in result.rc_projection.clauses} == {"VISIT_MEDICAL"}
    assert len(result.rc_unscoped_evidence) == 2


@pytest.mark.parametrize("policy", ["rc-specific-v5", "rc-type-proof-v6"])
def test_v5_never_assumes_unqualified_visit_means_site(policy):
    retrieval, _ = service(
        [chunk("Lot 7 : la visite est obligatoire.")], p=profile(review_policy=policy)
    )
    result = retrieval.retrieve(query="La visite de chantier est-elle obligatoire ?", scope=scope())
    assert not result.hits and result.state == "ABSTAIN"


def test_v5_preserves_upstream_condition_for_typed_dense_clause():
    text = (
        "Si le site est occupé : "
        + "texte " * 190
        + ". Lot 7 : la visite médicale est obligatoire."
    )
    retrieval, _ = service([chunk(text)], p=profile(review_policy="rc-specific-v5"))
    result = retrieval.retrieve(query="La visite médicale est-elle obligatoire ?", scope=scope())
    assert not result.hits and result.answer_state == "UNKNOWN"


@pytest.mark.parametrize("policy", ["rc-specific-v5", "rc-type-proof-v6"])
def test_v5_unknown_specific_question_never_selects_a_type(policy):
    retrieval, _ = service(
        [chunk("Lot 7 : la visite médicale est obligatoire.")],
        p=profile(review_policy=policy),
    )
    result = retrieval.retrieve(
        query="Comparer visite médicale et visite de chantier ?", scope=scope()
    )
    assert result.specific_intent.state == "UNKNOWN" and not result.hits
    assert {e.decision for e in result.score_trace} == {"SPECIFIC_QUERY_UNKNOWN"}


@pytest.mark.parametrize("opening,closing", [("«", "»"), ("“", "”"), ('"', '"'), ("'", "'")])
@pytest.mark.parametrize("policy", ["rc-specific-v5", "rc-type-proof-v6"])
def test_v5_never_promotes_typed_clause_inside_multisentence_quotation(opening, closing, policy):
    text = (
        f"Le texte fournit cet exemple : {opening} Début. "
        f"Lot 7 : la visite médicale est obligatoire. Fin. {closing}"
    )
    retrieval, _ = service([chunk(text)], p=profile(review_policy=policy))
    result = retrieval.retrieve(
        query="La visite médicale est-elle obligatoire pour le lot 7 ?", scope=scope()
    )
    assert not result.hits and result.answer_state == "UNKNOWN"


@pytest.mark.parametrize("policy", ["rc-specific-v5", "rc-type-proof-v6"])
def test_v5_quotation_opened_before_segment_is_not_lost(policy):
    text = (
        "Exemple : « Début. "
        + "texte " * 190
        + ". Lot 7 : la visite médicale est obligatoire. Fin. »"
    )
    retrieval, _ = service([chunk(text)], p=profile(review_policy=policy))
    result = retrieval.retrieve(query="La visite médicale est-elle obligatoire ?", scope=scope())
    assert not result.hits


@pytest.mark.parametrize("policy", ["rc-specific-v5", "rc-type-proof-v6"])
def test_v5_balanced_quotation_and_apostrophe_do_not_hide_genuine_negative_clause(policy):
    text = "Exemple « Début. Fin. ». Lot 7 : la visite médicale n'est pas obligatoire."
    retrieval, _ = service([chunk(text)], p=profile(review_policy=policy))
    result = retrieval.retrieve(
        query="La visite médicale est-elle obligatoire pour le lot 7 ?", scope=scope()
    )
    assert len(result.hits) == 1 and len(result.rc_projection.clauses) == 1
    assert result.rc_projection.clauses[0].value == "NOT_REQUIRED"


@pytest.mark.parametrize("policy", ["rc-specific-v5", "rc-type-proof-v6"])
def test_v5_curly_apostrophe_inside_quoted_text_never_closes_quotation(policy):
    text = (
        "Exemple : ‘ Cette visite n’est pas retenue. "
        "Lot 7 : la visite médicale est obligatoire. Fin. ’"
    )
    retrieval, _ = service([chunk(text)], p=profile(review_policy=policy))
    result = retrieval.retrieve(
        query="La visite médicale est-elle obligatoire pour le lot 7 ?", scope=scope()
    )
    assert not result.hits and result.answer_state == "UNKNOWN"


def test_v6_rescues_typed_negative_below_floor_without_applicability():
    from math import sqrt

    retrieval, encoder = service(
        [chunk("Lot 7 : la visite médicale n’est pas exigée.")],
        p=profile(review_policy="rc-type-proof-v6"),
    )
    encoder.query_vector = (0.84, sqrt(1 - 0.84**2)) + (0.0,) * 382
    result = retrieval.retrieve(query="La visite médicale est-elle obligatoire ?", scope=scope())
    assert len(result.hits) == 1 and result.score_trace[0].decision == "RC_TYPED_RESCUE"
    assert (
        result.answer_state == "UNKNOWN"
        and result.query_lot.state == "UNKNOWN"
        and not result.rc_projection.links
    )
    assert result.visit_type_evidence[0].visit_type_proof.signal == "VISIT_MEDICAL"
    assert result == retrieval.retrieve(
        query="La visite médicale est-elle obligatoire ?", scope=scope()
    )


@pytest.mark.parametrize(
    "text",
    [
        "Lot 7 : la visite médicale est obligatoire sauf dispense.",
        "Si le site est occupé. Lot 7 : la visite médicale est obligatoire.",
    ],
)
def test_v6_keeps_conditions_unknown_when_retrieving_typed_clause(text):
    retrieval, _ = service([chunk(text)], p=profile(review_policy="rc-type-proof-v6"))
    result = retrieval.retrieve(
        query="La visite médicale est-elle obligatoire pour le lot 7 ?", scope=scope()
    )
    assert len(result.hits) == 1 and result.state == "REVIEW_REQUIRED"
    assert not result.rc_projection.clauses and not result.rc_projection.links
    evidence = next(c for c in result.rc_projection.unknown_regions if c.visit_type_proof)
    assert evidence.value == "UNKNOWN" and evidence.condition_signals


def test_v6_type_without_directive_is_traced_but_never_rescued():
    retrieval, _ = service(
        [chunk("Lot 7 : la visite médicale est citée dans une annexe.")],
        p=profile(review_policy="rc-type-proof-v6"),
    )
    result = retrieval.retrieve(query="La visite médicale est-elle obligatoire ?", scope=scope())
    assert not result.hits and result.visit_type_evidence[0].visit_type_proof
    assert result.visit_type_evidence[0].directive_signal == "UNKNOWN"


def test_v6_typed_rescue_budget_does_not_mark_unselected_segment_as_selected():
    from math import sqrt

    docs = [
        chunk("Lot 7 : la visite médicale est obligatoire."),
        replace(
            chunk("Lot 8 : la visite médicale n’est pas exigée."),
            chunk_id=UUID(int=5),
            source_fragment_id=UUID(int=5),
        ),
    ]
    retrieval, encoder = service(docs, p=profile(review_policy="rc-type-proof-v6"))
    encoder.query_vector = (0.84, sqrt(1 - 0.84**2)) + (0.0,) * 382
    result = retrieval.retrieve(
        query="La visite médicale est-elle obligatoire ?", scope=scope(), top_k=1
    )
    assert len(result.hits) == 1
    assert [t.decision for t in result.score_trace] == ["RC_TYPED_RESCUE", "TOP_K_LIMIT"]


@pytest.mark.parametrize(
    "text",
    [
        "Lot 7 : la visite est obligatoire.",
        "Lot 7 : la visite de chantier est obligatoire.",
        "Le dossier médical est disponible. Lot 7 : la visite est obligatoire.",
        "Le texte cite « visite médicale obligatoire » dans une annexe.",
    ],
)
def test_v6_independent_type_never_promotes_wrong_kind_or_mention(text):
    retrieval, _ = service([chunk(text)], p=profile(review_policy="rc-type-proof-v6"))
    result = retrieval.retrieve(query="La visite médicale est-elle obligatoire ?", scope=scope())
    assert not result.hits and result.answer_state == "UNKNOWN"


def test_v6_recovers_type_across_segment_but_never_resolves_upstream_condition():
    from math import sqrt

    text = (
        "Si le site est occupé : "
        + "texte " * 190
        + ". Lot 7 : la visite médicale est obligatoire."
    )
    retrieval, encoder = service([chunk(text)], p=profile(review_policy="rc-type-proof-v6"))
    encoder.query_vector = (0.84, sqrt(1 - 0.84**2)) + (0.0,) * 382
    result = retrieval.retrieve(
        query="La visite médicale est-elle obligatoire pour le lot 7 ?", scope=scope()
    )
    assert len(result.hits) == 1 and result.score_trace[-1].decision == "RC_TYPED_RESCUE"
    evidence = next(e for e in result.rc_projection.unknown_regions if e.visit_type_proof)
    assert evidence.value == "UNKNOWN" and evidence.kind == "UNKNOWN"
    assert (
        evidence.condition_signals[0].excerpt == "Si"
        and evidence.condition_signals[0].start_byte == 0
    )


@pytest.mark.parametrize(
    "suffix",
    [
        "Sauf dispense délivrée par le médecin.",
        "Cette exigence s’applique seulement si le personnel est exposé.",
    ],
)
def test_v6_condition_after_period_does_not_disappear(suffix):
    from math import sqrt

    text = "Lot 7 : la visite médicale est obligatoire. " + suffix
    retrieval, encoder = service([chunk(text)], p=profile(review_policy="rc-type-proof-v6"))
    encoder.query_vector = (0.84, sqrt(1 - 0.84**2)) + (0.0,) * 382
    result = retrieval.retrieve(
        query="La visite médicale est-elle obligatoire pour le lot 7 ?", scope=scope()
    )
    assert (
        len(result.hits) == 1
        and not result.rc_projection.clauses
        and not result.rc_projection.links
    )
    evidence = next(e for e in result.rc_projection.unknown_regions if e.visit_type_proof)
    assert evidence.value == "UNKNOWN" and evidence.condition_signals


def test_v6_condition_after_selected_segment_is_preserved_from_exact_source():
    from math import sqrt

    text = "Lot 7 : la visite médicale est obligatoire. " + "texte " * 190 + ". Sauf dispense."
    retrieval, encoder = service([chunk(text)], p=profile(review_policy="rc-type-proof-v6"))
    encoder.query_vector = (0.84, sqrt(1 - 0.84**2)) + (0.0,) * 382
    result = retrieval.retrieve(
        query="La visite médicale est-elle obligatoire pour le lot 7 ?", scope=scope()
    )
    evidence = next(e for e in result.rc_projection.unknown_regions if e.visit_type_proof)
    assert (
        evidence.value == "UNKNOWN"
        and evidence.condition_signals[-1].start_byte > result.hits[0].end_byte
    )
