"""Tests for DBServiceClient.get_ingested_files against DB API app."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import List

from fastapi.testclient import TestClient

from db_service_api import app as db_app
from scheduler import DBServiceClient


def test_get_ingested_files_filters_by_time_window() -> None:
    client = TestClient(db_app)
    # Create ingestion_log and rows representing ingested files
    now = datetime.now(timezone.utc)
    inside_time = now - timedelta(minutes=30)
    outside_time = now - timedelta(hours=2)
    inside_dt = inside_time.strftime("%Y-%m-%d_%H%M")
    outside_dt = outside_time.strftime("%Y-%m-%d_%H%M")
    # Ensure ingestion_log exists
    client.post("/tables", json={"table_name": "ingestion_log", "columns": {"filename": "TEXT", "dataset": "TEXT", "ingested_at": "TEXT"}})
    # Insert two log rows, one inside, one outside window
    client.post("/tables/ingestion_log/rows", json={"row": {"filename": f"ACQ__{inside_dt}.csv", "dataset": "ACQ", "ingested_at": inside_time.isoformat(timespec="seconds")}})
    client.post("/tables/ingestion_log/rows", json={"row": {"filename": f"Productivity__{outside_dt}.csv", "dataset": "Productivity", "ingested_at": outside_time.isoformat(timespec="seconds")}})

    svc = DBServiceClient(api_url="", session=client)

    start = (now - timedelta(hours=1)).isoformat(timespec="seconds")
    end = now.isoformat(timespec="seconds")
    files: List[str] = svc.get_ingested_files(start, end)

    assert f"ACQ__{inside_dt}.csv" in files
    assert f"Productivity__{outside_dt}.csv" not in files
