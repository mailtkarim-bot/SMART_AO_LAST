"""SQLAlchemy adapter for B1 handover projections and verified document metadata."""

from __future__ import annotations

import hashlib
import json
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.orm import Session, sessionmaker

from app.modules.patron_action.application.handover_queries import (
    CaseHandoverOfferDocumentCandidate,
    CaseHandoverSnapshotProjection,
    technical_document_source,
)
from app.modules.patron_action.infrastructure.models.handover import CaseHandoverSnapshotRecord
from app.modules.patron_action.infrastructure.models.outcome import CaseOutcomeRecord
from app.modules.preparation.infrastructure.models import GeneratedTechnicalDocumentRecord
from app.modules.submission.infrastructure.models.submission import (
    SubmissionPackageAuthorizationRecord,
    SubmissionPackageRecord,
)


class SqlAlchemyCaseHandoverReader:
    def __init__(self, session_factory: sessionmaker[Session], *, storage=None) -> None:
        self._session_factory = session_factory
        self._storage = storage

    def list_for_case(
        self, *, tenant_id: UUID, case_id: UUID
    ) -> tuple[CaseHandoverSnapshotProjection, ...]:
        with self._session_factory() as session:
            rows = session.scalars(
                sa.select(CaseHandoverSnapshotRecord)
                .where(
                    CaseHandoverSnapshotRecord.tenant_id == tenant_id,
                    CaseHandoverSnapshotRecord.case_id == case_id,
                )
                .order_by(
                    CaseHandoverSnapshotRecord.created_at.desc(),
                    CaseHandoverSnapshotRecord.revision.desc(),
                )
            ).all()
            latest: dict[UUID, CaseHandoverSnapshotRecord] = {}
            for row in rows:
                latest.setdefault(row.outcome_id, row)
            selected = sorted(latest.values(), key=lambda item: (item.lot_reference, item.revision))
            return tuple(self._project(session, row) for row in selected)

    def _project(self, session, row):
        from app.modules.patron_action.infrastructure.models.handover_receipt import (
            CaseHandoverReceiptRecord,
        )
        from app.modules.patron_action.infrastructure.operational_handover import (
            current_handover_view,
        )

        snapshot, state, reasons, fingerprint = current_handover_view(
            session, row, storage=self._storage
        )
        receipts = session.scalars(
            sa.select(CaseHandoverReceiptRecord)
            .where(
                CaseHandoverReceiptRecord.tenant_id == row.tenant_id,
                CaseHandoverReceiptRecord.case_id == row.case_id,
                CaseHandoverReceiptRecord.snapshot_id == row.id,
            )
            .order_by(
                CaseHandoverReceiptRecord.created_at.desc(), CaseHandoverReceiptRecord.id.desc()
            )
            .limit(101)
        ).all()
        return CaseHandoverSnapshotProjection(
            id=row.id,
            outcome_id=row.outcome_id,
            lot_reference=row.lot_reference,
            submission_package_id=row.submission_package_id,
            package_version=row.package_version,
            manifest_sha256=row.manifest_sha256,
            revision=row.revision,
            created_at=row.created_at,
            snapshot_json=snapshot,
            view_sha256=fingerprint,
            source_state=state,
            source_reasons=reasons,
            receipts_truncated=len(receipts) > 100,
            receipts=tuple(
                dict(
                    receipt_id=str(receipt.id),
                    snapshot_revision=receipt.snapshot_revision,
                    view_sha256=receipt.view_sha256,
                    receipt_kind=receipt.receipt_kind,
                    note=receipt.note,
                    actor_id=str(receipt.actor_id),
                    membership_id=str(receipt.membership_id),
                    created_at=receipt.created_at.isoformat(),
                    scope_state="CURRENT" if receipt.view_sha256 == fingerprint else "HISTORICAL",
                )
                for receipt in receipts[:100]
            ),
        )

    def snapshot_for_case(self, *, tenant_id, case_id, snapshot_id):
        with self._session_factory() as session:
            row = session.scalar(
                sa.select(CaseHandoverSnapshotRecord).where(
                    CaseHandoverSnapshotRecord.tenant_id == tenant_id,
                    CaseHandoverSnapshotRecord.case_id == case_id,
                    CaseHandoverSnapshotRecord.id == snapshot_id,
                )
            )
            return self._project(session, row) if row is not None else None

    def history_for_case(self, *, tenant_id, case_id, before_snapshot_id=None):
        with self._session_factory() as session:
            statement = sa.select(CaseHandoverSnapshotRecord).where(
                CaseHandoverSnapshotRecord.tenant_id == tenant_id,
                CaseHandoverSnapshotRecord.case_id == case_id,
            )
            if before_snapshot_id is not None:
                cursor = session.scalar(
                    statement.where(CaseHandoverSnapshotRecord.id == before_snapshot_id)
                )
                if cursor is None:
                    raise PermissionError("NOT_FOUND_OR_FORBIDDEN")
                statement = statement.where(
                    sa.tuple_(CaseHandoverSnapshotRecord.created_at, CaseHandoverSnapshotRecord.id)
                    < sa.tuple_(cursor.created_at, cursor.id)
                )
            rows = session.scalars(
                statement.order_by(
                    CaseHandoverSnapshotRecord.created_at.desc(),
                    CaseHandoverSnapshotRecord.id.desc(),
                ).limit(21)
            ).all()
            return tuple(self._project(session, row) for row in rows)

    def condition_options(self, *, tenant_id, case_id):
        from app.modules.case.infrastructure.models.case import CaseRecord
        from app.modules.decision.infrastructure.models.decision import (
            DecisionConditionRecord,
            DecisionRecord,
        )
        from app.modules.patron_action.application.operational_handover import review_context_sha256

        with self._session_factory() as session:
            case = session.scalar(
                sa.select(CaseRecord)
                .where(CaseRecord.tenant_id == tenant_id, CaseRecord.id == case_id)
                .with_for_update(nowait=True)
            )
            if case is None:
                raise PermissionError("NOT_FOUND_OR_FORBIDDEN")
            decision = session.scalar(
                sa.select(DecisionRecord)
                .where(
                    DecisionRecord.tenant_id == tenant_id,
                    DecisionRecord.case_id == case_id,
                    DecisionRecord.decision_type == "GO_NO_GO",
                    DecisionRecord.validity == "CURRENT",
                )
                .order_by(DecisionRecord.cycle_number.desc(), DecisionRecord.updated_at.desc())
                .limit(1)
                .with_for_update(read=True, nowait=True)
            )
            context_sha = review_context_sha256(
                scope_fingerprint=case.scope_fingerprint,
                dce_version_id=case.applicable_dce_version_id,
                decision_id=decision.id if decision else None,
                decision_revision=decision.aggregate_revision if decision else None,
            )
            if decision is None:
                return {"source_context_sha256": context_sha, "items": []}
            rows = session.scalars(
                sa.select(DecisionConditionRecord)
                .where(
                    DecisionConditionRecord.tenant_id == tenant_id,
                    DecisionConditionRecord.decision_id == decision.id,
                )
                .order_by(DecisionConditionRecord.id)
                .limit(101)
            ).all()
            items = [
                dict(
                    condition_id=str(row.id),
                    private_label=row.label,
                    status=row.status,
                    decision_id=str(decision.id),
                    decision_revision=decision.aggregate_revision,
                    due_at=row.due_at.isoformat() if row.due_at else None,
                )
                for row in rows
            ]

            return {"source_context_sha256": context_sha, "items": items}

    def list_contract_options(self, *, tenant_id, case_id):
        from app.modules.patron_action.application.operational_handover import canonical_sha256
        from app.modules.patron_action.infrastructure.operational_handover import instrument_record
        from app.modules.pricing.infrastructure.models.contract_instrument_supersession import (
            ContractInstrumentSupersessionRecord as Supersession,
        )
        from app.modules.pricing.infrastructure.models.contract_instrument_version import (
            ContractInstrumentVersionRecord as Instrument,
        )

        with self._session_factory() as session:
            rows = session.scalars(
                sa.select(Instrument)
                .where(Instrument.tenant_id == tenant_id, Instrument.case_id == case_id)
                .order_by(Instrument.created_at.desc(), Instrument.id.desc())
                .limit(101)
            ).all()
            replaced = set(
                session.scalars(
                    sa.select(Supersession.replaced_contract_instrument_version_id).where(
                        Supersession.tenant_id == tenant_id, Supersession.case_id == case_id
                    )
                )
            )
            return tuple(
                dict(
                    instrument_version_id=str(row.id),
                    instrument_kind=row.instrument_kind,
                    version_reference=row.version_reference,
                    record_sha256=canonical_sha256(instrument_record(row)),
                    state="SUPERSEDED" if row.id in replaced else "DECLARED",
                )
                for row in rows
            )

    def offer_document_candidate(
        self, *, tenant_id: UUID, case_id: UUID, snapshot_id: UUID
    ) -> CaseHandoverOfferDocumentCandidate | None:
        with self._session_factory() as session:
            handover = session.scalar(
                sa.select(CaseHandoverSnapshotRecord).where(
                    CaseHandoverSnapshotRecord.tenant_id == tenant_id,
                    CaseHandoverSnapshotRecord.case_id == case_id,
                    CaseHandoverSnapshotRecord.id == snapshot_id,
                )
            )
            if handover is None:
                return None
            package = session.scalar(
                sa.select(SubmissionPackageRecord).where(
                    SubmissionPackageRecord.tenant_id == tenant_id,
                    SubmissionPackageRecord.case_id == case_id,
                    SubmissionPackageRecord.id == handover.submission_package_id,
                    SubmissionPackageRecord.version == handover.package_version,
                )
            )
            if package is None:
                return None
            authorization = session.scalar(
                sa.select(SubmissionPackageAuthorizationRecord.id)
                .where(
                    SubmissionPackageAuthorizationRecord.tenant_id == tenant_id,
                    SubmissionPackageAuthorizationRecord.submission_package_id == package.id,
                    SubmissionPackageAuthorizationRecord.package_version == package.version,
                    SubmissionPackageAuthorizationRecord.manifest_sha256 == package.manifest_sha256,
                    SubmissionPackageAuthorizationRecord.state == "AUTHORIZED",
                )
                .limit(1)
            )
            source = technical_document_source(
                package.manifest_json,
                document_id=package.technical_document_id,
                version=package.technical_document_version,
            )
            document = session.scalar(
                sa.select(GeneratedTechnicalDocumentRecord).where(
                    GeneratedTechnicalDocumentRecord.tenant_id == tenant_id,
                    GeneratedTechnicalDocumentRecord.id == package.technical_document_id,
                    GeneratedTechnicalDocumentRecord.package_id == package.preparation_package_id,
                    GeneratedTechnicalDocumentRecord.version == package.technical_document_version,
                    GeneratedTechnicalDocumentRecord.state == "GENERATED",
                    GeneratedTechnicalDocumentRecord.document_kind == "TECHNICAL_RESPONSE",
                )
            )
            offer = handover.snapshot_json.get("offer", {})
            return CaseHandoverOfferDocumentCandidate(
                manifest_json=package.manifest_json,
                manifest_sha256=package.manifest_sha256,
                snapshot_manifest_sha256=handover.manifest_sha256,
                snapshot_offer=offer if isinstance(offer, dict) else {},
                authorization_present=authorization is not None,
                technical_source_kind=source["kind"] if source else None,
                technical_source_sha256=source["sha256"] if source else None,
                technical_document_sha256=document.content_sha256 if document else None,
                technical_document_storage_key=document.storage_key if document else None,
                technical_document_format=document.content_format if document else "UNKNOWN",
            )

    def list_offer_options(
        self, *, tenant_id: UUID, case_id: UUID
    ) -> tuple[dict[str, object], ...]:
        from app.modules.case.infrastructure.models.case import CaseRecord

        with self._session_factory() as session:
            case = session.scalar(
                sa.select(CaseRecord).where(
                    CaseRecord.tenant_id == tenant_id, CaseRecord.id == case_id
                )
            )
            if case is None:
                return ()
            outcomes = session.scalars(
                sa.select(CaseOutcomeRecord)
                .where(
                    CaseOutcomeRecord.tenant_id == tenant_id,
                    CaseOutcomeRecord.case_id == case_id,
                )
                .order_by(CaseOutcomeRecord.created_at.desc(), CaseOutcomeRecord.id.desc())
            ).all()
            packages = session.scalars(
                sa.select(SubmissionPackageRecord)
                .where(
                    SubmissionPackageRecord.tenant_id == tenant_id,
                    SubmissionPackageRecord.case_id == case_id,
                )
                .order_by(SubmissionPackageRecord.version, SubmissionPackageRecord.id)
            ).all()
            latest_outcomes: dict[str, CaseOutcomeRecord] = {}
            for outcome in outcomes:
                latest_outcomes.setdefault(outcome.lot_reference, outcome)
            outcomes = [outcome for outcome in latest_outcomes.values() if outcome.outcome == "WON"]
            options: list[dict[str, object]] = []
            for outcome in outcomes:
                for package in packages:
                    if (
                        case.applicable_dce_version_id is not None
                        and package.dce_version_id != case.applicable_dce_version_id
                    ):
                        continue
                    manifest = package.manifest_json
                    scope = manifest.get("scope") if isinstance(manifest, dict) else None
                    lots = scope.get("lot_numbers", []) if isinstance(scope, dict) else []
                    if outcome.lot_reference not in {str(lot).strip() for lot in lots}:
                        continue
                    authorization = session.scalar(
                        sa.select(SubmissionPackageAuthorizationRecord.id)
                        .where(
                            SubmissionPackageAuthorizationRecord.tenant_id == tenant_id,
                            SubmissionPackageAuthorizationRecord.submission_package_id
                            == package.id,
                            SubmissionPackageAuthorizationRecord.package_version == package.version,
                            SubmissionPackageAuthorizationRecord.manifest_sha256
                            == package.manifest_sha256,
                            SubmissionPackageAuthorizationRecord.state == "AUTHORIZED",
                        )
                        .limit(1)
                    )
                    if authorization is None:
                        continue
                    raw = json.dumps(
                        manifest, ensure_ascii=False, sort_keys=True, separators=(",", ":")
                    ).encode("utf-8")
                    if hashlib.sha256(raw).hexdigest() != package.manifest_sha256:
                        continue
                    source = technical_document_source(
                        manifest,
                        document_id=package.technical_document_id,
                        version=package.technical_document_version,
                    )
                    if source is None:
                        continue
                    options.append(
                        {
                            "outcome_id": str(outcome.id),
                            "lot_reference": outcome.lot_reference,
                            "submission_package_id": str(package.id),
                            "package_version": package.version,
                            "manifest_sha256": package.manifest_sha256,
                            "dce_version_id": str(package.dce_version_id),
                            "technical_document_id": str(package.technical_document_id),
                            "technical_document_version": package.technical_document_version,
                            "technical_document_kind": source["kind"],
                            "technical_document_sha256": source["sha256"],
                        }
                    )
            return tuple(options)
