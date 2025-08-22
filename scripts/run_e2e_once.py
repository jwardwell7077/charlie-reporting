#!/usr/bin/env python3
"""One-click E2E runner: generate sim data, download via scheduler, ingest via consumer, generate a report.

Assumes servers are running:
- Simulator at SIM_BASE_URL (default http://localhost:8001)
- DB API at DB_API_URL (default http://localhost:8000)
- Report API at REPORT_API_URL (default http://localhost:8091)
"""
from __future__ import annotations

import os
import subprocess
import sys
import json
from datetime import datetime, timedelta, timezone

try:
    import requests  # type: ignore
except Exception:
    print("requests is required. Please install dependencies.")
    sys.exit(1)


def main() -> None:
    sim = os.environ.get("SIM_BASE_URL", "http://localhost:8001").rstrip("/")
    _ = os.environ.get("DB_API_URL", "http://localhost:8000").rstrip("/")
    rpt = os.environ.get("REPORT_API_URL", "http://localhost:8091").rstrip("/")

    # 1) Generate datasets in simulator
    gen_body = {"types": ["ACQ", "Productivity"], "rows": 25}
    r = requests.post(f"{sim}/sim/generate", json=gen_body, timeout=20)
    r.raise_for_status()
    print("Simulator generated:", r.json())

    # 2) Scheduler run-once (downloads new files)
    cmd_sched = [sys.executable, "scheduler.py", "run-once"]
    subprocess.check_call(cmd_sched, cwd=os.getcwd())
    print("Scheduler run-once complete")

    # 3) Consumer run-once (ingest + archive)
    cmd_cons = [sys.executable, "scripts/run_consumer_once.py"]
    subprocess.check_call(cmd_cons, cwd=os.getcwd())
    print("Consumer run-once complete")

    # 4) Generate report (CSV) over last 1 hour for ACQ
    now = datetime.now(timezone.utc)
    start = (now - timedelta(hours=1)).isoformat(timespec="seconds")
    end = now.isoformat(timespec="seconds")
    body = {"dataset": "ACQ", "start_time": start, "end_time": end, "format": "csv"}
    rr = requests.post(f"{rpt}/reports/generate", json=body, timeout=20)
    rr.raise_for_status()
    print("Report generated:", json.dumps(rr.json(), indent=2))


if __name__ == "__main__":
    main()
