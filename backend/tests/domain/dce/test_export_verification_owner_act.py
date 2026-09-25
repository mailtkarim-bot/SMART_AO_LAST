from uuid import uuid4
import pytest
from app.modules.dce.domain.export_verification_owner_act import ExportVerificationOwnerAct

def test_owner_act_is_explicit_and_separate() -> None:
    act = ExportVerificationOwnerAct(uuid4(), uuid4(), True, "Sens des états approuvé")
    act.validate()

def test_owner_act_requires_rationale() -> None:
    with pytest.raises(ValueError, match="OWNER_RATIONALE_REQUIRED"):
        ExportVerificationOwnerAct(uuid4(), uuid4(), True, "").validate()
