from __future__ import annotations

import base64
from datetime import datetime
from typing import cast
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.orm import Session

from app.modules.case.infrastructure.models.case import CaseRecord
from app.modules.dce.infrastructure.models.dce_extraction import (
    DceDocumentExtractionFragmentRecord,
    DceDocumentExtractionRecord,
)
from app.modules.decision.application.ports import (
    DecisionRiskDraft,
    DecisionRiskPage,
    DecisionRiskSnapshot,
    DecisionRiskTreatmentTransitionDraft,
)
from app.modules.decision.infrastructure.models.risk import (
    DecisionRiskRecord,
    DecisionRiskTreatmentTransitionRecord,
)


class SqlAlchemyDecisionRiskRepository:
    """SQLAlchemy adapter for the tenant-scoped structured risk register."""

    def case_exists(self, *, session: object, tenant_id: UUID, case_id: UUID) -> bool:
        db_session = cast(Session, session)
        return (
            db_session.scalar(
                sa.select(CaseRecord.id).where(
                    CaseRecord.tenant_id == tenant_id,
                    CaseRecord.id == case_id,
                )
            )
            is not None
        )

    def case_uses_dce_version(
        self, *, session: object, tenant_id: UUID, case_id: UUID, dce_version_id: UUID
    ) -> bool:
        db_session = cast(Session, session)
        return (
            db_session.scalar(
                sa.select(CaseRecord.id).where(
                    CaseRecord.tenant_id == tenant_id,
                    CaseRecord.id == case_id,
                    CaseRecord.applicable_dce_version_id == dce_version_id,
                )
            )
            is not None
        )

    def source_exists(
        self,
        *,
        session: object,
        tenant_id: UUID,
        dce_version_id: UUID,
        source_fragment_id: UUID,
    ) -> bool:
        db_session = cast(Session, session)
        return (
            db_session.scalar(
                sa.select(DceDocumentExtractionFragmentRecord.id)
                .join(
                    DceDocumentExtractionRecord,
                    sa.and_(
                        DceDocumentExtractionRecord.tenant_id
                        == DceDocumentExtractionFragmentRecord.tenant_id,
                        DceDocumentExtractionRecord.id
                        == DceDocumentExtractionFragmentRecord.extraction_id,
                    ),
                )
                .where(
                    DceDocumentExtractionFragmentRecord.tenant_id == tenant_id,
                    DceDocumentExtractionFragmentRecord.id == source_fragment_id,
                    DceDocumentExtractionRecord.dce_version_id == dce_version_id,
                    DceDocumentExtractionRecord.status == "COMPLETED",
                )
            )
            is not None
        )

    def source_supports(
        self,
        *,
        session: object,
        tenant_id: UUID,
        dce_version_id: UUID,
        source_fragment_id: UUID,
        source_excerpt: str,
        start_byte_offset: int,
        end_byte_offset: int,
    ) -> bool:
        db_session = cast(Session, session)
        fragment = db_session.scalar(
            sa.select(DceDocumentExtractionFragmentRecord)
            .join(
                DceDocumentExtractionRecord,
                sa.and_(
                    DceDocumentExtractionRecord.tenant_id
                    == DceDocumentExtractionFragmentRecord.tenant_id,
                    DceDocumentExtractionRecord.id
                    == DceDocumentExtractionFragmentRecord.extraction_id,
                ),
            )
            .where(
                DceDocumentExtractionFragmentRecord.tenant_id == tenant_id,
                DceDocumentExtractionFragmentRecord.id == source_fragment_id,
                DceDocumentExtractionRecord.dce_version_id == dce_version_id,
                DceDocumentExtractionRecord.status == "COMPLETED",
            )
        )
        if fragment is None:
            return False
        text_bytes = fragment.text.encode("utf-8")
        if not 0 <= start_byte_offset < end_byte_offset <= len(text_bytes):
            return False
        try:
            excerpt_at_offsets = text_bytes[start_byte_offset:end_byte_offset].decode("utf-8")
        except UnicodeDecodeError:
            return False
        return excerpt_at_offsets == source_excerpt

    def functional_exists(self, *, session: object, tenant_id: UUID, functional_key: str) -> bool:
        db_session = cast(Session, session)
        return (
            db_session.scalar(
                sa.select(DecisionRiskRecord.id).where(
                    DecisionRiskRecord.tenant_id == tenant_id,
                    DecisionRiskRecord.functional_key == functional_key,
                )
            )
            is not None
        )

    def create(self, *, session: object, draft: DecisionRiskDraft) -> None:
        db_session = cast(Session, session)
        draft.risk.validate()
        db_session.add(
            DecisionRiskRecord(
                id=draft.id,
                tenant_id=draft.tenant_id,
                case_id=draft.case_id,
                dce_version_id=draft.dce_version_id,
                source_fragment_id=draft.source_fragment_id,
                functional_key=draft.functional_key,
                category=draft.risk.category.value,
                risk_code=draft.risk.risk_code,
                title=draft.risk.title,
                statement=draft.risk.statement,
                severity=draft.risk.severity.value,
                likelihood=draft.risk.likelihood.value,
                treatment=draft.risk.treatment.value,
                source_excerpt=draft.risk.source_excerpt,
                source_locator_json=draft.risk.source_locator,
                start_byte_offset=draft.risk.start_byte_offset,
                end_byte_offset=draft.risk.end_byte_offset,
                actor_id=draft.actor_id,
                membership_id=draft.membership_id,
                command_id=draft.command_id,
                idempotency_key=draft.idempotency_key,
                correlation_id=draft.correlation_id,
                due_at=draft.due_at,
            )
        )

    def get_current(
        self, *, session: object, tenant_id: UUID, case_id: UUID, risk_id: UUID
    ) -> DecisionRiskSnapshot | None:
        db_session = cast(Session, session)
        risk = db_session.scalar(
            sa.select(DecisionRiskRecord).where(
                DecisionRiskRecord.tenant_id == tenant_id,
                DecisionRiskRecord.case_id == case_id,
                DecisionRiskRecord.id == risk_id,
            )
        )
        if risk is None:
            return None
        latest = self._latest_transition(session=db_session, tenant_id=tenant_id, risk_id=risk_id)
        return _risk_snapshot(risk=risk, latest=latest)

    def list_for_case(
        self,
        *,
        session: object,
        tenant_id: UUID,
        case_id: UUID,
        limit: int,
        after_created_at: datetime | None,
        after_id: UUID | None,
    ) -> DecisionRiskPage:
        db_session = cast(Session, session)
        page_limit = min(max(limit, 1), 100)

        statement = (
            sa.select(DecisionRiskRecord)
            .where(
                DecisionRiskRecord.tenant_id == tenant_id,
                DecisionRiskRecord.case_id == case_id,
            )
            .order_by(
                DecisionRiskRecord.created_at.asc(),
                DecisionRiskRecord.id.asc(),
            )
            .limit(page_limit + 1)
        )
        if after_created_at is not None and after_id is not None:
            statement = statement.where(
                sa.or_(
                    DecisionRiskRecord.created_at > after_created_at,
                    sa.and_(
                        DecisionRiskRecord.created_at == after_created_at,
                        DecisionRiskRecord.id > after_id,
                    ),
                )
            )

        risks = list(db_session.scalars(statement).all())
        has_more = len(risks) > page_limit
        risks = risks[:page_limit]

        latest_by_risk: dict[UUID, DecisionRiskTreatmentTransitionRecord] = {}
        if risks:
            risk_ids = [risk.id for risk in risks]
            transition_cte = (
                sa.select(
                    DecisionRiskTreatmentTransitionRecord,
                    sa.func.row_number()
                    .over(
                        partition_by=DecisionRiskTreatmentTransitionRecord.risk_id,
                        order_by=DecisionRiskTreatmentTransitionRecord.aggregate_revision.desc(),
                    )
                    .label("rn"),
                )
                .where(
                    DecisionRiskTreatmentTransitionRecord.tenant_id == tenant_id,
                    DecisionRiskTreatmentTransitionRecord.risk_id.in_(risk_ids),
                )
                .cte()
            )
            latest_rows = db_session.execute(
                sa.select(transition_cte).where(transition_cte.c.rn == 1)
            ).all()
            for row in latest_rows:
                transition = row[0]
                latest_by_risk[transition.risk_id] = transition

        items = tuple(
            _risk_snapshot(
                risk=risk,
                latest=latest_by_risk.get(risk.id),
            )
            for risk in risks
        )
        next_cursor = (
            _encode_cursor(items[-1].created_at, items[-1].id) if has_more and items else None
        )
        return DecisionRiskPage(items=items, next_cursor=next_cursor)

    def _latest_transition(
        self, *, session: Session, tenant_id: UUID, risk_id: UUID
    ) -> DecisionRiskTreatmentTransitionRecord | None:
        return session.scalar(
            sa.select(DecisionRiskTreatmentTransitionRecord)
            .where(
                DecisionRiskTreatmentTransitionRecord.tenant_id == tenant_id,
                DecisionRiskTreatmentTransitionRecord.risk_id == risk_id,
            )
            .order_by(DecisionRiskTreatmentTransitionRecord.aggregate_revision.desc())
            .limit(1)
        )

    def transition(self, *, session: object, draft: DecisionRiskTreatmentTransitionDraft) -> None:
        db_session = cast(Session, session)
        risk = db_session.scalar(
            sa.select(DecisionRiskRecord)
            .where(
                DecisionRiskRecord.tenant_id == draft.tenant_id,
                DecisionRiskRecord.id == draft.risk_id,
            )
            .with_for_update()
        )
        if risk is None:
            raise ValueError("RISK_NOT_FOUND_OR_FORBIDDEN")
        latest = db_session.scalar(
            sa.select(DecisionRiskTreatmentTransitionRecord)
            .where(
                DecisionRiskTreatmentTransitionRecord.tenant_id == draft.tenant_id,
                DecisionRiskTreatmentTransitionRecord.risk_id == draft.risk_id,
            )
            .order_by(DecisionRiskTreatmentTransitionRecord.aggregate_revision.desc())
            .limit(1)
        )
        current_treatment = latest.to_treatment if latest is not None else risk.treatment
        current_revision = latest.aggregate_revision if latest is not None else 1
        if current_treatment != draft.from_treatment:
            raise ValueError("RISK_TREATMENT_NOT_CURRENT")
        if current_revision + 1 != draft.aggregate_revision:
            raise ValueError("RISK_REVISION_CONFLICT")
        db_session.add(
            DecisionRiskTreatmentTransitionRecord(
                id=draft.id,
                tenant_id=draft.tenant_id,
                risk_id=draft.risk_id,
                from_treatment=draft.from_treatment,
                to_treatment=draft.to_treatment,
                evidence_excerpt=draft.evidence_excerpt,
                evidence_locator_json=dict(draft.evidence_locator),
                evidence_start_byte_offset=draft.evidence_start_byte_offset,
                evidence_end_byte_offset=draft.evidence_end_byte_offset,
                rationale=draft.rationale,
                aggregate_revision=draft.aggregate_revision,
                actor_id=draft.actor_id,
                membership_id=draft.membership_id,
                command_id=draft.command_id,
                idempotency_key=draft.idempotency_key,
                correlation_id=draft.correlation_id,
            )
        )


