from dataclasses import dataclass
from typing import Literal

import sqlalchemy as sa

from app.modules.case.infrastructure.models.case import CaseRecord
from app.modules.dce.infrastructure.models.dce_version import DceVersionRecord
from app.modules.pricing.infrastructure.models.contract_execution_evidence import (
    ContractExecutionEvidenceRecord,
)
from app.modules.pricing.infrastructure.models.contract_instrument_supersession import (
    ContractInstrumentSupersessionRecord,
)
from app.modules.pricing.infrastructure.models.contract_instrument_version import (
    ContractInstrumentVersionRecord,
)
from app.platform.security.context import ActorKind


@dataclass(frozen=True, slots=True)
class ContractExecutionEvidenceProjection:
    record: ContractExecutionEvidenceRecord
    reception_outcome: Literal[
        "WITH_RESERVATIONS", "UNDER_RESERVATIONS", "WITHOUT_RESERVATIONS", "UNKNOWN"
    ]
    version_relation: Literal["MATCHES_CASE_CURRENT", "REVIEW_REQUIRED", "UNKNOWN"]
    contract_instrument_version_relation: Literal["DECLARED", "REVIEW_REQUIRED", "UNKNOWN"]
    contract_instrument_version: ContractInstrumentVersionRecord | None


@dataclass(frozen=True, slots=True)
class ContractInstrumentSupersessionProjection:
    record: ContractInstrumentSupersessionRecord
    replacing_version: ContractInstrumentVersionRecord
    replaced_version: ContractInstrumentVersionRecord


class ContractExecutionEvidenceReadService:
    def __init__(self, *, session_factory):
        self._session_factory = session_factory

    def list_for_case(self, *, actor, case_id):
        if actor.actor_kind is not ActorKind.PATRON_ADMIN or actor.membership_id is None:
            raise PermissionError("PATRON_REQUIRED")
        with self._session_factory() as session:
            case = session.scalar(
                sa.select(CaseRecord).where(
                    CaseRecord.tenant_id == actor.tenant_id,
                    CaseRecord.id == case_id,
                )
            )
            if case is None:
                return ()
            rows = tuple(
                session.scalars(
                    sa.select(ContractExecutionEvidenceRecord)
                    .where(
                        ContractExecutionEvidenceRecord.tenant_id == actor.tenant_id,
                        ContractExecutionEvidenceRecord.case_id == case_id,
                    )
                    .order_by(
                        ContractExecutionEvidenceRecord.created_at.asc(),
                        ContractExecutionEvidenceRecord.id.asc(),
                    )
                ).all()
            )
            version_ids = {
                row.case_dce_version_id_at_recording
                for row in rows
                if row.case_dce_version_id_at_recording is not None
            }
            versions = (
                {
                    version.id: version
                    for version in session.scalars(
                        sa.select(DceVersionRecord).where(
                            DceVersionRecord.tenant_id == actor.tenant_id,
                            DceVersionRecord.id.in_(version_ids),
                        )
                    ).all()
                }
                if version_ids
                else {}
            )
            instrument_versions = {
                version.id: version
                for version in session.scalars(
                    sa.select(ContractInstrumentVersionRecord).where(
                        ContractInstrumentVersionRecord.tenant_id == actor.tenant_id,
                        ContractInstrumentVersionRecord.case_id == case_id,
                    )
                ).all()
            }
            superseded_instrument_version_ids = {
                relation.replaced_contract_instrument_version_id
                for relation in session.scalars(
                    sa.select(ContractInstrumentSupersessionRecord).where(
                        ContractInstrumentSupersessionRecord.tenant_id == actor.tenant_id,
                        ContractInstrumentSupersessionRecord.case_id == case_id,
                    )
                ).all()
            }
            projections = []
            for row in rows:
                declared_version_id = row.case_dce_version_id_at_recording
                version = versions.get(declared_version_id)
                if declared_version_id is None:
                    relation: Literal[
                        "MATCHES_CASE_CURRENT", "REVIEW_REQUIRED", "UNKNOWN"
                    ] = "UNKNOWN"
                elif (
                    declared_version_id != case.applicable_dce_version_id
                    or version is None
                    or version.lifecycle != "ADMITTED"
                    or version.integrity != "VERIFIED"
                ):
                    relation = "REVIEW_REQUIRED"
                else:
                    relation = "MATCHES_CASE_CURRENT"
                linked_instrument_id = row.contract_instrument_version_id
                if linked_instrument_id is None or linked_instrument_id not in instrument_versions:
                    instrument_relation: Literal[
                        "DECLARED", "REVIEW_REQUIRED", "UNKNOWN"
                    ] = "UNKNOWN"
                elif linked_instrument_id in superseded_instrument_version_ids:
                    instrument_relation = "REVIEW_REQUIRED"
                else:
                    instrument_relation = "DECLARED"
                projections.append(
                    ContractExecutionEvidenceProjection(
                        record=row,
                        reception_outcome=row.reception_outcome or "UNKNOWN",
                        version_relation=relation,
                        contract_instrument_version_relation=instrument_relation,
                        contract_instrument_version=instrument_versions.get(
                            row.contract_instrument_version_id
                        ),
                    )
                )
            return tuple(projections)


