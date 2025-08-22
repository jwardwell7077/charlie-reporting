"""Tests for Report Service API using in-process DB Service API via TestClient."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path

from fastapi.testclient import TestClient

from db_service_api import app as db_app
from report_service_api import app as report_app


def test_generate_csv_report(tmp_path: Path) -> None:
    # Prepare DB API with a dataset and some rows
    db_client = TestClient(db_app)
    dataset = "ACQ"
    # Recreate table cleanly
    db_client.post("/tables", json={"table_name": dataset, "columns": {"timestamp": "TEXT", "value": "TEXT"}})

    now = datetime.now(timezone.utc)
    rows = [
        {"timestamp": (now - timedelta(minutes=40)).isoformat(timespec="seconds"), "value": "a"},
        {"timestamp": (now - timedelta(minutes=20)).isoformat(timespec="seconds"), "value": "b"},
        {"timestamp": (now - timedelta(minutes=5)).isoformat(timespec="seconds"), "value": "c"},
    ]
    for r in rows:
        db_client.post(f"/tables/{dataset}/rows", json={"row": r})

    # Wire report app to use the in-process DB API TestClient
    report_app.state.db_session = db_client  # type: ignore[attr-defined]

    # Ensure reports directory is isolated
    report_app.dependency_overrides = {}

    client = TestClient(report_app)

    start = (now - timedelta(minutes=30)).isoformat(timespec="seconds")
    end = now.isoformat(timespec="seconds")

    resp = client.post("/reports/generate", json={
        "dataset": dataset,
        "start_time": start,
        "end_time": end,
        "format": "csv",
    })
    assert resp.status_code == 200
    payload = resp.json()
    filename = payload["filename"]
    path = Path(payload["path"])
    assert payload["dataset"] == dataset
    assert payload["format"] == "csv"
    assert payload["row_count"] >= 0
    # File exists and can be downloaded
    assert path.exists()

    dl = client.get(f"/reports/download/{filename}")
    assert dl.status_code == 200
    assert dl.headers["content-type"].startswith("text/csv")
    assert "value" in dl.text


def test_list_reports(tmp_path: Path) -> None:
    client = TestClient(report_app)
    res = client.get("/reports")
    assert res.status_code == 200
    assert "reports" in res.json()
