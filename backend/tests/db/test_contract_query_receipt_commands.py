from uuid import uuid4

import pytest
import sqlalchemy as sa
from sqlalchemy.orm import Session

from app.modules.dce.infrastructure.models.contract_query_receipt import ContractQueryReceiptRecord
from app.platform.persistence.models import TenantRecord
from tests.db.test_regulatory_profile_persistence import _case


def test_query_receipt_duplicate_identity_is_rejected(database_engine: sa.Engine) -> None:
    tenant_id, case_id, receipt_id = uuid4(), uuid4(), uuid4()
    with Session(database_engine) as session:
        session.add(TenantRecord(id=tenant_id, slug=f"receipt-{tenant_id.hex[:12]}", lifecycle="ACTIVE"))
        session.flush()
        session.add(_case(tenant_id=tenant_id, case_id=case_id, marker="q"))
        session.add(ContractQueryReceiptRecord(id=receipt_id, tenant_id=tenant_id, case_id=case_id, filters_json={}, order_key="revision_created_at", limit_value=50, offset_value=0, actor_id=uuid4()))
        session.commit()
        session.add(ContractQueryReceiptRecord(id=receipt_id, tenant_id=tenant_id, case_id=case_id, filters_json={}, order_key="revision_created_at", limit_value=50, offset_value=0, actor_id=uuid4()))
        with pytest.raises(sa.exc.IntegrityError):
            session.commit()
