#!/usr/bin/env python
"""Run pytest for each service that contains its own pytest.ini.
Aggregates exit codes; prints summary.
"""
from __future__ import annotations

import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
SERVICES_DIR = ROOT / "services"


def find_service_dirs():
    for svc in SERVICES_DIR.iterdir():
        if not svc.is_dir():
            continue
        if (svc / "pytest.ini").exists() and (svc / "tests").exists():
            yield svc


def run_pytest(service: pathlib.Path) -> int:
    print(f"\n=== Running tests for service: {service.name} ===")
    cmd = [sys.executable, "-m", "pytest"]
    result = subprocess.run(cmd, check=False, cwd=service)
    return result.returncode


def main() -> int:
    failures = []
    for svc in sorted(find_service_dirs()):
        code = run_pytest(svc)
        if code != 0:
            failures.append((svc.name, code))
    if failures:
        print("\n=== Summary: FAILURES ===")
        for name, code in failures:
            print(f"{name}: exit code {code}")
        return 1
    print("\nAll service test suites passed.")
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
