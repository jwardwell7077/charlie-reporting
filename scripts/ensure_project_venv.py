"""Fail fast if not running under the project-local virtual environment.

Usage (import side-effect) or run:
    python scripts/ensure_project_venv.py
Integrate in pytest.ini addopts or conftest to enforce.
"""
from __future__ import annotations

import pathlib
import sys

PROJECT_ROOT = pathlib.Path(__file__).resolve().parent.parent
EXPECTED = PROJECT_ROOT / '.venv'

# Resolve the actual interpreter path (follow symlinks)
exe = pathlib.Path(sys.executable).resolve()

problems: list[str] = []
if EXPECTED not in exe.parents:
    problems.append(f"Interpreter {exe} is not inside project .venv ({EXPECTED}).")

required_marker = EXPECTED / 'pyvenv.cfg'
if not required_marker.exists():
    problems.append(f"Missing pyvenv.cfg inside {EXPECTED}; venv may not be created.")

if problems:
    joined = "\n - ".join(["Environment enforcement issues:"] + problems)
    # Keep message short for CI logs
    raise SystemExit(joined)

if __name__ == '__main__':
    print(f"Interpreter OK: {exe}")
