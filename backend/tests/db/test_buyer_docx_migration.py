"""No binary artifact can be silently reinterpreted as historical Markdown."""

from uuid import uuid4

import pytest
import sqlalchemy as sa
from alembic import command
from alembic.config import Config
from app.modules.preparation.infrastructure.models import (
    GeneratedTechnicalDocumentRecord,
    TechnicalResponseDraftRecord,
)
from tests.db.test_response_contributions_workflow import response_case  # noqa: F401
from tests.support.database import ALEMBIC_INI, DATABASE_URL


def test_format_columns_upgrade_and_empty_downgrade_are_reversible(database_engine):
    config = Config(str(ALEMBIC_INI))
    config.set_main_option("sqlalchemy.url", DATABASE_URL)
    for name in ["generated_technical_documents", "technical_response_drafts"]:
        column = next(
            c
            for c in sa.inspect(database_engine).get_columns(name)
            if c["name"] == "content_format"
        )
        assert not column["nullable"] and "MARKDOWN" in column["default"]
    command.downgrade(config, "20261025_0145")
    assert "content_format" not in {
        c["name"] for c in sa.inspect(database_engine).get_columns("technical_response_drafts")
    }
    command.upgrade(config, "head")


def test_docx_requires_provenance_and_blocks_lossy_rollback(session_factory, request):
    w = request.getfixturevalue("response_case")

    def draft(provenance):
        return TechnicalResponseDraftRecord(
            id=uuid4(),
            tenant_id=w.actor.tenant_id,
            package_id=w.package_id,
            draft_id=uuid4(),
            source_document_id=w.generated_document_id,
            version=1,
            state="DRAFT",
            section_codes_json=["METHOD"],
            source_refs_json=[str(w.source.id)],
            responsible_role="COLLABORATEUR",
            content_sha256="a" * 64,
            storage_key="synthetic/docx",
            actor_id=w.actor.actor_id,
            membership_id=w.actor.membership_id,
            command_id=uuid4(),
            idempotency_key=uuid4(),
            content_format="DOCX",
            content_provenance_json=provenance,
        )

    with session_factory() as s:
        assert (
            s.get(GeneratedTechnicalDocumentRecord, w.generated_document_id).content_format
            == "MARKDOWN"
        )
        with pytest.raises(sa.exc.DBAPIError):
            s.add(draft(None))
            s.flush()
        s.rollback()
    with session_factory.begin() as s:
        s.add(draft({"schema_version": 1}))
    config = Config(str(ALEMBIC_INI))
    config.set_main_option("sqlalchemy.url", DATABASE_URL)
    with pytest.raises(RuntimeError, match="BUYER_DOCX_PROOF_LOSS_REFUSED"):
        command.downgrade(config, "20261025_0145")
