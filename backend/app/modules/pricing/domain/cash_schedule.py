"""Declared cash, never a legal calendar or a statement of available financing."""

from datetime import date
from typing import Annotated, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator

Amount = Annotated[int, Field(strict=True, ge=0, le=9_000_000_000_000_000)]
SignedAmount = Annotated[
    int, Field(strict=True, ge=-9_000_000_000_000_000, le=9_000_000_000_000_000)
]
Currency = Annotated[str, Field(pattern=r"^[A-Z]{3}$")]
References = Annotated[
    list[Annotated[str, Field(min_length=1, max_length=1000)]], Field(min_length=1, max_length=12)
]


class CashOpening(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True, validate_assignment=True)
    currency_code: Currency
    amount_minor: SignedAmount | None = None
    source_refs: References


class CashFlow(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True, validate_assignment=True)
    flow_id: UUID
    direction: Literal["INFLOW", "OUTFLOW"]
    currency_code: Currency
    amount_minor: Amount | None = None
    declared_date: date | None = None
    source_refs: References
    native_source_id: str | None = Field(default=None, max_length=100)


class CashDeclaration(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    period_start: date
    period_end: date
    status: Literal["ACTIVE", "CANCELLED"] = "ACTIVE"
    assumptions: str = Field(min_length=1, max_length=4000)
    openings: list[CashOpening] = Field(default_factory=list, max_length=8)
    flows: list[CashFlow] = Field(default_factory=list, max_length=120)

    @model_validator(mode="after")
    def coherent(self):
        if self.period_end < self.period_start or (self.period_end - self.period_start).days > 3660:
            raise ValueError("CASH_PERIOD_INVALID")
        if len({o.currency_code for o in self.openings}) != len(self.openings):
            raise ValueError("CASH_OPENING_DUPLICATED")
        if len({f.flow_id for f in self.flows}) != len(self.flows):
            raise ValueError("CASH_FLOW_DUPLICATED")
        currencies = {f.currency_code for f in self.flows} | {
            o.currency_code for o in self.openings
        }
        if len(currencies) > 8:
            raise ValueError("CASH_CURRENCIES_LIMIT")
        for f in self.flows:
            if f.declared_date and not self.period_start <= f.declared_date <= self.period_end:
                raise ValueError("CASH_DATE_OUTSIDE_DECLARED_PERIOD")
        return self


def project_schedule(declaration: CashDeclaration):
    groups = []
    codes = sorted(
        {f.currency_code for f in declaration.flows}
        | {o.currency_code for o in declaration.openings}
    )
    for code in codes:
        opening = next(
            (o.amount_minor for o in declaration.openings if o.currency_code == code), None
        )
        flows = sorted(
            (f for f in declaration.flows if f.currency_code == code),
            key=lambda f: (f.declared_date or date.max, str(f.flow_id)),
        )
        missing = []
        if opening is None:
            missing.append("OPENING_UNKNOWN")
        for f in flows:
            if f.amount_minor is None:
                missing.append(f"AMOUNT_UNKNOWN:{f.flow_id}")
            if f.declared_date is None:
                missing.append(f"DATE_UNKNOWN:{f.flow_id}")
        running = opening if not missing and declaration.status == "ACTIVE" else None
        rows = []
        for f in flows:
            if running is not None and f.amount_minor is not None:
                running += f.amount_minor if f.direction == "INFLOW" else -f.amount_minor
            rows.append(
                {
                    **f.model_dump(mode="json"),
                    "amount_minor": str(f.amount_minor) if f.amount_minor is not None else None,
                    "cumulative_minor": str(running) if running is not None else None,
                }
            )
        groups.append(
            dict(
                currency_code=code,
                opening_minor=str(opening) if opening is not None else None,
                closing_minor=str(running) if running is not None else None,
                missing=missing,
                rows=rows,
            )
        )
    return dict(
        currencies=groups,
        scope_state="PARTIAL",
        settlement_state="UNKNOWN",
        funding_peak_state="UNKNOWN",
        legal_effect_state="UNKNOWN",
        status=declaration.status,
    )
