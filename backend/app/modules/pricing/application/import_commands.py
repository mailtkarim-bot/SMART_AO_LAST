from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.platform.events.command_contracts import ApplicationCommand


class PricingImportSourceLocator(BaseModel):
    model_config = ConfigDict(extra="forbid")
    sheet: str = Field(min_length=1, max_length=31)
    row: int = Field(ge=1, le=1048576, strict=True)
    cells: dict[
        Literal["code", "designation", "unit", "quantity", "unit_price", "total_price"], str
    ] = Field(min_length=1, max_length=6)

    @model_validator(mode="after")
    def exact_row(self):
        import re

        if any(
            re.fullmatch(r"[A-Z]{1,3}" + str(self.row), value) is None
            for value in self.cells.values()
        ):
            raise ValueError("IMPORT_SOURCE_CELL_INVALID")
        return self


class CreatePricingImportRowCommand(BaseModel):
    """One normalized row produced by the server-side preview validator."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    row_number: int = Field(ge=1)
    code: str | None = None
    designation: str | None = None
    unit: str | None = None
    quantity_decimal: str | None = Field(
        default=None,
        pattern=r"^(0|[1-9][0-9]*)(\.[0-9]+)?$",
    )
    unit_price_minor: int | None = Field(default=None, ge=0)
    total_minor: int | None = Field(default=None, ge=0)
    errors: list[str] = Field(default_factory=list)
    source_locator: PricingImportSourceLocator | None = Field(
        default=None, exclude_if=lambda value: value is None
    )


class CreatePricingImportPreviewCommand(ApplicationCommand):
    """Persist a validated, normalized pricing preview without the source file."""

    command_type = "CreatePricingImportPreview"

    case_id: UUID
    document_kind: Literal["DPGF", "BPU", "EXCEL"]
    source_sha256: str = Field(pattern=r"^[a-f0-9]{64}$")
    rows: list[CreatePricingImportRowCommand] = Field(max_length=10_000)


class CommitPricingImportCommand(ApplicationCommand):
    """Apply one validated normalized import batch to a financial draft."""

    command_type = "CommitPricingImport"

    batch_id: UUID
    case_id: UUID
    report_id: UUID
    expected_batch_revision: int = Field(gt=0)
    expected_report_revision: int = Field(ge=0)
