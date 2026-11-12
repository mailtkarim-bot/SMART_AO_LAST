"""Native synthetic chain: refusals and exact retry on both sides of commit."""

import json
import os
from copy import deepcopy
from pathlib import Path
from typing import Any
from uuid import uuid4

import sqlalchemy as sa
from app.modules.pricing.application.case_closure import CaseClosureService
from app.modules.pricing.infrastructure.case_closure_reader import _record, fingerprint
from app.modules.pricing.infrastructure.models.contract_execution_evidence import (
    ContractExecutionEvidenceRecord,
)
from app.modules.pricing.infrastructure.models.payment_cycle_fact import PaymentCycleFactRecord
from app.modules.pricing.infrastructure.models.payment_post_reception_cycle import (
    PaymentPostReceptionCycleRecord,
)
from app.modules.pricing.infrastructure.models.post_reception_obligation import (
    PostReceptionObligationRecord,
)
from app.modules.pricing.infrastructure.models.post_reception_obligation_transition import (
    PostReceptionObligationTransitionRecord,
)
from app.platform.persistence.models import DomainEventRecord, OutboxMessageRecord, TenantRecord
from fastapi.testclient import TestClient
from tests.db.test_l11_v2_closure import (
    test_v2_changes_remain_explicit_in_closure_without_presuming_payment as _run,
)
from tests.db.test_regulatory_profile_persistence import _case


