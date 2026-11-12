"""Unqualified cell context must not enter RAG or price/decision comparisons."""

from hashlib import sha256
from types import SimpleNamespace
from unittest.mock import MagicMock
from uuid import uuid4

import pytest
from app.modules.dce.infrastructure.source_anchor_reader import SqlAlchemyDceSourceAnchorReader
from app.modules.decision.infrastructure import cctp_pricing_contradiction_reader as contradictions
from app.modules.decision.infrastructure import cctp_pricing_reader as crossing
from app.modules.knowledge.infrastructure.dce_source import SqlAlchemyDceRetrievalSource


def factory_for(session):
    factory = MagicMock()
    factory.return_value.__enter__.return_value = session
    return factory


def test_rag_source_does_not_admit_cell_context():
    tenant, case, version = uuid4(), uuid4(), uuid4()
    text = "Installer une vanne."
    fragment = SimpleNamespace(
        id=uuid4(),
        tenant_id=tenant,
        text=text,
        text_sha256=sha256(text.encode()).hexdigest(),
        ordinal=1,
        locator_json=dict(kind="docx_table_cell", table=1, row=1, column=1, paragraph=1, part=1),
    )
    session = MagicMock()
    session.execute.return_value.all.return_value = [
        (fragment, SimpleNamespace(dce_version_id=version))
    ]
    reader = SqlAlchemyDceRetrievalSource(session_factory=factory_for(session))
    assert reader.read_chunks(tenant_id=tenant, case_id=case, dce_version_id=version) == ()


def test_pricing_crossing_does_not_consume_cell_without_context(monkeypatch):
    session = MagicMock()
    session.scalar.return_value = uuid4()
    session.execute.side_effect = [
        SimpleNamespace(
            all=lambda: [(uuid4(), 1, dict(kind="docx_table_cell"), "Fourniture de panneau.")]
        ),
        SimpleNamespace(all=lambda: [(uuid4(), "DPGF", 1, "01", "Panneau", "m2")]),
    ]
    match = MagicMock(
        return_value=SimpleNamespace(score_bps=9000, match_score_bps=9000, match_basis="SYNTHETIC")
    )
    monkeypatch.setattr(crossing, "match_cctp_to_pricing_row", match)
    reader = crossing.SqlAlchemyDecisionCctpPricingCrossingReader(factory_for(session))
    assert reader.cross(tenant_id=uuid4(), case_id=uuid4(), limit=20) == ()
    match.assert_not_called()


def test_decision_contradiction_does_not_consume_cell_without_context(monkeypatch):
    session = MagicMock()
    session.scalar.return_value = uuid4()
    session.execute.side_effect = [
        SimpleNamespace(
            all=lambda: [(uuid4(), dict(kind="docx_table_cell"), "Les variantes sont interdites.")]
        ),
        SimpleNamespace(all=lambda: [(uuid4(), "DPGF", 1, "V01", "Variante", "m2")]),
    ]
    match = MagicMock(
        return_value=SimpleNamespace(score_bps=9000, match_score_bps=9000, match_basis="SYNTHETIC")
    )
    monkeypatch.setattr(contradictions, "match_cctp_to_pricing_row", match)
    monkeypatch.setattr(
        contradictions,
        "detect_cctp_pricing_contradiction",
        lambda **kwargs: SimpleNamespace(
            contradiction_type="VARIANT_PRICING_SCOPE_CONFLICT", comparison_basis="SYNTHETIC"
        ),
    )
    reader = contradictions.SqlAlchemyDecisionCctpPricingContradictionReader(factory_for(session))
    assert reader.detect(tenant_id=uuid4(), case_id=uuid4(), limit=20) == ()
    match.assert_not_called()


@pytest.mark.parametrize(
    "extractor,version,eligible",
    [
        ("smart-ao-deterministic", "3", False),
        ("other-parser", "4", False),
        ("smart-ao-deterministic", "4", True),
    ],
)
def test_cell_anchor_requires_qualified_extraction_recipe(extractor, version, eligible):
    fid, did, vid, eid, tenant = [uuid4() for _ in range(5)]
    loc = dict(kind="docx_table_cell", table=1, row=1, column=1, paragraph=1, part=1)
    fragment = SimpleNamespace(id=fid, ordinal=1, locator_json=loc, text_sha256="a" * 64)
    extraction = SimpleNamespace(
        id=eid,
        dce_version_id=vid,
        input_sha256="a" * 64,
        extractor_id=extractor,
        extractor_version=version,
    )
    document = SimpleNamespace(id=did, sha256="a" * 64)
    session = MagicMock()
    session.execute.return_value.all.return_value = [
        (fragment, extraction, document, SimpleNamespace())
    ]
    result = SqlAlchemyDceSourceAnchorReader().get(
        session=session, tenant_id=tenant, fragment_id=fid
    )
    assert (result is not None) == eligible
