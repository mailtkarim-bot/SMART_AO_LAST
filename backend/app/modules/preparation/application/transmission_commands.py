from uuid import UUID

from pydantic import Field, SerializerFunctionWrapHandler, model_serializer, model_validator

from app.modules.preparation.public.contracts import (
    SelectedResponseAnnex,
    SelectedResponseDraft,
    validate_annex_selection,
)
from app.platform.events.command_contracts import ApplicationCommand


class CreatePreparationSnapshotCommand(ApplicationCommand):
    """Freeze the current non-financial preparation facts for patron review."""

    command_type = "CreatePreparationSnapshot"

    package_id: UUID
    snapshot_id: UUID
    expected_package_revision: int = Field(ge=0)
    selected_response_draft: SelectedResponseDraft | None = None
    selected_annexes: list[SelectedResponseAnnex] = Field(default_factory=list, max_length=64)
    annex_justification: str | None = Field(default=None, min_length=1, max_length=2000)

    @model_validator(mode="after")
    def exact_annex_selection(self):
        validate_annex_selection(
            self.selected_response_draft, self.selected_annexes, self.annex_justification
        )
        return self

    @model_serializer(mode="wrap")
    def preserve_legacy_intent_hash(self, handler: SerializerFunctionWrapHandler) -> dict:
        serialized = handler(self)
        if self.selected_response_draft is None:
            serialized.pop("selected_response_draft", None)
        if not self.selected_annexes:
            serialized.pop("selected_annexes", None)
        if self.annex_justification is None:
            serialized.pop("annex_justification", None)
        return serialized


class TransmitPreparationSnapshotCommand(ApplicationCommand):
    """Transmit one immutable preparation snapshot to the patron."""

    command_type = "TransmitPreparationSnapshot"

    package_id: UUID
    snapshot_id: UUID
    transmission_id: UUID
    expected_package_revision: int = Field(ge=0)
