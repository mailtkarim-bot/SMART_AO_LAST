"""Allow the durable MFA recovery audit event.

Revision ID: 20260914_0069
Revises: 20260914_0068
Create Date: 2026-09-14
"""

from collections.abc import Sequence

from alembic import op

revision = "20260914_0069"
down_revision = "20260914_0068"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None

_PREVIOUS_EVENT_TYPE_CONSTRAINT = (
    "event_type IN ("
    "'AUTH_LOGIN_SUCCEEDED', 'AUTH_LOGIN_DENIED', "
    "'AUTH_REFRESH_SUCCEEDED', 'AUTH_REFRESH_DENIED', "
    "'AUTH_LOGOUT_SUCCEEDED', 'AUTH_SESSION_REJECTED', "
    "'AUTHZ_SUCCEEDED', 'AUTHZ_DENIED', 'AUTHZ_STEP_UP_REQUIRED', "
    "'AUTH_MFA_ENROLLMENT_STARTED', 'AUTH_MFA_ENROLLMENT_CONFIRMED', "
    "'AUTH_MFA_VERIFICATION_DENIED', 'AUTH_MFA_STEP_UP_SUCCEEDED', "
    "'AUTH_MFA_RECOVERY_USED', 'AUTH_MFA_DISABLED', "
    "'SUBMISSION_PACKAGE_EXPORTED'"
    ")"
)
_EVENT_TYPE_CONSTRAINT = _PREVIOUS_EVENT_TYPE_CONSTRAINT.replace(
    "'AUTH_MFA_RECOVERY_USED',",
    "'AUTH_MFA_RECOVERY_USED', 'AUTH_MFA_RECOVERY_COMPLETED',",
)


def upgrade() -> None:
    op.drop_constraint("event_type", "security_audit_events", type_="check")
    op.create_check_constraint("event_type", "security_audit_events", _EVENT_TYPE_CONSTRAINT)


def downgrade() -> None:
    op.drop_constraint("event_type", "security_audit_events", type_="check")
    op.create_check_constraint(
        "event_type",
        "security_audit_events",
        _PREVIOUS_EVENT_TYPE_CONSTRAINT,
    )
