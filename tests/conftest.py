"""Pytest session configuration hooking integration dependency preflight.

This file ensures the integration preflight script runs automatically once
at the start of the pytest session. It aborts the test run early if critical
failures are detected. The JSON summary produced by the script is exposed
via a session-scoped fixture for optional inspection in tests.
"""
from __future__ import annotations

import json
import subprocess
from pathlib import Path
import sys
from typing import Any, Dict

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = PROJECT_ROOT / "src"
SUMMARY_PATH = PROJECT_ROOT / "tests" / "integration_preflight_summary.json"
PRECHECK_SCRIPT = PROJECT_ROOT / "tests" / "check_integration_dependencies.py"

# Ensure 'src' folder is on sys.path so tests can import modules without 'src.' prefix
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))


def _run_preflight() -> dict[str, Any]:
    """Execute preflight script if summary absent or script newer.

    Returns:
        dict[str, Any]: Parsed JSON summary from the preflight execution.
    """
    needs_run = True
    if SUMMARY_PATH.exists():
        if PRECHECK_SCRIPT.exists() and SUMMARY_PATH.stat().st_mtime >= PRECHECK_SCRIPT.stat().st_mtime:
            needs_run = False
    if needs_run:
        # Run using same interpreter that invokes pytest for consistency.
        result = subprocess.run(
            ["python", str(PRECHECK_SCRIPT)],
            cwd=str(PROJECT_ROOT),
            capture_output=True,
            text=True,
            check=False,
        )
        print("[preflight stdout]\n" + result.stdout)
        if result.stderr:
            print("[preflight stderr]\n" + result.stderr)
        if result.returncode != 0:
            raise RuntimeError("Integration preflight failed; aborting tests.")
    if SUMMARY_PATH.exists():
        return json.loads(SUMMARY_PATH.read_text(encoding="utf-8"))
    raise RuntimeError("Preflight summary missing after execution.")


@pytest.fixture(scope="session", name="preflight_summary")
def fixture_preflight_summary() -> Dict[str, Any]:
    """Session fixture providing integration preflight summary.

    Returns:
        Dict[str, Any]: Parsed JSON summary dictionary.
    """
    return _run_preflight()
