"""Exercise the migrated C10 target CHECK, including PostgreSQL NULL semantics."""

from uuid import uuid4

import pytest
import sqlalchemy as sa


@pytest.mark.parametrize("table", ["preparation_reviews", "preparation_review_corrections"])
def test_migrated_review_target_requires_all_or_none(database_engine, table: str) -> None:
    with database_engine.connect() as connection, connection.begin():
        definition = connection.scalar(
            sa.text(
                "SELECT pg_get_constraintdef(oid) FROM pg_constraint "
                "WHERE contype = 'c' AND pg_get_constraintdef(oid) LIKE '%target_draft_id%' "
                "AND conrelid = to_regclass(:table)"
            ),
            {"table": table},
        )
        assert definition is not None
        # Reuse the actual migrated CHECK without unrelated parents/FKs or business writes.
        connection.exec_driver_sql(
            "CREATE TEMP TABLE c10_target_probe (target_draft_id uuid, "
            "target_draft_version integer, target_content_sha256 char(64), "
            f"{definition}) ON COMMIT DROP"
        )
        insert = sa.text("INSERT INTO c10_target_probe VALUES (:id, :version, :hash)")
        target_id = uuid4()
        for values in ((None, None, None), (target_id, 1, "a" * 64)):
            connection.execute(insert, dict(zip(("id", "version", "hash"), values, strict=True)))
        for invalid_values in (
            (target_id, 1, None),
            (target_id, None, None),
            (None, 1, None),
            (None, None, "a" * 64),
            (None, 1, "a" * 64),
            (target_id, None, "a" * 64),
            (target_id, 1, "invalid"),
        ):
            with pytest.raises(sa.exc.IntegrityError), connection.begin_nested():
                connection.execute(
                    insert, dict(zip(("id", "version", "hash"), invalid_values, strict=True))
                )