def test_refusals_and_exact_recovery_after_rectification_and_closure(
    session_factory, tmp_path, monkeypatch, closure_runner=None
):
    def qualify(factory, http, w, final):
        root = f"/api/v1/patron/cases/{w.case_id}/closure"

        def snapshot():
            models = (
                ContractExecutionEvidenceRecord,
                PostReceptionObligationRecord,
                PaymentCycleFactRecord,
                PaymentPostReceptionCycleRecord,
            )
            with factory() as session:
                result = {
                    model.__tablename__: [
                        _record(row)
                        for row in session.scalars(
                            sa.select(model)
                            .where(
                                model.tenant_id == w.actor.tenant_id,
                                model.case_id == w.case_id,
                            )
                            .order_by(model.id)
                        ).all()
                    ]
                    for model in models
                }
                result[PostReceptionObligationTransitionRecord.__tablename__] = [
                    _record(row)
                    for row in session.scalars(
                        sa.select(PostReceptionObligationTransitionRecord)
                        .join(
                            PostReceptionObligationRecord,
                            sa.and_(
                                PostReceptionObligationRecord.id
                                == PostReceptionObligationTransitionRecord.obligation_id,
                                PostReceptionObligationRecord.tenant_id
                                == PostReceptionObligationTransitionRecord.tenant_id,
                            ),
                        )
                        .where(
                            PostReceptionObligationRecord.tenant_id == w.actor.tenant_id,
                            PostReceptionObligationRecord.case_id == w.case_id,
                        )
                        .order_by(PostReceptionObligationTransitionRecord.id)
                    ).all()
                ]
                for model in (DomainEventRecord, OutboxMessageRecord):
                    result[model.__tablename__] = session.scalar(
                        sa.select(sa.func.count())
                        .select_from(model)
                        .where(model.tenant_id == w.actor.tenant_id)
                    )
                return result

        def command(view):
            return dict(
                command_id=str(uuid4()),
                idempotency_key=str(uuid4()),
                act_id=str(uuid4()),
                act_kind="RIGHTS_PRESERVATION",
                summary="Suivi synthétique après clôture locale.",
                source_refs=["source://synthetic/recovery"],
                evidence_refs=["proof://synthetic/recovery"],
                closure_review=dict(
                    expected_dossier_sha256=view["dossier_sha256"],
                    human_confirmed=True,
                    justification="Nouvel acte humain, aucun droit acquis déduit.",
                    comparisons=[],
                ),
            )

        before = snapshot()
        body = command(final)
        foreign_tenant, foreign_case, missing_case = uuid4(), uuid4(), uuid4()
        with factory.begin() as session:
            session.add(
                TenantRecord(
                    id=foreign_tenant, slug=f"foreign-{foreign_tenant.hex}", lifecycle="ACTIVE"
                )
            )
            session.flush()
            session.add(_case(tenant_id=foreign_tenant, case_id=foreign_case, marker="f"))
        receipts = []
        for target in (foreign_case, missing_case):
            url = f"/api/v1/patron/cases/{target}/closure"
            get = http.client.get(url, headers=http.patron_headers)
            post = http.client.post(url + "/acts", headers=http.patron_headers, json=body)
            assert get.status_code == post.status_code == 404
            assert get.json() == post.json() == {"detail": "NOT_FOUND_OR_FORBIDDEN"}
        assert http.client.get(root).status_code == 401
        assert (
            http.client.post(root + "/acts", headers=http.driver_headers, json=body).status_code
            == 403
        )
        assert snapshot() == before
        original = CaseClosureService.record
        current = final
        for after_commit in (False, True):
            body = command(current)
            frozen = deepcopy(body)
            before = snapshot()
            committed: list[Any] = []

            def unavailable(service, fault_after_commit=after_commit, results=committed, **kwargs):
                if fault_after_commit:
                    results.append(original(service, **kwargs))
                raise sa.exc.SQLAlchemyError("Synthetic local receipt unavailable")

            with monkeypatch.context() as patch:
                patch.setattr(CaseClosureService, "record", unavailable)
                unknown = http.client.post(root + "/acts", headers=http.patron_headers, json=body)
            assert unknown.status_code == 503 and unknown.json() == {"detail": "RESULT_UNKNOWN"}
            observed = snapshot()
            if not after_commit:
                assert observed == before
            else:
                assert len(observed[ContractExecutionEvidenceRecord.__tablename__]) == (
                    len(before[ContractExecutionEvidenceRecord.__tablename__]) + 1
                )
            # A fresh local HTTP client models reconnection, preserving exact intent and app.
            with TestClient(http.client.app) as resumed:
                recovered = resumed.post(root + "/acts", headers=http.patron_headers, json=body)
                assert recovered.status_code == (200 if after_commit else 201), recovered.text
                assert recovered.json()["replayed"] is after_commit
                assert recovered.json()["command_id"] == frozen["command_id"]
                assert recovered.json()["idempotency_key"] == frozen["idempotency_key"]
                assert recovered.json()["act_id"] == frozen["act_id"]
                if committed:
                    assert recovered.json()["result_code"] == committed[0].result_code
                stable = snapshot()
                repeated = resumed.post(root + "/acts", headers=http.patron_headers, json=body)
                assert repeated.status_code == 200 and repeated.json()["replayed"] is True
                assert snapshot() == stable
                response = resumed.get(root, headers=http.patron_headers)
                assert response.status_code == 200
                current = response.json()
            assert body == frozen
            assert len(stable[ContractExecutionEvidenceRecord.__tablename__]) == (
                len(before[ContractExecutionEvidenceRecord.__tablename__]) + 1
            )
            old_acts = {
                row["id"]: row for row in before[ContractExecutionEvidenceRecord.__tablename__]
            }
            new_acts = {
                row["id"]: row for row in stable[ContractExecutionEvidenceRecord.__tablename__]
            }
            assert set(new_acts) - set(old_acts) == {body["act_id"]}
            assert {key: new_acts[key] for key in old_acts} == old_acts
            for model in (
                PostReceptionObligationRecord,
                PaymentCycleFactRecord,
                PaymentPostReceptionCycleRecord,
                PostReceptionObligationTransitionRecord,
            ):
                assert stable[model.__tablename__] == before[model.__tablename__]
            if after_commit:
                assert stable == observed
            assert current["facts"] == final["facts"]
            assert current["open_obligation_ids"] == final["open_obligation_ids"]
            assert current["financial_observations"]["settlement_state"] == "UNKNOWN"
            assert current["external_receipt_state"] == current["legal_effect_state"] == "UNKNOWN"
            receipts.append(
                dict(
                    after_commit=after_commit,
                    unknown=unknown.json(),
                    recovered=recovered.json(),
                    snapshot_sha256=fingerprint(stable),
                )
            )
        if destination := os.environ.get("SMART_AO_TRANSVERSAL_RECOVERY_PROOF_DIR"):
            path = Path(destination)
            path.mkdir(parents=True, exist_ok=True)
            (path / "recovery.json").write_text(json.dumps(receipts, indent=2))
            (path / "final.json").write_text(json.dumps(current, ensure_ascii=False, indent=2))

    runner = closure_runner or _run
    runner(session_factory, tmp_path, monkeypatch, False, continuity_qualifier=qualify)
