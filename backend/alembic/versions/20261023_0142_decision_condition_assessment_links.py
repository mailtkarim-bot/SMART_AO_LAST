"""Append-only source links from native decision conditions to exact human acts."""

import sqlalchemy as sa
from alembic import op

revision = "20261023_0142"
down_revision = "20261023_0141"
branch_labels = None
depends_on = None


def upgrade():
    op.create_unique_constraint(
        "uq_decisions_tenant_case_id", "decisions", ["tenant_id", "case_id", "id"]
    )
    op.create_unique_constraint(
        "uq_assessments_tenant_case_id", "case_analysis_assessments", ["tenant_id", "case_id", "id"]
    )
    op.execute("""

CREATE TABLE decision_condition_assessment_links (
        id UUID NOT NULL,
        case_id UUID NOT NULL,
        decision_id UUID NOT NULL,
        context_id UUID NOT NULL,
        condition_id UUID NOT NULL,
        assessment_id UUID NOT NULL,
        assessment_revision INTEGER NOT NULL,
        source_context_sha256 CHAR(64) NOT NULL,
        justification VARCHAR(2000) NOT NULL,
        actor_id UUID NOT NULL,
        membership_id UUID NOT NULL,
        command_id UUID NOT NULL,
        idempotency_key UUID NOT NULL,
        tenant_id UUID NOT NULL,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
        CONSTRAINT pk_decision_condition_assessment_links PRIMARY KEY (tenant_id, id),
        CONSTRAINT fk_decision_condition_assessment_links__cases__tenant_id FOREIGN
KEY(tenant_id, case_id) REFERENCES cases (tenant_id, id),
        CONSTRAINT fk_decision_condition_assessment_links__decisions__tenant_id FOREIGN
KEY(tenant_id, case_id, decision_id) REFERENCES decisions (tenant_id, case_id, id),
        CONSTRAINT fk_decision_condition_assessment_links__decision_condit_5586 FOREIGN
KEY(tenant_id, decision_id, condition_id) REFERENCES decision_conditions (tenant_id,
decision_id, id),
        CONSTRAINT fk_decision_condition_assessment_links__decision_contex_18e0 FOREIGN
KEY(tenant_id, decision_id, context_id) REFERENCES decision_contexts (tenant_id, decision_id,
id),
        CONSTRAINT fk_decision_condition_assessment_links__case_analysis_a_2b3e FOREIGN
KEY(tenant_id, case_id, assessment_id) REFERENCES case_analysis_assessments (tenant_id, case_id,
id),
        CONSTRAINT uq_condition_assessment_exact UNIQUE (tenant_id, condition_id, assessment_id,
assessment_revision),
        CONSTRAINT uq_condition_assessment_command UNIQUE (tenant_id, command_id),
        CONSTRAINT uq_condition_assessment_idempotency UNIQUE (tenant_id, idempotency_key),
        CONSTRAINT ck_decision_condition_assessment_links__assessment_revision CHECK
(assessment_revision>0),
        CONSTRAINT ck_decision_condition_assessment_links__source_hash CHECK
(source_context_sha256 ~ '^[a-f0-9]{64}$'),
        CONSTRAINT ck_decision_condition_assessment_links__justification CHECK
(length(btrim(justification)) BETWEEN 1 AND 2000)
)

;
CREATE INDEX ix_condition_assessment_case ON decision_condition_assessment_links (tenant_id,
case_id, decision_id);
CREATE INDEX ix_decision_condition_assessment_links_tenant_id ON
decision_condition_assessment_links (tenant_id)
""")
    op.execute("""
    CREATE FUNCTION guard_condition_assessment_link() RETURNS trigger LANGUAGE plpgsql AS $$
    BEGIN
      IF TG_OP <> 'INSERT' THEN RAISE EXCEPTION 'CONDITION_ASSESSMENT_APPEND_ONLY'; END IF;
      IF NOT EXISTS(
        SELECT 1 FROM decisions d
        JOIN decision_conditions c ON c.tenant_id=d.tenant_id AND c.decision_id=d.id
        JOIN decision_contexts x ON x.tenant_id=d.tenant_id AND x.decision_id=d.id
        JOIN decision_context_references r ON r.tenant_id=x.tenant_id AND
r.decision_context_id=x.id
        JOIN case_analysis_assessments a ON a.tenant_id=d.tenant_id AND a.case_id=d.case_id
        WHERE d.tenant_id=NEW.tenant_id AND d.case_id=NEW.case_id AND d.id=NEW.decision_id
          AND d.validity='CURRENT' AND d.lifecycle='FINALIZED' AND d.outcome='CONDITIONAL_GO'
          AND d.context_status='FROZEN' AND d.selected_final_context_id=NEW.context_id
          AND x.id=NEW.context_id AND x.context_state='FROZEN'
          AND c.id=NEW.condition_id AND c.status='OPEN'
          AND r.aggregate_type='ANALYSIS_ASSESSMENT' AND r.aggregate_id=NEW.assessment_id
          AND r.aggregate_revision=NEW.assessment_revision AND
r.content_hash=NEW.source_context_sha256
          AND a.id=NEW.assessment_id AND a.revision=NEW.assessment_revision
          AND a.source_context_sha256=NEW.source_context_sha256
      ) THEN RAISE EXCEPTION 'CONDITION_ASSESSMENT_SOURCE_MISMATCH'; END IF;
      RETURN NEW;
    END $$;
    CREATE TRIGGER condition_assessment_guard BEFORE INSERT OR UPDATE OR DELETE ON
decision_condition_assessment_links
    FOR EACH ROW EXECUTE FUNCTION guard_condition_assessment_link();
""")


def downgrade():
    if op.get_bind().scalar(
        sa.text("SELECT EXISTS(SELECT 1 FROM decision_condition_assessment_links)")
    ):
        raise RuntimeError("CONDITION_ASSESSMENT_HISTORY_DOWNGRADE_REFUSED")
    op.drop_table("decision_condition_assessment_links")
    op.execute("DROP FUNCTION guard_condition_assessment_link()")
    op.drop_constraint("uq_assessments_tenant_case_id", "case_analysis_assessments", type_="unique")
    op.drop_constraint("uq_decisions_tenant_case_id", "decisions", type_="unique")
