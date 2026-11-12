"""Source-bound point treatments and human dossier preparation/review."""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "20261020_0138"
down_revision = "20261020_0137"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "case_analysis_assessments", sa.Column("treatment_json", postgresql.JSONB(), nullable=True)
    )
    op.execute(
        "ALTER TABLE case_analysis_assessments ADD CONSTRAINT ck_analysis_treatment_object "
        "CHECK (treatment_json IS NULL OR jsonb_typeof(treatment_json)='object')"
    )
    op.execute(
        "CREATE TABLE case_analysis_dossier_reviews (\n        tenant_"
        "id uuid NOT NULL, id uuid NOT NULL, case_id uuid NOT NULL, d"
        "ce_version_id uuid NOT NULL,\n        revision integer NOT NU"
        "LL, previous_id uuid, dossier_sha256 char(64) NOT NULL,\n    "
        "    phase varchar(16) NOT NULL, axes_json jsonb NOT NULL, sn"
        "apshot_json jsonb NOT NULL, justification text NOT NULL,\n   "
        "     actor_id uuid NOT NULL, membership_id uuid NOT NULL, co"
        "mmand_id uuid NOT NULL, idempotency_key uuid NOT NULL,\n     "
        "   created_at timestamptz NOT NULL DEFAULT now(), updated_at"
        " timestamptz NOT NULL DEFAULT now(),\n        PRIMARY KEY(ten"
        "ant_id,id), FOREIGN KEY(tenant_id,case_id) REFERENCES cases("
        "tenant_id,id),\n        FOREIGN KEY(tenant_id,dce_version_id)"
        " REFERENCES dce_versions(tenant_id,id),\n        FOREIGN KEY("
        "tenant_id,previous_id) REFERENCES case_analysis_dossier_revi"
        "ews(tenant_id,id),\n        UNIQUE(tenant_id,case_id,revision"
        "), UNIQUE(tenant_id,command_id), UNIQUE(tenant_id,idempotenc"
        "y_key),\n        CHECK(jsonb_typeof(snapshot_json)='object'),"
        " CHECK(phase IN ('PREPARED','REVIEWED')), CHECK(dossier_sha2"
        "56 ~ '^[0-9a-f]{64}$'),\n        CHECK(jsonb_typeof(axes_json"
        ")='array' AND jsonb_array_length(axes_json)=12),\n        CHE"
        "CK((revision=1 AND previous_id IS NULL) OR (revision>1 AND p"
        "revious_id IS NOT NULL)),\n        CHECK(length(btrim(justifi"
        "cation)) BETWEEN 1 AND 2000))"
    )
    op.execute(
        "CREATE FUNCTION guard_analysis_dossier_review() RETURNS trig"
        "ger LANGUAGE plpgsql AS $$\n    BEGIN\n        IF TG_OP <> 'IN"
        "SERT' THEN RAISE EXCEPTION 'ANALYSIS_DOSSIER_APPEND_ONLY'; E"
        "ND IF;\n        IF NOT EXISTS(SELECT 1 FROM cases WHERE tenan"
        "t_id=NEW.tenant_id AND id=NEW.case_id AND applicable_dce_ver"
        "sion_id=NEW.dce_version_id) THEN\n            RAISE EXCEPTION"
        " 'ANALYSIS_DOSSIER_STALE_VERSION'; END IF;\n        IF NEW.pr"
        "evious_id IS NOT NULL AND NOT EXISTS(SELECT 1 FROM case_anal"
        "ysis_dossier_reviews p\n            WHERE p.tenant_id=NEW.ten"
        "ant_id AND p.case_id=NEW.case_id AND p.id=NEW.previous_id AN"
        "D p.revision=NEW.revision-1) THEN\n            RAISE EXCEPTIO"
        "N 'ANALYSIS_DOSSIER_PREDECESSOR'; END IF;\n        IF (SELECT"
        " count(DISTINCT a->>'code') FROM jsonb_array_elements(NEW.ax"
        "es_json) a\n            WHERE a->>'code' IN ('COMMERCIAL','CA"
        "NDIDATURE','TECHNICAL','CONSTRUCTIBILITY','CONTRACT','PRICE'"
        ",'CASH','CAPACITY','PARTNERS','HSE','DOCUMENTS','RIGHTS')) <"
        "> 12 THEN\n            RAISE EXCEPTION 'ANALYSIS_DOSSIER_AXES"
        "'; END IF;\n        IF NEW.phase='REVIEWED' AND NOT EXISTS(SE"
        "LECT 1 FROM case_analysis_dossier_reviews p\n            WHER"
        "E p.tenant_id=NEW.tenant_id AND p.case_id=NEW.case_id AND p."
        "id=NEW.previous_id\n            AND p.phase='PREPARED' AND p."
        "dossier_sha256=NEW.dossier_sha256 AND p.axes_json=NEW.axes_j"
        "son) THEN\n            RAISE EXCEPTION 'ANALYSIS_DOSSIER_PHAS"
        "E'; END IF;\n        RETURN NEW;\n    END $$"
    )
    op.create_index(
        "ix_case_analysis_dossier_reviews_tenant_id", "case_analysis_dossier_reviews", ["tenant_id"]
    )
    op.execute(
        "CREATE TRIGGER analysis_dossier_guard BEFORE INSERT OR UPDATE OR DELETE "
        "ON case_analysis_dossier_reviews FOR EACH ROW "
        "EXECUTE FUNCTION guard_analysis_dossier_review()"
    )


def downgrade():
    op.execute(
        "DO $$ BEGIN IF EXISTS(SELECT 1 FROM case_analysis_dossier_reviews) OR EXISTS(\n"
        "        SELECT 1 FROM case_analysis_assessments WHERE treatment_json IS NOT NU"
        "LL) THEN\n        RAISE EXCEPTION 'ANALYSIS_DOSSIER_PRESENT_DOWNGRADE_FORBIDDEN"
        "'; END IF; END $$"
    )
    op.drop_table("case_analysis_dossier_reviews")
    op.execute("DROP FUNCTION guard_analysis_dossier_review()")
    op.execute("ALTER TABLE case_analysis_assessments DROP CONSTRAINT ck_analysis_treatment_object")
    op.drop_column("case_analysis_assessments", "treatment_json")
