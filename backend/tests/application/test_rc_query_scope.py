import pytest


@pytest.mark.parametrize(
    "query,lot,excerpt",
    [
        ("La visite est-elle obligatoire pour le lot 14 ?", 14, "lot 14"),
        ("Le lot 32 autorise-t-il des variantes ?", 32, "lot 32"),
        ("Mémoire technique : LOT n° 007 ?", 7, "LOT n° 007"),
    ],
)
def test_explicit_query_lot_has_exact_utf8_anchor(query, lot, excerpt):
    from app.modules.knowledge.application.rc_query_scope import parse_query_lot

    result = parse_query_lot(query)
    assert result.state == "CANDIDATE" and result.lot == lot
    assert query.encode()[result.start_byte : result.end_byte].decode() == excerpt


@pytest.mark.parametrize(
    "query",
    [
        "La visite est-elle obligatoire ?",
        "Comparer les lots 4 et 5 ?",
        "Lot 4 ou lot 5 ?",
        "Lot 4 à 7 ?",
        "Lot 4/5 ?",
        "Lot 0 ?",
        "Lot 4bis ?",
        "Lot 4 bis ?",
        "Lot 1234 ?",
        "Lot IV ?",
        "Sauf le lot 4, la visite est-elle obligatoire ?",
        "Si le lot 4 est retenu ?",
        "Pas le lot 4 : visite ?",
        "Lot 4.2 ?",
        "Lot 4 et 5 ?",
        "Lot 4 puis le lot 4 ?",
        "Sans le lot 4, visite obligatoire ?",
        "À l’exclusion du lot 4 : visite ?",
        "À défaut de lot 4 : visite ?",
        "En dehors du lot 4 : visite ?",
        "Visite du lot 4 jusqu’à 7 ?",
        "Lot 4 non compris : visite ?",
        "Lot 4—7 : visite ?",
        "Lot 4…7 : visite ?",
    ],
)
def test_absent_or_ambiguous_scope_never_selects_a_lot(query):
    from app.modules.knowledge.application.rc_query_scope import parse_query_lot

    result = parse_query_lot(query)
    assert result.state == "UNKNOWN" and result.lot is None


def test_query_budget_is_checked_before_parsing():
    from app.modules.knowledge.application.rc_query_scope import parse_query_lot

    with pytest.raises(ValueError):
        parse_query_lot("lot 4 " + "x" * 2000)
