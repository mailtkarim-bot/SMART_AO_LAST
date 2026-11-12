import pytest


@pytest.mark.parametrize(
    "query,subject",
    [
        ("La visite médicale est-elle obligatoire ?", "VISIT_MEDICAL"),
        ("Une visite de chantier est-elle facultative ?", "VISIT_SITE"),
        ("La visite du site est-elle exigée pour le lot 8 ?", "VISIT_SITE"),
    ],
)
def test_explicit_visit_kind_has_query_anchor(query, subject):
    from app.modules.knowledge.application.rc_specific_intent import parse_visit_intent

    intent = parse_visit_intent(query)
    assert intent.state == "CANDIDATE" and intent.subject == subject
    assert (
        query.encode()[intent.start_byte : intent.end_byte].decode().casefold().startswith("visite")
    )


@pytest.mark.parametrize(
    "query",
    [
        "Comparer visite médicale et visite de chantier ?",
        "La visite de chantier du centre médical est-elle obligatoire ?",
        "À quelle heure commence la visite médicale ?",
        "La visite est-elle médicale ?",
    ],
)
def test_ambiguous_or_uncovered_specific_questions_stay_unknown(query):
    from app.modules.knowledge.application.rc_specific_intent import parse_visit_intent

    intent = parse_visit_intent(query)
    assert intent.state == "UNKNOWN" and intent.subject is None


def test_generic_query_does_not_invent_a_site_kind():
    from app.modules.knowledge.application.rc_specific_intent import parse_visit_intent

    assert parse_visit_intent("La visite est-elle obligatoire ?").state == "NONE"
