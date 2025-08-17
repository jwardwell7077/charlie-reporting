"""Stub REST email fetcher entrypoint with venv enforcement."""
from __future__ import annotations

import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent
EXPECTED_VENV = ROOT / ".venv"

def _ensure_venv() -> None:
	exe = pathlib.Path(sys.executable).resolve()
	if EXPECTED_VENV.exists() and EXPECTED_VENV not in exe.parents:
		raise SystemExit(
			f"Wrong interpreter: {exe}\nActivate with: source .venv/bin/activate\nExpected inside: {EXPECTED_VENV}\n"
		)

def main() -> int:
	_ensure_venv()
	print("REST email fetcher placeholder (implementation pending).")
	return 0

if __name__ == "__main__":  # pragma: no cover
	raise SystemExit(main())
