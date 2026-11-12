"""Revisioned advisory plans in the existing append-only optimization register."""

import json
from dataclasses import asdict
from hashlib import sha256

import sqlalchemy as sa
from ortools import __version__ as ortools_version

from app.modules.case.infrastructure.models.case import CaseRecord
from app.modules.optimization.application.dated_capacity import (
    CapacityPeriod,
    CapacitySource,
    DatedCapacityOptimizer,
    DatedDemand,
    DatedSupply,
)
from app.modules.optimization.infrastructure.models import OptimizationRunRecord as Run
from app.platform.events.dispatcher import CommandContext, CommandExecutionError, HandlerOutcome
from app.platform.security.authorization import AuthorizationRequest, AuthorizationResource
from app.platform.security.capabilities import Capability
from app.platform.security.context import ActorKind, DataClassification


def _digest(value):
    return sha256(
        json.dumps(
            value, sort_keys=True, separators=(",", ":"), ensure_ascii=True, default=str
        ).encode()
    ).hexdigest()


def _case(session, tenant, case_id, *, lock=False):
    query = sa.select(CaseRecord).where(CaseRecord.tenant_id == tenant, CaseRecord.id == case_id)
    case = session.scalar(query.with_for_update() if lock else query)
    if case is None:
        raise PermissionError("NOT_FOUND_OR_FORBIDDEN")
    return case


def _context(case):
    return dict(
        dce_version_id=str(case.applicable_dce_version_id)
        if case.applicable_dce_version_id
        else None,
        scope_fingerprint=case.scope_fingerprint,
        dce_freshness=case.dce_freshness,
        lifecycle=case.lifecycle,
    )


def _runs(tenant, case_id):
    return sa.select(Run).where(
        Run.tenant_id == tenant,
        Run.case_id == case_id,
        Run.solver_id == DatedCapacityOptimizer.solver_id,
    )


class RecordDatedCapacityHandler:
    def execute(self, *, session, command, context):
        if context.actor_kind != "PATRON_ADMIN" or context.membership_id is None:
            raise CommandExecutionError("FORBIDDEN")
        try:
            case = _case(session, context.tenant_id, command.case_id, lock=True)
        except PermissionError as error:
            raise CommandExecutionError("NOT_FOUND_OR_FORBIDDEN") from error
        source_context = _context(case)
        if _digest(source_context) != command.context_sha256 or case.lifecycle != "ACTIVE":
            raise CommandExecutionError("CAPACITY_CONTEXT_CONFLICT")
        previous = session.scalar(
            _runs(context.tenant_id, case.id).order_by(Run.source_revision.desc()).limit(1)
        )
        revision = previous.source_revision if previous else 0
        if command.expected_revision != revision or session.get(Run, command.run_id) is not None:
            raise CommandExecutionError("CAPACITY_REVISION_CONFLICT")

        def source(row):
            return CapacitySource(**row.source.model_dump()) if row.source else None

        def period(row):
            return CapacityPeriod(row.start, row.end) if row.start and row.end else None

        demands = (
            tuple(
                DatedDemand(
                    row.id,
                    row.label,
                    row.resource_type,
                    row.units,
                    period(row),
                    source(row),
                    row.named_supply_id,
                )
                for row in command.demands
            )
            if command.demands is not None
            else None
        )
        supplies = (
            tuple(
                DatedSupply(
                    row.id, row.label, row.resource_type, row.units, period(row), source(row)
                )
                for row in command.supplies
            )
            if command.supplies is not None
            else None
        )
        result = DatedCapacityOptimizer().solve(demands=demands, supplies=supplies)
        inputs = dict(
            profile="dated-capacity-v1",
            source_kind="HUMAN_DECLARED",
            context=source_context,
            period_convention="START_INCLUDED_END_EXCLUDED",
            demands=[row.model_dump(mode="json") for row in command.demands]
            if command.demands is not None
            else None,
            supplies=[row.model_dump(mode="json") for row in command.supplies]
            if command.supplies is not None
            else None,
            justification=command.justification,
        )
        conflicts = [asdict(conflict) for conflict in result.conflicts]
        # JSON-compatible copy retains exact dates/UUIDs without modifying the legacy run shape.
        output = json.loads(
            json.dumps(
                dict(
                    assignments=[
                        dict(demand_id=str(did), supply_id=str(sid))
                        for did, sid in result.assignments.items()
                    ],
                    unknown_ids=[str(value) for value in result.unknown_ids],
                    conflicts=conflicts,
                    unassigned_demand_ids=[
                        str(row.id) for row in demands or () if row.id not in result.assignments
                    ],
                    solver_version=ortools_version,
                    reservation_state="NOT_RESERVED",
                    coverage_state="UNKNOWN",
                ),
                default=str,
            )
        )
        session.add(
            Run(
                id=command.run_id,
                tenant_id=context.tenant_id,
                case_id=case.id,
                source_revision=revision + 1,
                solver_id=DatedCapacityOptimizer.solver_id,
                status=result.status.value,
                input_sha256=_digest(inputs),
                input_snapshot_json=inputs,
                result_snapshot_json=output,
                actor_id=context.actor_id,
                command_id=command.command_id,
                idempotency_key=command.idempotency_key,
                correlation_id=context.correlation_id,
            )
        )
        session.flush()
        return HandlerOutcome(
            result_code="DATED_CAPACITY_RECORDED",
            events=(),
            aggregate_refs=(
                {
                    "aggregate_type": "OptimizationRun",
                    "aggregate_id": str(command.run_id),
                    "aggregate_revision": revision + 1,
                },
            ),
        )


