"""
Tests for Report Service API XLSX support.
Validates listing, generation, and download content-type.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

import pytest
from fastapi.testclient import TestClient

from report_service_api import app
from db_service_api import app as db_app

# Share one client for DB API to seed data
_db_client = TestClient(db_app)

@pytest.fixture(scope="module")
def client(tmp_path_factory: pytest.TempPathFactory) -> TestClient:
    # Isolate reports dir per test run
    tmp_dir = tmp_path_factory.mktemp("reports")
    app.state.reports_dir = Path(tmp_dir)
    # Mount a simple wrapper to call DB app via TestClient
    class _Sess:
        def get(self, url: str, **kwargs: Any):
            # Expect path-only URLs
            assert url.startswith("/"), "expected path-only URL"
            return _db_client.get(url, **kwargs)
    app.state.db_session = _Sess()
    return TestClient(app)


def _seed_table(dataset: str) -> None:
    # Create table and insert a couple of rows
    _db_client.post("/tables", json={"table_name": dataset, "schema": {"timestamp": "TEXT", "a": "TEXT"}})
    _db_client.post(f"/tables/{dataset}/rows", json={"row": {"timestamp": "2025-08-22T00:00:00Z", "a": "1"}})
    _db_client.post(f"/tables/{dataset}/rows", json={"row": {"timestamp": "2025-08-22T01:00:00Z", "a": "2"}})


def test_generate_and_download_xlsx(client: TestClient, tmp_path: Path) -> None:
    dataset = "acq_xlsx_test"
    _seed_table(dataset)
    resp = client.post(
        "/reports/generate",
        json={
            "dataset": dataset,
            "start_time": "2025-08-22T00:00:00Z",
            "end_time": "2025-08-22T23:59:59Z",
            "format": "xlsx",
        },
    )
    assert resp.status_code == 200, resp.text
    data: Dict[str, Any] = resp.json()
    assert data["format"] == "xlsx"
    assert data["filename"].endswith(".xlsx")

    # list reports includes the new xlsx
    lst = client.get("/reports")
    assert lst.status_code == 200
    names = [r["filename"] for r in lst.json()["reports"]]
    assert any(n.endswith(".xlsx") for n in names)

    # download content-type
    dl = client.get(f"/reports/download/{data['filename']}")
    assert dl.status_code == 200
    assert dl.headers.get("content-type", "").startswith(
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
