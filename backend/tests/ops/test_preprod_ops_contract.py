from __future__ import annotations

import subprocess
from pathlib import Path

from app.platform.persistence.schema import EXPECTED_ALEMBIC_HEAD

ROOT = Path(__file__).resolve().parents[3]
OPS = ROOT / "ops"


def test_preprod_operations_scripts_are_executable_and_syntactically_valid() -> None:
    scripts = sorted(OPS.glob("*.sh"))
    assert scripts
    for script in scripts:
        assert script.stat().st_mode & 0o111, script
        result = subprocess.run(["bash", "-n", str(script)], capture_output=True, text=True)
        assert result.returncode == 0, result.stderr


def test_preflight_loads_the_protected_preproduction_environment_file() -> None:
    preflight = (OPS / "preflight-checklist.sh").read_text(encoding="utf-8")
    assert 'ENV_FILE="${OPS_DIR}/.env.preprod"' in preflight
    assert '[[ -f "${ENV_FILE}" ]]' in preflight
    assert "stat -c '%a' \"${ENV_FILE}\"" in preflight
    assert 'docker compose --env-file "${ENV_FILE}" -f "${COMPOSE_FILE}" config' in preflight


def test_local_preprod_simulation_is_unique_loopback_only_and_self_cleaning() -> None:
    simulation = (ROOT / "scripts/simulate_preprod_local.sh").read_text(encoding="utf-8")
    assert 'PROJECT="smartao-local-preprod-${WORK_ID,,}"' in simulation
    assert 'docker compose --project-name "${PROJECT}"' in simulation
    assert '"127.0.0.1:18080:80"' in simulation
    assert '"127.0.0.1:18443:443"' in simulation
    assert '"127.0.0.1:18443:443/udp"' in simulation
    assert '"127.0.0.1:15432:5432"' not in simulation
    assert '"127.0.0.1:13310:3310"' not in simulation
    assert "compose down -v --remove-orphans" in simulation
    assert 'rm -rf -- "${WORK_DIR}"' in simulation
    assert "ClamdTcpMalwareScanAdapter" in simulation
    assert "C5_CLAMAV_ADAPTER" in simulation
    assert 'unavailable.verdict != "ERROR"' in simulation
    assert "container_ip_on_internal()" in simulation
    assert '\\"${PROJECT}_internal\\"' in simulation
    assert "@${postgres_ip}:5432/smart_ao" in simulation
    assert 'SMART_AO_C5_TEST_CLAMD_HOST="${clamav_ip}"' in simulation
    assert "SMART_AO_C5_TEST_CLAMD_PORT=3310" in simulation
    assert "docker inspect --format" in simulation
    assert "PostgreSQL/ClamAV host ports" in simulation
    assert "test_case_handover_http_e2e.py" in simulation


def test_compose_runtime_images_are_digest_pinned_and_clamav_is_private() -> None:
    compose = (OPS / "docker-compose.preprod.yml").read_text(encoding="utf-8")
    image_lines = [
        line.strip() for line in compose.splitlines() if line.strip().startswith("image:")
    ]
    assert image_lines
    assert all("@sha256:" in line for line in image_lines)
    assert "3310:" not in compose
    assert "3310" in compose


def test_7b_units_and_rotation_contract_are_present() -> None:
    expected = {
        "smart-ao-backup.service",
        "smart-ao-backup.timer",
        "smart-ao-healthcheck.service",
        "smart-ao-healthcheck.timer",
        "smart-ao-health-alert.service",
    }
    assert {path.name for path in (OPS / "systemd").iterdir()} >= expected
    runbook = (OPS / "README.md").read_text(encoding="utf-8")
    for marker in ("restore-preprod.sh", "rotate-jwt-key-preprod.sh", "SHA-256", "json-file"):
        assert marker in runbook


def test_deploy_starts_submission_notification_workers_explicitly() -> None:
    deploy_script = (OPS / "deploy-preprod.sh").read_text(encoding="utf-8")
    assert "submission-export-webhook-worker" in deploy_script
    assert "submission-export-smtp-worker" in deploy_script
    assert (
        "compose up -d backend dce-retention-worker submission-export-webhook-worker "
        "submission-export-smtp-worker" in deploy_script
    )


