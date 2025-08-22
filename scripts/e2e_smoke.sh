#!/usr/bin/env bash
set -euo pipefail

# Simple E2E smoke runner that starts services, waits for health, runs E2E, then cleans up.
# Usage:
#   bash scripts/e2e_smoke.sh

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
LOG_DIR="$ROOT_DIR/_e2e_logs"
mkdir -p "$LOG_DIR"

SIM_BASE_URL=${SIM_BASE_URL:-http://127.0.0.1:8001}
DB_API_URL=${DB_API_URL:-http://127.0.0.1:8000}
REPORT_API_URL=${REPORT_API_URL:-http://127.0.0.1:8091}

# Always use the project's virtualenv interpreter to avoid sitecustomize exits.
PY="$ROOT_DIR/.venv/bin/python"
if [ ! -x "$PY" ]; then
  echo "ERROR: $PY not found or not executable. Create it with: python3 -m venv .venv && .venv/bin/pip install -r requirements-unified.txt" >&2
  exit 1
fi

start_server() {
  local name=$1
  shift
  local logfile="$LOG_DIR/${name}.log"
  echo "Starting $name ... (logs: $logfile)"
  # shellcheck disable=SC2068
  nohup "$@" >"$logfile" 2>&1 &
  echo $!
}

wait_for() {
  local url=$1
  local tries=${2:-50}
  local delay=${3:-0.2}
  for ((i=1; i<=tries; i++)); do
    if curl -sf "$url" >/dev/null; then
      return 0
    fi
    sleep "$delay"
  done
  return 1
}

cleanup() {
  local code=$?
  echo "\nStopping services ..."
  for pid in ${PIDS:-}; do
    if kill -0 "$pid" 2>/dev/null; then
      kill "$pid" || true
      # give it a moment
      sleep 0.2
      kill -9 "$pid" 2>/dev/null || true
    fi
  done
  exit $code
}
trap cleanup EXIT INT TERM

cd "$ROOT_DIR"

PIDS=""
# Start services
SP_PID=$(start_server sim "$PY" -m uvicorn src.sharepoint_sim.server:app --reload --port 8001)
PIDS+=" $SP_PID"
DB_PID=$(start_server db  "$PY" -m uvicorn src.db_service_api:app        --reload --port 8000)
PIDS+=" $DB_PID"
RS_PID=$(start_server rpt "$PY" -m uvicorn src.report_service_api:app    --port   8091)
PIDS+=" $RS_PID"

# Wait for health
echo "Waiting for services to be healthy ..."
wait_for "$SIM_BASE_URL/sim/spec"
wait_for "$DB_API_URL/health"
wait_for "$REPORT_API_URL/health"

# Preflight
echo "\nPreflight checks:"
SIM_BASE_URL="$SIM_BASE_URL" DB_API_URL="$DB_API_URL" REPORT_API_URL="$REPORT_API_URL" \
  "$PY" scripts/preflight_health.py

# Run E2E once
echo "\nRunning E2E once ..."
SIM_BASE_URL="$SIM_BASE_URL" DB_API_URL="$DB_API_URL" REPORT_API_URL="$REPORT_API_URL" \
  "$PY" scripts/run_e2e_once.py

echo "\nE2E smoke completed successfully. Logs in $LOG_DIR"
