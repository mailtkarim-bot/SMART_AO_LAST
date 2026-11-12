#!/usr/bin/env bash
set -Eeuo pipefail

ROOT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
OPS_DIR="${ROOT_DIR}/ops"
ENV_FILE="${SMART_AO_PREPROD_ENV_FILE:-${OPS_DIR}/.env.preprod}"
COMPOSE_FILE="${OPS_DIR}/docker-compose.preprod.yml"
COMPOSE_PROJECT_NAME="${SMART_AO_COMPOSE_PROJECT_NAME:-}"
RESTORE_DB=""
RESTORE_DB_CREATED=0
RESTORE_VOLUME=""
RESTORE_VOLUME_CREATED=0
OBJECTS_MANIFEST=""
RESTORE_STATE_DIR=""
RESTORE_STATE_FILE=""
RESTORE_RUN_ID=""

fail() {
  printf 'ERROR: %s\n' "$*" >&2
  exit 1
}

load_environment() {
  [[ -f "${ENV_FILE}" ]] || fail "missing ${ENV_FILE}"
  [[ "$(stat -c '%a' "${ENV_FILE}")" == "600" ]] || fail "${ENV_FILE} must have mode 600"
  set -a
  # shellcheck disable=SC1090
  source "${ENV_FILE}"
  set +a
  for variable in POSTGRES_DB POSTGRES_USER POSTGRES_PASSWORD; do
    [[ -n "${!variable:-}" ]] || fail "${variable} is required"
    [[ "${!variable}" != REPLACE_WITH_* ]] || fail "${variable} still contains a placeholder"
  done
}

compose() {
  if [[ -n "${COMPOSE_PROJECT_NAME}" ]]; then
    docker compose --project-name "${COMPOSE_PROJECT_NAME}" \
      --env-file "${ENV_FILE}" -f "${COMPOSE_FILE}" "$@"
  else
    docker compose --env-file "${ENV_FILE}" -f "${COMPOSE_FILE}" "$@"
  fi
}

remove_owned_restore_volume() {
  local volume_name="$1" run_id="$2" volume_names volume_run_id
  volume_names="$(docker volume ls --format '{{.Name}}')" || return 1
  if ! grep -Fxq -- "${volume_name}" <<<"${volume_names}"; then
    return 0
  fi
  volume_run_id="$(docker volume inspect --format \
    '{{ index .Labels "com.smartao.restore.run" }}' "${volume_name}")" || return 1
  [[ "${volume_run_id}" == "${run_id}" ]] || return 1
  docker volume rm "${volume_name}" >/dev/null || return 1
}

recover_interrupted_restore() {
  local state_file="$1" expected_run_id="${1##*/restore-}" run_id database_name volume_name extra
  expected_run_id="${expected_run_id%.state}"
  [[ "${expected_run_id}" =~ ^[a-f0-9]{32}$ ]] \
    || { printf 'ERROR: invalid restore state filename\n' >&2; return 1; }
  [[ -f "${state_file}" && ! -L "${state_file}" \
    && "$(stat -c '%a' "${state_file}")" == "600" \
    && "$(stat -c '%u' "${state_file}")" == "$(id -u)" ]] \
    || { printf 'ERROR: unsafe restore state file\n' >&2; return 1; }
  {
    IFS= read -r run_id
    IFS= read -r database_name
    IFS= read -r volume_name
    IFS= read -r extra || true
  } <"${state_file}"
  [[ "${run_id}" == "${expected_run_id}" \
    && "${database_name}" == "smart_ao_restore_${run_id}" \
    && "${volume_name}" == "smart_ao_c5_restore_${run_id}" \
    && -z "${extra}" ]] \
    || { printf 'ERROR: invalid restore state contents\n' >&2; return 1; }

  compose exec -T postgres dropdb --if-exists -U "${POSTGRES_USER}" \
    "${database_name}" >/dev/null \
    || { printf 'ERROR: could not remove interrupted restore database\n' >&2; return 1; }
  remove_owned_restore_volume "${volume_name}" "${run_id}" \
    || { printf 'ERROR: interrupted restore volume ownership check or cleanup failed\n' >&2; return 1; }
  rm -f -- "${state_file}"
}

recover_interrupted_restores() {
  local state_file
  for state_file in "${RESTORE_STATE_DIR}"/restore-*.state; do
    [[ -e "${state_file}" ]] || continue
    recover_interrupted_restore "${state_file}" || return 1
  done
  # A kill while atomically writing the receipt happens before resource creation.
  rm -f -- "${RESTORE_STATE_DIR}"/.restore-*.tmp
}