def test_local_preprod_simulation_archives_and_restores_quarantine_in_isolation() -> None:
    simulator = (ROOT / "scripts" / "simulate_preprod_local.sh").read_text(encoding="utf-8")
    e2e = (ROOT / "backend" / "tests" / "db" / "test_case_handover_http_e2e.py").read_text(
        encoding="utf-8"
    )
    test_configuration = (ROOT / "backend" / "tests" / "conftest.py").read_text(encoding="utf-8")
    assert "BACKUP_MANIFEST" in simulator
    assert "ops/restore-preprod.sh" in simulator
    assert "sha256sum" in simulator
    assert "dce-quarantine" in simulator
    assert "path-traversal quarantine archive was accepted" in simulator
    assert "remaining_restore_volumes" in simulator
    assert "SMART_AO_TEST_PRESERVE_C5_RESTORE_FIXTURE" in simulator
    assert "SMART_AO_TEST_DISPOSABLE_DATABASE=1" in simulator
    assert "C5 SHA-256 mismatch restore was accepted" in simulator
    assert "remaining_traversal_restore_dbs" in simulator
    assert "smart_ao_restore_%" in simulator
    assert "verified_clean_count" in simulator
    assert '"${verified_clean_count}" == "${clean_count}"' in simulator
    assert 'docker cp "${C5_HOST_STORAGE_DIR}/."' in simulator
    assert "host_object_sha256" in simulator
    assert "SMART_AO_TEST_PRESERVE_C5_RESTORE_FIXTURE" in e2e
    assert "SMART_AO_TEST_DISPOSABLE_DATABASE" in e2e
    assert "SMART_AO_TEST_PRESERVE_C5_RESTORE_FIXTURE" in test_configuration


def test_restore_verifies_c5_objects_in_a_temporary_volume_with_cleanup() -> None:
    restore = (OPS / "restore-preprod.sh").read_text(encoding="utf-8")
    assert "case_contract_change_evidence_objects WHERE state = 'CLEAN'" in restore
    assert 'RESTORE_VOLUME="smart_ao_c5_restore_${RESTORE_RUN_ID}"' in restore
    assert "--label com.smartao.purpose=quarantine-restore-verification" in restore
    assert 'remove_owned_restore_volume "${RESTORE_VOLUME}" "${RESTORE_RUN_ID}"' in restore
    assert 'if [[ "${RESTORE_DB_CREATED}" == "1" && -n "${RESTORE_DB}" ]]' in restore
    assert 'if [[ "${RESTORE_VOLUME_CREATED}" == "1" && -n "${RESTORE_VOLUME}" ]]' in restore
    assert "verify_quarantine_restore.py" in restore
    assert "--network none --read-only" in restore
    assert 'sha256sum -- "${required_path}"' in restore
    assert "sha256sum --ignore-missing --check" not in restore


def test_restore_reclaims_only_its_interrupted_run_resources_after_sigkill() -> None:
    restore = (OPS / "restore-preprod.sh").read_text(encoding="utf-8")
    simulator = (ROOT / "scripts" / "simulate_preprod_local.sh").read_text(encoding="utf-8")
    assert 'RESTORE_STATE_DIR="${SMART_AO_RESTORE_STATE_DIR:-' in restore
    assert "flock -n 8" in restore
    assert "recover_interrupted_restores" in restore
    assert "com.smartao.restore.run" in restore
    assert 'created_volume="$(docker volume create \\' in restore
    assert "com.smartao.purpose=quarantine-restore-verification" in restore
    assert 'RESTORE_STATE_FILE="${RESTORE_STATE_DIR}/restore-${RESTORE_RUN_ID}.state"' in restore
    assert "restore-fault-entered" in simulator
    assert "restore recovery left a temporary database" in simulator
    assert "restore recovery left a temporary quarantine volume" in simulator
    assert "active quarantine volume changed during restore recovery" in simulator
    assert "repeat restore recovery changed finalized backup bytes" in simulator


def test_restore_refuses_to_delete_a_volume_with_a_mismatched_run_label() -> None:
    simulator = (ROOT / "scripts" / "simulate_preprod_local.sh").read_text(encoding="utf-8")
    assert "RESTORE_FIXTURE_VOLUME" in simulator
    assert "restore-mismatched-label.log" in simulator
    assert "restore accepted a mismatched volume run label" in simulator
    assert "unowned restore volume was removed" in simulator
    assert "mismatched-label restore changed active C5 object hashes" in simulator
    assert "mismatched-label restore changed finalized backups" in simulator
    assert "restore state receipt changed after ownership refusal" in simulator


def test_restore_does_not_drop_a_sentinel_database_from_a_malformed_receipt() -> None:
    simulator = (ROOT / "scripts" / "simulate_preprod_local.sh").read_text(encoding="utf-8")
    assert "run_malformed_receipt_cycle" in simulator
    assert "restore accepted a mismatched receipt database" in simulator
    assert "malformed-receipt restore dropped sentinel database" in simulator
    assert "malformed-receipt restore removed its volume" in simulator
    assert "malformed-receipt restore created or removed an isolated database" in simulator
    assert "malformed-receipt restore created or removed a temporary volume" in simulator
    assert "malformed receipt retry changed active C5 hashes" in simulator
    assert "malformed receipt retry changed finalized backups" in simulator
    assert "run_malformed_receipt_cycle 2" in simulator


