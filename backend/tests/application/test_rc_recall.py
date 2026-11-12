import pytest


@pytest.mark.parametrize(
    "query,subject",
    [
        ("La visite est-elle obligatoire ?", "VISIT"),
        ("Quelles obligations de visite sont prévues ?", "VISIT"),
        ("Le DC1 est-il obligatoire ?", "DC1"),
        ("Les variantes sont-elles autorisées ?", "VARIANTS"),
    ],
)
def test_only_bounded_generic_queries_request_a_subject_rescue(query, subject):
    from app.modules.knowledge.application.rc_recall import generic_rc_subject

    assert generic_rc_subject(query) == subject


@pytest.mark.parametrize(
    "query",
    [
        "La visite médicale est-elle obligatoire ?",
        "Quelle date de visite est obligatoire ?",
        "La visite est-elle obligatoire pour le lot 4 ?",
        "Lot 4 ou 5 : visite obligatoire ?",
        "La visite est-elle obligatoire si le site est occupé ?",
        "Quelle couleur RAL est obligatoire ?",
        "Le DC1 et le DC2 sont-ils requis ?",
    ],
)
def test_specific_or_ambiguous_queries_do_not_gain_generic_candidates(query):
    from app.modules.knowledge.application.rc_recall import generic_rc_subject

    assert generic_rc_subject(query) is None
