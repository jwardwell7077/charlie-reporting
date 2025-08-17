"""Abort execution if not running inside the project's .venv.

Usage: invoked early by tasks / quality gate scripts to guarantee the
correct interpreter. This enforces a single source of truth for tooling.
"""
from __future__ import annotations

import pathlib
import sys

EXPECTED_SEGMENT = ".venv"

EXEC = pathlib.Path(sys.executable).resolve()
if EXPECTED_SEGMENT not in EXEC.parts:
    sys.stderr.write(f"[venv-check] Expected to run inside .venv (found executable: {EXEC})\n")
    # Provide guidance
    proj_root = pathlib.Path(__file__).resolve().parents[1]
    activate = proj_root / ".venv" / "bin" / "activate"
    sys.stderr.write(f"Activate with: source {activate}\n")
    sys.exit(1)

# Optional: assert PYTHONPATH does not contain site-wide global paths if you want stricter isolation.
# for p in sys.path:
#     if p.startswith("/usr/lib/python"):
#         sys.stderr.write("[venv-check] Global site-packages detected in sys.path: " f"{p}\n")
#         sys.exit(1)