def test_restore_refuses_symlinked_and_permissive_state_receipts() -> None:
    simulator = (ROOT / "scripts" / "simulate_preprod_local.sh").read_text(encoding="utf-8")
    assert "run_unsafe_receipt_cycle symlink" in simulator
    assert "run_unsafe_receipt_cycle permissive" in simulator
    assert "ln -s --" in simulator
    assert "chmod 644" in simulator
    assert "state receipt target changed after refusal" in simulator
    assert "restore followed a symlinked state receipt" in simulator
    assert "restore accepted a mode-0644 state receipt" in simulator
    assert "unsafe-receipt refusal changed active C5 hashes" in simulator
    assert "unsafe-receipt refusal changed finalized backups" in simulator


def test_restore_lock_protects_an_active_restore_from_concurrent_cleanup() -> None:
    restore = (OPS / "restore-preprod.sh").read_text(encoding="utf-8")
    simulator = (ROOT / "scripts" / "simulate_preprod_local.sh").read_text(encoding="utf-8")
    assert 'flock -n 8 || fail "another restore is already running' in restore
    assert restore.index("flock -n 8") < restore.index("recover_interrupted_restores \\")
    assert "restore-concurrency-entered" in simulator
    assert "restore-concurrency-release" in simulator
    assert "second restore did not fail on the active lock" in simulator
    assert "concurrent restore modified the active receipt or resources" in simulator
    assert "first concurrent restore did not finish after release" in simulator
    assert "post-lock replay restore did not complete" in simulator


def test_restore_recovers_after_temporary_volume_removal_failure() -> None:
    restore = (OPS / "restore-preprod.sh").read_text(encoding="utf-8")
    simulator = (ROOT / "scripts" / "simulate_preprod_local.sh").read_text(encoding="utf-8")
    assert "restore cleanup incomplete; protected state retained for recovery" in restore
    assert "RESTORE_FAULT_VOLUME_RM" in simulator
    assert "restore-volume-rm-failure.log" in simulator
    assert "volume removal failure was not attempted in both cleanup paths" in simulator
    assert "volume removal failure did not retain its exact receipt and volume" in simulator
    assert "retry after volume removal failure did not restore normally" in simulator
    assert "volume removal failure recovery left stale restore resources" in simulator
    assert "restore replay after cleanup failure left temporary resources" in simulator


def test_restore_recovers_after_temporary_database_drop_failure() -> None:
    restore = (OPS / "restore-preprod.sh").read_text(encoding="utf-8")
    simulator = (ROOT / "scripts" / "simulate_preprod_local.sh").read_text(encoding="utf-8")
    assert "restore cleanup incomplete; protected state retained for recovery" in restore
    assert "RESTORE_FAULT_DB_DROP" in simulator
    assert "restore-dropdb-failures" in simulator
    assert "dropdb failure was not attempted in both cleanup paths" in simulator
    assert "dropdb failure did not retain its exact DB and receipt" in simulator
    assert "dropdb recovery did not remove its DB and restore normally" in simulator
    assert "dropdb retry replay left temporary resources" in simulator


def test_backup_script_supports_isolated_compose_and_simulation_uses_real_backup() -> None:
    backup = (OPS / "backup-preprod.sh").read_text(encoding="utf-8")
    restore = (OPS / "restore-preprod.sh").read_text(encoding="utf-8")
    simulator = (ROOT / "scripts" / "simulate_preprod_local.sh").read_text(encoding="utf-8")
    assert 'ENV_FILE="${SMART_AO_PREPROD_ENV_FILE:-${OPS_DIR}/.env.preprod}"' in backup
    assert 'COMPOSE_PROJECT_NAME="${SMART_AO_COMPOSE_PROJECT_NAME:-}"' in backup
    assert 'docker compose --project-name "${COMPOSE_PROJECT_NAME}"' in backup
    assert "^[a-z0-9][a-z0-9_-]{0,62}$" in backup
    assert "^[a-z0-9][a-z0-9_-]{0,62}$" in restore
    assert '[[ -s "${c5_archive}" ]]' in backup
    assert "docker run --rm --network none --read-only" in backup
    assert '--mount "type=volume,src=${volume_name},dst=/source,readonly"' in backup
    assert "--cap-add DAC_READ_SEARCH" in backup
    assert "date -u +%Y%m%dT%H%M%S%NZ)_$$" in backup
    assert 'manifest_tmp="${manifest}.tmp"' in backup
    assert "sha256sum --check --status" in backup
    assert "|| true" not in backup
    assert 'cd "${BACKUP_DIR}"\n    shopt -s nullglob' in backup
    assert "flock -n 9" in backup
    assert backup.count('exec 9>"${lock_file}"') == 1
    assert backup.count("flock -n 9") == 1
    assert "-name 'smart_ao_*.tmp' -delete" in backup
    assert "ops/backup-preprod.sh" in simulator
    assert "pg_dump" not in simulator
    assert "T[0-9]{15}Z_[0-9]+" in simulator
    assert "BACKUP_FAULT_MARKER" in simulator
    assert 'kill -KILL -- "-${BACKUP_TEST_PGID}"' in simulator
    assert "orphan_tar_tmp" in simulator
    assert "BACKUP_CONCURRENCY_RELEASE" in simulator
    assert "backup lock did not reject the concurrent run" in simulator


