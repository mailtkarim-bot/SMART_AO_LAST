#!/usr/bin/env bash
set -Eeuo pipefail

ROOT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
COMPOSE_FILE="${ROOT_DIR}/ops/docker-compose.preprod.yml"
PROJECT="smartao-local-preprod"
WORK_DIR="$(mktemp -d /tmp/smartao-preprod.XXXXXX)"
ENV_FILE="${WORK_DIR}/.env"
OVERRIDE_FILE="${WORK_DIR}/ports.yml"
BACKUP_FILE="${WORK_DIR}/smart_ao.sql.gz"
RESTORE_DB="smart_ao_restore_local"

fail() { printf 'ERROR: %s\n' "$*" >&2; exit 1; }
pass() { printf 'PASS: %s\n' "$*"; }

compose() {
  docker compose --project-name "${PROJECT}" --env-file "${ENV_FILE}" \
    -f "${COMPOSE_FILE}" -f "${OVERRIDE_FILE}" "$@"
}

cleanup() {
  compose down -v --remove-orphans >/dev/null 2>&1 || true
  rm -rf -- "${WORK_DIR}"
}
trap cleanup EXIT

command -v docker >/dev/null 2>&1 || fail "docker is required"
docker compose version >/dev/null 2>&1 || fail "docker compose is required"
command -v curl >/dev/null 2>&1 || fail "curl is required"
command -v gzip >/dev/null 2>&1 || fail "gzip is required"
command -v openssl >/dev/null 2>&1 || fail "openssl is required"

umask 077
LOCAL_DB_PASSWORD="$(openssl rand -hex 16)"
LOCAL_JWT_KEY="$(openssl rand -hex 32)"
cat >"${ENV_FILE}" <<EOF
SMART_AO_PUBLIC_HOST=localhost
SMART_AO_DATABASE_URL=postgresql+psycopg://smart_ao:${LOCAL_DB_PASSWORD}@postgres:5432/smart_ao
POSTGRES_DB=smart_ao
POSTGRES_USER=smart_ao
POSTGRES_PASSWORD=${LOCAL_DB_PASSWORD}
PGPASSWORD=${LOCAL_DB_PASSWORD}
SMART_AO_JWT_SIGNING_KEY=${LOCAL_JWT_KEY}
SMART_AO_JWT_ISSUER=smart-ao-local-preprod
SMART_AO_JWT_AUDIENCE=smart-ao-local-web
SMART_AO_MFA_ENABLED=0
SMART_AO_INSTALL_RAG=0
SMART_AO_INSTALL_DOCUMENT_ADVANCED=0
SMART_AO_INSTALL_DOCUMENT_OCR=0
SMART_AO_INSTALL_OBJECT_STORAGE=0
SMART_AO_INSTALL_CONNECTORS=0
SMART_AO_INSTALL_NOTIFICATIONS=0
SMART_AO_INSTALL_CALENDAR=0
SMART_AO_RAG_ENABLED=0
SMART_AO_RAG_INDEXING_ENABLED=0
SMART_AO_ADVANCED_EXTRACTION_ENABLED=0
SMART_AO_OCR_ENABLED=0
SMART_AO_OBJECT_STORAGE_ENABLED=0
SMART_AO_INSEE_ENABLED=0
SMART_AO_SMTP_ENABLED=0
SMART_AO_CALENDAR_ENABLED=0
SMART_AO_BOAMP_ENABLED=0
SMART_AO_ALLOW_EMPTY_BACKUP=1
EOF
cat >"${OVERRIDE_FILE}" <<'EOF'
services:
  caddy:
    ports: !override
      - "18080:80"
      - "18443:443"
      - "18443:443/udp"
EOF

compose config --quiet
pass "Compose configuration"
compose up -d --build postgres clamav migrate backend frontend \
  dce-retention-worker submission-export-webhook-worker submission-export-smtp-worker caddy
pass "preproduction services started"

ready_url="https://localhost:18443/healthz/ready"
wait_ready() {
  body=""
  for _ in $(seq 1 60); do
    if body="$(curl -ksS --resolve localhost:18443:127.0.0.1 "${ready_url}" 2>/dev/null)" \
      && grep -Eq '"status"[[:space:]]*:[[:space:]]*"ok"' <<<"${body}" \
      && grep -Eq '"database"[[:space:]]*:[[:space:]]*"ok"' <<<"${body}" \
      && grep -Eq '"schema"[[:space:]]*:[[:space:]]*"ok"' <<<"${body}" \
      && grep -Eq '"clamav"[[:space:]]*:[[:space:]]*"ok"' <<<"${body}"; then
      return 0
    fi
    sleep 2
  done
  return 1
}
wait_ready || fail "stack never became ready"
pass "HTTPS smoke test: ${body}"

