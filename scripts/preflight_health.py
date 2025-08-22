#!/usr/bin/env python3
"""Preflight health checks for local E2E demo.

Checks the availability of:
- SharePoint Simulator (GET /sim/spec)
- DB Service API (GET /health)
- Report Service API (GET /health)
"""
from __future__ import annotations

import os
import sys
import json
from typing import Tuple

try:
    import requests  # type: ignore
except Exception as exc:  # pragma: no cover
    print("requests is required. Please install dependencies.")
    raise


def check(url: str) -> Tuple[bool, str]:
    try:
        r = requests.get(url, timeout=5)
        ok = r.status_code == 200
        return ok, f"{r.status_code}"
    except Exception as e:  # noqa: BLE001
        return False, str(e)


def main() -> None:
    sim_base = os.environ.get("SIM_BASE_URL", "http://localhost:8001").rstrip("/")
    db_base = os.environ.get("DB_API_URL", "http://localhost:8000").rstrip("/")
    rpt_base = os.environ.get("REPORT_API_URL", "http://localhost:8091").rstrip("/")

    checks = {
        "sim": (f"{sim_base}/sim/spec",),
        "db": (f"{db_base}/health",),
        "report": (f"{rpt_base}/health",),
    }

    results = {}
    all_ok = True
    for name, (url,) in checks.items():
        ok, info = check(url)
        results[name] = {"url": url, "ok": ok, "info": info}
        all_ok = all_ok and ok

    print(json.dumps(results, indent=2))
    sys.exit(0 if all_ok else 1)


if __name__ == "__main__":
    main()
