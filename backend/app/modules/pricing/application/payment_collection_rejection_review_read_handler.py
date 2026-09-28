# ruff: noqa: E501, I001
import sqlalchemy as sa
from app.modules.pricing.infrastructure.models.payment_collection_rejection_review import PaymentCollectionRejectionReviewRecord
class PaymentCollectionRejectionReviewReadService:
    def __init__(self, *, session_factory): self._session_factory = session_factory
    def latest_for_case(self, *, actor, case_id):
        from app.platform.security.context import ActorKind
        if actor.actor_kind is not ActorKind.PATRON_ADMIN or actor.membership_id is None: raise PermissionError("PATRON_REQUIRED")
        with self._session_factory() as session:
            return session.scalar(sa.select(PaymentCollectionRejectionReviewRecord).where(PaymentCollectionRejectionReviewRecord.tenant_id == actor.tenant_id, PaymentCollectionRejectionReviewRecord.case_id == case_id).order_by(PaymentCollectionRejectionReviewRecord.created_at.desc()))
