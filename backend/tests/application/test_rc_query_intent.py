from hashlib import sha256

import pytest


@pytest.mark.parametrize(
    "query,subject,lot,subject_text",
    [
        (
            "La visite médicale est-elle obligatoire pour le lot 17 ?",
            "VISIT_MEDICAL",
            17,
            "visite médicale",
        ),
        (
            "Faut-il effectuer une visite médicale pour le lot 17 ?",
            "VISIT_MEDICAL",
            17,
            "visite médicale",
        ),
        ("Faut-il joindre le DC2 au dossier du lot 18 ?", "DC2", 18, "DC2"),
        ("Le formulaire DC2 est-il demandé pour le lot 18 ?", "DC2", 18, "DC2"),
        (
            "Le mémoire technique doit-il être remis pour le lot 18 ?",
            "MEMOIRE_TECHNIQUE",
            18,
            "mémoire technique",
        ),
        (
            "La participation à la visite de site est-elle imposée pour le lot 19 ?",
            "VISIT_SITE",
            19,
            "visite de site",
        ),
        ("Quelles visites sont imposées par le règlement ?", "VISIT", None, "visites"),
        ("Les visites sont-elles obligatoires ?", "VISIT", None, "visites"),
        (
            "Une visite médicale est-elle nécessaire pour le lot 17 ?",
            "VISIT_MEDICAL",
            17,
            "visite médicale",
        ),
        (
            "Est-ce que la visite de chantier est facultative pour le lot 20 ?",
            "VISIT_SITE",
            20,
            "visite de chantier",
        ),
        ("Le DC1 doit-il être fourni pour le lot 21 ?", "DC1", 21, "DC1"),
        ("Quelles sont les obligations de visite ?", "VISIT", None, "visite"),
    ],
)
def test_closed_obligation_intent_has_exact_original_query_anchors(
    query, subject, lot, subject_text
):
    from app.modules.knowledge.application.rc_query_intent import parse_rc_query_intent

    intent = parse_rc_query_intent(query)
    assert (intent.subject, intent.demand, intent.coverage) == (subject, "OBLIGATION", "COVERED")
    assert intent.scope.lot == lot
    assert intent.scope.state == ("CANDIDATE" if lot is not None else "UNKNOWN")
    assert intent.query_sha256 == sha256(query.encode()).hexdigest()
    anchors = [a for a in intent.anchors if a.signal == "SUBJECT"]
    assert len(anchors) == 1 and anchors[0].excerpt == subject_text
    assert any(a.signal == "DEMAND" for a in intent.anchors)
    for a in intent.anchors:
        assert query.encode()[a.start_byte : a.end_byte].decode() == a.excerpt


@pytest.mark.parametrize(
    "query",
    [
        "Le DC1 et le DC2 sont-ils requis pour le lot 17 ?",
        "Le DC2 est-il requis pour le lot 17 ou 18 ?",
        "La visite est-elle obligatoire si le site est fermé ?",
        "La visite médicale et de chantier est-elle obligatoire ?",
        "Faut-il joindre une visite médicale pour le lot 17 ?",
        "Le formulaire visite est-il obligatoire pour le lot 17 ?",
        "Que veut dire « le DC2 est-il obligatoire » ?",
        "Le DC2 est-il obligatoire pour le lot 0 ?",
        "Une visite commerciale est-elle obligatoire ?",
        "Quelle teinte RAL retenir ?",
    ],
)
def test_unproved_or_ambiguous_intent_is_never_covered(query):
    from app.modules.knowledge.application.rc_query_intent import parse_rc_query_intent

    assert parse_rc_query_intent(query).coverage in {"UNKNOWN", "AMBIGUOUS"}


@pytest.mark.parametrize(
    "query,demand",
    [
        ("À quelle heure commence la visite du lot 17 ?", "DATE_TIME"),
        ("Quand doit être remis le DC2 pour le lot 17 ?", "DATE_TIME"),
        ("Où se déroule la visite de chantier pour le lot 17 ?", "LOCATION"),
    ],
)
def test_recognized_unsupported_demand_does_not_claim_obligation_coverage(query, demand):
    from app.modules.knowledge.application.rc_query_intent import parse_rc_query_intent

    intent = parse_rc_query_intent(query)
    assert intent.demand == demand and intent.coverage == "UNSUPPORTED"
    for a in intent.anchors:
        assert query.encode()[a.start_byte : a.end_byte].decode() == a.excerpt


@pytest.mark.parametrize("query", ["", " " * 3, "x" * 2001])
def test_query_budget_is_explicit(query):
    from app.modules.knowledge.application.rc_query_intent import parse_rc_query_intent

    with pytest.raises(ValueError):
        parse_rc_query_intent(query)


@pytest.mark.parametrize("extended_forms", [False, True])
@pytest.mark.parametrize(
    "query,excerpt",
    [
        ("La visite de site est-elle obligatoire pour le lot 31 ?", "obligatoire"),
        ("Est-ce que la visite de chantier est facultative pour le lot 32 ?", "facultative"),
        ("La participation à la visite médicale est-elle imposée ?", "imposée"),
        ("Faut-il effectuer une visite de site pour le lot 33 ?", "Faut-il effectuer"),
        ("La visite de site doit-elle être effectuée ?", "doit-elle être effectuée"),
        ("À quelle heure débute la visite de site pour le lot 34 ?", "À quelle heure"),
    ],
)
def test_visit_demand_anchor_is_the_recognized_lexical_cue(extended_forms, query, excerpt):
    from app.modules.knowledge.application.rc_query_intent import parse_rc_query_intent

    intent = parse_rc_query_intent(query, extended_forms=extended_forms)
    demands = [a for a in intent.anchors if a.signal == "DEMAND"]
    assert len(demands) == 1
    expected_start = len(query[: query.index(excerpt)].encode())
    assert (demands[0].start_byte, demands[0].end_byte, demands[0].excerpt) == (
        expected_start,
        expected_start + len(excerpt.encode()),
        excerpt,
    )
    assert intent.query_sha256 == sha256(query.encode()).hexdigest()


@pytest.mark.parametrize(
    "query",
    [
        "Faut-il effectuer une visite de site et une visite médicale ?",
        "La visite de site est-elle obligatoire si ?",
    ],
)
def test_visit_anchor_contract_does_not_promote_multiple_or_truncated_requests(query):
    from app.modules.knowledge.application.rc_query_intent import parse_rc_query_intent

    intent = parse_rc_query_intent(query, extended_forms=True)
    assert intent.coverage in {"UNKNOWN", "AMBIGUOUS"}
    assert intent.demand == "UNKNOWN"
    assert not any(a.signal == "DEMAND" for a in intent.anchors)