def test_caddy_routes_all_health_endpoints_to_backend() -> None:
    caddyfile = (OPS / "Caddyfile").read_text(encoding="utf-8")
    assert "request_body {\n        max_size 150MB\n    }" in caddyfile
    assert "Content-Security-Policy" in caddyfile
    assert "@health path /healthz /healthz/*" in caddyfile
    health_block = caddyfile.split("@health path", maxsplit=1)[1].split("handle {", maxsplit=1)[0]
    assert "reverse_proxy backend:8000" in health_block
    assert 'respond "ok" 200' not in health_block


def test_preprod_trusts_forwarded_client_ip_only_on_internal_proxy_network() -> None:
    dockerfile = (OPS / "docker/backend.Dockerfile").read_text(encoding="utf-8")
    compose = (OPS / "docker-compose.preprod.yml").read_text(encoding="utf-8")
    assert "--proxy-headers" in dockerfile
    assert "--forwarded-allow-ips=172.30.0.0/24" in dockerfile
    assert "subnet: 172.30.0.0/24" in compose
    assert "  migrate:\n" in compose
    assert 'command: ["alembic", "-c", "/app/backend/alembic.ini", "upgrade", "head"]' in compose
    assert compose.count("service_completed_successfully") >= 7
    assert "backend:\n" in compose and "      - internal\n" in compose


def test_preprod_services_use_minimal_environment_allowlists() -> None:
    compose = (OPS / "docker-compose.preprod.yml").read_text(encoding="utf-8")
    assert "env_file:" not in compose

    backend = compose.split("  backend:", maxsplit=1)[1].split(
        "  dce-retention-worker:", maxsplit=1
    )[0]
    retention = compose.split("  dce-retention-worker:", maxsplit=1)[1].split(
        "  submission-export-webhook-worker:", maxsplit=1
    )[0]
    webhook = compose.split("  submission-export-webhook-worker:", maxsplit=1)[1].split(
        "  submission-export-smtp-worker:", maxsplit=1
    )[0]
    smtp = compose.split("  submission-export-smtp-worker:", maxsplit=1)[1].split(
        "\n  postgres:", maxsplit=1
    )[0]

    assert "SMART_AO_JWT_SIGNING_KEY" in backend
    assert "SMART_AO_JWT_KEY_ID" in backend
    assert "SMART_AO_JWT_VERIFICATION_KEYS_JSON" in backend
    assert "SMART_AO_JWT_SIGNING_KEY" not in retention
    assert "SMART_AO_JWT_SIGNING_KEY" not in webhook
    assert "SMART_AO_JWT_SIGNING_KEY" not in smtp
    assert "SMART_AO_EXPORT_WEBHOOK_SECRET" in webhook
    assert "POSTGRES_PASSWORD" not in backend
    assert "POSTGRES_PASSWORD" not in retention
    assert "POSTGRES_PASSWORD" not in webhook
    assert "POSTGRES_PASSWORD" not in smtp


def test_deploy_validates_libpq_password_alignment() -> None:
    deploy_script = (OPS / "deploy-preprod.sh").read_text(encoding="utf-8")
    assert "PGPASSWORD" in deploy_script
    assert 'PGPASSWORD}" == "${POSTGRES_PASSWORD}' in deploy_script


def test_readiness_contract_uses_shared_schema_head() -> None:
    application = (ROOT / "backend/app/bootstrap/application.py").read_text(encoding="utf-8")
    schema = (ROOT / "backend/app/platform/persistence/schema.py").read_text(encoding="utf-8")
    assert "from app.platform.persistence.schema import EXPECTED_ALEMBIC_HEAD" in application
    assert "EXPECTED_ALEMBIC_HEAD" in application
    assert f'EXPECTED_ALEMBIC_HEAD = "{EXPECTED_ALEMBIC_HEAD}"' in schema


