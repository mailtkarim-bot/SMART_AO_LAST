from dataclasses import dataclass

import sqlalchemy as sa

from app.modules.case.infrastructure.models.case import CaseRecord
from app.modules.pricing.infrastructure.models.contract_execution_evidence import (
    ContractExecutionEvidenceRecord,
)
from app.modules.pricing.infrastructure.models.contract_execution_evidence_requalification import (
    ContractExecutionEvidenceRequalificationRecord,
)
from app.modules.pricing.infrastructure.models.contract_instrument_supersession import (
    ContractInstrumentSupersessionRecord,
)
from app.modules.pricing.infrastructure.models.contract_instrument_version import (
    ContractInstrumentVersionRecord,
)
from app.platform.security.context import ActorKind


@dataclass(frozen=True, slots=True)
class ContractExecutionEvidenceRequalificationProjection:
    record: ContractExecutionEvidenceRequalificationRecord
    act: ContractExecutionEvidenceRecord
    supersession: ContractInstrumentSupersessionRecord
    resulting_version: ContractInstrumentVersionRecord | None


class ContractExecutionEvidenceRequalificationReadService:
    def __init__(self, *, session_factory):
        self._session_factory = session_factory

    def list_for_case(self, *, actor, case_id):
        if actor.actor_kind is not ActorKind.PATRON_ADMIN or actor.membership_id is None:
            raise PermissionError("PATRON_REQUIRED")
        with self._session_factory() as session:
            if session.scalar(
                sa.select(CaseRecord.id).where(
                    CaseRecord.tenant_id == actor.tenant_id,
                    CaseRecord.id == case_id,
                )
            ) is None:
                return ()
            rows = tuple(
                session.scalars(
                    sa.select(ContractExecutionEvidenceRequalificationRecord)
                    .where(
                        ContractExecutionEvidenceRequalificationRecord.tenant_id == actor.tenant_id,
                        ContractExecutionEvidenceRequalificationRecord.case_id == case_id,
                    )
                    .order_by(
                        ContractExecutionEvidenceRequalificationRecord.act_id.asc(),
                        ContractExecutionEvidenceRequalificationRecord.supersession_id.asc(),
                        ContractExecutionEvidenceRequalificationRecord.revision.asc(),
                        ContractExecutionEvidenceRequalificationRecord.created_at.asc(),
                        ContractExecutionEvidenceRequalificationRecord.id.asc(),
                    )
                ).all()
            )
            if not rows:
                return ()
            act_ids = {row.act_id for row in rows}
            supersession_ids = {row.supersession_id for row in rows}
            version_ids = {
                row.resulting_contract_instrument_version_id
                for row in rows
                if row.resulting_contract_instrument_version_id is not None
            }
            acts = {
                item.id: item
                for item in session.scalars(
                    sa.select(ContractExecutionEvidenceRecord).where(
                        ContractExecutionEvidenceRecord.tenant_id == actor.tenant_id,
                        ContractExecutionEvidenceRecord.case_id == case_id,
                        ContractExecutionEvidenceRecord.id.in_(act_ids),
                    )
                ).all()
            }
            supersessions = {
                item.id: item
                for item in session.scalars(
                    sa.select(ContractInstrumentSupersessionRecord).where(
                        ContractInstrumentSupersessionRecord.tenant_id == actor.tenant_id,
                        ContractInstrumentSupersessionRecord.case_id == case_id,
                        ContractInstrumentSupersessionRecord.id.in_(supersession_ids),
                    )
                ).all()
            }
            versions = (
                {
                    item.id: item
                    for item in session.scalars(
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
                ContractExecutionEvidenceRequalificationProjection(
                    record=row,
                    act=acts[row.act_id],
                    supersession=supersessions[row.supersession_id],
                    resulting_version=versions.get(
                        row.resulting_contract_instrument_version_id
                    ),
                )
                for row in rows
            )
