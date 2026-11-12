"""Closed organisation of current source signals, never a completeness verdict."""

from __future__ import annotations

from dataclasses import asdict
from uuid import UUID

AXES = (
    ("COMMERCIAL", "Intérêt commercial"),
    ("CANDIDATURE", "Candidature"),
    ("TECHNICAL", "Périmètre technique"),
    ("CONSTRUCTIBILITY", "Constructibilité et logistique"),
    ("CONTRACT", "Contrat"),
    ("PRICE", "Prix et marge"),
    ("CASH", "Trésorerie et garanties"),
    ("CAPACITY", "Capacité et ressources"),
    ("PARTNERS", "Partenaires"),
    ("HSE", "HSE, environnement et réglementation"),
    ("DOCUMENTS", "Documents et engagements de l’offre"),
    ("RIGHTS", "Droits, réception et sortie"),
)
_REQUIREMENT_AXIS = {
    "CANDIDATURE_DOCUMENT": "CANDIDATURE",
    "SITE_VISIT": "CANDIDATURE",
    "AWARD_CRITERION_SIGNAL": "COMMERCIAL",
    "NEGOTIATION_SIGNAL": "COMMERCIAL",
    "OFFER_DOCUMENT": "DOCUMENTS",
    "SUBMISSION_DEADLINE_SIGNAL": "DOCUMENTS",
    "SUBMISSION_CHANNEL": "DOCUMENTS",
    "FILE_CONSTRAINT": "DOCUMENTS",
    "OFFER_VALIDITY_SIGNAL": "DOCUMENTS",
    "CONTRACT_RISK_SIGNAL": "CONTRACT",
    "TECHNICAL_PRESCRIPTION": "TECHNICAL",
    "LOGISTICS_CONSTRAINT": "CONSTRUCTIBILITY",
    "SCHEDULE_CONSTRAINT": "CAPACITY",
    "HSE_CONSTRAINT": "HSE",
    "PAYMENT_TERM_SIGNAL": "CASH",
    "ACCEPTANCE_TERM_SIGNAL": "RIGHTS",
}


def exact_source_excerpt(text: str, start: int | None, end: int | None) -> str | None:
    raw = text.encode("utf-8")
    if start is None or end is None or not 0 <= start < end <= len(raw) or end - start > 8000:
        return None
    try:
        return raw[start:end].decode("utf-8")
    except UnicodeDecodeError:
        return None


def build_analysis_summary(
    *,
    case_id: UUID,
    dce_version_id: UUID,
    case_scope_kind: str,
    requirements,
    risks,
    coverage,
    truncated: bool,
    source_context_state: str = "UNKNOWN",
):
    axes = []
    for code, label in AXES:
        items = []
        for item in (*requirements, *risks):
            target = (
                _REQUIREMENT_AXIS.get(item["native_type"])
                if item["kind"] == "REQUIREMENT"
                else {"CCAP": "CONTRACT", "CCTP": "TECHNICAL"}.get(item["native_type"])
            )
            assessment = item.get("human_assessment")
            if assessment and assessment["state"] == "CURRENT" and assessment.get("treatment"):
                target = assessment["treatment"]["axis_code"]
            if target == code:
                items.append(
                    dict(
                        item,
                        applicability="UNKNOWN",
                        expected_evidence="UNKNOWN",
                        residual_risk="UNKNOWN",
                        responsible=None,
                        action=None,
                        consequences="UNKNOWN",
                        follow_ups=item.get("follow_ups", [])[:300]
                        if source_context_state == "CURRENT"
                        and item.get("source_state") == "CURRENT_SOURCE"
                        else [],
                        follow_up_state="RECORDED"
                        if source_context_state == "CURRENT"
                        and item.get("source_state") == "CURRENT_SOURCE"
                        and item.get("follow_ups")
                        else "UNKNOWN",
                    )
                )
        axes.append(
            dict(
                code=code,
                label=label,
                status="REVIEW_REQUIRED" if items else "NON_EVALUATED",
                mapping_basis="NATIVE_REGISTER_TYPE_ONLY",
                items=items,
            )
        )
    return dict(
        case_id=case_id,
        dce_version_id=dce_version_id,
        case_scope_kind=case_scope_kind,
        status="REVIEW_REQUIRED",
        analysis_complete=False,
        coverage_scope="CURRENT_DCE_ONLY",
        truncated=truncated
        or any(len(i.get("follow_ups", [])) > 300 for i in (*requirements, *risks)),
        source_context_state=source_context_state,
        axes=axes,
        coverage=asdict(coverage) if coverage is not None else None,
    )


