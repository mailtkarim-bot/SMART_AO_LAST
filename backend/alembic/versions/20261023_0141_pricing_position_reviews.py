"""Revisioned human links from imported positions to existing cost/source registers."""

import sqlalchemy as sa
from alembic import op

revision = "20261023_0141"
down_revision = "20261022_0140"
branch_labels = None
depends_on = None


def upgrade():
    op.execute("""
    CREATE TABLE pricing_position_reviews (
    id UUID NOT NULL,
    case_id UUID NOT NULL,
    position_id UUID NOT NULL,
    revision INTEGER NOT NULL,
    previous_id UUID,
    requirement_id UUID,
    offer_price_id UUID,
    scope_review_id UUID,
    base_sha256 CHAR(64) NOT NULL,
    basis_sha256 CHAR(64) NOT NULL,
    source_snapshot_json JSONB NOT NULL,
    justification VARCHAR(2000) NOT NULL,
    actor_id UUID NOT NULL,
    membership_id UUID NOT NULL,
    command_id UUID NOT NULL,
    idempotency_key UUID NOT NULL,
    tenant_id UUID NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
    CONSTRAINT pk_pricing_position_reviews PRIMARY KEY (tenant_id, case_id, id),
    CONSTRAINT fk_ppr_case FOREIGN KEY(tenant_id, case_id) REFERENCES cases (tenant_id,
    id) ON DELETE RESTRICT,
    CONSTRAINT fk_ppr_position FOREIGN KEY(tenant_id, position_id) REFERENCES
    pricing_import_rows (tenant_id, id) ON DELETE RESTRICT,
    CONSTRAINT fk_ppr_previous FOREIGN KEY(tenant_id, case_id, previous_id) REFERENCES
    pricing_position_reviews (tenant_id, case_id, id) ON DELETE RESTRICT,
    CONSTRAINT fk_ppr_requirement FOREIGN KEY(tenant_id, requirement_id) REFERENCES
    dce_requirements (tenant_id, id) ON DELETE RESTRICT,
    CONSTRAINT fk_ppr_offer FOREIGN KEY(tenant_id, case_id, offer_price_id) REFERENCES
    partner_offer_price_declarations (tenant_id, case_id, id) ON DELETE RESTRICT,
    CONSTRAINT fk_ppr_scope FOREIGN KEY(tenant_id, case_id, scope_review_id) REFERENCES
    partner_offer_scope_reviews (tenant_id, case_id, id) ON DELETE RESTRICT,
    CONSTRAINT uq_ppr_position_revision UNIQUE (tenant_id, case_id, position_id,
    revision),
    CONSTRAINT uq_ppr_command UNIQUE (tenant_id, command_id),
    CONSTRAINT uq_ppr_idempotency UNIQUE (tenant_id, idempotency_key),
    CONSTRAINT ck_pricing_position_reviews__revision_positive CHECK (revision > 0),
    CONSTRAINT ck_pricing_position_reviews__source_hashes CHECK (basis_sha256 ~
    '^[a-f0-9]{64}$' AND base_sha256 ~ '^[a-f0-9]{64}$'),
    CONSTRAINT ck_pricing_position_reviews__source_object CHECK
    (jsonb_typeof(source_snapshot_json)='object'),
    CONSTRAINT ck_pricing_position_reviews__justification CHECK
    (length(btrim(justification)) BETWEEN 1 AND 2000)
    )
    """)
    op.execute("""
    CREATE INDEX ix_ppr_latest ON pricing_position_reviews (tenant_id, case_id,
    position_id, revision)
    """)
    op.execute("""
    CREATE INDEX ix_pricing_position_reviews_tenant_id ON pricing_position_reviews
    (tenant_id)
    """)
    op.execute("""
    CREATE TABLE pricing_position_cost_references (
    case_id UUID NOT NULL,
    review_id UUID NOT NULL,
    line_id UUID NOT NULL,
    report_id UUID NOT NULL,
    report_revision INTEGER NOT NULL,
    tenant_id UUID NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
    CONSTRAINT pk_pricing_position_cost_references PRIMARY KEY (tenant_id, case_id,
    review_id, line_id),
    CONSTRAINT fk_ppr_cost_review FOREIGN KEY(tenant_id, case_id, review_id) REFERENCES
    pricing_position_reviews (tenant_id, case_id, id) ON DELETE RESTRICT,
    CONSTRAINT fk_ppr_cost_line FOREIGN KEY(tenant_id, line_id) REFERENCES
    financial_report_lines (tenant_id, id) ON DELETE RESTRICT,
    CONSTRAINT fk_ppr_cost_report FOREIGN KEY(tenant_id, report_id) REFERENCES
    financial_report_snapshots (tenant_id, id) ON DELETE RESTRICT,
    CONSTRAINT ck_pricing_position_cost_references__report_revision CHECK (report_revision
    >= 0)
    )
    """)
    op.execute("""
    CREATE INDEX ix_ppr_cost_refs ON pricing_position_cost_references (tenant_id, case_id,
    line_id)
    """)
    op.execute("""
    CREATE INDEX ix_pricing_position_cost_references_tenant_id ON
    pricing_position_cost_references (tenant_id)
    """)
    op.execute("""
    CREATE FUNCTION guard_pricing_position_review() RETURNS trigger LANGUAGE plpgsql AS $$
    DECLARE previous_record uuid; previous_revision integer; version_id uuid;
    BEGIN
    IF TG_OP <> 'INSERT' THEN RAISE EXCEPTION 'PRICING_POSITION_APPEND_ONLY'; END IF;
    SELECT applicable_dce_version_id INTO version_id FROM cases
    WHERE tenant_id=NEW.tenant_id AND id=NEW.case_id FOR UPDATE;
    IF NOT FOUND THEN RAISE EXCEPTION 'PRICING_POSITION_CASE_UNAVAILABLE'; END IF;
    IF version_id IS DISTINCT FROM (NEW.source_snapshot_json->>'dce_version_id')::uuid
    THEN RAISE EXCEPTION 'PRICING_POSITION_STALE_VERSION'; END IF;
    IF NOT EXISTS(SELECT 1 FROM pricing_import_rows r JOIN pricing_import_batches b
    ON b.tenant_id=r.tenant_id AND b.id=r.batch_id WHERE r.tenant_id=NEW.tenant_id
    AND r.id=NEW.position_id AND b.case_id=NEW.case_id)
    THEN RAISE EXCEPTION 'PRICING_POSITION_SCOPE_MISMATCH'; END IF;
    SELECT id,revision INTO previous_record,previous_revision FROM
    pricing_position_reviews
    WHERE tenant_id=NEW.tenant_id AND case_id=NEW.case_id AND position_id=NEW.position_id
    ORDER BY revision DESC LIMIT 1;
    IF NEW.revision<>coalesce(previous_revision,0)+1 OR NEW.previous_id IS DISTINCT FROM
    previous_record
    THEN RAISE EXCEPTION 'PRICING_POSITION_REVISION_CONFLICT'; END IF;
    RETURN NEW;
    END $$;
    CREATE TRIGGER pricing_position_review_guard BEFORE INSERT OR UPDATE OR DELETE ON
    pricing_position_reviews
    FOR EACH ROW EXECUTE FUNCTION guard_pricing_position_review();
    """)
    op.execute("""
    CREATE FUNCTION guard_pricing_position_cost_reference() RETURNS trigger LANGUAGE
    plpgsql AS $$
    BEGIN
    IF TG_OP <> 'INSERT' THEN RAISE EXCEPTION 'PRICING_POSITION_APPEND_ONLY'; END IF;
    IF NOT EXISTS(SELECT 1 FROM financial_report_lines l JOIN financial_report_snapshots r
    ON r.tenant_id=l.tenant_id AND r.id=l.snapshot_id
    WHERE l.tenant_id=NEW.tenant_id AND l.id=NEW.line_id AND r.id=NEW.report_id
    AND r.case_id=NEW.case_id AND r.aggregate_revision=NEW.report_revision
    AND l.category IN ('DIRECT_COST','OVERHEAD','SUBCONTRACTING','CONTINGENCY'))
    THEN RAISE EXCEPTION 'PRICING_POSITION_COST_SCOPE_MISMATCH'; END IF;
    IF NOT EXISTS(SELECT 1 FROM pricing_position_reviews p,
    jsonb_array_elements(p.source_snapshot_json->'costs') c
    WHERE p.tenant_id=NEW.tenant_id AND p.case_id=NEW.case_id AND p.id=NEW.review_id
    AND c->>'line_id'=NEW.line_id::text AND c->>'report_id'=NEW.report_id::text
    AND (c->>'report_revision')::integer=NEW.report_revision)
    THEN RAISE EXCEPTION 'PRICING_POSITION_COST_SNAPSHOT_MISMATCH'; END IF;
    RETURN NEW;
    END $$;
    CREATE TRIGGER pricing_position_cost_guard BEFORE INSERT OR UPDATE OR DELETE ON
    pricing_position_cost_references
    FOR EACH ROW EXECUTE FUNCTION guard_pricing_position_cost_reference();
    """)


def downgrade():
    if op.get_bind().scalar(sa.text("SELECT EXISTS(SELECT 1 FROM pricing_position_reviews)")):
        raise RuntimeError("PRICING_POSITION_HISTORY_DOWNGRADE_REFUSED")
    op.drop_table("pricing_position_cost_references")
    op.drop_table("pricing_position_reviews")
    op.execute("""
    DROP FUNCTION guard_pricing_position_cost_reference()
    """)
    op.execute("""
    DROP FUNCTION guard_pricing_position_review()
    """)
