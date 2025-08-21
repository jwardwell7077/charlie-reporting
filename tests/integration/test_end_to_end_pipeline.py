"""End-to-end test: Scheduler -> SharePoint stub -> FileConsumer -> DB.

This test verifies the full pipeline, using:
- Scheduler SyncJob to download files to an ingestion directory.
- FileConsumer to read those files and send to a DB stub, archiving afterward.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from scheduler import Scheduler, SharePointClient, DBServiceClient
from consumer.file_watcher import FileConsumer


class _DBCapture(DBServiceClient):
    """DB stub that captures payloads sent by FileConsumer."""

    def __init__(self) -> None:
        super().__init__()
        self.payloads: list[str] = []

    def get_ingested_files(self, start_time: str, end_time: str) -> list[str]:  # noqa: D401
        return []

    def send_to_db(self, data: str) -> None:  # type: ignore[override]
        self.payloads.append(data)


def test_end_to_end_scheduler_to_consumer_to_db(tmp_path: Path) -> None:
    """Full chain should download files, process them, and archive afterward."""
    ingestion = tmp_path / "ingest"
    archive = tmp_path / "archive"
    cfg: Dict[str, Any] = {
        "sharepoint_folder": "/Shared Documents/Reports",
        "ingestion_dir": str(ingestion),
    }

    db = _DBCapture()

    # 1) Download from SharePoint stub into ingestion dir
    scheduler = Scheduler(config=cfg, sharepoint_client=SharePointClient({}), db_service_client=db)
    scheduler.run_once()

    # Sanity: files present
    files = sorted(ingestion.glob("*.csv"))
    assert files, "Expected downloaded files in ingestion dir"

    # 2) Consume files and send to DB, archiving afterward
    consumer = FileConsumer(input_dir=ingestion, archive_dir=archive, db_service=db)
    consumer.consume_new_files()

    # After consumption, ingestion should be empty and archive should have files
    assert not any(ingestion.glob("*.csv")), "Ingestion directory should be empty after processing"
    assert any(archive.glob("*.csv")), "Archive directory should contain processed files"

    # DB capture should have payloads for each processed file
    assert db.payloads, "DB should have received payloads"
