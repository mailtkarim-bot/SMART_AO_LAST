"""Source-exact full name control through native reimport, review/P5 and ZIP."""

import pytest
from tests.db.test_l08_integrated_packet import (
    test_same_case_integrates_response_controls_and_native_rectification as _run,
)


@pytest.mark.parametrize("name", ["Memoire.pdf", "technical-response.md"])
def test_buyer_full_literal_names_are_compared_on_both_exact_packets(
    session_factory, tmp_path, monkeypatch, name
):
    _run(session_factory, tmp_path, monkeypatch, False, buyer_requested_name=name)