def _risk_snapshot(
    *,
    risk: DecisionRiskRecord,
    latest: DecisionRiskTreatmentTransitionRecord | None,
) -> DecisionRiskSnapshot:
    evidence = None
    if latest is not None:
        evidence = {
            "excerpt": latest.evidence_excerpt,
            "locator": dict(latest.evidence_locator_json),
            "start_byte_offset": latest.evidence_start_byte_offset,
            "end_byte_offset": latest.evidence_end_byte_offset,
            "rationale": latest.rationale,
        }
    return DecisionRiskSnapshot(
        id=risk.id,
        tenant_id=risk.tenant_id,
        case_id=risk.case_id,
        dce_version_id=risk.dce_version_id,
        source_fragment_id=risk.source_fragment_id,
        risk_code=risk.risk_code,
        category=risk.category,
        title=risk.title,
        severity=risk.severity,
        likelihood=risk.likelihood,
        treatment=latest.to_treatment if latest is not None else risk.treatment,
        revision=latest.aggregate_revision if latest is not None else 1,
        due_at=risk.due_at,
        created_at=risk.created_at,
        latest_treatment_evidence=evidence,
    )


def _encode_cursor(created_at: datetime, risk_id: UUID) -> str:
    payload = f"{created_at.isoformat()}|{risk_id}"
    return base64.urlsafe_b64encode(payload.encode("utf-8")).decode("ascii").rstrip("=")