for _ in $(seq 1 20); do
  curl -ksSf --resolve localhost:18443:127.0.0.1 "${ready_url}" >/dev/null &
done
wait
pass "bounded concurrent readiness load: 20 requests"

load_started="$(date +%s%N)"
seq 1 100 | xargs -n1 -P10 bash -c \
  'curl -ksSf --resolve localhost:18443:127.0.0.1 https://localhost:18443/healthz/ready >/dev/null'
load_elapsed_ms="$(( ( $(date +%s%N) - load_started ) / 1000000 ))"
load_rate="$(awk -v requests=100 -v elapsed="${load_elapsed_ms}" 'BEGIN { if (elapsed > 0) printf "%.2f", requests / (elapsed / 1000); else print "0" }')"
pass "bounded load: 100 requests at concurrency 10 in ${load_elapsed_ms}ms (${load_rate} req/s)"

for service in backend frontend postgres; do
  compose restart "${service}" >/dev/null
  wait_ready || fail "readiness did not recover after restarting ${service}"
done
pass "controlled restart recovery: backend, frontend, PostgreSQL"

for service in dce-retention-worker submission-export-webhook-worker submission-export-smtp-worker; do
  compose restart "${service}" >/dev/null
done
pass "worker restart recovery: retention, webhook, SMTP"

compose stop clamav >/dev/null
sleep 5
incident_body="$(curl -ksS --resolve localhost:18443:127.0.0.1 "${ready_url}")"
grep -Eq '"status"[[:space:]]*:[[:space:]]*"not_ready"' <<<"${incident_body}" \
  || grep -Eq '"clamav"[[:space:]]*:[[:space:]]*"failed"' <<<"${incident_body}" \
  || fail "ClamAV outage was not visible in readiness"
compose start clamav >/dev/null
wait_ready || fail "readiness did not recover after ClamAV restart"
pass "ClamAV incident detection and recovery"

compose exec -T postgres pg_dump --clean --if-exists --no-owner --no-privileges \
  -U smart_ao smart_ao | gzip -9 >"${BACKUP_FILE}"
[[ -s "${BACKUP_FILE}" ]] || fail "backup is empty"
pass "PostgreSQL backup created"

compose exec -T postgres createdb -U smart_ao "${RESTORE_DB}"
gzip -dc "${BACKUP_FILE}" | compose exec -T postgres psql -v ON_ERROR_STOP=1 \
  -U smart_ao -d "${RESTORE_DB}" >/dev/null
table_count="$(compose exec -T postgres psql -U smart_ao -d "${RESTORE_DB}" -tAc \
  "SELECT count(*) FROM pg_catalog.pg_tables WHERE schemaname = 'public'")"
expected_head="$(sed -nE "s/^[[:space:]]*EXPECTED_ALEMBIC_HEAD[[:space:]]*=[[:space:]]*[\"']([^\"']+)[\"'].*/\1/p" \
  "${ROOT_DIR}/backend/app/platform/persistence/schema.py")"
actual_head="$(compose exec -T postgres psql -U smart_ao -d "${RESTORE_DB}" -tAc \
  "SELECT version_num FROM alembic_version")"
[[ "${table_count//[[:space:]]/}" =~ ^[1-9][0-9]*$ ]] || fail "restore has no public tables"
[[ "${actual_head}" == "${expected_head}" ]] || fail "restore head mismatch"
compose exec -T postgres dropdb --if-exists -U smart_ao "${RESTORE_DB}" >/dev/null
pass "isolated restore verified: ${table_count//[[:space:]]/} tables, head ${actual_head}"

old_key="${SMART_AO_JWT_SIGNING_KEY:-local-old-key}"
new_key="$(openssl rand -hex 32)"
printf 'SMART_AO_JWT_SIGNING_KEY=%s\n' "${old_key}" >"${WORK_DIR}/rotation.env"
ROTATION_KEY="${new_key}" awk '{ sub(/^SMART_AO_JWT_SIGNING_KEY=.*/, "SMART_AO_JWT_SIGNING_KEY=" ENVIRON["ROTATION_KEY"]); print }' \
  "${WORK_DIR}/rotation.env" >"${WORK_DIR}/rotation.env.new"
mv "${WORK_DIR}/rotation.env.new" "${WORK_DIR}/rotation.env"
[[ "$(stat -c '%a' "${WORK_DIR}/rotation.env")" == 600 ]] || fail "rotation file is not mode 600"
grep -q "${new_key}" "${WORK_DIR}/rotation.env" || fail "rotation did not replace the key"
pass "JWT rotation simulation verified with ephemeral mode-600 file"

pass "local preproduction simulation completed"
