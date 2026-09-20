from __future__ import annotations

from datetime import UTC, datetime

import pytest
from app.interfaces.http.routes.patron_boamp_opportunities import _source_status
from app.modules.market_watch.infrastructure.boamp import BoampRegistryUnavailable

CHECKED_AT = datetime(2026, 9, 15, 0, 0, tzinfo=UTC)
LAST_SUCCESS = datetime(2026, 9, 14, 21, 30, tzinfo=UTC)


class AvailableSource:
    def search(self, *, text: str, limit: int, offset: int):
        assert (text, limit, offset) == ("travaux", 1, 0)
        return ()


class UnavailableSource:
    def search(self, *, text: str, limit: int, offset: int):
        raise BoampRegistryUnavailable("offline")


@pytest.mark.parametrize(
    ("source_search", "expected_state"),
    [
        (AvailableSource(), "AVAILABLE"),
        (UnavailableSource(), "UNAVAILABLE"),
        (None, "UNKNOWN"),
    ],
)
def test_source_status_is_closed_and_preserves_last_success(source_search, expected_state):
    status = _source_status(
        source_search=source_search,
        checked_at=CHECKED_AT,
        last_success_at=LAST_SUCCESS,
    )

    assert status.source == "BOAMP"
    assert status.state == expected_state
    assert status.checked_at == CHECKED_AT.isoformat()
    assert status.last_success_at == LAST_SUCCESS.isoformat()
    assert status.retryable is True
    assert status.manual_entry_available is True
