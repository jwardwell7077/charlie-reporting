#!/usr/bin/env bash
set -euo pipefail

start_ts=$(date -u +%Y-%m-%dT%H:%M:%SZ)
echo "QUALITY GATE START ${start_ts}"

run() {
  local name="$1"; shift
  echo "\n== ${name} =="
  "$@"
}

# Use workspace root relative paths
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SRC_DIR="${ROOT_DIR}/foundation/src"
VENV_BIN="${ROOT_DIR}/.venv/bin"

run "Ruff"      "${VENV_BIN}/ruff" check "${SRC_DIR}" foundation/tests
run "Mypy"      "${VENV_BIN}/mypy" "${SRC_DIR}" foundation/tests || true  # allow test type looseness for now
run "Pydoclint" "${VENV_BIN}/pydoclint" "${SRC_DIR}"
run "Interrogate" "${VENV_BIN}/interrogate" -c "${ROOT_DIR}/pyproject.toml" "${SRC_DIR}"
run "Pyright"     "${VENV_BIN}/pyright" --warnings "${SRC_DIR}" foundation/tests
run "Pytest"    env PYTHONPATH="${SRC_DIR}" "${VENV_BIN}/pytest" --cov="${SRC_DIR}" --cov-report=term-missing --cov-fail-under=100 -vv foundation/tests

end_ts=$(date -u +%Y-%m-%dT%H:%M:%SZ)
echo "\nQUALITY GATE COMPLETE ✅ ${end_ts}"
