"""Project-wide Python startup customizations.

This enforces that any execution within this repository uses the local .venv
interpreter. Python automatically imports sitecustomize if present on sys.path.
"""
from __future__ import annotations

import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent
VENV = ROOT / '.venv'
exe = pathlib.Path(sys.executable).resolve()
if VENV.exists() and VENV not in exe.parents:
    msg = (
        f"ERROR: Wrong interpreter: {exe}\n"
        f"Expected interpreter inside {VENV}. Activate with: source .venv/bin/activate\n"
        "Aborting."
    )
    raise SystemExit(msg)
