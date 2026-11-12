from hashlib import sha256

import pytest


@pytest.mark.parametrize(
    "query,subject,actor,obj,action,lot",
    [
        (
            "Chaque candidat doit-il remettre un formulaire DC1 signé ?",
            "DC1",
            "Chaque candidat",
            "un formulaire DC1 signé",
            "remettre",
            None,
        ),
        (
            "Le soumissionnaire doit-il joindre le DC2 renseigné au dossier ?",
            "DC2",
            "Le soumissionnaire",
            "le DC2 renseigné",
            "joindre",
            None,
        ),
        (
            "Pour préparer sa candidature, le candidat doit-il fournir le DC1 pour le lot 18 ?",
            "DC1",
            "le candidat",
            "le DC1",
            "fournir",
            18,
        ),
        (
            "Pour constituer son dossier, chaque titulaire doit-il "
            "présenter un mémoire technique ?",
            "MEMOIRE_TECHNIQUE",
            "chaque titulaire",
            "un mémoire technique",
            "présenter",
            None,
        ),
        (
            "Pour le lot n° 21, l’employeur doit-il effectuer une visite médicale ?",
            "VISIT_MEDICAL",
            "l’employeur",
            "une visite médicale",
            "effectuer",
            21,
        ),
        (
            "Les opérateurs doivent-ils réaliser la visite du site pour le lot 24 ?",
            "VISIT_SITE",
            "Les opérateurs",
            "la visite du site",
            "réaliser",
            24,
        ),
        (
            "Le candidat ne doit-il pas remettre le DC2 ?",
            "DC2",
            "Le candidat",
            "le DC2",
            "remettre",
            None,
        ),
        (
            "Le titulaire est-il tenu de proposer une variante ?",
            "VARIANTS",
            "Le titulaire",
            "une variante",
            "proposer",
            None,
        ),
        (
            "Pour rédiger notre offre, chaque candidat doit joindre le DC1 à sa candidature ?",
            "DC1",
            "chaque candidat",
            "le DC1",
            "joindre",
            None,
        ),
    ],
)
def test_v4_distinct_actor_object_and_obligation_proofs(query, subject, actor, obj, action, lot):
    from app.modules.knowledge.application.rc_actor_intent_v4 import recognize_rc_intent

    result = recognize_rc_intent(query)
    assert result.mechanism == "rc-actor-intent-v4"
    assert result.intent is not None
    assert result.intent.coverage == "COVERED" and result.intent.demand == "OBLIGATION"
    assert result.intent.subject == subject and result.intent.scope.lot == lot
    assert (
        result.actor is not None
        and result.object_evidence is not None
        and result.action_evidence is not None
    )
    assert result.actor.excerpt == actor and result.object_evidence.excerpt == obj
    assert result.action_evidence.excerpt == action
    assert result.intent.query_sha256 == sha256(query.encode()).hexdigest()
    anchors = [*result.intent.anchors, result.actor, result.object_evidence, result.action_evidence]
    anchors.extend(c.context for c in result.contexts)
    for a in anchors:
        assert a is not None
        assert query.encode()[a.start_byte : a.end_byte] == a.excerpt.encode()
    assert result == recognize_rc_intent(query)
    if " sa candidature," in query or " son dossier," in query:
        assert result.contexts[0].owner == result.actor


