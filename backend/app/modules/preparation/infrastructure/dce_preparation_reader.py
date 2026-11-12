"""SQLAlchemy adapter for the preparation DCE read port."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.orm import Session

from app.modules.dce.infrastructure.models.dce_requirement_confirmations import (
    DceRequirementConfirmationCurrentRecord,
)
from app.modules.dce.infrastructure.models.dce_requirements import DceRequirementRecord
from app.modules.dce.infrastructure.models.dce_version import DceVersionRecord
from app.modules.preparation.application.ports import (
    PreparationDceInput,
    PreparationRequirementInput,
)


class SqlAlchemyPreparationDceReader:
    """Translate DCE ORM records into the preparation read contract."""

    def read(
        self,
        *,
        session: Session,
        tenant_id: UUID,
        dce_version_id: UUID,
        as_of: datetime,
    ) -> PreparationDceInput | None:
        try:
            return self._read(
                session=session, tenant_id=tenant_id, dce_version_id=dce_version_id, as_of=as_of
            )
        except sa.exc.OperationalError as error:
            from app.platform.events.dispatcher import CommandExecutionError

            raise CommandExecutionError("VERSION_CONFLICT") from error

    def _read(self, *, session, tenant_id, dce_version_id, as_of):
        del as_of
        dce = session.scalar(
            sa.select(DceVersionRecord).where(
                DceVersionRecord.tenant_id == tenant_id,
                DceVersionRecord.id == dce_version_id,
            )
        )
        if dce is None:
            return None
        from app.modules.dce.infrastructure.preparation_readiness import (
            current_preparation_readiness,
        )

        readiness, source_manifest = current_preparation_readiness(session, version=dce, lock=True)
        from app.modules.dce.infrastructure.models.dce_requirements import (
            DceRequirementMaterializationRunRecord,
        )

        current_run = (
            session.scalar(
                sa.select(DceRequirementMaterializationRunRecord.id)
                .where(
                    DceRequirementMaterializationRunRecord.tenant_id == tenant_id,
                    DceRequirementMaterializationRunRecord.dce_version_id == dce_version_id,
                )
                .order_by(
                    DceRequirementMaterializationRunRecord.created_at.desc(),
                    (DceRequirementMaterializationRunRecord.status != "COMPLETED").desc(),
                    DceRequirementMaterializationRunRecord.id.desc(),
                )
                .limit(1)
            )
            if source_manifest
            else None
        )
        requirements = tuple(
            PreparationRequirementInput(
                requirement_id=requirement.id,
                requirement_type=requirement.requirement_type,
                directive_signal=requirement.directive_signal,
                confirmation_outcome=(
                    confirmation.outcome
                    if (
                        confirmation := session.scalar(
                            sa.select(DceRequirementConfirmationCurrentRecord)
                            .where(
                                DceRequirementConfirmationCurrentRecord.tenant_id == tenant_id,
                                DceRequirementConfirmationCurrentRecord.requirement_id
                                == requirement.id,
                            )
                            .with_for_update(read=True, nowait=True)
                        )
                    )
                    is not None
                    else None
                ),
                confirmation_id=confirmation.confirmation_id if confirmation is not None else None,
                confirmation_revision=confirmation.revision if confirmation is not None else None,
            )
            for requirement in session.scalars(
                sa.select(DceRequirementRecord)
                .where(
                    DceRequirementRecord.tenant_id == tenant_id,
                    DceRequirementRecord.dce_version_id == dce_version_id,
                    DceRequirementRecord.requirements_run_id == current_run
                    if current_run is not None
                    else sa.true(),
                )
                .order_by(DceRequirementRecord.id)
                .with_for_update(read=True, nowait=True)
            ).all()
        )
        return PreparationDceInput(
            analysis_readiness=readiness,
            source_manifest_sha256=source_manifest,
            requirements=requirements,
        )
