"""Append immutable source-bound L04 human assessments."""

import sqlalchemy as sa
from alembic import op

revision = "20261020_0137"
down_revision = "20261010_0136"
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        "CREATE TABLE case_analysis_assessments (\n tenant_id UUID NOT NULL,\n "
        "created_at timestamptz NOT NULL DEFAULT now(),\n updated_at timestamptz"
        " NOT NULL DEFAULT now(),\n id UUID NOT NULL,\n case_id UUID NOT NULL,\n "
        "point_kind VARCHAR(16) NOT NULL,\n point_id UUID NOT NULL,\n risk_id "
        "UUID,\n requirement_id UUID,\n dce_version_id UUID NOT NULL,\n "
        "source_fragment_id UUID NOT NULL,\n scope_fingerprint CHAR(64) NOT "
        "NULL,\n native_revision INTEGER NOT NULL,\n source_context_sha256 "
        "CHAR(64) NOT NULL,\n source_manifest_json JSONB NOT NULL,\n revision "
        "INTEGER NOT NULL,\n previous_assessment_id UUID,\n "
        "expected_evidence_state VARCHAR(16) NOT NULL,\n expected_evidence TEXT,"
        "\n residual_risk_state VARCHAR(16) NOT NULL,\n residual_risk TEXT,\n "
        "unknown_reason TEXT,\n justification TEXT NOT NULL,\n actor_id UUID NOT "
        "NULL,\n membership_id UUID NOT NULL,\n command_id UUID NOT NULL,\n "
        "idempotency_key UUID NOT NULL,\n correlation_id UUID,\n CONSTRAINT "
        "fk_analysis_assessments_0 FOREIGN KEY (tenant_id) REFERENCES tenants "
        "(id) ON DELETE RESTRICT,\n CONSTRAINT fk_analysis_assessments_1 FOREIGN"
        " KEY (tenant_id,case_id) REFERENCES cases (tenant_id,id) ON DELETE "
        "RESTRICT,\n CONSTRAINT fk_analysis_assessments_2 FOREIGN KEY "
        "(tenant_id,risk_id) REFERENCES decision_risks (tenant_id,id) ON DELETE"
        " RESTRICT,\n CONSTRAINT fk_analysis_assessments_3 FOREIGN KEY "
        "(tenant_id,requirement_id) REFERENCES dce_requirements (tenant_id,id) "
        "ON DELETE RESTRICT,\n CONSTRAINT fk_analysis_assessments_4 FOREIGN KEY "
        "(tenant_id,dce_version_id) REFERENCES dce_versions (tenant_id,id) ON "
        "DELETE RESTRICT,\n CONSTRAINT fk_analysis_assessments_5 FOREIGN KEY "
        "(tenant_id,source_fragment_id) REFERENCES "
        "dce_document_extraction_fragments (tenant_id,id) ON DELETE RESTRICT,\n "
        "CONSTRAINT fk_analysis_assessments_6 FOREIGN KEY "
        "(tenant_id,previous_assessment_id) REFERENCES "
        "case_analysis_assessments (tenant_id,id) ON DELETE RESTRICT,\n "
        "CONSTRAINT pk_case_analysis_assessments PRIMARY KEY (tenant_id,id),\n "
        "CONSTRAINT uq_analysis_assessments_1 UNIQUE "
        "(tenant_id,case_id,point_kind,point_id,revision),\n CONSTRAINT "
        "uq_analysis_assessments_2 UNIQUE (tenant_id,command_id),\n CONSTRAINT "
        "uq_analysis_assessments_3 UNIQUE (tenant_id,idempotency_key),\n "
        "CONSTRAINT ck_case_analysis_assessments__analysis_point_identity CHECK"
        " ((point_kind='RISK' AND risk_id IS NOT NULL AND risk_id=point_id AND "
        "requirement_id IS NULL) OR (point_kind='REQUIREMENT' AND "
        "requirement_id IS NOT NULL AND requirement_id=point_id AND risk_id IS "
        "NULL)),\n CONSTRAINT ck_case_analysis_assessments__analysis_revisions "
        "CHECK (native_revision>=0 AND ((revision=1 AND previous_assessment_id "
        "IS NULL) OR (revision>1 AND previous_assessment_id IS NOT NULL))),\n "
        "CONSTRAINT ck_case_analysis_assessments__analysis_source_hash CHECK "
        "(source_context_sha256 ~ '^[0-9a-f]{64}$' AND scope_fingerprint ~ "
        "'^[0-9a-f]{64}$'),\n CONSTRAINT "
        "ck_case_analysis_assessments__analysis_manifest CHECK "
        "(jsonb_typeof(source_manifest_json)='object'),\n CONSTRAINT "
        "ck_case_analysis_assessments__analysis_justification CHECK "
        "(char_length(btrim(justification)) BETWEEN 1 AND 2000),\n CONSTRAINT "
        "ck_case_analysis_assessments__analysis_unknown_reason CHECK "
        "((expected_evidence_state<>'UNKNOWN' AND "
        "residual_risk_state<>'UNKNOWN') OR (unknown_reason IS NOT NULL AND "
        "char_length(btrim(unknown_reason)) BETWEEN 1 AND 2000)),\n CONSTRAINT "
        "ck_case_analysis_assessments__analysis_expected_evidence CHECK "
        "((expected_evidence_state='DECLARED' AND expected_evidence IS NOT NULL"
        " AND char_length(btrim(expected_evidence)) BETWEEN 1 AND 2000) OR "
        "(expected_evidence_state='UNKNOWN' AND expected_evidence IS NULL)),\n "
        "CONSTRAINT ck_case_analysis_assessments__analysis_residual_risk CHECK "
        "((residual_risk_state='DECLARED' AND residual_risk IS NOT NULL AND "
        "char_length(btrim(residual_risk)) BETWEEN 1 AND 2000) OR "
        "(residual_risk_state='UNKNOWN' AND residual_risk IS NULL))\n)"
    )
    op.execute(
        "CREATE INDEX ix_case_analysis_assessments_tenant_id ON "
        "case_analysis_assessments(tenant_id)"
    )
    op.execute(
        "CREATE FUNCTION reject_analysis_assessment_mutation() RETURNS trigger "
        "LANGUAGE plpgsql AS $$ BEGIN RAISE EXCEPTION "
        "'ANALYSIS_ASSESSMENT_APPEND_ONLY'; END $$"
    )
    op.execute(
        "CREATE TRIGGER analysis_assessment_immutable BEFORE UPDATE OR DELETE "
        "ON case_analysis_assessments FOR EACH ROW EXECUTE FUNCTION "
        "reject_analysis_assessment_mutation()"
    )

    op.execute(
        "CREATE FUNCTION validate_analysis_assessment_origin() RETURNS trigger "
        "LANGUAGE plpgsql AS $$\nBEGIN\n IF NOT EXISTS (SELECT 1 FROM cases c "
        "WHERE c.tenant_id=NEW.tenant_id AND c.id=NEW.case_id AND "
        "c.applicable_dce_version_id=NEW.dce_version_id AND "
        "c.scope_fingerprint=NEW.scope_fingerprint) THEN\n  RAISE EXCEPTION "
        "'ANALYSIS_ASSESSMENT_CASE_CONTEXT_MISMATCH';\n END IF;\n IF "
        "NEW.point_kind='RISK' AND NOT EXISTS (SELECT 1 FROM decision_risks r "
        "WHERE r.tenant_id=NEW.tenant_id AND r.case_id=NEW.case_id AND "
        "r.id=NEW.risk_id AND r.dce_version_id=NEW.dce_version_id AND "
        "r.source_fragment_id=NEW.source_fragment_id) THEN\n  RAISE EXCEPTION "
        "'ANALYSIS_ASSESSMENT_RISK_CONTEXT_MISMATCH';\n END IF;\n IF "
        "NEW.point_kind='REQUIREMENT' AND NOT EXISTS (SELECT 1 FROM "
        "dce_requirements r WHERE r.tenant_id=NEW.tenant_id AND "
        "r.id=NEW.requirement_id AND r.dce_version_id=NEW.dce_version_id) THEN"
        "\n  RAISE EXCEPTION 'ANALYSIS_ASSESSMENT_REQUIREMENT_CONTEXT_MISMATCH';"
        "\n END IF;\n IF NEW.previous_assessment_id IS NOT NULL AND NOT EXISTS "
        "(SELECT 1 FROM case_analysis_assessments p WHERE "
        "p.tenant_id=NEW.tenant_id AND p.case_id=NEW.case_id AND "
        "p.point_kind=NEW.point_kind AND p.point_id=NEW.point_id AND "
        "p.id=NEW.previous_assessment_id AND p.revision=NEW.revision-1) THEN\n  "
        "RAISE EXCEPTION 'ANALYSIS_ASSESSMENT_PREDECESSOR_MISMATCH';\n END IF;\n "
        "RETURN NEW;\nEND $$"
    )
    op.execute(
        "CREATE TRIGGER analysis_assessment_origin BEFORE INSERT ON "
        "case_analysis_assessments FOR EACH ROW EXECUTE FUNCTION "
        "validate_analysis_assessment_origin()"
    )


def downgrade():
    if op.get_bind().scalar(sa.text("SELECT EXISTS(SELECT 1 FROM case_analysis_assessments)")):
        raise RuntimeError("ANALYSIS_ASSESSMENTS_PRESENT_DOWNGRADE_FORBIDDEN")
    op.execute("DROP TABLE case_analysis_assessments")
    op.execute("DROP FUNCTION reject_analysis_assessment_mutation()")
    op.execute("DROP FUNCTION validate_analysis_assessment_origin()")
