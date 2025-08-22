"""Project-wide Python startup customizations.

This enforces that any execution within this repository uses the local .venv
interpreter. Python automatically imports sitecustomize if present on sys.path.
"""
from __future__ import annotations

import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent
VENV = ROOT / ".venv"

# Prefer sys.prefix to detect active venv reliably across platforms/symlinks.
# In a venv, sys.prefix points to the venv root; sys.base_prefix points to the base interpreter.
if VENV.exists():
    try:
        active_prefix = pathlib.Path(sys.prefix).resolve()
    except Exception:  # pragma: no cover - very early interpreter state
        active_prefix = pathlib.Path(sys.prefix)
    venv_root = VENV.resolve()
    if active_prefix != venv_root:
        msg = (
            f"ERROR: Wrong interpreter prefix: {active_prefix}\n"
            f"Expected interpreter inside {venv_root}. Activate with: source .venv/bin/activate\n"
            "Aborting."
        )
        raise SystemExit(msg)