def project_analysis_pricing(scenarios, *, case_id: UUID, source_context_state: str):
    """Expose recorded economics only; no DCE or lot applicability is inferred."""
    result = []
    for scenario in scenarios:
        if scenario.case_id != case_id:
            continue
        reason = (
            "DCE_CONTEXT_UNPROVEN"
            if source_context_state != "CURRENT"
            else "SCENARIO_ARCHIVED"
            if scenario.state == "ARCHIVED"
            else scenario.source_basis_reason or "SOURCE_UNPROVEN"
            if scenario.source_basis_state != "DECLARED_COMPLETE"
            or scenario.source_snapshot_id is None
            else None
        )
        result.append(
            dict(
                scenario_id=scenario.scenario_id,
                revision=scenario.version,
                state="UNKNOWN" if reason else "RECORDED",
                unknown_reason=reason,
                dce_applicability="UNKNOWN",
                details=None if reason else asdict(scenario),
            )
        )
    return result


def project_analysis_cash(reports, *, case_id: UUID, source_context_state: str):
    """A recorded balance is neither a dated cash schedule nor a funding peak."""
    result = []
    for report in reports:
        if report.case_id != case_id:
            continue
        lines = [line for line in report.lines if line.category == "FORECAST_CASHFLOW"]
        reason = None
        if source_context_state != "CURRENT":
            reason = "DCE_CONTEXT_UNPROVEN"
        elif report.status != "PUBLISHED":
            reason = "REPORT_NOT_PUBLISHED"
        elif not lines:
            reason = "CASH_DECLARATION_MISSING"
        elif sum(line.amount_minor for line in lines) != report.summary.get(
            "forecast_cashflow_minor"
        ):
            reason = "CASH_DECLARATION_MISMATCH"
        result.append(
            dict(
                report_id=report.report_id,
                revision=report.aggregate_revision,
                state="UNKNOWN" if reason else "DECLARED",
                unknown_reason=reason,
                schedule_state="UNKNOWN",
                funding_peak_state="UNKNOWN",
                scope_state="UNKNOWN",
                details=None
                if reason
                else dict(
                    case_id=report.case_id,
                    currency_code=report.currency_code,
                    calculated_at=report.calculated_at,
                    ruleset_version=report.ruleset_version,
                    forecast_cashflow_minor=report.summary["forecast_cashflow_minor"],
                    lines=[
                        dict(line_id=line.line_id, label=line.label, amount_minor=line.amount_minor)
                        for line in lines
                    ],
                ),
            )
        )
    return result


def project_analysis_capacity(reading, *, case_id: UUID, source_context_state: str):
    """Recorded advisory inputs are never a reservation or proof of lot coverage."""
    if reading["case_id"] != str(case_id):
        return []
    current = reading["current"]
    records = ([current] if current else []) + reading["history"]
    result = []
    for record in records:
        reason = (
            "DCE_CONTEXT_UNPROVEN"
            if source_context_state != "CURRENT"
            else "CAPACITY_CONTEXT_OR_INTEGRITY_UNPROVEN"
            if current is None
            else "HISTORICAL_CALCULATION"
            if record["state"] != "CURRENT"
            else None
        )
        result.append(
            dict(
                run_id=record["run_id"],
                revision=record["revision"],
                input_sha256=record["input_sha256"],
                state="REVIEW_REQUIRED" if reason else "RECORDED",
                unknown_reason=reason,
                lot_state="UNKNOWN",
                dce_applicability="UNKNOWN",
                details=None
                if reason
                else dict(
                    case_id=str(case_id),
                    status=record["status"],
                    inputs=record["inputs"],
                    result=record["result"],
                    reservation_state="NOT_RESERVED",
                    coverage_state="UNKNOWN",
                ),
            )
        )
    return result
