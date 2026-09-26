from uuid import uuid4
import pytest
from app.modules.dce.domain.human_resumption_act import HumanResumptionAct, HumanResumptionState

def test_resumption_act_is_explicit() -> None:
    HumanResumptionAct(uuid4(), uuid4(), HumanResumptionState.ACKNOWLEDGED, "Relève vérifiée").validate()

def test_resumption_act_requires_rationale() -> None:
    with pytest.raises(ValueError, match="RESUMPTION_RATIONALE_REQUIRED"):
        HumanResumptionAct(uuid4(), uuid4(), HumanResumptionState.BLOCKED, "").validate()
