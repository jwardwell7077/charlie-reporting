#!/usr/bin/env bash
set -euo pipefail
PROJECT_ROOT="$(git rev-parse --show-toplevel)"
EXPECTED="$PROJECT_ROOT/.venv"
PY=$(command -v python)
if [[ "$PY" != $EXPECTED/* ]]; then
  echo "Pre-commit: wrong interpreter $PY (expected under $EXPECTED)" >&2
  exit 1
fi
python scripts/ensure_project_venv.py || exit 1