def test_healthcheck_validates_application_json_payloads() -> None:
    healthcheck = (OPS / "healthcheck-preprod.sh").read_text(encoding="utf-8")
    assert 'live_body="$(curl' in healthcheck
    assert 'ready_body="$(curl' in healthcheck
    assert '"process"[[:space:]]*:[[:space:]]*"ok"' in healthcheck
    assert '"database"[[:space:]]*:[[:space:]]*"ok"' in healthcheck
    assert '"schema"[[:space:]]*:[[:space:]]*"ok"' in healthcheck
    assert '"clamav"[[:space:]]*:[[:space:]]*"ok"' in healthcheck


def test_backend_docker_context_excludes_demonstrations_and_tests() -> None:
    dockerignore = (ROOT / "ops/docker/backend.Dockerfile.dockerignore").read_text(encoding="utf-8")
    assert "backend/app/demonstrations/" in dockerignore
    assert "backend/tests/" in dockerignore
    assert "web/" in dockerignore
    # The frontend image must keep its own context: the shared root ignore
    # must not exclude web/, or frontend.Dockerfile can never build.
    root_ignore = (ROOT / ".dockerignore").read_text(encoding="utf-8")
    assert not root_ignore.startswith("web/")
    assert "\nweb/\n" not in root_ignore
    frontend_ignore = (ROOT / "ops/docker/frontend.Dockerfile.dockerignore").read_text(
        encoding="utf-8"
    )
    assert "backend/" in frontend_ignore


def test_dev_compose_is_loopback_bound_and_not_repurposable_as_preprod() -> None:
    compose = (ROOT / "docker-compose.yml").read_text(encoding="utf-8")
    assert "SMART_AO_ENV: development" in compose
    assert '"127.0.0.1:${SMART_AO_POSTGRES_HOST_PORT:-5432}:5432"' in compose
    assert '"127.0.0.1:8000:8000"' in compose
    assert "local-development-signing-key-change-me" in compose
    assert "dev-only-signing-key" not in compose
    env_example = (ROOT / ".env.example").read_text(encoding="utf-8")
    assert "SMART_AO_ENV=development" in env_example
    assert "SMART_AO_JWT_SIGNING_KEY=" in env_example
    assert "local-development-signing-key-change-me-" in env_example
    assert 'command: ["alembic", "-c", "/app/backend/alembic.ini", "upgrade", "head"]' in compose
    assert compose.count("no-new-privileges:true") >= 5
    assert "service_completed_successfully" in compose
    local_override = (ROOT / "compose.local-dev.yml").read_text(encoding="utf-8")
    assert '"127.0.0.1:5433:5432"' in local_override


def test_frontend_image_and_service_run_non_root_with_healthcheck() -> None:
    dockerfile = (OPS / "docker/frontend.Dockerfile").read_text(encoding="utf-8")
    compose = (OPS / "docker-compose.preprod.yml").read_text(encoding="utf-8")
    caddyfile = (OPS / "Caddyfile").read_text(encoding="utf-8")
    assert "USER nginx" in dockerfile
    assert "EXPOSE 8080" in dockerfile
    assert "HEALTHCHECK" in dockerfile
    frontend = compose.split("  frontend:\n    build:", maxsplit=1)[1].split(
        "  backend:", maxsplit=1
    )[0]
    assert '      - "8080"' in frontend
    assert "healthcheck:" in frontend
    assert "reverse_proxy frontend:8080" in caddyfile


def test_ci_audits_frontend_production_dependencies() -> None:
    workflow = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
    assert "name: Frontend dependency audit" in workflow
    assert "pnpm audit --prod --audit-level high" in workflow


def test_egress_services_join_private_and_edge_networks() -> None:
    compose = (OPS / "docker-compose.preprod.yml").read_text(encoding="utf-8")
    clamav = compose.split("  clamav:", maxsplit=1)[1].split("\n\n  volumes:", maxsplit=1)[0]
    webhook = compose.split("  submission-export-webhook-worker:", maxsplit=1)[1].split(
        "\n  postgres:", maxsplit=1
    )[0]
    for service in (clamav, webhook):
        assert "      - internal" in service
        assert "      - edge" in service


def test_optional_dependency_build_flags_are_explicit() -> None:
    dockerfile = (OPS / "docker/backend.Dockerfile").read_text(encoding="utf-8")
    compose = (OPS / "docker-compose.preprod.yml").read_text(encoding="utf-8")
    assert "ARG SMART_AO_INSTALL_CONNECTORS=0" in dockerfile
    assert "ARG SMART_AO_INSTALL_DOCUMENT_OCR=0" in dockerfile
    assert "uv sync --frozen --no-dev --no-editable --extra document-ocr" in dockerfile
    assert "ARG SMART_AO_INSTALL_OBJECT_STORAGE=0" in dockerfile
    assert "uv sync --frozen --no-dev --no-editable --extra object-storage" in dockerfile
    assert "uv sync --frozen --no-dev --no-editable --extra connectors" in dockerfile
    assert "SMART_AO_INSTALL_CONNECTORS" in compose
    assert "SMART_AO_INSTALL_RAG" in compose
    assert "SMART_AO_INSTALL_DOCUMENT_ADVANCED" in compose
    assert "SMART_AO_INSTALL_DOCUMENT_OCR" in compose
    assert "SMART_AO_INSTALL_OBJECT_STORAGE" in compose


