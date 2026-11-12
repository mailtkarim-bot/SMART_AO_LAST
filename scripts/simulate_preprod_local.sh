#!/usr/bin/env bash
set -Eeuo pipefail

ROOT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT_DIR}"
COMPOSE_FILE="${ROOT_DIR}/ops/docker-compose.preprod.yml"
WORK_DIR="$(mktemp -d /tmp/smartao-preprod.XXXXXX)"
WORK_ID="${WORK_DIR##*.}"
PROJECT="smartao-local-preprod-${WORK_ID,,}"
ENV_FILE="${WORK_DIR}/.env"
OVERRIDE_FILE="${WORK_DIR}/ports.yml"
OPS_BACKUP_DIR="${WORK_DIR}/ops-backups"
RESTORE_STATE_DIR="${WORK_DIR}/restore-state"
C5_HOST_STORAGE_DIR="${WORK_DIR}/c5-evidence"
BACKUP_TEST_PGID=""
BACKUP_TEST_LAUNCH_PID=""
RESTORE_FIXTURE_VOLUME=""
RESTORE_FIXTURE_RUN_ID=""
RESTORE_FIXTURE_DB_ID=""
RESTORE_FIXTURE_DB_NAME=""
RESTORE_FIXTURE_LABEL_RUN_ID=""
RESTORE_FIXTURE_STATE_FILE=""
RESTORE_FIXTURE_STATE_TARGET=""
RESTORE_FAILURE_DB=""
RESTORE_FAILURE_RUN_ID=""
RESTORE_FAILURE_VOLUME=""
RESTORE_FAILURE_STATE=""

fail() { printf 'ERROR: %s\n' "$*" >&2; exit 1; }
pass() { printf 'PASS: %s\n' "$*"; }

compose() {
  docker compose --project-name "${PROJECT}" --env-file "${ENV_FILE}" \
    -f "${COMPOSE_FILE}" -f "${OVERRIDE_FILE}" "$@"
}

container_ip_on_internal() {
  local container="$1"
  local template="{{range \$name, \$network := .NetworkSettings.Networks}}{{if eq \$name \"${PROJECT}_internal\"}}{{\$network.IPAddress}}{{end}}{{end}}"
  docker inspect --format "${template}" "${container}"
}

