"""Load campaigns are operator-selected HTTP GETs, without redirect or file access."""

import importlib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread

import pytest


@pytest.fixture
def campaign(monkeypatch):
    monkeypatch.syspath_prepend(str(Path(__file__).resolve().parents[3]))
    return importlib.import_module("scripts.run_vps_load_campaign")


@pytest.mark.parametrize(
    "base,path",
    [
        ("file:///tmp", "piece"),
        ("ftp://example.test", "piece"),
        ("https://operator:fixture@example.test", "api"),  # pragma: allowlist secret -- fake URL
        ("https://example.test?token=fixture", "api"),
        ("https://example.test", "https://other.test/api"),
        ("https://example.test", "//other.test/api"),
        ("https://example.test", "../private"),
        ("https://example.test", "api\\private"),
    ],
)
def test_non_http_or_unbounded_destination_is_refused(campaign, base, path):
    with pytest.raises(ValueError):
        campaign._url_for_path(base, path)


def test_http_destination_preserves_query_and_prefix(campaign):
    assert campaign._url_for_path("https://example.test/prefix/", "/api?limit=2") == (
        "https://example.test/prefix/api?limit=2"
    )


def test_redirect_is_not_followed_with_bearer_token(campaign):
    received = []

    class Target(BaseHTTPRequestHandler):
        def do_GET(self):
            received.append(self.headers.get("Authorization"))
            self.send_response(200)
            self.end_headers()

        def log_message(self, format, *args):
            pass

    with ThreadingHTTPServer(("127.0.0.1", 0), Target) as target:

        class Origin(Target):
            def do_GET(self):
                self.send_response(302)
                self.send_header("Location", f"http://127.0.0.1:{target.server_port}/target")
                self.end_headers()

        with ThreadingHTTPServer(("127.0.0.1", 0), Origin) as origin:
            threads = [
                Thread(target=server.serve_forever, daemon=True) for server in (target, origin)
            ]
            for thread in threads:
                thread.start()
            try:
                result = campaign._request(
                    f"http://127.0.0.1:{origin.server_port}", "/api", "synthetic-token", 2
                )
                assert result.status == 302
                assert result.error_code == "HTTP_302"
                assert received == []
            finally:
                origin.shutdown()
                target.shutdown()
                for thread in threads:
                    thread.join(timeout=2)
