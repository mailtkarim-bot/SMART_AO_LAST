from datetime import date
from uuid import uuid4

import pytest
from app.modules.pricing.domain.contract_execution_evidence import (
    ContractExecutionActKind,
    ContractReceptionOutcome,
    build_contract_execution_evidence,
)
from app.modules.pricing.domain.contract_instrument_version import (
    ContractInstrumentKind,
    build_contract_instrument_version,
)


def test_preserves_declared_act_sources_proofs_and_event_date_without_deriving_deadline() -> None:
    event = build_contract_execution_evidence(
        case_id=uuid4(),
        act_kind=ContractExecutionActKind.RIGHTS_PRESERVATION,
        summary="Réserve transmise par courrier recommandé",
        source_refs=("ccap://clause/14", "ccap://version/2"),
        evidence_refs=("document://courrier/sha256:abc", "document://accuse/sha256:def"),
        declared_event_date=date(2026, 9, 28),
    )

    assert event.declared_event_date == date(2026, 9, 28)
    assert event.source_refs == ("ccap://clause/14", "ccap://version/2")
    assert event.evidence_refs == ("document://courrier/sha256:abc", "document://accuse/sha256:def")
    assert not hasattr(event, "legal_conclusion")
    assert not hasattr(event, "calculated_deadline")


@pytest.mark.parametrize(
    ("field", "value", "error"),
    [
        ("summary", "  ", "CONTRACT_EXECUTION_SUMMARY_REQUIRED"),
        ("source_refs", (), "CONTRACT_EXECUTION_SOURCE_REQUIRED"),
        ("source_refs", ("  ",), "CONTRACT_EXECUTION_SOURCE_REQUIRED"),
        ("source_refs", ("s" * 1001,), "CONTRACT_EXECUTION_SOURCE_REQUIRED"),
        ("evidence_refs", (), "CONTRACT_EXECUTION_EVIDENCE_REQUIRED"),
        ("evidence_refs", ("  ",), "CONTRACT_EXECUTION_EVIDENCE_REQUIRED"),
        ("evidence_refs", ("e" * 1001,), "CONTRACT_EXECUTION_EVIDENCE_REQUIRED"),
    ],
)
def test_rejects_an_act_without_its_declared_summary_source_or_proof(field, value, error) -> None:
    values = {
        "case_id": uuid4(),
        "act_kind": ContractExecutionActKind.WORK_RECEPTION,
        "summary": "PV de réception transmis",
        "source_refs": ("ccap://clause/24",),
        "evidence_refs": ("document://pv/sha256:abc",),
        "declared_event_date": None,
    }
    values[field] = value

    with pytest.raises(ValueError, match=error):
        build_contract_execution_evidence(**values)


def test_only_closed_human_declared_act_categories_are_accepted() -> None:
    with pytest.raises(ValueError):
        ContractExecutionActKind("AUTOMATIC_FORCLUSION")


@pytest.mark.parametrize("outcome", list(ContractReceptionOutcome))
def test_work_reception_preserves_explicit_reception_outcome(outcome) -> None:
    receipt = build_contract_execution_evidence(
        case_id=uuid4(),
        act_kind=ContractExecutionActKind.WORK_RECEPTION,
        reception_outcome=outcome,
        summary="PV déclaré par le Patron",
        source_refs=("ccap://clause/24",),
        evidence_refs=("document://pv",),
    )
    assert receipt.reception_outcome is outcome


def test_non_reception_act_cannot_carry_a_reception_outcome() -> None:
    with pytest.raises(ValueError, match="CONTRACT_RECEPTION_OUTCOME_NOT_APPLICABLE"):
        build_contract_execution_evidence(
            case_id=uuid4(),
            act_kind=ContractExecutionActKind.RIGHTS_PRESERVATION,
            reception_outcome=ContractReceptionOutcome.WITH_RESERVATIONS,
            summary="Courrier de réserve",
            source_refs=("ccap://clause/24",),
            evidence_refs=("document://courrier",),
        )


def test_contract_instrument_version_is_a_sourced_human_declared_record() -> None:
    instrument = build_contract_instrument_version(
        case_id=uuid4(),
        instrument_kind=ContractInstrumentKind.SIGNED_CONTRACT,
        version_reference="MARCHE-SIGNE-2026-04-12",
        source_refs=("contract://document/1",),
        evidence_refs=("document://signed-contract/sha256:abc",),
    )

    assert instrument.instrument_kind is ContractInstrumentKind.SIGNED_CONTRACT
    assert instrument.version_reference == "MARCHE-SIGNE-2026-04-12"
    assert instrument.source_refs == ("contract://document/1",)
    assert instrument.evidence_refs == ("document://signed-contract/sha256:abc",)


@pytest.mark.parametrize(
    "reference",
    ["", "   ", "v" * 501],
)
def test_contract_instrument_version_reference_is_bounded(reference) -> None:
    with pytest.raises(ValueError, match="CONTRACT_INSTRUMENT_REFERENCE_REQUIRED"):
        build_contract_instrument_version(
            case_id=uuid4(),
            instrument_kind=ContractInstrumentKind.AMENDMENT,
            version_reference=reference,
            source_refs=("contract://document/1",),
            evidence_refs=("document://contract/sha256:abc",),
        )


@pytest.mark.parametrize(
    ("sources", "proofs", "error"),
    [
        ((), ("document://contract",), "CONTRACT_INSTRUMENT_SOURCE_REQUIRED"),
        (("contract://document",), (), "CONTRACT_INSTRUMENT_PROOF_REQUIRED"),
    ],
)
def test_contract_instrument_version_requires_source_and_proof(sources, proofs, error) -> None:
    with pytest.raises(ValueError, match=error):
        build_contract_instrument_version(
            case_id=uuid4(),
            instrument_kind=ContractInstrumentKind.SIGNED_CONTRACT,
            version_reference="MARCHE-1",
            source_refs=sources,
            evidence_refs=proofs,
        )
