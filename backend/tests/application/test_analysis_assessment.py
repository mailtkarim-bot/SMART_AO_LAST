from uuid import uuid4

import pytest
from pydantic import ValidationError


def fields():
    return dict(
        command_id=uuid4(),
        idempotency_key=uuid4(),
        assessment_id=uuid4(),
        case_id=uuid4(),
        point_kind="RISK",
        point_id=uuid4(),
        expected_revision=0,
        source_context_sha256="a" * 64,
        expected_evidence_state="DECLARED",
        expected_evidence="Attestation du fournisseur",
        residual_risk_state="UNKNOWN",
        residual_risk=None,
        unknown_reason="Impact restant non qualifié",
        justification="Relecture Patron du point exact",
        human_confirmed=True,
    )


def test_human_assessment_command_validates_closed_unknown_states():
    from app.modules.case.application.analysis_assessment import RecordAnalysisAssessmentCommand

    assert RecordAnalysisAssessmentCommand(**fields()).expected_revision == 0
    for change in [
        dict(expected_evidence=" "),
        dict(residual_risk="Risque deviné"),
        dict(unknown_reason=None),
        dict(human_confirmed=False),
        dict(expected_revision=-1),
        dict(source_context_sha256="x"),
        dict(point_kind="FINANCIAL_EXPORT"),
    ]:
        with pytest.raises(ValidationError):
            RecordAnalysisAssessmentCommand(**dict(fields(), **change))


def test_source_context_fingerprint_tracks_scope_revision_and_region_only():
    from app.modules.case.application.analysis_assessment import source_context_digest

    point = dict(
        kind="RISK",
        item_id=str(uuid4()),
        native_revision=1,
        source_anchor=dict(fragment_sha256="a" * 64),
        start_byte_offset=0,
        end_byte_offset=8,
    )
    scope = dict(scope_kind="SINGLE_LOT", scope_json={"lot": "2"}, scope_fingerprint="b" * 64)
    digest = source_context_digest(
        point=point, tenant_id=uuid4(), case_id=uuid4(), version_id=uuid4(), scope=scope
    )
    assert len(digest) == 64
    tenant, case, version = uuid4(), uuid4(), uuid4()

    def calculate(p=point, sc=scope):
        return source_context_digest(
            point=p, tenant_id=tenant, case_id=case, version_id=version, scope=sc
        )

    original = calculate()
    for changed in [
        dict(point, native_revision=2),
        dict(point, end_byte_offset=9),
        dict(point, source_anchor=dict(fragment_sha256="b" * 64)),
    ]:
        assert calculate(changed) != original
    assert calculate(sc=dict(scope, scope_json={"lot": "9"})) != original
    assert calculate(dict(point, table_context=None)) == original
    assert calculate(dict(point, table_context={"state": "UNKNOWN", "cells": []})) != original
    context = {"state": "EXACT_SOURCE", "cells": [{"text": "Ne pas intervenir"}]}
    assert calculate(dict(point, table_context=context)) != calculate(
        dict(point, table_context={"state": "EXACT_SOURCE", "cells": [{"text": "Intervenir"}]})
    )


def test_write_requires_recent_mfa_before_dispatch():
    from dataclasses import replace
    from datetime import UTC, datetime, timedelta
    from types import SimpleNamespace

    from app.modules.case.application.analysis_assessment import (
        AnalysisAssessmentService,
        RecordAnalysisAssessmentCommand,
    )
    from app.platform.security.authorization import AuthorizationPolicy
    from app.platform.security.capabilities import capabilities_for
    from app.platform.security.context import ActorKind

    from tests.api.test_case_dce_reading_routes import _Resolver

    actor = replace(
        _Resolver().resolve(access_token="test-token"),
        actor_kind=ActorKind.PATRON_ADMIN,
        capabilities=capabilities_for(ActorKind.PATRON_ADMIN),
        mfa_verified_at=datetime.now(tz=UTC) - timedelta(days=1),
    )
    calls = []
    service = AnalysisAssessmentService(
        dispatcher=SimpleNamespace(dispatch=lambda **kw: calls.append(kw)),
        policy=AuthorizationPolicy(),
    )
    with pytest.raises(PermissionError):
        service.execute(
            actor=actor,
            command=RecordAnalysisAssessmentCommand(**fields()),
            now=datetime.now(tz=UTC),
        )
    assert calls == []