@pytest.mark.parametrize(
    "query",
    [
        "Pour préparer sa candidature, le DC1 est-il requis ?",
        "Pour préparer sa candidature et son mémoire, le candidat doit-il fournir le DC1 ?",
        "Le candidat doit-il remettre le DC1 et le DC2 ?",
        "Le candidat doit-il remettre le DC1 et effectuer une visite ?",
        "Le candidat doit-il remettre le DC1 si une variante est proposée ?",
        "Si le titulaire change, le candidat doit-il remettre le DC1 ?",
        "Le candidat doit-il remettre le DC1 sauf pour le lot 19 ?",
        "Le candidat doit-il remettre le certificat DC2 ?",
        "Le candidat doit-il remettre un dossier contenant le DC1 ?",
        "Le candidat doit-il effectuer le DC1 ?",
        "Le candidat doit-il joindre la visite médicale ?",
        "Le candidat doit-il effectuer une visite virtuelle ?",
        "Le candidat doit-il remettre le DC1 périmé ?",
        "Le candidat doit-il ne pas remettre le DC1 ?",
        "Les candidats doit-il remettre le DC1 ?",
        "Le candidat doit-il remettre le DC1 pour le lot A ?",
        "Le candidat doit-il remettre le DC1 pour les lots 1 et 2 ?",
        "Le candidat doit-il remettre le DC1 pour le lot -2 ?",
        "Le candidat doit-il remettre le DC1 pour le lot 2 bis ?",
        "Le candidat doit-il remettre le DC1 pour le lot 2.5 ?",
        "Le candidat doit-il remettre son document ?",
        "Pour préparer son offre du lot 18, le candidat doit-il remettre le DC1 ?",
        "Le candidat doit-il remettre le DC1 pour préparer sa réponse sans engagement ?",
    ],
)
def test_v4_never_promotes_unproved_relations(query):
    from app.modules.knowledge.application.rc_actor_intent_v4 import recognize_rc_intent

    result = recognize_rc_intent(query)
    assert result.intent is not None
    assert result.intent.coverage != "COVERED"


def test_financial_query_is_refused_before_fallback(monkeypatch):
    from app.modules.knowledge.application import rc_actor_intent_v4 as module

    monkeypatch.setattr(module, "_v3", lambda q: pytest.fail("financial query reached fallback"))
    result = module.recognize_rc_intent("Le candidat doit-il joindre la DPGF ?")
    assert result.intent is None and result.reason == "FINANCIAL_SCOPE_REFUSED"


@pytest.mark.parametrize("query", [None, "", "a" * 2001, "\ud800"])
def test_invalid_budget_or_unicode_is_safe(query):
    from app.modules.knowledge.application.rc_actor_intent_v4 import recognize_rc_intent

    result = recognize_rc_intent(query)
    assert result.intent is None and result.reason == "INVALID_QUERY_BUDGET"


@pytest.mark.parametrize(
    "query",
    [
        "Le candidat doit-il effectuer le formulaire visite médicale ?",
        "Le candidat doit-il présenter le formulaire variante ?",
        "Les\tcandidats doit-il remettre le DC1 ?",
        "Les\u00a0candidats doit-il remettre le DC1 ?",
    ],
)
def test_review_unproved_head_and_number_are_not_promoted(query):
    from app.modules.knowledge.application.rc_actor_intent_v4 import recognize_rc_intent

    result = recognize_rc_intent(query)
    assert result.intent is not None
    assert result.intent.coverage != "COVERED"


@pytest.mark.parametrize("space", ["\t", "\u00a0"])
def test_review_explicit_plural_proof_accepts_unicode_whitespace(space):
    from app.modules.knowledge.application.rc_actor_intent_v4 import recognize_rc_intent

    result = recognize_rc_intent(f"Les{space}candidats doivent-ils remettre le DC1 ?")
    assert result.intent is not None
    assert result.intent.coverage == "COVERED"


def test_actorless_form_keeps_full_object_and_request_without_inventing_actor():
    from app.modules.knowledge.application.rc_actor_intent_v4 import recognize_rc_intent

    result = recognize_rc_intent("Pour préparer notre offre, le DC1 est-il requis ?")
    assert result.intent is not None
    assert result.intent.coverage == "COVERED" and result.actor is None
    assert result.object_evidence is not None
    assert result.object_evidence.excerpt == "le DC1"
    assert next(a.excerpt for a in result.intent.anchors if a.signal == "DEMAND") == "est-il requis"
    assert result.contexts[0].owner is None


def test_fallback_keeps_the_nominal_request_predicate():
    from app.modules.knowledge.application.rc_actor_intent_v4 import recognize_rc_intent

    r = recognize_rc_intent("Le DC1 est-il une pièce obligatoire ?")
    assert r.intent is not None
    assert (
        next(a.excerpt for a in r.intent.anchors if a.signal == "DEMAND")
        == "est-il une pièce obligatoire"
    )
