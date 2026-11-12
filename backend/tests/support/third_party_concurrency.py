"""A source read and a native later rejection must serialize on the document."""

from concurrent.futures import ThreadPoolExecutor
from threading import Event
from time import monotonic, sleep

import sqlalchemy as sa
from app.modules.enterprise.application.enterprise_upload import VerifyEnterpriseDocumentHandler
from app.modules.preparation.application.review import PreparationReviewHandler


def reject_after_control_read(factory, client, read_path, write_path, headers, body, monkeypatch):
    reached, release, writer_started = Event(), Event(), Event()
    original = PreparationReviewHandler.reread_response_plan_sources
    writer = VerifyEnterpriseDocumentHandler.execute

    def read(self, **kwargs):
        result = original(self, **kwargs)
        reached.set()
        assert release.wait(15), "Synthetic read release timed out"
        return result

    def write(self, **kwargs):
        writer_started.set()
        return writer(self, **kwargs)

    with monkeypatch.context() as patch, ThreadPoolExecutor(max_workers=2) as pool:
        patch.setattr(PreparationReviewHandler, "reread_response_plan_sources", read)
        patch.setattr(VerifyEnterpriseDocumentHandler, "execute", write)
        reading = pool.submit(client.get, read_path, headers=headers)
        assert reached.wait(10), "Reader did not acquire proof locks"
        writing = pool.submit(client.post, write_path, headers=headers, json=body)
        assert writer_started.wait(10), "Native writer did not start"
        blocked = False
        deadline = monotonic() + 5
        try:
            while monotonic() < deadline:
                with factory() as session:
                    blocked = bool(
                        session.scalar(
                            sa.text(
                                "SELECT count(*) FROM pg_stat_activity "
                                "WHERE datname=current_database() AND wait_event_type='Lock' "
                                "AND cardinality(pg_blocking_pids(pid))>0"
                            )
                        )
                    )
                if blocked:
                    break
                sleep(0.05)
            assert blocked and not writing.done(), (
                "Rejection must wait for the source-consuming transaction"
            )
        finally:
            release.set()
        checked = reading.result(15)
        rejected = writing.result(15)
        assert checked.status_code == 200 and checked.json()["source_state"] == "CURRENT", (
            checked.text
        )
        assert rejected.status_code == 200, rejected.text
