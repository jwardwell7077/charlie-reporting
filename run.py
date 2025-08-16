#!/usr/bin/env python
"""Monolithic convenience entrypoint.

This script now ONLY ensures the correct interpreter is used and prints
guidance; actual service execution has moved to per-service packages.
"""
from __future__ import annotations

import pathlib
import sys
import textwrap

ROOT = pathlib.Path(__file__).resolve().parent
EXPECTED_VENV = ROOT / '.venv'

def ensure_project_venv() -> None:
    exe = pathlib.Path(sys.executable).resolve()
    if EXPECTED_VENV.exists() and EXPECTED_VENV not in exe.parents:
        raise SystemExit(
            f"Wrong interpreter: {exe}\nActivate with: source .venv/bin/activate\n" + 
            f"Expected inside: {EXPECTED_VENV}\n"
        )

def main() -> int:
    ensure_project_venv()
    msg = textwrap.dedent(
        """
        Charlie Reporting – Unified Launcher

        Services are now invoked via their packages or scripts, e.g.:
          - Outlook Relay: python -m outlook_relay.main
          - Tests:        .venv/bin/python -m pytest

        This launcher only verifies environment correctness.
        """
    ).strip()
    print(msg)
    return 0

if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())