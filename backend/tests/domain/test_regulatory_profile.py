from datetime import UTC, datetime
from uuid import uuid4

import pytest

from app.modules.case.domain.regulatory_profile import (
    RegulatoryApplicabilityStatus,
    RegulatoryProfile,
)


def test_profile_accepts_sourced_active_facts() -> None:
    profile = RegulatoryProfile(
        case_id=uuid4(),
        profile_version=1,
        status=RegulatoryApplicabilityStatus.ACTIVE,
        facts={"market_kind": "PUBLIC", "work_kind": "INFRASTRUCTURE"},
        source_refs=("dce:rc:p3",),
        effective_from=datetime(2026, 1, 1, tzinfo=UTC),
    )

    assert profile.status is RegulatoryApplicabilityStatus.ACTIVE
    assert profile.source_refs == ("dce:rc:p3",)


def test_profile_requires_a_source() -> None:
    with pytest.raises(ValueError, match="source_refs"):
        RegulatoryProfile(
            case_id=uuid4(),
            profile_version=1,
            status=RegulatoryApplicabilityStatus.REVIEW_REQUIRED,
            facts={"market_kind": "PUBLIC"},
            source_refs=(),
        )


def test_future_profile_requires_effective_date() -> None:
    with pytest.raises(ValueError, match="effective_from"):
        RegulatoryProfile(
            case_id=uuid4(),
            profile_version=1,
            status=RegulatoryApplicabilityStatus.FUTURE,
            facts={"rule": "future"},
            source_refs=("official:rule:2026",),
        )


def test_profile_version_is_positive() -> None:
    with pytest.raises(ValueError, match="profile_version"):
        RegulatoryProfile(
            case_id=uuid4(),
            profile_version=0,
            status=RegulatoryApplicabilityStatus.UNKNOWN_APPLICABILITY,
            facts={"market_kind": "PRIVATE"},
            source_refs=("manual:case",),
        )