class DatedCapacityService:
    def __init__(self, *, session_factory, dispatcher, policy):
        self._factory = session_factory
        self._dispatcher = dispatcher
        self._policy = policy

    def _authorize(self, actor, case_id, now, *, write=False):
        if actor.actor_kind is not ActorKind.PATRON_ADMIN or actor.membership_id is None:
            raise PermissionError("FORBIDDEN")
        decision = self._policy.authorize(
            context=actor,
            request=AuthorizationRequest(
                action=Capability.ASSIGNMENT_MANAGE if write else Capability.CASE_DCE_READ,
                resource=AuthorizationResource(
                    resource_type="CASE_CAPACITY",
                    resource_id=case_id,
                    case_id=case_id,
                    tenant_id=actor.tenant_id,
                    classification=DataClassification.INTERNAL_OPERATIONAL,
                ),
                evaluated_at=now,
                mfa_required=write,
            ),
        )
        if not decision.allowed:
            raise PermissionError("FORBIDDEN")

    def record(self, *, actor, command, now):
        self._authorize(actor, command.case_id, now, write=True)
        return self._dispatcher.dispatch(
            command=command,
            context=CommandContext(
                tenant_id=actor.tenant_id,
                case_id=command.case_id,
                actor_id=actor.actor_id,
                actor_kind=actor.actor_kind.value,
                membership_id=actor.membership_id,
                identity_id=actor.identity_id,
                session_id=actor.session_id,
                received_at=now,
                correlation_id=actor.correlation_id,
            ),
        )

    def read(self, *, actor, case_id, now):
        self._authorize(actor, case_id, now)
        with self._factory() as session:
            session.connection(execution_options={"isolation_level": "REPEATABLE READ"})
            return read_dated_capacity_in_session(
                session, tenant_id=actor.tenant_id, case_id=case_id
            )


def read_dated_capacity_in_session(session, *, tenant_id, case_id):
    """Share native validation within a caller-owned consistent database snapshot."""
    case = _case(session, tenant_id, case_id)
    context = _context(case)
    rows = session.scalars(
        _runs(tenant_id, case_id).order_by(Run.source_revision.desc()).limit(21)
    ).all()
    current = None
    history = []
    for index, row in enumerate(rows[:20]):
        valid = (
            _digest(row.input_snapshot_json) == row.input_sha256
            and row.input_snapshot_json.get("context") == context
            and case.lifecycle == "ACTIVE"
            and case.dce_freshness != "REVIEW_REQUIRED"
        )
        item = dict(
            run_id=str(row.id),
            revision=row.source_revision,
            status=row.status,
            state="CURRENT" if index == 0 and valid else "HISTORICAL",
            input_sha256=row.input_sha256,
            inputs=row.input_snapshot_json,
            result=row.result_snapshot_json,
            created_at=row.created_at,
        )
        if index == 0 and valid:
            current = item
        else:
            history.append(item)
    return dict(
        case_id=str(case_id),
        context_sha256=_digest(context),
        revision=rows[0].source_revision if rows else 0,
        current=current,
        state="CURRENT" if current else "REVIEW_REQUIRED" if rows else "UNKNOWN",
        history=history,
        history_has_more=len(rows) > 20,
        coverage_state="UNKNOWN",
        reservation_state="NOT_RESERVED",
    )