def test_insee_connector_is_disabled_by_default_and_secret_is_backend_only() -> None:
    compose = (OPS / "docker-compose.preprod.yml").read_text(encoding="utf-8")
    backend = compose.split("  backend:", maxsplit=1)[1].split(
        "  dce-retention-worker:", maxsplit=1
    )[0]
    retention = compose.split("  dce-retention-worker:", maxsplit=1)[1].split(
        "  submission-export-webhook-worker:", maxsplit=1
    )[0]
    webhook = compose.split("  submission-export-webhook-worker:", maxsplit=1)[1].split(
        "  submission-export-smtp-worker:", maxsplit=1
    )[0]
    smtp = compose.split("  submission-export-smtp-worker:", maxsplit=1)[1].split(
        "\n  postgres:", maxsplit=1
    )[0]
    assert "SMART_AO_INSEE_ENABLED: ${SMART_AO_INSEE_ENABLED:-0}" in backend
    assert "SMART_AO_INSEE_API_TOKEN: ${SMART_AO_INSEE_API_TOKEN:-}" in backend
    assert "SMART_AO_INSEE_API_TOKEN" not in retention
    assert "SMART_AO_INSEE_API_TOKEN" not in webhook
    assert "SMART_AO_INSEE_API_TOKEN" not in smtp


def test_optional_notifications_build_and_runtime_flags_are_explicit() -> None:
    dockerfile = (OPS / "docker/backend.Dockerfile").read_text(encoding="utf-8")
    compose = (OPS / "docker-compose.preprod.yml").read_text(encoding="utf-8")
    assert "ARG SMART_AO_INSTALL_NOTIFICATIONS=0" in dockerfile
    assert "uv sync --frozen --no-dev --no-editable --extra notifications" in dockerfile
    assert "SMART_AO_INSTALL_NOTIFICATIONS" in compose
    assert "SMART_AO_SMTP_ENABLED: ${SMART_AO_SMTP_ENABLED:-0}" in compose
    assert "SMART_AO_SMTP_TO: ${SMART_AO_SMTP_TO:-}" in compose
    assert "python -m app.workers.submission_export_smtp" in compose


def test_smtp_credentials_are_allowlisted_only_for_backend() -> None:
    compose = (OPS / "docker-compose.preprod.yml").read_text(encoding="utf-8")
    backend = compose.split("  backend:", maxsplit=1)[1].split(
        "  dce-retention-worker:", maxsplit=1
    )[0]
    retention = compose.split("  dce-retention-worker:", maxsplit=1)[1].split(
        "  submission-export-webhook-worker:", maxsplit=1
    )[0]
    webhook = compose.split("  submission-export-webhook-worker:", maxsplit=1)[1].split(
        "  submission-export-smtp-worker:", maxsplit=1
    )[0]
    smtp = compose.split("  submission-export-smtp-worker:", maxsplit=1)[1].split(
        "\n  postgres:", maxsplit=1
    )[0]
    assert "SMART_AO_SMTP_PASSWORD" in backend
    assert "SMART_AO_SMTP_USERNAME" in backend
    assert "SMART_AO_SMTP_PASSWORD" not in retention
    assert "SMART_AO_SMTP_PASSWORD" not in webhook
    assert "SMART_AO_SMTP_PASSWORD" in smtp
    assert "SMART_AO_SMTP_TO" in smtp


def test_validation_commands_install_calendar_extra() -> None:
    makefile = (ROOT / "Makefile").read_text(encoding="utf-8")
    assert "uv sync --group dev --extra calendar" in makefile
    assert "uv run --extra calendar pytest" in makefile


def test_optional_calendar_build_flag_is_explicit() -> None:
    dockerfile = (OPS / "docker/backend.Dockerfile").read_text(encoding="utf-8")
    compose = (OPS / "docker-compose.preprod.yml").read_text(encoding="utf-8")
    assert "ARG SMART_AO_INSTALL_CALENDAR=0" in dockerfile
    assert "uv sync --frozen --no-dev --no-editable --extra calendar" in dockerfile
    assert "SMART_AO_INSTALL_CALENDAR" in compose
    assert "SMART_AO_CALENDAR_ENABLED: ${SMART_AO_CALENDAR_ENABLED:-0}" in compose