write_restore_state() {
  local state_tmp="${RESTORE_STATE_DIR}/.restore-${RESTORE_RUN_ID}.tmp"
  (umask 077; printf '%s\n%s\n%s\n' \
    "${RESTORE_RUN_ID}" "${RESTORE_DB}" "${RESTORE_VOLUME}" >"${state_tmp}") \
    || return 1
  chmod 600 "${state_tmp}" || return 1
  mv -- "${state_tmp}" "${RESTORE_STATE_FILE}"
}

usage() {
  cat <<'EOF'
Usage: ops/restore-preprod.sh <backup.sql.gz> [verify]

The restore SQL is loaded into a temporary isolated PostgreSQL database. The
matching C5 quarantine archive is checksum-verified and restored into a
temporary Docker volume; CLEAN C5 object hashes are checked against that
database. Both temporary targets are removed on success or failure. The active
database and quarantine volume are never mounted for writing.
EOF
}

main() {
  [[ "${1:-}" != "" && "${1:-}" != "-h" ]] || { usage; exit 2; }
  command -v docker >/dev/null 2>&1 || fail "docker is required"
  command -v gzip >/dev/null 2>&1 || fail "gzip is required"
  command -v sha256sum >/dev/null 2>&1 || fail "sha256sum is required"
  command -v mktemp >/dev/null 2>&1 || fail "mktemp is required"
  command -v flock >/dev/null 2>&1 || fail "flock is required"
  command -v tr >/dev/null 2>&1 || fail "tr is required"
  local backup_file="$1"
  [[ -f "${backup_file}" ]] || fail "backup does not exist: ${backup_file}"
  load_environment
  if [[ -n "${COMPOSE_PROJECT_NAME}" && ! "${COMPOSE_PROJECT_NAME}" =~ ^[a-z0-9][a-z0-9_-]{0,62}$ ]]; then
    fail "invalid SMART_AO_COMPOSE_PROJECT_NAME"
  fi

  local backup_prefix="${backup_file%.sql.gz}"
  local manifest="${backup_prefix}.sha256"
  local quarantine_archive="${backup_prefix}.dce_quarantine.tar.gz"
  [[ -f "${manifest}" ]] || fail "checksum manifest is missing beside backup"
  [[ -f "${quarantine_archive}" ]] || fail "C5 quarantine archive is missing beside backup"
  local required_file
  local required_path expected_checksum actual_checksum
  for required_path in "${backup_file}" "${quarantine_archive}"; do
    required_file="$(basename -- "${required_path}")"
    expected_checksum="$(awk -v required="${required_file}" \
      '$2 == required { print $1 }' "${manifest}")"
    [[ "${expected_checksum}" =~ ^[a-f0-9]{64}$ ]] \
      || fail "checksum manifest does not uniquely cover ${required_file}"
    actual_checksum="$(sha256sum -- "${required_path}" | awk '{print $1}')"
    [[ "${actual_checksum}" == "${expected_checksum}" ]] \
      || fail "backup checksum mismatch for ${required_file}"
  done

  local postgres_container actual_project state_base docker_context context_hash
  postgres_container="$(compose ps --status running -q postgres | head -n 1)"
  [[ -n "${postgres_container}" ]] || fail "running PostgreSQL container is required"
  actual_project="$(docker inspect --format \
    '{{ index .Config.Labels "com.docker.compose.project" }}' "${postgres_container}")"
  [[ "${actual_project}" =~ ^[a-z0-9][a-z0-9_-]{0,62}$ ]] \
    || fail "cannot resolve the active Compose project"
  if [[ -n "${COMPOSE_PROJECT_NAME}" && "${COMPOSE_PROJECT_NAME}" != "${actual_project}" ]]; then
    fail "configured Compose project does not match the running PostgreSQL container"
  fi
  COMPOSE_PROJECT_NAME="${actual_project}"
  docker_context="$(docker context show)" || fail "cannot determine the active Docker context"
  [[ -n "${docker_context}" ]] || fail "active Docker context name is empty"
  context_hash="$(printf '%s' "${docker_context}" | sha256sum | awk '{print $1}')"
  state_base="${XDG_STATE_HOME:-${HOME:-}/.local/state}"
  [[ -n "${SMART_AO_RESTORE_STATE_DIR:-}" || "${state_base}" != "/.local/state" ]] \
    || fail "HOME or SMART_AO_RESTORE_STATE_DIR is required for protected restore state"
  RESTORE_STATE_DIR="${SMART_AO_RESTORE_STATE_DIR:-${state_base}/smart-ao/restore/${actual_project}-${context_hash:0:16}}"
  [[ ! -L "${RESTORE_STATE_DIR}" ]] || fail "restore state directory must not be a symlink"
  [[ "${RESTORE_STATE_DIR}" == /* ]] || fail "restore state directory must be absolute"
  install -d -m 700 "${RESTORE_STATE_DIR}"
  [[ -d "${RESTORE_STATE_DIR}" && ! -L "${RESTORE_STATE_DIR}" ]] \
    || fail "restore state directory must be a real directory"
  [[ "$(stat -c '%a' "${RESTORE_STATE_DIR}")" == "700" \
    && "$(stat -c '%u' "${RESTORE_STATE_DIR}")" == "$(id -u)" ]] \
    || fail "restore state directory must be owned by this user with mode 700"
  local restore_lock="${RESTORE_STATE_DIR}/restore.lock"
  [[ ! -L "${restore_lock}" ]] || fail "restore lock path must not be a symlink"
  exec 8>"${restore_lock}"
  flock -n 8 || fail "another restore is already running for ${actual_project}"
  recover_interrupted_restores \
    || fail "could not safely recover the interrupted restore resources"

  RESTORE_RUN_ID="$(tr -d '-' </proc/sys/kernel/random/uuid)"
  [[ "${RESTORE_RUN_ID}" =~ ^[a-f0-9]{32}$ ]] || fail "cannot generate a restore run ID"
  RESTORE_DB="smart_ao_restore_${RESTORE_RUN_ID}"
  RESTORE_VOLUME="smart_ao_c5_restore_${RESTORE_RUN_ID}"
  RESTORE_STATE_FILE="${RESTORE_STATE_DIR}/restore-${RESTORE_RUN_ID}.state"
  write_restore_state || fail "could not persist protected restore state"
  cleanup() {
    local exit_status=$? cleanup_failed=0
    trap - EXIT
    if [[ "${RESTORE_DB_CREATED}" == "1" && -n "${RESTORE_DB}" ]]; then
      if compose exec -T postgres dropdb --if-exists -U "${POSTGRES_USER}" \
        "${RESTORE_DB}" >/dev/null 2>&1; then
        RESTORE_DB_CREATED=0
      else
        cleanup_failed=1
      fi
    fi
    if [[ "${RESTORE_VOLUME_CREATED}" == "1" && -n "${RESTORE_VOLUME}" ]]; then
      if remove_owned_restore_volume "${RESTORE_VOLUME}" "${RESTORE_RUN_ID}"; then
        RESTORE_VOLUME_CREATED=0
      else
        cleanup_failed=1
      fi
    fi
    if [[ -n "${OBJECTS_MANIFEST}" ]]; then
      rm -f -- "${OBJECTS_MANIFEST}" || cleanup_failed=1
    fi
    if [[ "${cleanup_failed}" == "0" && -n "${RESTORE_STATE_FILE}" ]]; then
      rm -f -- "${RESTORE_STATE_FILE}" || cleanup_failed=1
    fi
    if [[ "${cleanup_failed}" == "1" ]]; then
      printf 'ERROR: restore cleanup incomplete; protected state retained for recovery\n' >&2
      exit_status=1
    fi
    exit "${exit_status}"
  }
  trap cleanup EXIT

  compose exec -T postgres createdb -U "${POSTGRES_USER}" "${RESTORE_DB}"
  RESTORE_DB_CREATED=1
  gzip -dc -- "${backup_file}" | compose exec -T postgres psql -v ON_ERROR_STOP=1 -U "${POSTGRES_USER}" -d "${RESTORE_DB}" >/dev/null
  local table_count
  table_count="$(compose exec -T postgres psql -U "${POSTGRES_USER}" -d "${RESTORE_DB}" -tAc "SELECT count(*) FROM pg_catalog.pg_tables WHERE schemaname = 'public'")"
  [[ "${table_count}" =~ ^[[:space:]]*[1-9][0-9]*[[:space:]]*$ ]] || fail "restored database has no public tables"
  compose exec -T postgres psql -v ON_ERROR_STOP=1 -U "${POSTGRES_USER}" -d "${RESTORE_DB}" \
    -tAc "SELECT to_regclass('public.tenants'), to_regclass('public.command_receipts'), to_regclass('public.outbox_messages')" \
    | grep -q 'tenants.*command_receipts.*outbox_messages' \
    || fail "restored database is missing required durability tables"

  local expected_head actual_head trigger_count
  expected_head="$(sed -nE 's/^[[:space:]]*EXPECTED_ALEMBIC_HEAD[[:space:]]*=[[:space:]]*[\"'"'"']([^\"'"'"']+)[\"'"'"'].*/\1/p' "${ROOT_DIR}/backend/app/platform/persistence/schema.py")"
  [[ -n "${expected_head}" ]] || fail "cannot determine expected Alembic head"
  actual_head="$(compose exec -T postgres psql -U "${POSTGRES_USER}" -d "${RESTORE_DB}" -tAc "SELECT version_num FROM alembic_version")"
  [[ "${actual_head}" == "${expected_head}" ]] || fail "restored database head ${actual_head} differs from expected ${expected_head}"
  compose exec -T postgres psql -v ON_ERROR_STOP=1 -U "${POSTGRES_USER}" -d "${RESTORE_DB}" \
    -tAc "SELECT to_regclass('public.decision_condition_transitions')" \
    | grep -q 'decision_condition_transitions' \
    || fail "restored database is missing Decision condition transition table"
  trigger_count="$(compose exec -T postgres psql -U "${POSTGRES_USER}" -d "${RESTORE_DB}" -tAc "SELECT count(*) FROM pg_trigger WHERE tgname = 'trg_decision_condition_transitions_append_only' AND NOT tgisinternal")"
  [[ "${trigger_count//[[:space:]]/}" == "1" ]] || fail "restored database is missing append-only Decision condition trigger"

  OBJECTS_MANIFEST="$(mktemp "${TMPDIR:-/tmp}/smart-ao-c5-objects.XXXXXX.tsv")"
  chmod 600 "${OBJECTS_MANIFEST}"
  compose exec -T postgres psql -v ON_ERROR_STOP=1 -U "${POSTGRES_USER}" -d "${RESTORE_DB}" \
    -At -F $'\t' -c "SELECT storage_key, sha256 FROM case_contract_change_evidence_objects WHERE state = 'CLEAN' ORDER BY storage_key" \
    >"${OBJECTS_MANIFEST}"

  local backend_container backend_image created_volume
  backend_container="$(compose ps --status running -q backend | head -n 1)"
  [[ -n "${backend_container}" ]] || fail "backend container is required for isolated C5 restore verification"
  backend_image="$(docker inspect --format '{{.Image}}' "${backend_container}")"
  [[ "${backend_image}" =~ ^sha256:[a-f0-9]{64}$ ]] || fail "cannot resolve the running backend image"
  created_volume="$(docker volume create \
    --label com.smartao.purpose=quarantine-restore-verification \
    --label "com.smartao.restore.run=${RESTORE_RUN_ID}" "${RESTORE_VOLUME}")"
  [[ "${created_volume}" == "${RESTORE_VOLUME}" ]] \
    || fail "could not create isolated quarantine restore volume"
  RESTORE_VOLUME_CREATED=1

  docker run --rm --network none --read-only --user 0 --cap-drop ALL \
    --cap-add DAC_READ_SEARCH \
    --security-opt no-new-privileges:true \
    --mount "type=volume,src=${RESTORE_VOLUME},dst=/restore" \
    --mount "type=bind,src=${quarantine_archive},dst=/archive.tar.gz,readonly" \
    --mount "type=bind,src=${OBJECTS_MANIFEST},dst=/objects.tsv,readonly" \
    --mount "type=bind,src=${OPS_DIR}/verify_quarantine_restore.py,dst=/verify.py,readonly" \
    "${backend_image}" python /verify.py --archive /archive.tar.gz --destination /restore \
    --objects-manifest /objects.tsv
  remove_owned_restore_volume "${RESTORE_VOLUME}" "${RESTORE_RUN_ID}" \
    || fail "could not remove isolated quarantine restore volume"
  RESTORE_VOLUME_CREATED=0
  RESTORE_VOLUME=""

  compose exec -T postgres dropdb --if-exists -U "${POSTGRES_USER}" "${RESTORE_DB}" >/dev/null
  RESTORE_DB_CREATED=0
  RESTORE_DB=""
  printf 'Isolated restore verification passed for %s (tables=%s)\n' \
    "${backup_file}" "${table_count//[[:space:]]/}"
}

main "$@"