class ContractInstrumentVersionReadService:
    def __init__(self, *, session_factory):
        self._session_factory = session_factory

    def list_for_case(self, *, actor, case_id):
        if actor.actor_kind is not ActorKind.PATRON_ADMIN or actor.membership_id is None:
            raise PermissionError("PATRON_REQUIRED")
        with self._session_factory() as session:
            return tuple(
                session.scalars(
                    sa.select(ContractInstrumentVersionRecord)
                    .where(
                        ContractInstrumentVersionRecord.tenant_id == actor.tenant_id,
                        ContractInstrumentVersionRecord.case_id == case_id,
                    )
                    .order_by(
                        ContractInstrumentVersionRecord.created_at.asc(),
                        ContractInstrumentVersionRecord.id.asc(),
                    )
                ).all()
            )


class ContractInstrumentSupersessionReadService:
    def __init__(self, *, session_factory):
        self._session_factory = session_factory

    def list_for_case(self, *, actor, case_id):
        if actor.actor_kind is not ActorKind.PATRON_ADMIN or actor.membership_id is None:
            raise PermissionError("PATRON_REQUIRED")
        with self._session_factory() as session:
            if (
                session.scalar(
                    sa.select(CaseRecord.id).where(
                        CaseRecord.tenant_id == actor.tenant_id,
                        CaseRecord.id == case_id,
                    )
                )
                is None
            ):
                return ()
            rows = tuple(
                session.scalars(
                    sa.select(ContractInstrumentSupersessionRecord)
                    .where(
                        ContractInstrumentSupersessionRecord.tenant_id == actor.tenant_id,
                        ContractInstrumentSupersessionRecord.case_id == case_id,
                    )
                    .order_by(
                        ContractInstrumentSupersessionRecord.created_at.asc(),
                        ContractInstrumentSupersessionRecord.id.asc(),
                    )
                ).all()
            )
            version_ids = {
                version_id
                for row in rows
                for version_id in (
                    row.replacing_contract_instrument_version_id,
                    row.replaced_contract_instrument_version_id,
                )
            }
            versions = (
                {
                    version.id: version
                    for version in session.scalars(
                        sa.select(ContractInstrumentVersionRecord).where(
                            ContractInstrumentVersionRecord.tenant_id == actor.tenant_id,
                            ContractInstrumentVersionRecord.case_id == case_id,
                            ContractInstrumentVersionRecord.id.in_(version_ids),
                        )
                    ).all()
                }
                if version_ids
                else {}
            )
            return tuple(
                ContractInstrumentSupersessionProjection(
                    record=row,
                    replacing_version=versions[row.replacing_contract_instrument_version_id],
                    replaced_version=versions[row.replaced_contract_instrument_version_id],
                )
                for row in rows
            )
