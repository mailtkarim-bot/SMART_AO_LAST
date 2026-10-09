from datetime import UTC, datetime
from types import SimpleNamespace
from typing import cast
from uuid import uuid4

import pytest
from app.modules.dce.application.queries import (
    CaseDceReadingAvailability,
    CaseDceReadingRequirementProjection,
)
from app.modules.dce.application.source_anchor_projection import (
    DceSourceAnchorProjection,
    DceSourceLocator,
    DceSourceLocatorKind,
)
from app.modules.dce.infrastructure.case_dce_reading_reader import (
    SqlAlchemyCaseDceReadingReader,
    _positive_int,
    _safe_document_family,
    _safe_locator_token,
    _source_locator_label,
)

NOW = datetime(2026, 8, 19, 12, 0, tzinfo=UTC)


class _ScalarSequenceSession:
    def __init__(self, *values):
        self.values = list(values)

    def scalar(self, statement):
        return self.values.pop(0)


def test_reader_returns_broken_reference_without_leaking_dce_data():
    case = SimpleNamespace(
        id=uuid4(),
        title="Affaire",
        lifecycle="ACTIVE",
        commercial_stage="ANALYSIS",
        dce_freshness="REVIEW_REQUIRED",
        applicable_dce_version_id=uuid4(),
    )
    reader = SqlAlchemyCaseDceReadingReader(_ScalarSequenceSession(case, None))

    lookup = reader.get(tenant_id=uuid4(), case_id=case.id)

    assert lookup is not None
    assert lookup.availability is CaseDceReadingAvailability.DCE_REFERENCE_BROKEN
    assert lookup.reading is None
    assert lookup.work_label == "Affaire"


@pytest.mark.parametrize(
    ("classification", "expected"),
    [
        (family, family)
        for family in ("RC", "CCAP", "CCTP", "AE", "BPU", "DPGF", "PLAN", "ANNEX", "RECTIFICATION")
    ]
    + [(None, "SOURCE_UNCLASSIFIED"), ("UNKNOWN", "SOURCE_UNCLASSIFIED")],
)
def test_safe_document_family_exposes_only_closed_vocabulary(classification, expected):
    assert _safe_document_family(classification) == expected


@pytest.mark.parametrize(
    ("locator", "family", "expected"),
    [
        ({"kind": "pdf_page", "page": 3}, "CCTP", "CCTP · page 3"),
        ({"kind": "docx_paragraph", "paragraph": 4}, "AE", "AE · paragraphe 4"),
        ({"kind": "text_line", "line": 8}, "RC", "RC · ligne 8"),
        ({"kind": "xlsx_cell", "sheet": "BPU", "cell": "C12"}, "BPU", "BPU · cellule BPU!C12"),
        ({"kind": "pdf_page", "page": 0}, "CCTP", "Source localisée"),
        ({"kind": "pdf_page", "page": True}, "CCTP", "Source localisée"),
        ({"kind": "xlsx_cell", "sheet": "bad\n", "cell": "C12"}, "BPU", "Source localisée"),
        ({"kind": "xlsx_cell", "sheet": "BPU", "cell": "C" * 17}, "BPU", "Source localisée"),
        (None, "SOURCE_UNCLASSIFIED", "Source localisée"),
    ],
)
def test_source_locator_label_is_bounded_and_human_readable(locator, family, expected):
    assert _source_locator_label(document_family=family, locator_json=locator) == expected


def test_case_reader_attaches_source_anchor_without_changing_legacy_locator_label(monkeypatch):
    from app.modules.dce.infrastructure import case_dce_reading_reader as module

    tenant_id, fragment_id = uuid4(), uuid4()
    anchor = DceSourceAnchorProjection(
        source_anchor_id=fragment_id,
        dce_version_id=uuid4(),
        dce_document_id=uuid4(),
        extraction_id=uuid4(),
        fragment_ordinal=1,
        source_sha256="a" * 64,
        extractor_id="smart-ao-native",
        extractor_version="2",
        fragment_sha256="b" * 64,
        locator=DceSourceLocator(
            kind=DceSourceLocatorKind.PDF_PAGE,
            coordinates={"page": 2, "part": 1},
        ),
    )
    row = SimpleNamespace(
        id=uuid4(),
        requirement_type="ADMINISTRATIVE",
        directive_signal="REQUIRED",
        uncertainty_status="TO_CONFIRM",
        outcome=None,
        revision=None,
        classification="CCTP",
        locator_json={"kind": "pdf_page", "page": 2},
        source_fragment_id=fragment_id,
    )

    class Session:
        def execute(self, _statement):
            return SimpleNamespace(all=lambda: [row])

    def get_many(self, *, session, tenant_id, fragment_ids, dce_version_id):
        assert isinstance(session, Session)
        assert tenant_id == tenant_id_expected
        assert tuple(fragment_ids) == (fragment_id,)
        assert dce_version_id == anchor.dce_version_id
        return {fragment_id: anchor}

    tenant_id_expected = tenant_id
    monkeypatch.setattr(module.SqlAlchemyDceSourceAnchorReader, "get_many", get_many)
    projection = module.SqlAlchemyCaseDceReadingReader(Session())._read_requirements(
        tenant_id=tenant_id,
        dce_version_id=anchor.dce_version_id,
    )[0]

    assert projection.source_locator_label == "CCTP · page 2"
    assert projection.source_anchor == anchor


@pytest.mark.parametrize("value", [1, 10, 999])
def test_positive_int_accepts_only_positive_integers(value):
    assert _positive_int(value) is True


@pytest.mark.parametrize("value", [0, -1, True, False, "1", None])
def test_positive_int_rejects_invalid_values(value):
    assert _positive_int(value) is False


@pytest.mark.parametrize("value", ["sheet", "C12", "x" * 80])
def test_safe_locator_token_accepts_bounded_clean_text(value):
    assert _safe_locator_token(value, maximum_length=80) is True


@pytest.mark.parametrize("value", [None, "", " ", "x" * 81, "line\n", "line\r"])
def test_safe_locator_token_rejects_untrusted_text(value):
    assert _safe_locator_token(value, maximum_length=80) is False


def test_reader_counters_classify_all_closed_outcomes():
    requirements = [
        SimpleNamespace(confirmation_outcome="CONFIRMED"),
        SimpleNamespace(confirmation_outcome="REVIEW_REQUIRED"),
        SimpleNamespace(confirmation_outcome="NOT_APPLICABLE"),
        SimpleNamespace(confirmation_outcome="PENDING_HUMAN_CONFIRMATION"),
    ]

    counters = SqlAlchemyCaseDceReadingReader._counters(
        cast(list[CaseDceReadingRequirementProjection], requirements)
    )

    assert counters.total == 4
    assert counters.confirmed == 1
    assert counters.review_required == 1
    assert counters.not_applicable == 1
    assert counters.pending_human_confirmation == 1