def test_boamp_public_search_is_explicit_and_secretless() -> None:
    compose = (OPS / "docker-compose.preprod.yml").read_text(encoding="utf-8")
    backend = compose.split("  backend:", maxsplit=1)[1].split(
        "  dce-retention-worker:", maxsplit=1
    )[0]
    assert "SMART_AO_BOAMP_ENABLED: ${SMART_AO_BOAMP_ENABLED:-0}" in backend
    assert "SMART_AO_BOAMP_BASE_URL" in backend
    assert "SMART_AO_BOAMP_TIMEOUT_SECONDS" in backend
    assert "BOAMP_API_TOKEN" not in compose


def test_dce_extraction_wrapper_is_one_shot_and_uses_private_env() -> None:
    wrapper = (OPS / "run-dce-extraction-preprod.sh").read_text(encoding="utf-8")
    assert "[[ $# -ne 2 ]]" in wrapper
    assert "stat -c '%a' \"$ENV_FILE\"" in wrapper
    assert '"$ENV_FILE"' in wrapper
    assert "run --rm --no-deps --no-ansi backend" in wrapper
    assert "python -m app.workers.dce_extraction" in wrapper
    assert '--tenant-id "$tenant_id"' in wrapper
    assert '--dce-document-id "$dce_document_id"' in wrapper


def test_dce_analysis_wrapper_is_one_shot_and_uses_private_env() -> None:
    wrapper = (OPS / "run-dce-analysis-preprod.sh").read_text(encoding="utf-8")
    compose = (OPS / "docker-compose.preprod.yml").read_text(encoding="utf-8")

    assert "[[ $# -ne 2 ]]" in wrapper
    assert "stat -c '%a' \"$ENV_FILE\"" in wrapper
    assert '"$ENV_FILE"' in wrapper
    assert "--profile dce-analysis run --rm --no-deps --no-ansi dce-rc-analysis-runner" in wrapper
    assert "python -m app.workers.dce_analysis" in wrapper
    assert '--tenant-id "$tenant_id"' in wrapper
    assert '--dce-version-id "$dce_version_id"' in wrapper
    assert "dce-rc-analysis-runner:" in compose
    assert 'profiles: ["dce-analysis"]' in compose
    assert 'command: ["python", "-m", "app.workers.dce_analysis"]' in compose
    assert 'restart: "no"' in compose
    assert (
        "dce-rc-analysis-runner"
        not in compose.split("  backend:", maxsplit=1)[1].split(
            "  dce-retention-worker:", maxsplit=1
        )[0]
    )


def test_dce_requirements_wrapper_is_one_shot_and_profiled() -> None:
    wrapper = (OPS / "run-dce-requirements-preprod.sh").read_text(encoding="utf-8")
    compose = (OPS / "docker-compose.preprod.yml").read_text(encoding="utf-8")

    assert "[[ $# -ne 3 ]]" in wrapper
    assert "stat -c '%a' \"$ENV_FILE\"" in wrapper
    assert (
        "--profile dce-requirements run --rm --no-deps --no-ansi dce-requirements-runner"
    ) in wrapper
    assert "python -m app.workers.dce_requirements" in wrapper
    assert '--tenant-id "$tenant_id"' in wrapper
    assert '--dce-version-id "$dce_version_id"' in wrapper
    assert '--dce-rc-analysis-id "$dce_rc_analysis_id"' in wrapper
    assert "dce-requirements-runner:" in compose
    assert 'profiles: ["dce-requirements"]' in compose
    assert 'command: ["python", "-m", "app.workers.dce_requirements"]' in compose
    assert 'restart: "no"' in compose


def test_rag_indexing_is_explicitly_opt_in_and_one_shot() -> None:
    compose = (OPS / "docker-compose.preprod.yml").read_text(encoding="utf-8")
    worker = (OPS / "run-knowledge-embeddings-preprod.sh").read_text(encoding="utf-8")

    assert "SMART_AO_RAG_ENABLED: ${SMART_AO_RAG_ENABLED:-0}" in compose
    assert "SMART_AO_RAG_INDEXING_ENABLED: ${SMART_AO_RAG_INDEXING_ENABLED:-0}" in compose
    assert "SMART_AO_BGE_LOCAL_FILES_ONLY: ${SMART_AO_BGE_LOCAL_FILES_ONLY:-1}" in compose
    assert "python -m app.workers.knowledge_embeddings" in worker
    assert '--tenant-id "$tenant_id"' in worker
    assert '--case-id "$case_id"' in worker
    assert '--dce-version-id "$dce_version_id"' in worker
    assert "[[ $# -ne 3 ]]" in worker
    assert "stat -c '%a' \"$ENV_FILE\"" in worker
    assert "run --rm --no-deps --no-ansi backend" in worker
    assert "ports:" not in worker


