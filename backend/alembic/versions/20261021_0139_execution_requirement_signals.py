"""Extend source-only execution signals; populated downgrade refuses proof loss."""

import sqlalchemy as sa
from alembic import op

revision = "20261021_0139"
down_revision = "20261020_0138"
branch_labels = None
depends_on = None
OLD_REQUIREMENT_KIND = (
    "requirement_kind IN ('RC_DOCUMENT_CANDIDATURE', 'RC_CONTENT_OFFER', "
    "'RC_SUBMISSION_DEADLINE', 'RC_RESPONSE_CHANNEL', 'RC_FILE_CONSTRAINT', "
    "'RC_SITE_VISIT', 'RC_AWARD_CRITERION', 'RC_NEGOTIATION', "
    "'RC_OFFER_VALIDITY', 'CCAP_PENALTIES', 'CCAP_RETENTION_GUARANTEE', "
    "'CCAP_GUARANTEE', 'CCAP_INSURANCE', 'CCTP_VARIANTS', 'CCAP_SUBCONTRACTING', "
    "'CCAP_QUALIFICATIONS')"
)
NEW_REQUIREMENT_KIND = (
    "requirement_kind IN ('RC_DOCUMENT_CANDIDATURE', 'RC_CONTENT_OFFER', "
    "'RC_SUBMISSION_DEADLINE', 'RC_RESPONSE_CHANNEL', 'RC_FILE_CONSTRAINT', "
    "'RC_SITE_VISIT', 'RC_AWARD_CRITERION', 'RC_NEGOTIATION', "
    "'RC_OFFER_VALIDITY', 'CCAP_PENALTIES', 'CCAP_RETENTION_GUARANTEE', "
    "'CCAP_GUARANTEE', 'CCAP_INSURANCE', 'CCTP_VARIANTS', 'CCAP_SUBCONTRACTING', "
    "'CCAP_QUALIFICATIONS', 'DCE_TECHNICAL_PRESCRIPTION', "
    "'DCE_LOGISTICS_CONSTRAINT', 'DCE_SCHEDULE_CONSTRAINT', 'DCE_HSE_CONSTRAINT',"
    " 'DCE_PAYMENT_TERM', 'DCE_ACCEPTANCE_TERM')"
)
OLD_REQUIREMENT_TYPE = (
    "requirement_type IN ('CANDIDATURE_DOCUMENT', 'OFFER_DOCUMENT', "
    "'SUBMISSION_DEADLINE_SIGNAL', 'SUBMISSION_CHANNEL', 'FILE_CONSTRAINT', "
    "'SITE_VISIT', 'AWARD_CRITERION_SIGNAL', 'NEGOTIATION_SIGNAL', "
    "'OFFER_VALIDITY_SIGNAL', 'CONTRACT_RISK_SIGNAL')"
)
NEW_REQUIREMENT_TYPE = (
    "requirement_type IN ('CANDIDATURE_DOCUMENT', 'OFFER_DOCUMENT', "
    "'SUBMISSION_DEADLINE_SIGNAL', 'SUBMISSION_CHANNEL', 'FILE_CONSTRAINT', "
    "'SITE_VISIT', 'AWARD_CRITERION_SIGNAL', 'NEGOTIATION_SIGNAL', "
    "'OFFER_VALIDITY_SIGNAL', 'CONTRACT_RISK_SIGNAL', 'TECHNICAL_PRESCRIPTION', "
    "'LOGISTICS_CONSTRAINT', 'SCHEDULE_CONSTRAINT', 'HSE_CONSTRAINT', "
    "'PAYMENT_TERM_SIGNAL', 'ACCEPTANCE_TERM_SIGNAL')"
)


def _set_constraints(new):
    for table, name, expression in [
        (
            "dce_rc_requirement_observations",
            "requirement_kind",
            NEW_REQUIREMENT_KIND if new else OLD_REQUIREMENT_KIND,
        ),
        (
            "dce_requirements",
            "requirement_type",
            NEW_REQUIREMENT_TYPE if new else OLD_REQUIREMENT_TYPE,
        ),
    ]:
        op.drop_constraint(name, table, type_="check")
        op.create_check_constraint(name, table, expression)


def upgrade():
    _set_constraints(True)


def downgrade():
    conn = op.get_bind()
    # DDL locks exclude concurrent inserts until the transaction commits.
    conn.execute(
        sa.text(
            "LOCK TABLE dce_rc_requirement_observations, dce_requirements IN ACCESS EXCLUSIVE MODE"
        )
    )
    if conn.execute(
        sa.text(
            "SELECT EXISTS (SELECT 1 FROM dce_rc_requirement_observations WHERE "
            "requirement_kind LIKE 'DCE_%')"
        )
    ).scalar_one():
        raise RuntimeError("L04_EXECUTION_SIGNALS_PRESENT")
    _set_constraints(False)
