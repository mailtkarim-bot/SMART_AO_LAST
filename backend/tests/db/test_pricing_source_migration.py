"""Nullable expansion preserves history; downgrade cannot discard source evidence."""

import pytest
import sqlalchemy as sa
from alembic import command
from alembic.config import Config
from app.modules.pricing.application.import_commands import CreatePricingImportRowCommand
from app.modules.pricing.infrastructure.models import PricingImportRowRecord
from app.platform.persistence.schema import EXPECTED_ALEMBIC_HEAD
from tests.application.test_financial_report_draft_lines import NOW, _seed_draft
from tests.application.test_pricing_import_creation import _command, _service
from tests.support.database import ALEMBIC_INI, DATABASE_URL


def config():
    value = Config(str(ALEMBIC_INI))
    value.set_main_option("sqlalchemy.url", DATABASE_URL)
    return value


def test_migration_preserves_legacy_rows_without_inventing_sources(session_factory):
    actor, case, _, _ = _seed_draft(session_factory)
    _service(session_factory).create(actor=actor, command=_command(case), now=NOW)
    with session_factory() as s:
        before = list(
            s.execute(sa.select(PricingImportRowRecord.id, PricingImportRowRecord.total_minor))
        )
    command.downgrade(config(), "20261021_0139")
    command.upgrade(config(), "head")
    with session_factory() as s:
        after = list(
            s.execute(sa.select(PricingImportRowRecord.id, PricingImportRowRecord.total_minor))
        )
        assert after == before
        assert all(
            x is None for x in s.scalars(sa.select(PricingImportRowRecord.source_locator_json))
        )


def test_populated_downgrade_refuses_source_loss(session_factory):
    actor, case, _, _ = _seed_draft(session_factory)
    row = CreatePricingImportRowCommand(
        row_number=2,
        designation="Poste",
        quantity_decimal="1",
        total_minor=100,
        source_locator={"sheet": "Lot 1", "row": 2, "cells": {"designation": "B2"}},
    )
    _service(session_factory).create(actor=actor, command=_command(case, rows=[row]), now=NOW)
    with pytest.raises(RuntimeError, match="PRICING_IMPORT_SOURCE_PROOF_LOSS_REFUSED"):
        command.downgrade(config(), "20261021_0139")
    with session_factory() as s:
        assert s.scalar(sa.text("select version_num from alembic_version")) == EXPECTED_ALEMBIC_HEAD
        assert (
            s.scalar(
                sa.select(PricingImportRowRecord.source_locator_json).where(
                    PricingImportRowRecord.tenant_id == actor.tenant_id
                )
            )
            == row.source_locator.model_dump()
        )
