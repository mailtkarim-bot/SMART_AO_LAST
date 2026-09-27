#!/usr/bin/env bash
set -Eeuo pipefail

# SMART_AO continuous validation loop.
# It chains reproducible checks, records a handoff, and stops on a real failure.
# It intentionally never edits production code or auto-approves owner decisions.

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

MODE="targeted"
if [[ "${1:-}" == "--full-backend" ]]; then MODE="full-backend"; fi

STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
OUT_DIR="${ROOT_DIR}/.codex/continuous-runs/${STAMP}"
mkdir -p "$OUT_DIR"

log(){ printf '[%s] %s\n' "$(date -u +%H:%M:%S)" "$*" | tee -a "$OUT_DIR/run.log"; }
run(){ local name="$1"; shift; log "START $name"; "$@" >"$OUT_DIR/${name}.log" 2>&1 || { log "FAIL $name"; tail -80 "$OUT_DIR/${name}.log"; exit 1; }; log "PASS $name"; }

log "ROOT $ROOT_DIR"
git status --short >"$OUT_DIR/git-status.txt"
git rev-parse HEAD >"$OUT_DIR/head.txt"

if [[ "$MODE" == "full-backend" ]]; then
  run backend-full env SMART_AO_TEST_DATABASE_URL="${SMART_AO_TEST_DATABASE_URL:?set SMART_AO_TEST_DATABASE_URL for --full-backend}" ./.venv/bin/pytest backend/tests -q
else
  run backend-targeted env SMART_AO_TEST_DATABASE_URL="${SMART_AO_TEST_DATABASE_URL:?set SMART_AO_TEST_DATABASE_URL for targeted mode}" ./.venv/bin/pytest -q \
    backend/tests/architecture/test_application_infrastructure_boundary.py \
    backend/tests/architecture/test_schema_head_contract.py \
    backend/tests/ops/test_preprod_ops_contract.py \
    backend/tests/ops/test_product_freeze_authority_contract.py
fi

run frontend-test pnpm --dir web test -- --runInBand
run frontend-typecheck pnpm --dir web typecheck
run frontend-lint pnpm --dir web lint
run frontend-build pnpm --dir web build

cat >"$OUT_DIR/README.md" <<EOF
# SMART_AO continuous run

- UTC: $STAMP
- mode: $MODE
- commit: $(git rev-parse HEAD)
- result: PASS
- production code: unchanged by this loop
- owner decision: none inferred
EOF
log "PASS all checks; evidence: $OUT_DIR"