active_clean_object_hashes() {
  local backend_container="$1" clean_rows storage_key expected_sha256 actual_sha256
  clean_rows="$(compose exec -T postgres psql -U smart_ao -d smart_ao -At -F $'\t' \
    -c "SELECT storage_key, sha256 FROM case_contract_change_evidence_objects WHERE state = 'CLEAN' ORDER BY storage_key")" \
    || return 1
  [[ -n "${clean_rows}" ]] || return 1
  while IFS=$'\t' read -r storage_key expected_sha256; do
    [[ "${storage_key}" =~ ^[A-Za-z0-9._/-]+$ \
      && "${storage_key}" != /* && "${storage_key}" != *..* \
      && "${expected_sha256}" =~ ^[a-f0-9]{64}$ ]] || return 1
    actual_sha256="$(docker exec "${backend_container}" sha256sum -- \
      "/var/lib/smart_ao/dce-quarantine/${storage_key}" | awk '{print $1}')" \
      || return 1
    [[ "${actual_sha256}" == "${expected_sha256}" ]] || return 1
    printf '%s\t%s\n' "${storage_key}" "${actual_sha256}"
  done <<<"${clean_rows}"
}

run_malformed_receipt_cycle() {
  local cycle="$1" created_fixture_volume receipt_hash_before backup_hash_before sentinel_db_name
  local active_hashes_before active_hashes_after sentinel_marker database_count
  RESTORE_FIXTURE_RUN_ID="$(tr -d '-' </proc/sys/kernel/random/uuid)"
  RESTORE_FIXTURE_DB_ID="$(tr -d '-' </proc/sys/kernel/random/uuid)"
  while [[ "${RESTORE_FIXTURE_DB_ID}" == "${RESTORE_FIXTURE_RUN_ID}" ]]; do
    RESTORE_FIXTURE_DB_ID="$(tr -d '-' </proc/sys/kernel/random/uuid)"
  done
  RESTORE_FIXTURE_DB_NAME="smart_ao_restore_${RESTORE_FIXTURE_DB_ID}"
  sentinel_db_name="${RESTORE_FIXTURE_DB_NAME}"
  RESTORE_FIXTURE_VOLUME="smart_ao_c5_restore_${RESTORE_FIXTURE_RUN_ID}"
  RESTORE_FIXTURE_LABEL_RUN_ID="${RESTORE_FIXTURE_RUN_ID}"
  RESTORE_FIXTURE_STATE_FILE="${RESTORE_STATE_DIR}/restore-${RESTORE_FIXTURE_RUN_ID}.state"
  [[ ! -e "${RESTORE_FIXTURE_STATE_FILE}" ]] \
    || fail "malformed-receipt fixture state path already exists"
  database_count="$(compose exec -T postgres psql -U smart_ao -d smart_ao -tAc \
    "SELECT count(*) FROM pg_database WHERE datname = '${RESTORE_FIXTURE_DB_NAME}'")"
  [[ "${database_count//[[:space:]]/}" == "0" ]] \
    || fail "malformed-receipt sentinel database name is already in use"
  compose exec -T postgres createdb -U smart_ao "${RESTORE_FIXTURE_DB_NAME}"
  compose exec -T postgres psql -v ON_ERROR_STOP=1 -U smart_ao \
    -d "${RESTORE_FIXTURE_DB_NAME}" \
    -c "CREATE TABLE restore_sentinel (marker text PRIMARY KEY); INSERT INTO restore_sentinel VALUES ('must-survive');" \
    >/dev/null
  created_fixture_volume="$(docker volume create \
    --label com.smartao.purpose=quarantine-restore-verification \
    --label "com.smartao.restore.run=${RESTORE_FIXTURE_LABEL_RUN_ID}" \
    "${RESTORE_FIXTURE_VOLUME}")"
  [[ "${created_fixture_volume}" == "${RESTORE_FIXTURE_VOLUME}" ]] \
    || fail "could not create malformed-receipt sentinel volume"
  (umask 077; printf '%s\n%s\n%s\n' \
    "${RESTORE_FIXTURE_RUN_ID}" "${RESTORE_FIXTURE_DB_NAME}" \
    "${RESTORE_FIXTURE_VOLUME}" >"${RESTORE_FIXTURE_STATE_FILE}")
  chmod 600 "${RESTORE_FIXTURE_STATE_FILE}"
  receipt_hash_before="$(sha256sum -- "${RESTORE_FIXTURE_STATE_FILE}" | awk '{print $1}')"
  backup_hash_before="$(sha256sum -- "${BACKUP_FILE}" "${QUARANTINE_BACKUP_FILE}" \
    "${BACKUP_MANIFEST}" | sha256sum | awk '{print $1}')"
  active_hashes_before="$(active_clean_object_hashes "${backend_container}")" \
    || fail "could not verify active C5 hashes before malformed-receipt refusal"
  [[ -n "${active_hashes_before}" ]] \
    || fail "active C5 hash proof is empty before malformed-receipt refusal"

  if SMART_AO_PREPROD_ENV_FILE="${ENV_FILE}" \
    SMART_AO_COMPOSE_PROJECT_NAME="${PROJECT}" \
    SMART_AO_RESTORE_STATE_DIR="${RESTORE_STATE_DIR}" \
    "${ROOT_DIR}/ops/restore-preprod.sh" "${BACKUP_FILE}" \
    >"${WORK_DIR}/restore-malformed-receipt-${cycle}.log" 2>&1; then
    fail "restore accepted a mismatched receipt database"
  fi
  grep -q "invalid restore state contents" \
    "${WORK_DIR}/restore-malformed-receipt-${cycle}.log" \
    || fail "malformed-receipt restore failed for an unexpected reason"
  database_count="$(compose exec -T postgres psql -U smart_ao -d smart_ao -tAc \
    "SELECT count(*) FROM pg_database WHERE datname = '${RESTORE_FIXTURE_DB_NAME}'")"
  [[ "${database_count//[[:space:]]/}" == "1" ]] \
    || fail "malformed-receipt restore dropped sentinel database"
  [[ "$(compose exec -T postgres psql -U smart_ao -d smart_ao -tAc \
    "SELECT count(*) FROM pg_database WHERE datname LIKE 'smart_ao_restore_%'")" \
    =~ ^[[:space:]]*1[[:space:]]*$ ]] \
    || fail "malformed-receipt restore created or removed an isolated database"
  [[ "$(compose exec -T postgres psql -U smart_ao -d smart_ao -tAc \
    "SELECT count(*) FROM pg_database WHERE datname = 'smart_ao_restore_${RESTORE_FIXTURE_RUN_ID}'")" \
    =~ ^[[:space:]]*0[[:space:]]*$ ]] \
    || fail "malformed-receipt restore created the receipt database"
  sentinel_marker="$(compose exec -T postgres psql -U smart_ao \
    -d "${RESTORE_FIXTURE_DB_NAME}" -tAc \
    "SELECT marker FROM restore_sentinel")"
  [[ "${sentinel_marker//[[:space:]]/}" == "must-survive" ]] \
    || fail "malformed-receipt restore changed sentinel database contents"
  [[ "$(docker volume inspect --format '{{.Name}}' "${RESTORE_FIXTURE_VOLUME}")" \
    == "${RESTORE_FIXTURE_VOLUME}" ]] \
    || fail "malformed-receipt restore removed its volume"
  [[ "$(docker volume inspect --format \
    '{{ index .Labels "com.smartao.restore.run" }}' "${RESTORE_FIXTURE_VOLUME}")" \
    == "${RESTORE_FIXTURE_LABEL_RUN_ID}" ]] \
    || fail "malformed-receipt restore changed sentinel volume label"
  [[ "$(docker volume ls -q \
    --filter label=com.smartao.purpose=quarantine-restore-verification)" \
    == "${RESTORE_FIXTURE_VOLUME}" ]] \
    || fail "malformed-receipt restore created or removed a temporary volume"
  [[ -f "${RESTORE_FIXTURE_STATE_FILE}" && ! -L "${RESTORE_FIXTURE_STATE_FILE}" \
    && "$(stat -c '%a' "${RESTORE_FIXTURE_STATE_FILE}")" == "600" \
    && "$(sha256sum -- "${RESTORE_FIXTURE_STATE_FILE}" | awk '{print $1}')" == "${receipt_hash_before}" ]] \
    || fail "malformed-receipt restore changed its receipt"
  [[ "$(docker inspect --format \
    '{{range .Mounts}}{{if eq .Destination "/var/lib/smart_ao/dce-quarantine"}}{{.Name}}{{end}}{{end}}' \
    "${backend_container}")" == "${active_quarantine_volume}" ]] \
    || fail "malformed-receipt restore changed the active quarantine volume"
  active_hashes_after="$(active_clean_object_hashes "${backend_container}")" \
    || fail "could not verify active C5 hashes after malformed-receipt refusal"
  [[ "${active_hashes_after}" == "${active_hashes_before}" ]] \
    || fail "malformed receipt retry changed active C5 hashes"
  [[ "$(sha256sum -- "${BACKUP_FILE}" "${QUARANTINE_BACKUP_FILE}" \
    "${BACKUP_MANIFEST}" | sha256sum | awk '{print $1}')" == "${backup_hash_before}" ]] \
    || fail "malformed receipt retry changed finalized backups"
  (cd "${OPS_BACKUP_DIR}" && sha256sum --check "$(basename -- "${BACKUP_MANIFEST}")" >/dev/null)

  # Clean only the sentinel DB/volume/receipt that this fixture created.
  [[ "${RESTORE_FIXTURE_DB_NAME}" == "smart_ao_restore_${RESTORE_FIXTURE_DB_ID}" \
    && "${RESTORE_FIXTURE_DB_ID}" =~ ^[a-f0-9]{32}$ ]] \
    || fail "test harness lost ownership of its sentinel database"
  compose exec -T postgres dropdb --if-exists -U smart_ao \
    "${RESTORE_FIXTURE_DB_NAME}" >/dev/null
  [[ "$(docker volume inspect --format \
    '{{ index .Labels "com.smartao.restore.run" }}' "${RESTORE_FIXTURE_VOLUME}")" \
    == "${RESTORE_FIXTURE_LABEL_RUN_ID}" ]] \
    || fail "test harness lost ownership of its sentinel volume"
  docker volume rm "${RESTORE_FIXTURE_VOLUME}" >/dev/null
  rm -f -- "${RESTORE_FIXTURE_STATE_FILE}"
  RESTORE_FIXTURE_VOLUME=""
  RESTORE_FIXTURE_RUN_ID=""
  RESTORE_FIXTURE_DB_ID=""
  RESTORE_FIXTURE_DB_NAME=""
  RESTORE_FIXTURE_LABEL_RUN_ID=""
  RESTORE_FIXTURE_STATE_FILE=""
  database_count="$(compose exec -T postgres psql -U smart_ao -d smart_ao -tAc \
    "SELECT count(*) FROM pg_database WHERE datname = '${sentinel_db_name}'")"
  [[ "${database_count//[[:space:]]/}" == "0" ]] \
    || fail "test harness did not clean its sentinel database"
  [[ -z "$(docker volume ls -q \
    --filter label=com.smartao.purpose=quarantine-restore-verification)" ]] \
    || fail "test harness did not clean its sentinel volume"
}

run_unsafe_receipt_cycle() {
  local receipt_kind="$1" cycle="$2" sentinel_marker receipt_hash_before target_hash_before
  local backup_hash_before active_hashes_before active_hashes_after created_fixture_volume
  local restore_log error_phrase database_count volume_names
  RESTORE_FIXTURE_RUN_ID="$(tr -d '-' </proc/sys/kernel/random/uuid)"
  RESTORE_FIXTURE_DB_ID="$(tr -d '-' </proc/sys/kernel/random/uuid)"
  while [[ "${RESTORE_FIXTURE_DB_ID}" == "${RESTORE_FIXTURE_RUN_ID}" ]]; do
    RESTORE_FIXTURE_DB_ID="$(tr -d '-' </proc/sys/kernel/random/uuid)"
  done
  RESTORE_FIXTURE_DB_NAME="smart_ao_restore_${RESTORE_FIXTURE_DB_ID}"
  RESTORE_FIXTURE_VOLUME="smart_ao_c5_restore_${RESTORE_FIXTURE_RUN_ID}"
  RESTORE_FIXTURE_LABEL_RUN_ID="${RESTORE_FIXTURE_RUN_ID}"
  RESTORE_FIXTURE_STATE_FILE="${RESTORE_STATE_DIR}/restore-${RESTORE_FIXTURE_RUN_ID}.state"
  sentinel_marker="${receipt_kind}-${cycle}-must-survive"
  restore_log="${WORK_DIR}/restore-unsafe-${receipt_kind}-${cycle}.log"
  error_phrase="unsafe restore state file"
  [[ ! -e "${RESTORE_FIXTURE_STATE_FILE}" && ! -L "${RESTORE_FIXTURE_STATE_FILE}" ]] \
    || fail "unsafe-receipt fixture state path already exists"
  if [[ "${receipt_kind}" == "symlink" ]]; then
    install -d -m 700 "${WORK_DIR}/restore-receipt-sentinels"
    RESTORE_FIXTURE_STATE_TARGET="${WORK_DIR}/restore-receipt-sentinels/${RESTORE_FIXTURE_RUN_ID}.state"
    (umask 077; printf '%s\n%s\n%s\n' \
      "${RESTORE_FIXTURE_RUN_ID}" "${RESTORE_FIXTURE_DB_NAME}" \
      "${RESTORE_FIXTURE_VOLUME}" >"${RESTORE_FIXTURE_STATE_TARGET}")
    chmod 600 "${RESTORE_FIXTURE_STATE_TARGET}"
    ln -s -- "${RESTORE_FIXTURE_STATE_TARGET}" "${RESTORE_FIXTURE_STATE_FILE}"
    [[ -L "${RESTORE_FIXTURE_STATE_FILE}" ]] \
      || fail "symlink receipt fixture was not created as a symlink"
    target_hash_before="$(sha256sum -- "${RESTORE_FIXTURE_STATE_TARGET}" | awk '{print $1}')"
  elif [[ "${receipt_kind}" == "permissive" ]]; then
    RESTORE_FIXTURE_STATE_TARGET=""
    (umask 077; printf '%s\n%s\n%s\n' \
      "${RESTORE_FIXTURE_RUN_ID}" "${RESTORE_FIXTURE_DB_NAME}" \
      "${RESTORE_FIXTURE_VOLUME}" >"${RESTORE_FIXTURE_STATE_FILE}")
    chmod 644 "${RESTORE_FIXTURE_STATE_FILE}"
  else
    fail "unknown unsafe-receipt fixture kind"
  fi
  receipt_hash_before="$(sha256sum -- "${RESTORE_FIXTURE_STATE_TARGET:-${RESTORE_FIXTURE_STATE_FILE}}" | awk '{print $1}')"
  compose exec -T postgres createdb -U smart_ao "${RESTORE_FIXTURE_DB_NAME}"
  compose exec -T postgres psql -v ON_ERROR_STOP=1 -U smart_ao \
    -d "${RESTORE_FIXTURE_DB_NAME}" \
    -c "CREATE TABLE restore_sentinel (marker text PRIMARY KEY); INSERT INTO restore_sentinel VALUES ('${sentinel_marker}');" \
    >/dev/null
  created_fixture_volume="$(docker volume create \
    --label com.smartao.purpose=quarantine-restore-verification \
    --label "com.smartao.restore.run=${RESTORE_FIXTURE_LABEL_RUN_ID}" \
    "${RESTORE_FIXTURE_VOLUME}")"
  [[ "${created_fixture_volume}" == "${RESTORE_FIXTURE_VOLUME}" ]] \
    || fail "could not create unsafe-receipt sentinel volume"

  backup_hash_before="$(sha256sum -- "${BACKUP_FILE}" "${QUARANTINE_BACKUP_FILE}" \
    "${BACKUP_MANIFEST}" | sha256sum | awk '{print $1}')"
  active_hashes_before="$(active_clean_object_hashes "${backend_container}")" \
    || fail "could not verify active C5 hashes before unsafe-receipt refusal"
  [[ -n "${active_hashes_before}" ]] \
    || fail "active C5 hash proof is empty before unsafe-receipt refusal"

  if SMART_AO_PREPROD_ENV_FILE="${ENV_FILE}" \
    SMART_AO_COMPOSE_PROJECT_NAME="${PROJECT}" \
    SMART_AO_RESTORE_STATE_DIR="${RESTORE_STATE_DIR}" \
    "${ROOT_DIR}/ops/restore-preprod.sh" "${BACKUP_FILE}" \
    >"${restore_log}" 2>&1; then
    if [[ "${receipt_kind}" == "symlink" ]]; then
      fail "restore followed a symlinked state receipt"
    fi
    fail "restore accepted a mode-0644 state receipt"
  fi
  grep -q "unsafe restore state file" "${restore_log}" \
    || fail "unsafe-receipt restore refused for an unexpected reason"
  database_count="$(compose exec -T postgres psql -U smart_ao -d smart_ao -tAc \
    "SELECT count(*) FROM pg_database WHERE datname = '${RESTORE_FIXTURE_DB_NAME}'")"
  [[ "${database_count//[[:space:]]/}" == "1" ]] \
    || fail "unsafe-receipt refusal removed sentinel database"
  [[ "$(compose exec -T postgres psql -U smart_ao -d "${RESTORE_FIXTURE_DB_NAME}" -tAc \
    "SELECT marker FROM restore_sentinel")" == "${sentinel_marker}" ]] \
    || fail "unsafe-receipt refusal changed sentinel database contents"
  [[ "$(compose exec -T postgres psql -U smart_ao -d smart_ao -tAc \
    "SELECT count(*) FROM pg_database WHERE datname LIKE 'smart_ao_restore_%'")" \
    =~ ^[[:space:]]*1[[:space:]]*$ ]] \
    || fail "unsafe-receipt refusal created or removed an isolated database"
  [[ "$(docker volume inspect --format '{{.Name}}' "${RESTORE_FIXTURE_VOLUME}")" \
    == "${RESTORE_FIXTURE_VOLUME}" ]] \
    || fail "unsafe-receipt refusal removed sentinel volume"
  [[ "$(docker volume inspect --format \
    '{{ index .Labels "com.smartao.restore.run" }}' "${RESTORE_FIXTURE_VOLUME}")" \
    == "${RESTORE_FIXTURE_LABEL_RUN_ID}" ]] \
    || fail "unsafe-receipt refusal changed sentinel volume label"
  volume_names="$(docker volume ls -q --filter label=com.smartao.purpose=quarantine-restore-verification)"
  [[ "${volume_names}" == "${RESTORE_FIXTURE_VOLUME}" ]] \
    || fail "unsafe-receipt refusal created or removed a temporary volume"
  if [[ "${receipt_kind}" == "symlink" ]]; then
    [[ -L "${RESTORE_FIXTURE_STATE_FILE}" \
      && "$(readlink -- "${RESTORE_FIXTURE_STATE_FILE}")" == "${RESTORE_FIXTURE_STATE_TARGET}" \
      && "$(sha256sum -- "${RESTORE_FIXTURE_STATE_TARGET}" | awk '{print $1}')" == "${target_hash_before}" ]] \
      || fail "state receipt target changed after refusal"
  else
    [[ -f "${RESTORE_FIXTURE_STATE_FILE}" && ! -L "${RESTORE_FIXTURE_STATE_FILE}" \
      && "$(stat -c '%a' "${RESTORE_FIXTURE_STATE_FILE}")" == "644" \
      && "$(sha256sum -- "${RESTORE_FIXTURE_STATE_FILE}" | awk '{print $1}')" == "${receipt_hash_before}" ]] \
      || fail "permissive state receipt changed after refusal"
  fi
  [[ "$(docker inspect --format \
    '{{range .Mounts}}{{if eq .Destination "/var/lib/smart_ao/dce-quarantine"}}{{.Name}}{{end}}{{end}}' \
    "${backend_container}")" == "${active_quarantine_volume}" ]] \
    || fail "unsafe-receipt refusal changed active quarantine volume"
  active_hashes_after="$(active_clean_object_hashes "${backend_container}")" \
    || fail "could not verify active C5 hashes after unsafe-receipt refusal"
  [[ "${active_hashes_after}" == "${active_hashes_before}" ]] \
    || fail "unsafe-receipt refusal changed active C5 hashes"
  [[ "$(sha256sum -- "${BACKUP_FILE}" "${QUARANTINE_BACKUP_FILE}" \
    "${BACKUP_MANIFEST}" | sha256sum | awk '{print $1}')" == "${backup_hash_before}" ]] \
    || fail "unsafe-receipt refusal changed finalized backups"
  (cd "${OPS_BACKUP_DIR}" && sha256sum --check "$(basename -- "${BACKUP_MANIFEST}")" >/dev/null)

  [[ "${RESTORE_FIXTURE_DB_NAME}" == "smart_ao_restore_${RESTORE_FIXTURE_DB_ID}" \
    && "${RESTORE_FIXTURE_DB_ID}" =~ ^[a-f0-9]{32}$ ]] \
    || fail "test harness lost ownership of unsafe-receipt sentinel database"
  compose exec -T postgres dropdb --if-exists -U smart_ao \
    "${RESTORE_FIXTURE_DB_NAME}" >/dev/null
  [[ "$(docker volume inspect --format \
    '{{ index .Labels "com.smartao.restore.run" }}' "${RESTORE_FIXTURE_VOLUME}")" \
    == "${RESTORE_FIXTURE_LABEL_RUN_ID}" ]] \
    || fail "test harness lost ownership of unsafe-receipt sentinel volume"
  docker volume rm "${RESTORE_FIXTURE_VOLUME}" >/dev/null
  if [[ -n "${RESTORE_FIXTURE_STATE_TARGET}" ]]; then
    [[ -L "${RESTORE_FIXTURE_STATE_FILE}" \
      && "$(readlink -- "${RESTORE_FIXTURE_STATE_FILE}")" == "${RESTORE_FIXTURE_STATE_TARGET}" \
      && "$(sha256sum -- "${RESTORE_FIXTURE_STATE_TARGET}" | awk '{print $1}')" == "${target_hash_before}" ]] \
      || fail "refusing to clean an altered symlink fixture target"
    rm -f -- "${RESTORE_FIXTURE_STATE_FILE}" "${RESTORE_FIXTURE_STATE_TARGET}"
  else
    [[ -f "${RESTORE_FIXTURE_STATE_FILE}" && ! -L "${RESTORE_FIXTURE_STATE_FILE}" \
      && "$(stat -c '%a' "${RESTORE_FIXTURE_STATE_FILE}")" == "644" \
      && "$(sha256sum -- "${RESTORE_FIXTURE_STATE_FILE}" | awk '{print $1}')" == "${receipt_hash_before}" ]] \
      || fail "refusing to clean an altered permissive receipt fixture"
    rm -f -- "${RESTORE_FIXTURE_STATE_FILE}"
  fi
  RESTORE_FIXTURE_VOLUME=""
  RESTORE_FIXTURE_RUN_ID=""
  RESTORE_FIXTURE_DB_ID=""
  RESTORE_FIXTURE_DB_NAME=""
  RESTORE_FIXTURE_LABEL_RUN_ID=""
  RESTORE_FIXTURE_STATE_FILE=""
  RESTORE_FIXTURE_STATE_TARGET=""
  database_count="$(compose exec -T postgres psql -U smart_ao -d smart_ao -tAc \
    "SELECT count(*) FROM pg_database WHERE datname LIKE 'smart_ao_restore_%'")"
  [[ "${database_count//[[:space:]]/}" == "0" ]] \
    || fail "unsafe-receipt harness did not clean its sentinel database"
  [[ -z "$(docker volume ls -q \
    --filter label=com.smartao.purpose=quarantine-restore-verification)" ]] \
    || fail "unsafe-receipt harness did not clean its sentinel volume"
  [[ -z "$(find "${RESTORE_STATE_DIR}" -maxdepth 1 -type l -name 'restore-*.state' -print -quit)" \
    && -z "$(find "${RESTORE_STATE_DIR}" -maxdepth 1 -type f -name 'restore-*.state' -print -quit)" ]] \
    || fail "unsafe-receipt harness left a state fixture"
}

run_dropdb_failure_cycle() {
  local failure_marker="${WORK_DIR}/restore-dropdb-failures"
  local failure_log="${WORK_DIR}/restore-dropdb-failure.log"
  local backup_hash active_hashes attempt_count database_name run_id state_file
  local fields database_count clean_object_count recovery_log replay_log
  backup_hash="$(sha256sum -- "${BACKUP_FILE}" "${QUARANTINE_BACKUP_FILE}" \
    "${BACKUP_MANIFEST}" | sha256sum | awk '{print $1}')"
  active_hashes="$(active_clean_object_hashes "${backend_container}")" \
    || fail "could not read active C5 hashes before dropdb failure injection"

  if SMART_AO_PREPROD_ENV_FILE="${ENV_FILE}" \
    SMART_AO_COMPOSE_PROJECT_NAME="${PROJECT}" \
    SMART_AO_RESTORE_STATE_DIR="${RESTORE_STATE_DIR}" \
    RESTORE_FAULT_DB_DROP=1 \
    RESTORE_FAULT_DB_DROP_MARKER="${failure_marker}" \
    REAL_DOCKER_BIN="${restore_real_docker_bin}" \
    PATH="${restore_fault_bin}:${PATH}" \
    "${ROOT_DIR}/ops/restore-preprod.sh" "${BACKUP_FILE}" \
    >"${failure_log}" 2>&1; then
    fail "restore succeeded despite injected dropdb failures"
  fi
  grep -q "restore cleanup incomplete; protected state retained for recovery" \
    "${failure_log}" \
    || fail "dropdb failure did not retain protected state through EXIT cleanup"
  attempt_count="$(wc -l <"${failure_marker}")"
  [[ "${attempt_count//[[:space:]]/}" == "2" ]] \
    || fail "dropdb failure was not attempted in both cleanup paths"

  database_name="$(head -n 1 "${failure_marker}")"
  [[ "${database_name}" =~ ^smart_ao_restore_[a-f0-9]{32}$ ]] \
    || fail "injected dropdb failure did not identify one temporary restore database"
  run_id="${database_name#smart_ao_restore_}"
  RESTORE_FAILURE_DB="${database_name}"
  RESTORE_FAILURE_RUN_ID="${run_id}"
  RESTORE_FAILURE_VOLUME="smart_ao_c5_restore_${run_id}"
  state_file="${RESTORE_STATE_DIR}/restore-${run_id}.state"
  RESTORE_FAILURE_STATE="${state_file}"
  [[ -f "${state_file}" && ! -L "${state_file}" \
    && "$(stat -c '%a' "${state_file}")" == "600" ]] \
    || fail "dropdb failure did not retain its exact DB and receipt"
  mapfile -t fields <"${state_file}"
  [[ "${#fields[@]}" == "3" \
    && "${fields[0]}" == "${run_id}" \
    && "${fields[1]}" == "${database_name}" \
    && "${fields[2]}" == "${RESTORE_FAILURE_VOLUME}" ]] \
    || fail "dropdb failure receipt does not retain exact DB/volume ownership"
  database_count="$(compose exec -T postgres psql -U smart_ao -d smart_ao -tAc \
    "SELECT count(*) FROM pg_database WHERE datname = '${database_name}'")"
  [[ "${database_count//[[:space:]]/}" == "1" ]] \
    || fail "dropdb failure did not preserve the temporary restore database"
  [[ "$(compose exec -T postgres psql -U smart_ao -d "${database_name}" -tAc \
    "SELECT count(*) FROM pg_catalog.pg_tables WHERE schemaname = 'public'")" \
    =~ ^[[:space:]]*171[[:space:]]*$ ]] \
    || fail "dropdb failure damaged the restored sentinel database"
  clean_object_count="$(compose exec -T postgres psql -U smart_ao -d "${database_name}" -tAc \
    "SELECT count(*) FROM case_contract_change_evidence_objects WHERE state = 'CLEAN'")"
  [[ "${clean_object_count//[[:space:]]/}" == "${clean_count}" ]] \
    || fail "dropdb failure changed the restored CLEAN evidence rows"
  [[ -z "$(docker volume ls -q \
    --filter label=com.smartao.purpose=quarantine-restore-verification)" ]] \
    || fail "dropdb failure left a temporary volume that should already be removed"
  [[ "$(docker inspect --format \
    '{{range .Mounts}}{{if eq .Destination "/var/lib/smart_ao/dce-quarantine"}}{{.Name}}{{end}}{{end}}' \
    "${backend_container}")" == "${active_quarantine_volume}" \
    && "$(active_clean_object_hashes "${backend_container}")" == "${active_hashes}" ]] \
    || fail "dropdb failure changed active C5 objects"
  [[ "$(sha256sum -- "${BACKUP_FILE}" "${QUARANTINE_BACKUP_FILE}" \
    "${BACKUP_MANIFEST}" | sha256sum | awk '{print $1}')" == "${backup_hash}" ]] \
    || fail "dropdb failure changed finalized backups"
  (cd "${OPS_BACKUP_DIR}" && sha256sum --check "$(basename -- "${BACKUP_MANIFEST}")" >/dev/null)

  recovery_log="${WORK_DIR}/restore-after-dropdb-failure.log"
  SMART_AO_PREPROD_ENV_FILE="${ENV_FILE}" \
  SMART_AO_COMPOSE_PROJECT_NAME="${PROJECT}" \
  SMART_AO_RESTORE_STATE_DIR="${RESTORE_STATE_DIR}" \
    "${ROOT_DIR}/ops/restore-preprod.sh" "${BACKUP_FILE}" \
    >"${recovery_log}" 2>&1
  grep -q 'tables=171' "${recovery_log}" \
    || fail "dropdb recovery did not remove its DB and restore normally"
  database_count="$(compose exec -T postgres psql -U smart_ao -d smart_ao -tAc \
    "SELECT count(*) FROM pg_database WHERE datname LIKE 'smart_ao_restore_%'" | tr -d '[:space:]')"
  [[ "${database_count}" == "0" \
    && -z "$(docker volume ls -q --filter label=com.smartao.purpose=quarantine-restore-verification)" \
    && ! -e "${state_file}" ]] \
    || fail "dropdb recovery left stale resources: db=${database_count:-none}"
  [[ "$(docker inspect --format \
    '{{range .Mounts}}{{if eq .Destination "/var/lib/smart_ao/dce-quarantine"}}{{.Name}}{{end}}{{end}}' \
    "${backend_container}")" == "${active_quarantine_volume}" \
    && "$(active_clean_object_hashes "${backend_container}")" == "${active_hashes}" ]] \
    || fail "dropdb recovery changed active C5 objects"
  [[ "$(sha256sum -- "${BACKUP_FILE}" "${QUARANTINE_BACKUP_FILE}" \
    "${BACKUP_MANIFEST}" | sha256sum | awk '{print $1}')" == "${backup_hash}" ]] \
    || fail "dropdb recovery changed finalized backups"

  replay_log="${WORK_DIR}/restore-after-dropdb-failure-replay.log"
  SMART_AO_PREPROD_ENV_FILE="${ENV_FILE}" \
  SMART_AO_COMPOSE_PROJECT_NAME="${PROJECT}" \
  SMART_AO_RESTORE_STATE_DIR="${RESTORE_STATE_DIR}" \
    "${ROOT_DIR}/ops/restore-preprod.sh" "${BACKUP_FILE}" \
    >"${replay_log}" 2>&1
  grep -q 'tables=171' "${replay_log}" \
    || fail "dropdb retry replay restore did not complete"
  database_count="$(compose exec -T postgres psql -U smart_ao -d smart_ao -tAc \
    "SELECT count(*) FROM pg_database WHERE datname LIKE 'smart_ao_restore_%'" | tr -d '[:space:]')"
  [[ "${database_count}" == "0" \
    && -z "$(docker volume ls -q --filter label=com.smartao.purpose=quarantine-restore-verification)" \
    && ! -e "${state_file}" ]] \
    || fail "dropdb retry replay left temporary resources: db=${database_count:-none}"
  [[ "$(active_clean_object_hashes "${backend_container}")" == "${active_hashes}" \
    && "$(sha256sum -- "${BACKUP_FILE}" "${QUARANTINE_BACKUP_FILE}" \
      "${BACKUP_MANIFEST}" | sha256sum | awk '{print $1}')" == "${backup_hash}" ]] \
    || fail "dropdb retry replay changed active C5 objects or finalized backups"
  RESTORE_FAILURE_DB=""
  RESTORE_FAILURE_RUN_ID=""
  RESTORE_FAILURE_VOLUME=""
  RESTORE_FAILURE_STATE=""
  pass "dropdb failure retained its DB/receipt after both attempts; next restore recovered it, and a replay left no resources"
}

cleanup() {
  if [[ -n "${BACKUP_TEST_PGID}" ]]; then
    kill -KILL -- "-${BACKUP_TEST_PGID}" >/dev/null 2>&1 || true
  fi
  if [[ -n "${BACKUP_TEST_LAUNCH_PID}" ]]; then
    kill -KILL "${BACKUP_TEST_LAUNCH_PID}" >/dev/null 2>&1 || true
    wait "${BACKUP_TEST_LAUNCH_PID}" >/dev/null 2>&1 || true
  fi
  if [[ -n "${RESTORE_FIXTURE_VOLUME}" && -n "${RESTORE_FIXTURE_LABEL_RUN_ID}" ]]; then
    fixture_label_run_id="$(docker volume inspect --format \
      '{{ index .Labels "com.smartao.restore.run" }}' "${RESTORE_FIXTURE_VOLUME}" 2>/dev/null || true)"
    if [[ "${fixture_label_run_id}" == "${RESTORE_FIXTURE_LABEL_RUN_ID}" ]]; then
      docker volume rm "${RESTORE_FIXTURE_VOLUME}" >/dev/null 2>&1 || true
    fi
  fi
  if [[ "${RESTORE_FIXTURE_DB_ID}" =~ ^[a-f0-9]{32}$ \
    && "${RESTORE_FIXTURE_DB_NAME}" == "smart_ao_restore_${RESTORE_FIXTURE_DB_ID}" ]]; then
    compose exec -T postgres dropdb --if-exists -U smart_ao \
      "${RESTORE_FIXTURE_DB_NAME}" >/dev/null 2>&1 || true
  fi
  if [[ -n "${RESTORE_FIXTURE_STATE_FILE}" \
    && "${RESTORE_FIXTURE_STATE_FILE}" == "${RESTORE_STATE_DIR}"/restore-*.state ]]; then
    rm -f -- "${RESTORE_FIXTURE_STATE_FILE}"
  fi
  if [[ -n "${RESTORE_FIXTURE_STATE_TARGET}" \
    && "${RESTORE_FIXTURE_STATE_TARGET}" == "${WORK_DIR}"/restore-receipt-sentinels/* \
    && -f "${RESTORE_FIXTURE_STATE_TARGET}" && ! -L "${RESTORE_FIXTURE_STATE_TARGET}" ]]; then
    rm -f -- "${RESTORE_FIXTURE_STATE_TARGET}"
  fi
  if [[ "${RESTORE_FAILURE_RUN_ID}" =~ ^[a-f0-9]{32}$ \
    && "${RESTORE_FAILURE_DB}" == "smart_ao_restore_${RESTORE_FAILURE_RUN_ID}" ]]; then
    compose exec -T postgres dropdb --if-exists -U smart_ao \
      "${RESTORE_FAILURE_DB}" >/dev/null 2>&1 || true
  fi
  if [[ "${RESTORE_FAILURE_RUN_ID}" =~ ^[a-f0-9]{32}$ \
    && "${RESTORE_FAILURE_VOLUME}" == "smart_ao_c5_restore_${RESTORE_FAILURE_RUN_ID}" ]]; then
    failure_volume_run_id="$(docker volume inspect --format \
      '{{ index .Labels "com.smartao.restore.run" }}' "${RESTORE_FAILURE_VOLUME}" 2>/dev/null || true)"
    if [[ "${failure_volume_run_id}" == "${RESTORE_FAILURE_RUN_ID}" ]]; then
      docker volume rm "${RESTORE_FAILURE_VOLUME}" >/dev/null 2>&1 || true
    fi
  fi
  if [[ -n "${RESTORE_FAILURE_STATE}" \
    && "${RESTORE_FAILURE_STATE}" == "${RESTORE_STATE_DIR}"/restore-*.state ]]; then
    rm -f -- "${RESTORE_FAILURE_STATE}"
  fi
  compose down -v --remove-orphans >/dev/null 2>&1 || true
  rm -rf -- "${WORK_DIR}"
}
trap cleanup EXIT

printf 'Local preproduction test project: %s\nTemporary work directory: %s\n' \
  "${PROJECT}" "${WORK_DIR}"

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
      - "127.0.0.1:18080:80"
      - "127.0.0.1:18443:443"
      - "127.0.0.1:18443:443/udp"
EOF

compose config --quiet
pass "Compose configuration"
compose up -d --build postgres clamav migrate backend frontend \
  dce-retention-worker submission-export-webhook-worker submission-export-smtp-worker caddy
pass "preproduction services started"
postgres_container="$(compose ps -q postgres)"
clamav_container="$(compose ps -q clamav)"
postgres_ip="$(container_ip_on_internal "${postgres_container}")"
clamav_ip="$(container_ip_on_internal "${clamav_container}")"
[[ "${postgres_ip}" =~ ^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$ ]] \
  || fail "PostgreSQL has no IPv4 address on the project-internal network"
[[ "${clamav_ip}" =~ ^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$ ]] \
  || fail "ClamAV has no IPv4 address on the project-internal network"
pass "test runner targets services by project-internal IP; no PostgreSQL/ClamAV host ports"

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

compose exec -T backend python - <<'PY'
import asyncio
import tempfile
from pathlib import Path

from app.modules.dce.infrastructure.quarantine import (
    ClamdTcpMalwareScanAdapter,
    LocalQuarantineStorageAdapter,
)

EICAR = b"X5O!P%@AP[4\\PZX54(P^)7CC)7}$EICAR-STANDARD-ANTIVIRUS-TEST-FILE!$H+H*"


async def stream(content: bytes):
    yield content


async def main():
    with tempfile.TemporaryDirectory(prefix="smartao-c5-clamd-") as folder:
        storage = LocalQuarantineStorageAdapter(root=Path(folder))
        await storage.write(
            storage_key="probe/clean.bin",
            stream=stream(b"SMART_AO synthetic C5 clean-file probe"),
            max_bytes=1024,
        )
        await storage.write(
            storage_key="probe/eicar.bin",
            stream=stream(EICAR),
            max_bytes=1024,
        )
        clean = await ClamdTcpMalwareScanAdapter(
            storage=storage, host="clamav", port=3310, timeout_seconds=5
        ).scan(storage_key="probe/clean.bin")
        infected = await ClamdTcpMalwareScanAdapter(
            storage=storage, host="clamav", port=3310, timeout_seconds=5
        ).scan(storage_key="probe/eicar.bin")
        unavailable = await ClamdTcpMalwareScanAdapter(
            storage=storage, host="clamav", port=3311, timeout_seconds=1
        ).scan(storage_key="probe/clean.bin")
        print(
            "C5_CLAMAV_ADAPTER "
            f"clean={clean.verdict} infected={infected.verdict} "
            f"unavailable={unavailable.verdict} "
            f"version={clean.scanner_signature_version}"
        )
        if clean.verdict != "CLEAN":
            raise SystemExit("C5 ClamAV adapter did not return CLEAN for a synthetic clean file")
        if infected.verdict != "INFECTED":
            raise SystemExit("C5 ClamAV adapter did not detect the EICAR test signature")
        if unavailable.verdict != "ERROR":
            raise SystemExit("C5 ClamAV adapter did not fail closed on an unavailable port")


asyncio.run(main())
PY
pass "C5 ClamAV adapter verdicts: CLEAN, INFECTED, ERROR"

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

old_key="${SMART_AO_JWT_SIGNING_KEY:-local-old-key}"
new_key="$(openssl rand -hex 32)"
printf 'SMART_AO_JWT_SIGNING_KEY=%s\n' "${old_key}" >"${WORK_DIR}/rotation.env"
ROTATION_KEY="${new_key}" awk '{ sub(/^SMART_AO_JWT_SIGNING_KEY=.*/, "SMART_AO_JWT_SIGNING_KEY=" ENVIRON["ROTATION_KEY"]); print }' \
  "${WORK_DIR}/rotation.env" >"${WORK_DIR}/rotation.env.new"
mv "${WORK_DIR}/rotation.env.new" "${WORK_DIR}/rotation.env"
[[ "$(stat -c '%a' "${WORK_DIR}/rotation.env")" == 600 ]] || fail "rotation file is not mode 600"
grep -q "${new_key}" "${WORK_DIR}/rotation.env" || fail "rotation did not replace the key"
pass "JWT rotation simulation verified with ephemeral mode-600 file"

SMART_AO_TEST_DATABASE_URL="postgresql+psycopg://smart_ao:${LOCAL_DB_PASSWORD}@${postgres_ip}:5432/smart_ao" \
SMART_AO_C5_TEST_CLAMD_HOST="${clamav_ip}" \
SMART_AO_C5_TEST_CLAMD_PORT=3310 \
  "${ROOT_DIR}/.venv/bin/pytest" --import-mode=importlib -q --tb=short \
  "${ROOT_DIR}/backend/tests/db/test_case_handover_http_e2e.py"
pass "C5 HTTP/PostgreSQL E2E with normal fixture cleanup and migration downgrade"

install -d -m 700 "${C5_HOST_STORAGE_DIR}"
SMART_AO_TEST_DATABASE_URL="postgresql+psycopg://smart_ao:${LOCAL_DB_PASSWORD}@${postgres_ip}:5432/smart_ao" \
SMART_AO_C5_TEST_CLAMD_HOST="${clamav_ip}" \
SMART_AO_C5_TEST_CLAMD_PORT=3310 \
SMART_AO_TEST_PRESERVE_C5_RESTORE_FIXTURE=1 \
SMART_AO_TEST_DISPOSABLE_DATABASE=1 \
SMART_AO_TEST_C5_QUARANTINE_ROOT="${C5_HOST_STORAGE_DIR}" \
  "${ROOT_DIR}/.venv/bin/pytest" --import-mode=importlib -q --tb=short \
  "${ROOT_DIR}/backend/tests/db/test_case_handover_http_e2e.py"
pass "C5 HTTP/PostgreSQL E2E preserved fixture with real local ClamAV"

clean_count="$(compose exec -T postgres psql -U smart_ao -d smart_ao -tAc \
  "SELECT count(*) FROM case_contract_change_evidence_objects WHERE state = 'CLEAN'")"
[[ "${clean_count//[[:space:]]/}" =~ ^[1-9][0-9]*$ ]] \
  || fail "C5 E2E did not preserve a CLEAN database fixture"
clean_row="$(compose exec -T postgres psql -U smart_ao -d smart_ao -At -F $'\t' \
  -c "SELECT storage_key, sha256 FROM case_contract_change_evidence_objects WHERE state = 'CLEAN' ORDER BY storage_key LIMIT 1")"
c5_storage_key="${clean_row%%$'\t'*}"
c5_expected_sha256="${clean_row#*$'\t'}"
[[ -n "${c5_storage_key}" && "${c5_expected_sha256}" =~ ^[a-f0-9]{64}$ ]] \
  || fail "C5 CLEAN row did not provide a storage key and SHA-256"
[[ -f "${C5_HOST_STORAGE_DIR}/${c5_storage_key}" ]] \
  || fail "C5 CLEAN object bytes are missing from the isolated host fixture"
host_object_sha256="$(sha256sum -- "${C5_HOST_STORAGE_DIR}/${c5_storage_key}" | awk '{print $1}')"
[[ "${host_object_sha256}" == "${c5_expected_sha256}" ]] \
  || fail "C5 host fixture object hash does not match its database row"
backend_container="$(compose ps -q backend)"
docker cp "${C5_HOST_STORAGE_DIR}/." \
  "${backend_container}:/var/lib/smart_ao/dce-quarantine/" >/dev/null
compose exec -T --user 0 backend chown -R 10001:10001 \
  /var/lib/smart_ao/dce-quarantine

install -d -m 700 "${OPS_BACKUP_DIR}"
install -d -m 700 "${RESTORE_STATE_DIR}"
SMART_AO_PREPROD_ENV_FILE="${ENV_FILE}" \
SMART_AO_COMPOSE_PROJECT_NAME="${PROJECT}" \
SMART_AO_BACKUP_DIR="${OPS_BACKUP_DIR}" \
  "${ROOT_DIR}/ops/backup-preprod.sh" >"${WORK_DIR}/backup-preprod.log"
backup_timestamp="$(sed -n 's/^Backup completed: //p' "${WORK_DIR}/backup-preprod.log")"
[[ "${backup_timestamp}" =~ ^[0-9]{8}T[0-9]{15}Z_[0-9]+$ ]] \
  || fail "ops backup did not return its unique timestamp"
BACKUP_FILE="${OPS_BACKUP_DIR}/smart_ao_${backup_timestamp}.sql.gz"
QUARANTINE_BACKUP_FILE="${OPS_BACKUP_DIR}/smart_ao_${backup_timestamp}.dce_quarantine.tar.gz"
BACKUP_MANIFEST="${OPS_BACKUP_DIR}/smart_ao_${backup_timestamp}.sha256"
[[ -s "${BACKUP_FILE}" && -s "${QUARANTINE_BACKUP_FILE}" && -s "${BACKUP_MANIFEST}" ]] \
  || fail "ops backup did not create its SQL, C5 quarantine, and manifest files"
(cd "${OPS_BACKUP_DIR}" && sha256sum --check "$(basename -- "${BACKUP_MANIFEST}")" >/dev/null)
pass "C5 SQL and quarantine backup created by ops/backup-preprod.sh with verified manifest"

SMART_AO_PREPROD_ENV_FILE="${ENV_FILE}" SMART_AO_COMPOSE_PROJECT_NAME="${PROJECT}" \
  SMART_AO_RESTORE_STATE_DIR="${RESTORE_STATE_DIR}" \
  "${ROOT_DIR}/ops/restore-preprod.sh" "${BACKUP_FILE}" \
  >"${WORK_DIR}/restore-success.log" 2>&1
verified_clean_count="$(awk '/C5 quarantine restore verified/ { print $5; exit }' \
  "${WORK_DIR}/restore-success.log")"
[[ "${verified_clean_count}" =~ ^[1-9][0-9]*$ ]] \
  || fail "C5 restore did not verify any CLEAN object hashes"
[[ "${verified_clean_count}" == "${clean_count}" ]] \
  || fail "C5 restore verified ${verified_clean_count} objects but DB contains ${clean_count} CLEAN rows"
grep -q 'tables=171' "${WORK_DIR}/restore-success.log" \
  || fail "ops restore did not verify the expected isolated PostgreSQL table count"
pass "C5 quarantine archive restored; DB-backed hashes verified for ${verified_clean_count} CLEAN objects in an isolated Docker volume"

hash_mismatch_sql="${WORK_DIR}/smart_ao_hash_mismatch.sql.gz"
hash_mismatch_archive="${WORK_DIR}/smart_ao_hash_mismatch.dce_quarantine.tar.gz"
hash_mismatch_manifest="${WORK_DIR}/smart_ao_hash_mismatch.sha256"
cp -- "${BACKUP_FILE}" "${hash_mismatch_sql}"
python3 - "${QUARANTINE_BACKUP_FILE}" "${hash_mismatch_archive}" "${c5_storage_key}" <<'PY'
import copy
import io
import sys
import tarfile
from pathlib import PurePosixPath

source_path, target_path, expected_key = sys.argv[1:]
found = 0
with tarfile.open(source_path, "r:gz") as source, tarfile.open(target_path, "w:gz") as target:
    for member in source:
        relative_name = "/".join(part for part in PurePosixPath(member.name).parts if part != ".")
        if member.isfile():
            content_file = source.extractfile(member)
            if content_file is None:
                raise SystemExit("backup archive contains an unreadable regular file")
            content = content_file.read()
            if relative_name == expected_key:
                if not content:
                    raise SystemExit("C5 CLEAN object unexpectedly has empty content")
                content = bytes([content[0] ^ 1]) + content[1:]
                found += 1
            target.addfile(copy.copy(member), io.BytesIO(content))
        else:
            target.addfile(copy.copy(member))
if found != 1:
    raise SystemExit("C5 CLEAN object was not found exactly once in quarantine archive")
PY
chmod 600 "${hash_mismatch_sql}" "${hash_mismatch_archive}"
(cd "${WORK_DIR}" && sha256sum "$(basename -- "${hash_mismatch_sql}")" \
  "$(basename -- "${hash_mismatch_archive}")" >"$(basename -- "${hash_mismatch_manifest}")")
if SMART_AO_PREPROD_ENV_FILE="${ENV_FILE}" SMART_AO_COMPOSE_PROJECT_NAME="${PROJECT}" \
  SMART_AO_RESTORE_STATE_DIR="${RESTORE_STATE_DIR}" \
  "${ROOT_DIR}/ops/restore-preprod.sh" "${hash_mismatch_sql}" \
  >"${WORK_DIR}/hash-mismatch-restore.log" 2>&1; then
  fail "C5 SHA-256 mismatch restore was accepted"
fi
grep -q "C5 quarantine object SHA-256 mismatch" "${WORK_DIR}/hash-mismatch-restore.log" \
  || fail "C5 restore failed without detecting the object SHA-256 mismatch"
remaining_restore_dbs="$(compose exec -T postgres psql -U smart_ao -d smart_ao -tAc \
  "SELECT count(*) FROM pg_database WHERE datname LIKE 'smart_ao_restore_%'")"
[[ "${remaining_restore_dbs//[[:space:]]/}" == "0" ]] \
  || fail "hash-mismatch restore left a temporary PostgreSQL database"
remaining_restore_volumes="$(docker volume ls -q \
  --filter label=com.smartao.purpose=quarantine-restore-verification)"
[[ -z "${remaining_restore_volumes}" ]] \
  || fail "hash-mismatch restore left a temporary Docker volume"
pass "C5 SHA-256 mismatch rejected; temporary PostgreSQL database and Docker volume removed"

attack_sql="${WORK_DIR}/smart_ao_path_traversal.sql.gz"
attack_archive="${WORK_DIR}/smart_ao_path_traversal.dce_quarantine.tar.gz"
attack_manifest="${WORK_DIR}/smart_ao_path_traversal.sha256"
cp -- "${BACKUP_FILE}" "${attack_sql}"
python3 - "${attack_archive}" <<'PY'
import io
import sys
import tarfile

with tarfile.open(sys.argv[1], "w:gz") as archive:
    member = tarfile.TarInfo("../escape.bin")
    content = b"synthetic traversal attempt"
    member.size = len(content)
    archive.addfile(member, io.BytesIO(content))
PY
chmod 600 "${attack_sql}" "${attack_archive}"
(cd "${WORK_DIR}" && sha256sum "$(basename -- "${attack_sql}")" \
  "$(basename -- "${attack_archive}")" >"$(basename -- "${attack_manifest}")")
if SMART_AO_PREPROD_ENV_FILE="${ENV_FILE}" SMART_AO_COMPOSE_PROJECT_NAME="${PROJECT}" \
  SMART_AO_RESTORE_STATE_DIR="${RESTORE_STATE_DIR}" \
  "${ROOT_DIR}/ops/restore-preprod.sh" "${attack_sql}" \
  >"${WORK_DIR}/attack-restore.log" 2>&1; then
  fail "path-traversal quarantine archive was accepted"
fi
remaining_traversal_restore_dbs="$(compose exec -T postgres psql -U smart_ao -d smart_ao -tAc \
  "SELECT count(*) FROM pg_database WHERE datname LIKE 'smart_ao_restore_%'")"
[[ "${remaining_traversal_restore_dbs//[[:space:]]/}" == "0" ]] \
  || fail "path-traversal restore left a temporary PostgreSQL database"
remaining_restore_volumes="$(docker volume ls -q \
  --filter label=com.smartao.purpose=quarantine-restore-verification)"
[[ -z "${remaining_restore_volumes}" ]] \
  || fail "path-traversal restore left a temporary Docker volume"
pass "path-traversal restore rejected; temporary PostgreSQL database and Docker volume removed"

fault_docker_bin="${WORK_DIR}/backup-fault-bin"
fault_marker="${WORK_DIR}/backup-fault-entered"
fault_backup_log="${WORK_DIR}/backup-interrupted.log"
real_docker_bin="$(command -v docker)"
install -d -m 700 "${fault_docker_bin}"
cat >"${fault_docker_bin}/docker" <<'SH'
#!/usr/bin/env bash
set -Eeuo pipefail
if [[ "${1:-}" == "run" ]]; then
  if [[ "${BACKUP_CONCURRENCY_MODE:-}" == "block" ]]; then
    : >"${BACKUP_CONCURRENCY_MARKER}"
    while [[ ! -e "${BACKUP_CONCURRENCY_RELEASE}" ]]; do sleep 0.05; done
    tar -czf - --files-from /dev/null
    exit 0
  fi
  printf 'partial archive stream'
  : >"${BACKUP_FAULT_MARKER}"
  exec sleep 300
fi
exec "${REAL_DOCKER_BIN}" "$@"
SH
chmod 700 "${fault_docker_bin}/docker"
(cd "${OPS_BACKUP_DIR}" && sha256sum --check "$(basename -- "${BACKUP_MANIFEST}")" >/dev/null)

concurrency_marker="${WORK_DIR}/backup-concurrency-entered"
concurrency_release="${WORK_DIR}/backup-concurrency-release"
concurrency_backup_log="${WORK_DIR}/backup-concurrency-first.log"
concurrent_reject_log="${WORK_DIR}/backup-concurrency-second.log"
setsid --fork --wait env \
  REAL_DOCKER_BIN="${real_docker_bin}" \
  BACKUP_CONCURRENCY_MODE=block \
  BACKUP_CONCURRENCY_MARKER="${concurrency_marker}" \
  BACKUP_CONCURRENCY_RELEASE="${concurrency_release}" \
  BACKUP_FAULT_MARKER="${fault_marker}" \
  PATH="${fault_docker_bin}:${PATH}" \
  SMART_AO_PREPROD_ENV_FILE="${ENV_FILE}" \
  SMART_AO_COMPOSE_PROJECT_NAME="${PROJECT}" \
  SMART_AO_BACKUP_DIR="${OPS_BACKUP_DIR}" \
  "${ROOT_DIR}/ops/backup-preprod.sh" >"${concurrency_backup_log}" 2>&1 &
BACKUP_TEST_LAUNCH_PID=$!
for _ in $(seq 1 100); do
  helper_pid="$(ps -o pid= --ppid "${BACKUP_TEST_LAUNCH_PID}" | awk 'NR == 1 {print $1}')"
  if [[ "${helper_pid}" =~ ^[0-9]+$ ]]; then
    helper_pgid="$(ps -o pgid= -p "${helper_pid}" | awk '{print $1}')"
    shell_pgid="$(ps -o pgid= -p "$$" | awk '{print $1}')"
    if [[ "${helper_pgid}" =~ ^[0-9]+$ && "${helper_pgid}" != "${shell_pgid}" ]]; then
      BACKUP_TEST_PGID="${helper_pgid}"
    fi
  fi
  [[ -e "${concurrency_marker}" ]] && break
  sleep 0.1
done
[[ -e "${concurrency_marker}" && -n "${BACKUP_TEST_PGID}" ]] \
  || fail "first backup did not reach the blocked tar helper"
concurrency_tmp="$(find "${OPS_BACKUP_DIR}" -maxdepth 1 -type f \
  -name 'smart_ao_*.dce_quarantine.tar.gz.tmp' -print -quit)"
[[ -n "${concurrency_tmp}" && -e "${concurrency_tmp}" ]] \
  || fail "blocked first backup has no temporary archive"
if SMART_AO_PREPROD_ENV_FILE="${ENV_FILE}" \
  SMART_AO_COMPOSE_PROJECT_NAME="${PROJECT}" \
  SMART_AO_BACKUP_DIR="${OPS_BACKUP_DIR}" \
  "${ROOT_DIR}/ops/backup-preprod.sh" >"${concurrent_reject_log}" 2>&1; then
  fail "backup lock did not reject the concurrent run"
fi
grep -q "another backup is already running" "${concurrent_reject_log}" \
  || fail "concurrent backup failed before reaching the lock"
[[ -e "${concurrency_tmp}" ]] \
  || fail "concurrent rejected run cleaned the active backup temporary archive"
(cd "${OPS_BACKUP_DIR}" && sha256sum --check "$(basename -- "${BACKUP_MANIFEST}")" >/dev/null)
touch "${concurrency_release}"
if ! wait "${BACKUP_TEST_LAUNCH_PID}"; then
  fail "first backup did not complete after releasing the tar helper"
fi
concurrency_timestamp="$(sed -n 's/^Backup completed: //p' "${concurrency_backup_log}")"
[[ "${concurrency_timestamp}" =~ ^[0-9]{8}T[0-9]{15}Z_[0-9]+$ ]] \
  || fail "first concurrent backup did not publish its manifest"
concurrency_manifest="${OPS_BACKUP_DIR}/smart_ao_${concurrency_timestamp}.sha256"
[[ -s "${concurrency_manifest}" ]] || fail "first concurrent backup manifest is missing"
(cd "${OPS_BACKUP_DIR}" && sha256sum --check \
  "$(basename -- "${concurrency_manifest}")" >/dev/null)
BACKUP_TEST_PGID=""
BACKUP_TEST_LAUNCH_PID=""
pass "second concurrent backup was rejected before cleanup; first published a valid manifest and previous backups remained valid"

setsid --fork --wait env \
  REAL_DOCKER_BIN="${real_docker_bin}" \
  BACKUP_FAULT_MARKER="${fault_marker}" \
  PATH="${fault_docker_bin}:${PATH}" \
  SMART_AO_PREPROD_ENV_FILE="${ENV_FILE}" \
  SMART_AO_COMPOSE_PROJECT_NAME="${PROJECT}" \
  SMART_AO_BACKUP_DIR="${OPS_BACKUP_DIR}" \
  "${ROOT_DIR}/ops/backup-preprod.sh" >"${fault_backup_log}" 2>&1 &
BACKUP_TEST_LAUNCH_PID=$!
for _ in $(seq 1 100); do
  helper_pid="$(ps -o pid= --ppid "${BACKUP_TEST_LAUNCH_PID}" | awk 'NR == 1 {print $1}')"
  if [[ "${helper_pid}" =~ ^[0-9]+$ ]]; then
    helper_pgid="$(ps -o pgid= -p "${helper_pid}" | awk 'NR == 1 {print $1}')"
    shell_pgid="$(ps -o pgid= -p "$$" | awk 'NR == 1 {print $1}')"
    if [[ "${helper_pgid}" =~ ^[0-9]+$ && "${helper_pgid}" != "${shell_pgid}" ]]; then
      BACKUP_TEST_PGID="${helper_pgid}"
    fi
  fi
  [[ -e "${fault_marker}" ]] && break
  sleep 0.1
done
[[ -e "${fault_marker}" && -n "${BACKUP_TEST_PGID}" ]] \
  || fail "backup tar helper was not reached in the isolated process group"
orphan_tar_tmp="$(find "${OPS_BACKUP_DIR}" -maxdepth 1 -type f \
  -name 'smart_ao_*.dce_quarantine.tar.gz.tmp' -print -quit)"
[[ -n "${orphan_tar_tmp}" && -s "${orphan_tar_tmp}" ]] \
  || fail "SIGKILL test did not leave the expected partial quarantine .tmp"
orphan_prefix="${orphan_tar_tmp%.dce_quarantine.tar.gz.tmp}"
orphan_sql="${orphan_prefix}.sql.gz"
orphan_manifest="${orphan_prefix}.sha256"
orphan_final_archive="${orphan_prefix}.dce_quarantine.tar.gz"
[[ -s "${orphan_sql}" && ! -e "${orphan_manifest}" && ! -e "${orphan_final_archive}" ]] \
  || fail "interrupted backup published a manifest or final C5 archive"
orphan_sql_sha256_before="$(sha256sum -- "${orphan_sql}" | awk '{print $1}')"
kill -KILL -- "-${BACKUP_TEST_PGID}"
if wait "${BACKUP_TEST_LAUNCH_PID}"; then
  fail "backup completed after its tar helper was killed"
fi
BACKUP_TEST_PGID=""
BACKUP_TEST_LAUNCH_PID=""
if SMART_AO_PREPROD_ENV_FILE="${ENV_FILE}" SMART_AO_COMPOSE_PROJECT_NAME="${PROJECT}" \
  SMART_AO_RESTORE_STATE_DIR="${RESTORE_STATE_DIR}" \
  "${ROOT_DIR}/ops/restore-preprod.sh" "${orphan_sql}" \
  >"${WORK_DIR}/restore-incomplete-backup.log" 2>&1; then
  fail "restore accepted an interrupted backup without a complete manifest"
fi
grep -q "checksum manifest is missing" "${WORK_DIR}/restore-incomplete-backup.log" \
  || fail "restore rejected incomplete backup for an unexpected reason"
(cd "${OPS_BACKUP_DIR}" && sha256sum --check "$(basename -- "${BACKUP_MANIFEST}")" >/dev/null)

SMART_AO_PREPROD_ENV_FILE="${ENV_FILE}" \
SMART_AO_COMPOSE_PROJECT_NAME="${PROJECT}" \
SMART_AO_BACKUP_DIR="${OPS_BACKUP_DIR}" \
  "${ROOT_DIR}/ops/backup-preprod.sh" >"${WORK_DIR}/backup-after-interruption.log"
recovery_backup_timestamp="$(sed -n 's/^Backup completed: //p' \
  "${WORK_DIR}/backup-after-interruption.log")"
[[ "${recovery_backup_timestamp}" =~ ^[0-9]{8}T[0-9]{15}Z_[0-9]+$ ]] \
  || fail "backup did not complete after orphan cleanup"
recovery_manifest="${OPS_BACKUP_DIR}/smart_ao_${recovery_backup_timestamp}.sha256"
[[ -s "${recovery_manifest}" ]] || fail "recovery backup manifest is missing"
(cd "${OPS_BACKUP_DIR}" && sha256sum --check \
  "$(basename -- "${recovery_manifest}")" >/dev/null)
[[ ! -e "${orphan_tar_tmp}" ]] || fail "next backup did not remove the orphaned .tmp file"
remaining_backup_temps="$(find "${OPS_BACKUP_DIR}" -maxdepth 1 -type f \
  -name 'smart_ao_*.tmp' -print -quit)"
[[ -z "${remaining_backup_temps}" ]] || fail "recovery backup left a temporary file"
[[ -s "${orphan_sql}" && ! -e "${orphan_manifest}" ]] \
  || fail "next backup cleanup modified the incomplete SQL artifact"
orphan_sql_sha256_after="$(sha256sum -- "${orphan_sql}" | awk '{print $1}')"
[[ "${orphan_sql_sha256_after}" == "${orphan_sql_sha256_before}" ]] \
  || fail "next backup cleanup modified a final-named file from the interrupted run"
(cd "${OPS_BACKUP_DIR}" && sha256sum --check "$(basename -- "${BACKUP_MANIFEST}")" >/dev/null)
pass "SIGKILL backup had no manifest and restore rejected it; next real backup removed orphan .tmp, verified its manifest, and preserved finalized files"

restore_fault_bin="${WORK_DIR}/restore-fault-bin"
restore_fault_marker="${WORK_DIR}/restore-fault-entered"
restore_fault_log="${WORK_DIR}/restore-interrupted.log"
install -d -m 700 "${restore_fault_bin}"
cat >"${restore_fault_bin}/docker" <<'SH'
#!/usr/bin/env bash
set -Eeuo pipefail
if [[ "${1:-}" == "compose" && "${RESTORE_FAULT_DB_DROP:-}" == "1" ]]; then
  dropdb_seen=0
  for arg in "$@"; do
    if [[ "${arg}" == "dropdb" ]]; then
      dropdb_seen=1
    elif [[ "${dropdb_seen}" == "1" && "${arg}" =~ ^smart_ao_restore_[a-f0-9]{32}$ ]]; then
      printf '%s\n' "${arg}" >>"${RESTORE_FAULT_DB_DROP_MARKER}"
      exit 74
    fi
  done
fi
if [[ "${1:-}" == "volume" && "${2:-}" == "rm" \
  && "${RESTORE_FAULT_VOLUME_RM:-}" == "1" \
  && "${3:-}" =~ ^smart_ao_c5_restore_[a-f0-9]{32}$ ]]; then
  printf '%s\n' "${3}" >>"${RESTORE_FAULT_VOLUME_RM_MARKER}"
  exit 73
fi
if [[ "${1:-}" == "run" && "${RESTORE_FAULT_MODE:-}" == "block" ]]; then
  : >"${RESTORE_FAULT_MARKER}"
  if [[ -n "${RESTORE_FAULT_RELEASE:-}" ]]; then
    while [[ ! -e "${RESTORE_FAULT_RELEASE}" ]]; do sleep 0.05; done
    exec "${REAL_DOCKER_BIN}" "$@"
  fi
  exec sleep 300
fi
exec "${REAL_DOCKER_BIN}" "$@"
SH
chmod 700 "${restore_fault_bin}/docker"
restore_real_docker_bin="$(command -v docker)"
setsid --fork --wait env \
  REAL_DOCKER_BIN="${restore_real_docker_bin}" \
  RESTORE_FAULT_MODE=block \
  RESTORE_FAULT_MARKER="${restore_fault_marker}" \
  PATH="${restore_fault_bin}:${PATH}" \
  SMART_AO_PREPROD_ENV_FILE="${ENV_FILE}" \
  SMART_AO_COMPOSE_PROJECT_NAME="${PROJECT}" \
  SMART_AO_RESTORE_STATE_DIR="${RESTORE_STATE_DIR}" \
  "${ROOT_DIR}/ops/restore-preprod.sh" "${BACKUP_FILE}" \
  >"${restore_fault_log}" 2>&1 &
BACKUP_TEST_LAUNCH_PID=$!
for _ in $(seq 1 100); do
  helper_pid="$(ps -o pid= --ppid "${BACKUP_TEST_LAUNCH_PID}" | awk 'NR == 1 {print $1}')"
  if [[ "${helper_pid}" =~ ^[0-9]+$ ]]; then
    helper_pgid="$(ps -o pgid= -p "${helper_pid}" | awk '{print $1}')"
    shell_pgid="$(ps -o pgid= -p "$$" | awk '{print $1}')"
    if [[ "${helper_pgid}" =~ ^[0-9]+$ && "${helper_pgid}" != "${shell_pgid}" ]]; then
      BACKUP_TEST_PGID="${helper_pgid}"
    fi
  fi
  [[ -e "${restore_fault_marker}" ]] && break
  sleep 0.1
done
[[ -e "${restore_fault_marker}" && -n "${BACKUP_TEST_PGID}" ]] \
  || fail "restore did not reach the blocked object verifier"
restore_state_file="$(find "${RESTORE_STATE_DIR}" -maxdepth 1 -type f \
  -name 'restore-*.state' -print -quit)"
[[ -n "${restore_state_file}" && -s "${restore_state_file}" ]] \
  || fail "interrupted restore has no durable ownership receipt"
mapfile -t restore_state_fields <"${restore_state_file}"
[[ "${#restore_state_fields[@]}" == "3" ]] || fail "restore ownership receipt is malformed"
restore_run_id="${restore_state_fields[0]}"
interrupted_restore_db="${restore_state_fields[1]}"
interrupted_restore_volume="${restore_state_fields[2]}"
[[ "${restore_run_id}" =~ ^[a-f0-9]{32}$ \
  && "${interrupted_restore_db}" == "smart_ao_restore_${restore_run_id}" \
  && "${interrupted_restore_volume}" == "smart_ao_c5_restore_${restore_run_id}" ]] \
  || fail "restore receipt does not identify one exact isolated run"
interrupted_db_count="$(compose exec -T postgres psql -U smart_ao -d smart_ao -tAc \
  "SELECT count(*) FROM pg_database WHERE datname = '${interrupted_restore_db}'")"
[[ "${interrupted_db_count//[[:space:]]/}" == "1" ]] \
  || fail "SIGKILL injection did not leave the owned temporary database"
interrupted_volume_run="$(docker volume inspect --format \
  '{{ index .Labels "com.smartao.restore.run" }}' "${interrupted_restore_volume}")"
[[ "${interrupted_volume_run}" == "${restore_run_id}" ]] \
  || fail "SIGKILL injection did not leave the owned temporary quarantine volume"
backend_container="$(compose ps -q backend | head -n 1)"
active_quarantine_volume="$(docker inspect --format \
  '{{range .Mounts}}{{if eq .Destination "/var/lib/smart_ao/dce-quarantine"}}{{.Name}}{{end}}{{end}}' \
  "${backend_container}")"
[[ -n "${active_quarantine_volume}" && "${active_quarantine_volume}" != "${interrupted_restore_volume}" ]] \
  || fail "restore temporary volume aliases the active quarantine volume"
backup_sql_hash_before="$(sha256sum -- "${BACKUP_FILE}" | awk '{print $1}')"
backup_archive_hash_before="$(sha256sum -- "${QUARANTINE_BACKUP_FILE}" | awk '{print $1}')"
backup_manifest_hash_before="$(sha256sum -- "${BACKUP_MANIFEST}" | awk '{print $1}')"
kill -KILL -- "-${BACKUP_TEST_PGID}"
if wait "${BACKUP_TEST_LAUNCH_PID}"; then
  fail "restore completed after its verifier process was killed"
fi
BACKUP_TEST_PGID=""
BACKUP_TEST_LAUNCH_PID=""
[[ -s "${restore_state_file}" ]] \
  || fail "SIGKILL unexpectedly ran restore cleanup or removed its recovery receipt"
recovered_restore_log="${WORK_DIR}/restore-after-sigkill.log"
SMART_AO_PREPROD_ENV_FILE="${ENV_FILE}" \
SMART_AO_COMPOSE_PROJECT_NAME="${PROJECT}" \
SMART_AO_RESTORE_STATE_DIR="${RESTORE_STATE_DIR}" \
  "${ROOT_DIR}/ops/restore-preprod.sh" "${BACKUP_FILE}" \
  >"${recovered_restore_log}" 2>&1
grep -q 'tables=171' "${recovered_restore_log}" \
  || fail "restore did not complete after reclaiming interrupted resources"
remaining_restore_dbs="$(compose exec -T postgres psql -U smart_ao -d smart_ao -tAc \
  "SELECT count(*) FROM pg_database WHERE datname LIKE 'smart_ao_restore_%'")"
[[ "${remaining_restore_dbs//[[:space:]]/}" == "0" ]] \
  || fail "restore recovery left a temporary database"
remaining_restore_volumes="$(docker volume ls -q \
  --filter label=com.smartao.purpose=quarantine-restore-verification)"
[[ -z "${remaining_restore_volumes}" ]] \
  || fail "restore recovery left a temporary quarantine volume"
[[ -z "$(find "${RESTORE_STATE_DIR}" -maxdepth 1 -type f -name 'restore-*.state' -print -quit)" ]] \
  || fail "restore recovery left an ownership receipt after cleanup"
recovered_active_volume="$(docker inspect --format \
  '{{range .Mounts}}{{if eq .Destination "/var/lib/smart_ao/dce-quarantine"}}{{.Name}}{{end}}{{end}}' \
  "${backend_container}")"
[[ "${recovered_active_volume}" == "${active_quarantine_volume}" ]] \
  || fail "active quarantine volume changed during restore recovery"
[[ "$(sha256sum -- "${BACKUP_FILE}" | awk '{print $1}')" == "${backup_sql_hash_before}" \
  && "$(sha256sum -- "${QUARANTINE_BACKUP_FILE}" | awk '{print $1}')" == "${backup_archive_hash_before}" \
  && "$(sha256sum -- "${BACKUP_MANIFEST}" | awk '{print $1}')" == "${backup_manifest_hash_before}" ]] \
  || fail "restore recovery modified finalized backup files"

SMART_AO_PREPROD_ENV_FILE="${ENV_FILE}" \
SMART_AO_COMPOSE_PROJECT_NAME="${PROJECT}" \
SMART_AO_RESTORE_STATE_DIR="${RESTORE_STATE_DIR}" \
  "${ROOT_DIR}/ops/restore-preprod.sh" "${BACKUP_FILE}" \
  >"${WORK_DIR}/restore-recovery-idempotent.log" 2>&1
[[ "$(compose exec -T postgres psql -U smart_ao -d smart_ao -tAc \
  "SELECT count(*) FROM pg_database WHERE datname LIKE 'smart_ao_restore_%'")" =~ ^[[:space:]]*0[[:space:]]*$ ]] \
  || fail "repeat restore recovery left a temporary database"
[[ -z "$(docker volume ls -q \
  --filter label=com.smartao.purpose=quarantine-restore-verification)" ]] \
  || fail "repeat restore recovery left a temporary quarantine volume"
[[ "$(docker inspect --format \
  '{{range .Mounts}}{{if eq .Destination "/var/lib/smart_ao/dce-quarantine"}}{{.Name}}{{end}}{{end}}' \
  "${backend_container}")" == "${active_quarantine_volume}" ]] \
  || fail "repeat restore recovery changed the active quarantine volume"
[[ "$(sha256sum -- "${BACKUP_FILE}" | awk '{print $1}')" == "${backup_sql_hash_before}" \
  && "$(sha256sum -- "${QUARANTINE_BACKUP_FILE}" | awk '{print $1}')" == "${backup_archive_hash_before}" \
  && "$(sha256sum -- "${BACKUP_MANIFEST}" | awk '{print $1}')" == "${backup_manifest_hash_before}" ]] \
  || fail "repeat restore recovery changed finalized backup bytes"
pass "SIGKILL restore reclaimed only receipt-owned DB/volume; repeat recovery was idempotent and active quarantine/backups stayed unchanged"

restore_concurrency_marker="${WORK_DIR}/restore-concurrency-entered"
restore_concurrency_release="${WORK_DIR}/restore-concurrency-release"
restore_concurrency_first_log="${WORK_DIR}/restore-concurrency-first.log"
restore_concurrency_second_log="${WORK_DIR}/restore-concurrency-second.log"
setsid --fork --wait env \
  REAL_DOCKER_BIN="${restore_real_docker_bin}" \
  RESTORE_FAULT_MODE=block \
  RESTORE_FAULT_MARKER="${restore_concurrency_marker}" \
  RESTORE_FAULT_RELEASE="${restore_concurrency_release}" \
  PATH="${restore_fault_bin}:${PATH}" \
  SMART_AO_PREPROD_ENV_FILE="${ENV_FILE}" \
  SMART_AO_COMPOSE_PROJECT_NAME="${PROJECT}" \
  SMART_AO_RESTORE_STATE_DIR="${RESTORE_STATE_DIR}" \
  "${ROOT_DIR}/ops/restore-preprod.sh" "${BACKUP_FILE}" \
  >"${restore_concurrency_first_log}" 2>&1 &
BACKUP_TEST_LAUNCH_PID=$!
for _ in $(seq 1 100); do
  helper_pid="$(ps -o pid= --ppid "${BACKUP_TEST_LAUNCH_PID}" | awk 'NR == 1 {print $1}')"
  if [[ "${helper_pid}" =~ ^[0-9]+$ ]]; then
    helper_pgid="$(ps -o pgid= -p "${helper_pid}" | awk '{print $1}')"
    shell_pgid="$(ps -o pgid= -p "$$" | awk '{print $1}')"
    if [[ "${helper_pgid}" =~ ^[0-9]+$ && "${helper_pgid}" != "${shell_pgid}" ]]; then
      BACKUP_TEST_PGID="${helper_pgid}"
    fi
  fi
  [[ -e "${restore_concurrency_marker}" ]] && break
  sleep 0.1
done
[[ -e "${restore_concurrency_marker}" && -n "${BACKUP_TEST_PGID}" ]] \
  || fail "first concurrent restore did not reach the blocked verifier"
concurrent_restore_state_file="$(find "${RESTORE_STATE_DIR}" -maxdepth 1 -type f \
  -name 'restore-*.state' -print -quit)"
[[ -n "${concurrent_restore_state_file}" && -s "${concurrent_restore_state_file}" ]] \
  || fail "first concurrent restore did not publish its ownership receipt"
mapfile -t concurrent_restore_state_fields <"${concurrent_restore_state_file}"
[[ "${#concurrent_restore_state_fields[@]}" == "3" ]] \
  || fail "first concurrent restore receipt is malformed"
concurrent_restore_run_id="${concurrent_restore_state_fields[0]}"
concurrent_restore_db="${concurrent_restore_state_fields[1]}"
concurrent_restore_volume="${concurrent_restore_state_fields[2]}"
[[ "${concurrent_restore_run_id}" =~ ^[a-f0-9]{32}$ \
  && "${concurrent_restore_db}" == "smart_ao_restore_${concurrent_restore_run_id}" \
  && "${concurrent_restore_volume}" == "smart_ao_c5_restore_${concurrent_restore_run_id}" ]] \
  || fail "first concurrent restore receipt does not identify its exact resources"
concurrent_restore_receipt_hash="$(sha256sum -- "${concurrent_restore_state_file}" | awk '{print $1}')"
concurrent_restore_db_count="$(compose exec -T postgres psql -U smart_ao -d smart_ao -tAc \
  "SELECT count(*) FROM pg_database WHERE datname = '${concurrent_restore_db}'")"
[[ "${concurrent_restore_db_count//[[:space:]]/}" == "1" ]] \
  || fail "first concurrent restore database was not present while verifier blocked"
[[ "$(compose exec -T postgres psql -U smart_ao -d "${concurrent_restore_db}" -tAc \
  "SELECT count(*) FROM pg_catalog.pg_tables WHERE schemaname = 'public'")" =~ ^[[:space:]]*171[[:space:]]*$ ]] \
  || fail "first concurrent restore database contents are incomplete"
[[ "$(docker volume inspect --format \
  '{{ index .Labels "com.smartao.restore.run" }}' "${concurrent_restore_volume}")" \
  == "${concurrent_restore_run_id}" ]] \
  || fail "first concurrent restore volume ownership label is invalid"
active_clean_hashes_before_concurrent_restore="$(active_clean_object_hashes "${backend_container}")" \
  || fail "could not verify active C5 objects before concurrent restore refusal"
concurrent_backup_hash_before="$(sha256sum -- "${BACKUP_FILE}" \
  "${QUARANTINE_BACKUP_FILE}" "${BACKUP_MANIFEST}" | sha256sum | awk '{print $1}')"
if SMART_AO_PREPROD_ENV_FILE="${ENV_FILE}" \
  SMART_AO_COMPOSE_PROJECT_NAME="${PROJECT}" \
  SMART_AO_RESTORE_STATE_DIR="${RESTORE_STATE_DIR}" \
  "${ROOT_DIR}/ops/restore-preprod.sh" "${BACKUP_FILE}" \
  >"${restore_concurrency_second_log}" 2>&1; then
  fail "second concurrent restore unexpectedly succeeded"
fi
grep -q "another restore is already running" "${restore_concurrency_second_log}" \
  || fail "second restore did not fail on the active lock"
[[ "$(sha256sum -- "${concurrent_restore_state_file}" | awk '{print $1}')" \
  == "${concurrent_restore_receipt_hash}" ]] \
  || fail "concurrent restore modified the active receipt or resources"
[[ "$(compose exec -T postgres psql -U smart_ao -d smart_ao -tAc \
  "SELECT count(*) FROM pg_database WHERE datname = '${concurrent_restore_db}'")" =~ ^[[:space:]]*1[[:space:]]*$ ]] \
  || fail "concurrent restore removed the active temporary database"
[[ "$(docker volume inspect --format \
  '{{ index .Labels "com.smartao.restore.run" }}' "${concurrent_restore_volume}")" \
  == "${concurrent_restore_run_id}" ]] \
  || fail "concurrent restore removed or altered the active temporary volume"
[[ "$(docker inspect --format \
  '{{range .Mounts}}{{if eq .Destination "/var/lib/smart_ao/dce-quarantine"}}{{.Name}}{{end}}{{end}}' \
  "${backend_container}")" == "${active_quarantine_volume}" ]] \
  || fail "concurrent restore changed the active quarantine volume"
active_clean_hashes_after_concurrent_restore="$(active_clean_object_hashes "${backend_container}")" \
  || fail "could not verify active C5 objects after concurrent restore refusal"
[[ "${active_clean_hashes_after_concurrent_restore}" == "${active_clean_hashes_before_concurrent_restore}" ]] \
  || fail "concurrent restore changed active C5 object hashes"
[[ "$(sha256sum -- "${BACKUP_FILE}" "${QUARANTINE_BACKUP_FILE}" \
  "${BACKUP_MANIFEST}" | sha256sum | awk '{print $1}')" == "${concurrent_backup_hash_before}" ]] \
  || fail "concurrent restore changed finalized backups"
(cd "${OPS_BACKUP_DIR}" && sha256sum --check "$(basename -- "${BACKUP_MANIFEST}")" >/dev/null)
touch "${restore_concurrency_release}"
if ! wait "${BACKUP_TEST_LAUNCH_PID}"; then
  fail "first concurrent restore did not finish after release"
fi
BACKUP_TEST_PGID=""
BACKUP_TEST_LAUNCH_PID=""
grep -q 'tables=171' "${restore_concurrency_first_log}" \
  || fail "first concurrent restore did not verify the full database"
[[ "$(compose exec -T postgres psql -U smart_ao -d smart_ao -tAc \
  "SELECT count(*) FROM pg_database WHERE datname LIKE 'smart_ao_restore_%'")" =~ ^[[:space:]]*0[[:space:]]*$ ]] \
  || fail "first concurrent restore left a temporary database"
[[ -z "$(docker volume ls -q --filter label=com.smartao.purpose=quarantine-restore-verification)" ]] \
  || fail "first concurrent restore left a temporary volume"
[[ -z "$(find "${RESTORE_STATE_DIR}" -maxdepth 1 -type f -name 'restore-*.state' -print -quit)" ]] \
  || fail "first concurrent restore left its ownership receipt"
SMART_AO_PREPROD_ENV_FILE="${ENV_FILE}" \
SMART_AO_COMPOSE_PROJECT_NAME="${PROJECT}" \
SMART_AO_RESTORE_STATE_DIR="${RESTORE_STATE_DIR}" \
  "${ROOT_DIR}/ops/restore-preprod.sh" "${BACKUP_FILE}" \
  >"${WORK_DIR}/restore-after-concurrency.log" 2>&1
grep -q 'tables=171' "${WORK_DIR}/restore-after-concurrency.log" \
  || fail "post-lock replay restore did not complete"
[[ "$(compose exec -T postgres psql -U smart_ao -d smart_ao -tAc \
  "SELECT count(*) FROM pg_database WHERE datname LIKE 'smart_ao_restore_%'")" =~ ^[[:space:]]*0[[:space:]]*$ \
  && -z "$(docker volume ls -q --filter label=com.smartao.purpose=quarantine-restore-verification)" \
  && -z "$(find "${RESTORE_STATE_DIR}" -maxdepth 1 -type f -name 'restore-*.state' -print -quit)" ]] \
  || fail "post-lock replay restore left temporary resources"
[[ "$(docker inspect --format \
  '{{range .Mounts}}{{if eq .Destination "/var/lib/smart_ao/dce-quarantine"}}{{.Name}}{{end}}{{end}}' \
  "${backend_container}")" == "${active_quarantine_volume}" ]] \
  || fail "post-lock replay restore changed the active quarantine volume"
[[ "$(active_clean_object_hashes "${backend_container}")" == "${active_clean_hashes_before_concurrent_restore}" ]] \
  || fail "post-lock replay restore changed active C5 object hashes"
[[ "$(sha256sum -- "${BACKUP_FILE}" "${QUARANTINE_BACKUP_FILE}" \
  "${BACKUP_MANIFEST}" | sha256sum | awk '{print $1}')" == "${concurrent_backup_hash_before}" ]] \
  || fail "post-lock replay restore changed finalized backups"
pass "concurrent restore was rejected before receipt cleanup; first restore completed after release and a normal replay succeeded"

volume_rm_failure_marker="${WORK_DIR}/restore-volume-rm-failures"
volume_rm_failure_log="${WORK_DIR}/restore-volume-rm-failure.log"
volume_rm_failure_backup_hash="$(sha256sum -- "${BACKUP_FILE}" \
  "${QUARANTINE_BACKUP_FILE}" "${BACKUP_MANIFEST}" | sha256sum | awk '{print $1}')"
volume_rm_failure_active_hashes="$(active_clean_object_hashes "${backend_container}")" \
  || fail "could not verify active C5 hashes before volume-removal failure injection"
if SMART_AO_PREPROD_ENV_FILE="${ENV_FILE}" \
  SMART_AO_COMPOSE_PROJECT_NAME="${PROJECT}" \
  SMART_AO_RESTORE_STATE_DIR="${RESTORE_STATE_DIR}" \
  RESTORE_FAULT_VOLUME_RM=1 \
  RESTORE_FAULT_VOLUME_RM_MARKER="${volume_rm_failure_marker}" \
  REAL_DOCKER_BIN="${restore_real_docker_bin}" \
  PATH="${restore_fault_bin}:${PATH}" \
  "${ROOT_DIR}/ops/restore-preprod.sh" "${BACKUP_FILE}" \
  >"${volume_rm_failure_log}" 2>&1; then
  fail "restore succeeded despite injected temporary volume-removal failures"
fi
grep -q "could not remove isolated quarantine restore volume" "${volume_rm_failure_log}" \
  || fail "restore volume-removal failure was not reported from the main path"
grep -q "restore cleanup incomplete; protected state retained for recovery" \
  "${volume_rm_failure_log}" \
  || fail "restore volume-removal failure did not retain protected state in EXIT cleanup"
volume_rm_failure_attempts="$(wc -l <"${volume_rm_failure_marker}")"
[[ "${volume_rm_failure_attempts//[[:space:]]/}" == "2" ]] \
  || fail "volume removal failure was not attempted in both cleanup paths"
volume_rm_failure_name="$(head -n 1 "${volume_rm_failure_marker}")"
[[ "${volume_rm_failure_name}" =~ ^smart_ao_c5_restore_[a-f0-9]{32}$ ]] \
  || fail "injected volume-removal failure did not name one owned temporary volume"
volume_rm_failure_state="${RESTORE_STATE_DIR}/restore-${volume_rm_failure_name#smart_ao_c5_restore_}.state"
volume_rm_failure_run_id="${volume_rm_failure_name#smart_ao_c5_restore_}"
[[ -f "${volume_rm_failure_state}" && ! -L "${volume_rm_failure_state}" \
  && "$(stat -c '%a' "${volume_rm_failure_state}")" == "600" ]] \
  || fail "volume removal failure did not retain its exact receipt and volume"
mapfile -t volume_rm_failure_fields <"${volume_rm_failure_state}"
[[ "${#volume_rm_failure_fields[@]}" == "3" \
  && "${volume_rm_failure_fields[0]}" == "${volume_rm_failure_run_id}" \
  && "${volume_rm_failure_fields[1]}" == "smart_ao_restore_${volume_rm_failure_run_id}" \
  && "${volume_rm_failure_fields[2]}" == "${volume_rm_failure_name}" ]] \
  || fail "volume-removal failure receipt does not retain exact resource ownership"
[[ "$(compose exec -T postgres psql -U smart_ao -d smart_ao -tAc \
  "SELECT count(*) FROM pg_database WHERE datname LIKE 'smart_ao_restore_%'")" =~ ^[[:space:]]*0[[:space:]]*$ ]] \
  || fail "volume removal failure did not remove the completed temporary database"
[[ "$(docker volume inspect --format '{{.Name}}' "${volume_rm_failure_name}")" \
  == "${volume_rm_failure_name}" \
  && "$(docker volume inspect --format \
    '{{ index .Labels "com.smartao.restore.run" }}' "${volume_rm_failure_name}")" \
    == "${volume_rm_failure_run_id}" ]] \
  || fail "volume-removal failure did not preserve the receipt-owned volume"
[[ "$(docker volume ls -q --filter label=com.smartao.purpose=quarantine-restore-verification)" \
  == "${volume_rm_failure_name}" ]] \
  || fail "volume-removal failure left an unexpected restore volume"
[[ "$(docker inspect --format \
  '{{range .Mounts}}{{if eq .Destination "/var/lib/smart_ao/dce-quarantine"}}{{.Name}}{{end}}{{end}}' \
  "${backend_container}")" == "${active_quarantine_volume}" ]] \
  || fail "volume-removal failure changed the active quarantine volume"
[[ "$(active_clean_object_hashes "${backend_container}")" == "${volume_rm_failure_active_hashes}" ]] \
  || fail "volume-removal failure changed active C5 hashes"
[[ "$(sha256sum -- "${BACKUP_FILE}" "${QUARANTINE_BACKUP_FILE}" \
  "${BACKUP_MANIFEST}" | sha256sum | awk '{print $1}')" == "${volume_rm_failure_backup_hash}" ]] \
  || fail "volume-removal failure changed finalized backups"

SMART_AO_PREPROD_ENV_FILE="${ENV_FILE}" \
SMART_AO_COMPOSE_PROJECT_NAME="${PROJECT}" \
SMART_AO_RESTORE_STATE_DIR="${RESTORE_STATE_DIR}" \
  "${ROOT_DIR}/ops/restore-preprod.sh" "${BACKUP_FILE}" \
  >"${WORK_DIR}/restore-after-volume-rm-failure.log" 2>&1
grep -q 'tables=171' "${WORK_DIR}/restore-after-volume-rm-failure.log" \
  || fail "retry after volume removal failure did not restore normally"
post_recovery_restore_db_count="$(compose exec -T postgres psql -U smart_ao -d smart_ao -tAc \
  "SELECT count(*) FROM pg_database WHERE datname LIKE 'smart_ao_restore_%'" | tr -d '[:space:]')"
post_recovery_restore_volumes="$(docker volume ls -q \
  --filter label=com.smartao.purpose=quarantine-restore-verification | paste -sd ',')"
post_recovery_receipt_exists=0
[[ -e "${volume_rm_failure_state}" || -L "${volume_rm_failure_state}" ]] \
  && post_recovery_receipt_exists=1
[[ "${post_recovery_restore_db_count}" == "0" \
  && -z "${post_recovery_restore_volumes}" \
  && "${post_recovery_receipt_exists}" == "0" ]] \
  || fail "volume removal failure recovery left stale restore resources: db=${post_recovery_restore_db_count:-none} volumes=${post_recovery_restore_volumes:-none} receipt=${post_recovery_receipt_exists}"
[[ "$(docker inspect --format \
  '{{range .Mounts}}{{if eq .Destination "/var/lib/smart_ao/dce-quarantine"}}{{.Name}}{{end}}{{end}}' \
  "${backend_container}")" == "${active_quarantine_volume}" \
  && "$(active_clean_object_hashes "${backend_container}")" == "${volume_rm_failure_active_hashes}" ]] \
  || fail "volume removal failure recovery changed active C5 objects"
[[ "$(sha256sum -- "${BACKUP_FILE}" "${QUARANTINE_BACKUP_FILE}" \
  "${BACKUP_MANIFEST}" | sha256sum | awk '{print $1}')" == "${volume_rm_failure_backup_hash}" ]] \
  || fail "volume removal failure recovery changed finalized backups"
SMART_AO_PREPROD_ENV_FILE="${ENV_FILE}" \
SMART_AO_COMPOSE_PROJECT_NAME="${PROJECT}" \
SMART_AO_RESTORE_STATE_DIR="${RESTORE_STATE_DIR}" \
  "${ROOT_DIR}/ops/restore-preprod.sh" "${BACKUP_FILE}" \
  >"${WORK_DIR}/restore-after-volume-rm-failure-replay.log" 2>&1
grep -q 'tables=171' "${WORK_DIR}/restore-after-volume-rm-failure-replay.log" \
  || fail "restore replay after cleanup failure did not complete"
post_failure_replay_db_count="$(compose exec -T postgres psql -U smart_ao -d smart_ao -tAc \
  "SELECT count(*) FROM pg_database WHERE datname LIKE 'smart_ao_restore_%'" | tr -d '[:space:]')"
post_failure_replay_volumes="$(docker volume ls -q \
  --filter label=com.smartao.purpose=quarantine-restore-verification | paste -sd ',')"
post_failure_replay_receipt_exists=0
[[ -e "${volume_rm_failure_state}" || -L "${volume_rm_failure_state}" ]] \
  && post_failure_replay_receipt_exists=1
[[ "${post_failure_replay_db_count}" == "0" \
  && -z "${post_failure_replay_volumes}" \
  && "${post_failure_replay_receipt_exists}" == "0" ]] \
  || fail "restore replay after cleanup failure left temporary resources: db=${post_failure_replay_db_count:-none} volumes=${post_failure_replay_volumes:-none} receipt=${post_failure_replay_receipt_exists}"
pass "volume removal failure retained its receipt, DB was removed, retry recovered only its volume, and another restore replay succeeded"

run_dropdb_failure_cycle

RESTORE_FIXTURE_RUN_ID="$(tr -d '-' </proc/sys/kernel/random/uuid)"
RESTORE_FIXTURE_LABEL_RUN_ID="$(tr -d '-' </proc/sys/kernel/random/uuid)"
while [[ "${RESTORE_FIXTURE_LABEL_RUN_ID}" == "${RESTORE_FIXTURE_RUN_ID}" ]]; do
  RESTORE_FIXTURE_LABEL_RUN_ID="$(tr -d '-' </proc/sys/kernel/random/uuid)"
done
RESTORE_FIXTURE_VOLUME="smart_ao_c5_restore_${RESTORE_FIXTURE_RUN_ID}"
RESTORE_FIXTURE_STATE_FILE="${RESTORE_STATE_DIR}/restore-${RESTORE_FIXTURE_RUN_ID}.state"
[[ "$(compose exec -T postgres psql -U smart_ao -d smart_ao -tAc \
  "SELECT count(*) FROM pg_database WHERE datname = 'smart_ao_restore_${RESTORE_FIXTURE_RUN_ID}'")" =~ ^[[:space:]]*0[[:space:]]*$ ]] \
  || fail "mismatched-label fixture database name is already in use"
[[ ! -e "${RESTORE_FIXTURE_STATE_FILE}" ]] \
  || fail "mismatched-label fixture receipt path already exists"
created_fixture_volume="$(docker volume create \
  --label com.smartao.purpose=quarantine-restore-verification \
  --label "com.smartao.restore.run=${RESTORE_FIXTURE_LABEL_RUN_ID}" \
  "${RESTORE_FIXTURE_VOLUME}")"
[[ "${created_fixture_volume}" == "${RESTORE_FIXTURE_VOLUME}" ]] \
  || fail "could not create mismatched-label restore fixture volume"
(umask 077; printf '%s\n%s\n%s\n' \
  "${RESTORE_FIXTURE_RUN_ID}" \
  "smart_ao_restore_${RESTORE_FIXTURE_RUN_ID}" \
  "${RESTORE_FIXTURE_VOLUME}" >"${RESTORE_FIXTURE_STATE_FILE}")
chmod 600 "${RESTORE_FIXTURE_STATE_FILE}"
mismatched_receipt_hash_before="$(sha256sum -- "${RESTORE_FIXTURE_STATE_FILE}" | awk '{print $1}')"
mismatched_label_backup_hash_before="$(sha256sum -- "${BACKUP_FILE}" "${QUARANTINE_BACKUP_FILE}" \
  "${BACKUP_MANIFEST}" | sha256sum | awk '{print $1}')"
active_clean_object_hashes_before="$(active_clean_object_hashes "${backend_container}")" \
  || fail "could not read all active CLEAN C5 objects before mismatched-label refusal"
[[ -n "${active_clean_object_hashes_before}" ]] \
  || fail "active CLEAN C5 hash proof is empty before mismatched-label refusal"
if SMART_AO_PREPROD_ENV_FILE="${ENV_FILE}" \
  SMART_AO_COMPOSE_PROJECT_NAME="${PROJECT}" \
  SMART_AO_RESTORE_STATE_DIR="${RESTORE_STATE_DIR}" \
  "${ROOT_DIR}/ops/restore-preprod.sh" "${BACKUP_FILE}" \
  >"${WORK_DIR}/restore-mismatched-label.log" 2>&1; then
  fail "restore accepted a mismatched volume run label"
fi
grep -q "interrupted restore volume ownership check or cleanup failed" \
  "${WORK_DIR}/restore-mismatched-label.log" \
  || fail "mismatched-label restore failed for an unexpected reason"
docker volume inspect --format '{{.Name}}' "${RESTORE_FIXTURE_VOLUME}" \
  | grep -Fxq -- "${RESTORE_FIXTURE_VOLUME}" \
  || fail "unowned restore volume was removed"
mismatched_label_after="$(docker volume inspect --format \
  '{{ index .Labels "com.smartao.restore.run" }}' "${RESTORE_FIXTURE_VOLUME}")"
[[ "${mismatched_label_after}" == "${RESTORE_FIXTURE_LABEL_RUN_ID}" ]] \
  || fail "mismatched-label restore changed the unowned volume label"
[[ -f "${RESTORE_FIXTURE_STATE_FILE}" && ! -L "${RESTORE_FIXTURE_STATE_FILE}" \
  && "$(stat -c '%a' "${RESTORE_FIXTURE_STATE_FILE}")" == "600" \
  && "$(sha256sum -- "${RESTORE_FIXTURE_STATE_FILE}" | awk '{print $1}')" == "${mismatched_receipt_hash_before}" ]] \
  || fail "restore state receipt changed after ownership refusal"
[[ "$(compose exec -T postgres psql -U smart_ao -d smart_ao -tAc \
  "SELECT count(*) FROM pg_database WHERE datname = 'smart_ao_restore_${RESTORE_FIXTURE_RUN_ID}'")" =~ ^[[:space:]]*0[[:space:]]*$ ]] \
  || fail "mismatched-label restore created the receipt database"
[[ "$(docker inspect --format \
  '{{range .Mounts}}{{if eq .Destination "/var/lib/smart_ao/dce-quarantine"}}{{.Name}}{{end}}{{end}}' \
  "${backend_container}")" == "${active_quarantine_volume}" ]] \
  || fail "mismatched-label restore changed the active C5 volume"
active_clean_object_hashes_after="$(active_clean_object_hashes "${backend_container}")" \
  || fail "could not read all active CLEAN C5 objects after mismatched-label refusal"
[[ "${active_clean_object_hashes_after}" == "${active_clean_object_hashes_before}" ]] \
  || fail "mismatched-label restore changed active C5 object hashes"
[[ "$(sha256sum -- "${BACKUP_FILE}" "${QUARANTINE_BACKUP_FILE}" \
  "${BACKUP_MANIFEST}" | sha256sum | awk '{print $1}')" == "${mismatched_label_backup_hash_before}" ]] \
  || fail "mismatched-label restore changed finalized backups"
(cd "${OPS_BACKUP_DIR}" && sha256sum --check "$(basename -- "${BACKUP_MANIFEST}")" >/dev/null)

# The fixture belongs to this harness, and its exact mismatched label is checked before deletion.
[[ "$(docker volume inspect --format \
  '{{ index .Labels "com.smartao.restore.run" }}' "${RESTORE_FIXTURE_VOLUME}")" == "${RESTORE_FIXTURE_LABEL_RUN_ID}" ]] \
  || fail "test harness lost ownership of its mismatched-label fixture volume"
docker volume rm "${RESTORE_FIXTURE_VOLUME}" >/dev/null
rm -f -- "${RESTORE_FIXTURE_STATE_FILE}"
RESTORE_FIXTURE_VOLUME=""
RESTORE_FIXTURE_RUN_ID=""
RESTORE_FIXTURE_LABEL_RUN_ID=""
RESTORE_FIXTURE_STATE_FILE=""
pass "mismatched restore label refused; unowned volume and receipt were preserved, active C5 objects/backups unchanged, fixture then safely removed"

run_malformed_receipt_cycle 1
run_malformed_receipt_cycle 2
pass "malformed restore receipt refused twice; sentinel database, volume, receipt, active C5 objects and finalized backups were preserved before fixture cleanup"

run_unsafe_receipt_cycle symlink 1
run_unsafe_receipt_cycle symlink 2
run_unsafe_receipt_cycle permissive 1
run_unsafe_receipt_cycle permissive 2
pass "symlinked and mode-0644 restore receipts refused twice each; outside targets, sentinel DBs/volumes, active C5 objects and finalized backups remained intact before fixture cleanup"

pass "local preproduction simulation completed"