def test_rag_runtime_does_not_receive_unrelated_credentials() -> None:
    compose = (OPS / "docker-compose.preprod.yml").read_text(encoding="utf-8")
    backend = compose.split("  backend:", maxsplit=1)[1].split(
        "  dce-retention-worker:", maxsplit=1
    )[0]

    assert "SMART_AO_RAG_ENABLED" in backend
    assert "SMART_AO_RAG_INDEXING_ENABLED" in backend
    assert "SMART_AO_JWT_SIGNING_KEY" in backend
    assert "SMART_AO_SMTP_PASSWORD" in backend
    assert "SMART_AO_INSEE_API_TOKEN" in backend
    assert "SMART_AO_EXPORT_WEBHOOK_SECRET" not in backend


def test_signature_http_configuration_is_backend_only_and_fail_closed() -> None:
    compose = (OPS / "docker-compose.preprod.yml").read_text(encoding="utf-8")
    backend = compose.split("  backend:", maxsplit=1)[1].split(
        "  dce-retention-worker:", maxsplit=1
    )[0]
    retention = compose.split("  dce-retention-worker:", maxsplit=1)[1].split(
        "  submission-export-webhook-worker:", maxsplit=1
    )[0]
    webhook = compose.split("  submission-export-webhook-worker:", maxsplit=1)[1].split(
        "  submission-export-smtp-worker:", maxsplit=1
    )[0]
    smtp = compose.split("  submission-export-smtp-worker:", maxsplit=1)[1].split(
        "\n  postgres:", maxsplit=1
    )[0]

    assert "SMART_AO_SIGNATURE_PROVIDER: ${SMART_AO_SIGNATURE_PROVIDER:-}" in backend
    assert "SMART_AO_SIGNATURE_CALLBACK_SECRET: ${SMART_AO_SIGNATURE_CALLBACK_SECRET:-}" in backend
    for unrelated_service in (retention, webhook, smtp):
        assert "SMART_AO_SIGNATURE_CALLBACK_SECRET" not in unrelated_service
        assert "SMART_AO_SIGNATURE_PROVIDER" not in unrelated_service


def test_cockpit_projection_worker_is_explicitly_profiled_and_internal() -> None:
    compose = (OPS / "docker-compose.preprod.yml").read_text(encoding="utf-8")
    worker = compose.split("  cockpit-projection-worker:", maxsplit=1)[1].split(
        "\n  postgres:", maxsplit=1
    )[0]
    assert 'profiles: ["cockpit-projection"]' in worker
    assert "command: python -m app.workers.cockpit_projection" in worker
    assert (
        "SMART_AO_COCKPIT_PROJECTION_ENABLED: ${SMART_AO_COCKPIT_PROJECTION_ENABLED:-0}"
    ) in worker
    assert "      - internal" in worker
    assert "      - edge" not in worker


def test_deploy_ocr_opt_in_requires_explicit_install_and_local_runtime_preflight() -> None:
    deploy_script = (OPS / "deploy-preprod.sh").read_text(encoding="utf-8")
    assert "validate_ocr_configuration" in deploy_script
    assert "SMART_AO_OCR_ENABLED=1 requires SMART_AO_INSTALL_DOCUMENT_OCR=1" in deploy_script
    assert "validate_ocr_runtime" in deploy_script
    for variable in (
        "SMART_AO_OCR_DET_MODEL_PATH",
        "SMART_AO_OCR_CLS_MODEL_PATH",
        "SMART_AO_OCR_REC_MODEL_PATH",
        "SMART_AO_OCR_REC_KEYS_PATH",
    ):
        assert variable in deploy_script
    assert "compose build --pull backend" in deploy_script
    assert "validate_ocr_runtime\n  compose up -d postgres clamav" in deploy_script


def test_manual_deployment_guide_matches_current_schema_head_and_ocr_flags() -> None:
    guide = (
        ROOT
        / "docs/Actifs/06_Dependances_et_exploitation/SMART_AO_PREPRODUCTION_VPS_RUNBOOK_v0.1.md"
    ).read_text(encoding="utf-8")
    schema = (ROOT / "backend/app/platform/persistence/schema.py").read_text(encoding="utf-8")
    assert f'EXPECTED_ALEMBIC_HEAD = "{EXPECTED_ALEMBIC_HEAD}"' in schema
    assert EXPECTED_ALEMBIC_HEAD in guide
    assert "20260920_0090" in guide
    assert "SMART_AO_INSTALL_DOCUMENT_OCR=0" in guide
    assert "SMART_AO_OCR_ENABLED=0" in guide
    assert "ne télécharge aucun modèle ni dictionnaire" in guide
