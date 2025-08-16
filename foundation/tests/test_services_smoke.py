"""Smoke tests for services layer to raise coverage and validate basic behaviors."""
from __future__ import annotations

from pathlib import Path
from typing import Any

from fastapi.testclient import TestClient

from services.api import app
from services.sharepoint_stub import SharePointStub


def test_sharepoint_stub_upload_and_list(tmp_path: Path) -> None:
    lib = tmp_path / "lib"
    stub = SharePointStub(lib)
    src = tmp_path / "sample.txt"
    src.write_text("hello")
    uploaded = stub.upload(src)
    assert uploaded.exists()
    files = stub.list_files()
    assert uploaded in files


def test_api_health_endpoint() -> None:
    client = TestClient(app)
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_api_ingest_and_generate_hourly(tmp_path: Path, monkeypatch: Any) -> None:
    # Monkeypatch settings loader to isolate environment and paths.
    from config import settings as settings_module
    from config.settings import (
        CollectorConfig,
        EmailConfig,
        ReportConfig,
        SchedulesConfig,
        Settings,
    )

    def fake_load_settings() -> Settings:  # noqa: D401
        """Return ephemeral settings object pointing into tmp paths."""
        return Settings(
            schedules=SchedulesConfig(hourly_interval_minutes=60, quad_daily_times=None),
            data_sources=[],
            collector=CollectorConfig(
                input_root=tmp_path / "input",
                staging_dir=tmp_path / "staging",
                archive_dir=tmp_path / "archive",
            ),
            report=ReportConfig(
                output_dir=tmp_path / "out",
                workbook_name="test.xlsx",
                columns={},
            ),
            email=EmailConfig(
                from_addr="noreply@example.com",
                recipients=[],
                subject_template="Daily Report {date}",
                include_sheets=[],
            ),
        )

    monkeypatch.setattr(settings_module, "load_settings", fake_load_settings)  # type: ignore[arg-type]
    monkeypatch.setenv("PYTHONPATH", "foundation/src")

    client = TestClient(app)
    # No data sources -> ingest returns zeros
    r_ingest = client.post("/ingest")
    assert r_ingest.status_code == 200
    data = r_ingest.json()
    assert data["staged_files"] == 0
    assert data["rows_loaded_total"] == 0

    r_gen = client.post("/generate/hourly")
    assert r_gen.status_code == 200
    workbook_path = Path(r_gen.json()["workbook"])
    assert workbook_path.exists()
