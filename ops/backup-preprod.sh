#!/usr/bin/env bash
set -Eeuo pipefail

ROOT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
OPS_DIR="${ROOT_DIR}/ops"
ENV_FILE="${SMART_AO_PREPROD_ENV_FILE:-${OPS_DIR}/.env.preprod}"
COMPOSE_FILE="${OPS_DIR}/docker-compose.preprod.yml"
COMPOSE_PROJECT_NAME="${SMART_AO_COMPOSE_PROJECT_NAME:-}"
BACKUP_DIR="${SMART_AO_BACKUP_DIR:-/var/backups/smart-ao}"
RETENTION_DAYS="${SMART_AO_BACKUP_RETENTION_DAYS:-30}"

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

container_for_service() {
  compose ps -q "$1" 2>/dev/null | head -n 1
}

volume_for_mount() {
  local container="$1" destination="$2" volume_name
  [[ -n "${container}" ]] || return 0
  volume_name="$(docker inspect "${container}" --format '{{range .Mounts}}{{if eq .Destination "'"${destination}"'"}}{{.Name}}{{end}}{{end}}')"
  [[ -n "${volume_name}" ]] || return 0
  printf '%s\n' "${volume_name}"
}

backup_volume() {
  local container="$1" helper_image="$2" destination="$3" output="$4" volume_name
  volume_name="$(volume_for_mount "${container}" "${destination}")"
  if [[ -z "${volume_name}" ]]; then
    if [[ "${SMART_AO_BACKUP_ALLOW_MISSING_VOLUMES:-0}" == "1" ]]; then
      printf 'WARNING: skipping absent volume %s by explicit override.\n' "${destination}" >&2
      return 0
    fi
    fail "expected persistent volume is not mounted: ${destination}"
  fi
  if ! docker run --rm --network none --read-only --user 0 --cap-drop ALL \
    --cap-add DAC_READ_SEARCH --security-opt no-new-privileges:true \
    --mount "type=volume,src=${volume_name},dst=/source,readonly" \
    "${helper_image}" tar --numeric-owner --xattrs --acls -czf - -C /source . \
    >"${output}.tmp"; then
    rm -f -- "${output}.tmp"
    fail "could not archive private volume ${destination}"
  fi
  chmod 600 "${output}.tmp"
  mv -- "${output}.tmp" "${output}"
}

main() {
  command -v docker >/dev/null 2>&1 || fail "docker is required"
  command -v gzip >/dev/null 2>&1 || fail "gzip is required"
  command -v sha256sum >/dev/null 2>&1 || fail "sha256sum is required"
  command -v tar >/dev/null 2>&1 || fail "tar is required"
  command -v flock >/dev/null 2>&1 || fail "flock is required"
  load_environment
  if [[ -n "${COMPOSE_PROJECT_NAME}" && ! "${COMPOSE_PROJECT_NAME}" =~ ^[a-z0-9][a-z0-9_-]{0,62}$ ]]; then
    fail "invalid SMART_AO_COMPOSE_PROJECT_NAME"
  fi
  [[ "${RETENTION_DAYS}" =~ ^[0-9]+$ ]] || fail "SMART_AO_BACKUP_RETENTION_DAYS must be an integer"
  umask 077
  install -d -m 700 "${BACKUP_DIR}"
  local lock_file="${BACKUP_DIR}/.backup-preprod.lock"
  exec 9>"${lock_file}"
  flock -n 9 || fail "another backup is already running for ${BACKUP_DIR}"
  find "${BACKUP_DIR}" -maxdepth 1 -type f -name 'smart_ao_*.tmp' -delete

  local timestamp sql_file c5_archive manifest manifest_tmp backend_container backend_image caddy_container
  local -a manifest_files
  timestamp="$(date -u +%Y%m%dT%H%M%S%NZ)_$$"
  sql_file="${BACKUP_DIR}/smart_ao_${timestamp}.sql.gz"
  manifest="${BACKUP_DIR}/smart_ao_${timestamp}.sha256"
  manifest_tmp="${manifest}.tmp"
  backend_container="$(container_for_service backend)"
  [[ -n "${backend_container}" ]] || fail "backend container is required to archive private volumes"
  backend_image="$(docker inspect --format '{{.Image}}' "${backend_container}")"
  [[ "${backend_image}" =~ ^sha256:[a-f0-9]{64}$ ]] || fail "cannot resolve the running backend image"
  caddy_container="$(container_for_service caddy)"

  compose exec -T postgres pg_dump --clean --if-exists --no-owner --no-privileges \
    -U "${POSTGRES_USER}" "${POSTGRES_DB}" | gzip -9 >"${sql_file}.tmp"
  mv -- "${sql_file}.tmp" "${sql_file}"
  chmod 600 "${sql_file}"

  c5_archive="${BACKUP_DIR}/smart_ao_${timestamp}.dce_quarantine.tar.gz"
  backup_volume "${backend_container}" "${backend_image}" /var/lib/smart_ao/dce-quarantine \
    "${c5_archive}"
  [[ -s "${c5_archive}" ]] || fail "required C5 quarantine volume backup is missing"
  backup_volume "${caddy_container}" "${backend_image}" /data \
    "${BACKUP_DIR}/smart_ao_${timestamp}.caddy_data.tar.gz"
  backup_volume "${caddy_container}" "${backend_image}" /config \
    "${BACKUP_DIR}/smart_ao_${timestamp}.caddy_config.tar.gz"

  if ! (
    cd "${BACKUP_DIR}"
    shopt -s nullglob
    manifest_files=("smart_ao_${timestamp}.sql.gz" "smart_ao_${timestamp}".*.tar.gz)
    shopt -u nullglob
    (( ${#manifest_files[@]} >= 2 )) || exit 1
    sha256sum -- "${manifest_files[@]}" >"$(basename -- "${manifest_tmp}")" \
      && sha256sum --check --status "$(basename -- "${manifest_tmp}")"
  ); then
    rm -f -- "${manifest_tmp}"
    fail "could not create and verify the complete backup manifest"
  fi
  chmod 600 "${manifest_tmp}"
  mv -- "${manifest_tmp}" "${manifest}"

  find "${BACKUP_DIR}" -maxdepth 1 -type f -name 'smart_ao_*' \
    -mtime "+${RETENTION_DAYS}" -delete
  printf 'Backup completed: %s\n' "${timestamp}"
}

main "$@"
