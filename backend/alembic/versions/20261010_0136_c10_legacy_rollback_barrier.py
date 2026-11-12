"""Block legacy Submission writes for C10 candidates without current qualification.

The transaction-local markers identify current handlers; this is a rollback
compatibility barrier, not a defense against arbitrary SQL using the app role.
"""

from collections.abc import Sequence

from alembic import op

revision = "20261010_0136"
down_revision = "20261009_0135"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.execute(
        """
        CREATE FUNCTION guard_c10_submission_candidate_insert()
        RETURNS trigger
        LANGUAGE plpgsql
        SET search_path = pg_catalog, public, pg_temp
        AS $$
        DECLARE
            schema3 boolean := COALESCE(NEW.manifest_json->>'schema_version' = '3', false);
            has_source boolean := NEW.manifest_json ? 'preparation_source';
            has_plan boolean;
        BEGIN
            SELECT EXISTS (
                SELECT 1 FROM public.preparation_response_plans plan
                WHERE plan.tenant_id = NEW.tenant_id
                  AND plan.package_id = NEW.preparation_package_id
            ) INTO has_plan;
            IF schema3 OR has_source OR has_plan THEN
                IF current_setting('smartao.c10_candidate_qualified', true) IS DISTINCT FROM '1'
                   OR NOT schema3 OR NOT has_source THEN
                    RAISE EXCEPTION 'C10_SUBMISSION_ROLLBACK_BLOCKED';
                END IF;
            END IF;
            RETURN NEW;
        END;
        $$;
        """
    )
    op.execute(
        """
        CREATE TRIGGER c10_submission_candidate_rollback_guard
        BEFORE INSERT ON public.submission_packages
        FOR EACH ROW EXECUTE FUNCTION guard_c10_submission_candidate_insert();
        """
    )
    op.execute(
        """
        CREATE FUNCTION guard_c10_submission_authorization_insert()
        RETURNS trigger
        LANGUAGE plpgsql
        SET search_path = pg_catalog, public, pg_temp
        AS $$
        DECLARE
            is_c10 boolean;
        BEGIN
            SELECT EXISTS (
                SELECT 1 FROM public.submission_packages package
                WHERE package.tenant_id = NEW.tenant_id
                  AND package.id = NEW.submission_package_id
                  AND (
                      package.manifest_json->>'schema_version' = '3'
                      OR package.manifest_json ? 'preparation_source'
                      OR EXISTS (
                          SELECT 1 FROM public.preparation_response_plans plan
                          WHERE plan.tenant_id = package.tenant_id
                            AND plan.package_id = package.preparation_package_id
                      )
                  )
            ) INTO is_c10;
            IF is_c10
               AND current_setting('smartao.c10_p5_qualified', true) IS DISTINCT FROM '1' THEN
                RAISE EXCEPTION 'C10_SUBMISSION_ROLLBACK_BLOCKED';
            END IF;
            RETURN NEW;
        END;
        $$;
        """
    )
    op.execute(
        """
        CREATE TRIGGER c10_submission_authorization_rollback_guard
        BEFORE INSERT ON public.submission_package_authorizations
        FOR EACH ROW EXECUTE FUNCTION guard_c10_submission_authorization_insert();
        """
    )
    op.execute(
        """
        CREATE FUNCTION guard_c10_submission_export_event()
        RETURNS trigger
        LANGUAGE plpgsql
        SET search_path = pg_catalog, public, pg_temp
        AS $$
        DECLARE
            is_c10 boolean;
        BEGIN
            IF NEW.aggregate_type <> 'SubmissionPackage'
               OR NEW.event_type <> 'SubmissionPackageExported' THEN
                RETURN NEW;
            END IF;
            SELECT EXISTS (
                SELECT 1 FROM public.submission_packages package
                WHERE package.tenant_id = NEW.tenant_id
                  AND package.id = NEW.aggregate_id
                  AND (
                      package.manifest_json->>'schema_version' = '3'
                      OR package.manifest_json ? 'preparation_source'
                      OR EXISTS (
                          SELECT 1 FROM public.preparation_response_plans plan
                          WHERE plan.tenant_id = package.tenant_id
                            AND plan.package_id = package.preparation_package_id
                      )
                  )
            ) INTO is_c10;
            IF is_c10
               AND current_setting('smartao.c10_export_qualified', true) IS DISTINCT FROM '1' THEN
                RAISE EXCEPTION 'C10_SUBMISSION_ROLLBACK_BLOCKED';
            END IF;
            RETURN NEW;
        END;
        $$;
        """
    )
    op.execute(
        """
        CREATE TRIGGER c10_submission_export_rollback_guard
        BEFORE INSERT ON public.domain_events
        FOR EACH ROW EXECUTE FUNCTION guard_c10_submission_export_event();
        """
    )


def downgrade() -> None:
    op.execute(
        """
        DO $$
        BEGIN
            IF EXISTS (SELECT 1 FROM public.preparation_response_plans)
               OR EXISTS (
                    SELECT 1 FROM public.submission_packages package
                    WHERE package.manifest_json->>'schema_version' = '3'
                       OR package.manifest_json ? 'preparation_source'
               ) THEN
                RAISE EXCEPTION 'C10_SUBMISSION_ROLLBACK_BARRIER_DOWNGRADE_BLOCKED';
            END IF;
        END;
        $$;
        """
    )
    op.execute(
        "DROP TRIGGER IF EXISTS c10_submission_export_rollback_guard ON public.domain_events"
    )
    op.execute(
        "DROP TRIGGER IF EXISTS c10_submission_authorization_rollback_guard "
        "ON public.submission_package_authorizations"
    )
    op.execute(
        "DROP TRIGGER IF EXISTS c10_submission_candidate_rollback_guard "
        "ON public.submission_packages"
    )
    op.execute("DROP FUNCTION IF EXISTS guard_c10_submission_export_event()")
    op.execute("DROP FUNCTION IF EXISTS guard_c10_submission_authorization_insert()")
    op.execute("DROP FUNCTION IF EXISTS guard_c10_submission_candidate_insert()")
