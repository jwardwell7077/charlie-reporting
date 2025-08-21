"""Failure-mode tests for SyncJob (download retries/backoff)."""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List
from unittest.mock import MagicMock

import pytest

from scheduler import SyncJob, SharePointClient, DBServiceClient


class FlakySharePoint(SharePointClient):
    def __init__(self, fail_times: int) -> None:
        super().__init__({})
        self._fail_times = fail_times
        self._calls: int = 0

    def list_files(self, folder: str) -> List[str]:  # type: ignore[override]
        return ["ACQ__2025-08-21_1200.csv"]

    def download_file(self, folder: str, filename: str, dest: Path) -> Path:  # type: ignore[override]
        self._calls += 1
        if self._calls <= self._fail_times:
            raise RuntimeError("network error")
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text("col\nval\n")
        return dest


def test_syncjob_retries_and_succeeds(tmp_path: Path) -> None:
    cfg: Dict[str, Any] = {
        "sharepoint_folder": "/Shared Documents/Reports",
        "ingestion_dir": str(tmp_path),
        "max_retries": 3,
        "retry_delay_seconds": 0,
    }
    sp = FlakySharePoint(fail_times=2)
    db = DBServiceClient(api_url="", session=MagicMock())
    db.get_ingested_files = MagicMock(return_value=[])  # type: ignore

    job = SyncJob(cfg, sp, db)
    out = job.run()
    assert out == ["ACQ__2025-08-21_1200.csv"]


def test_syncjob_exhausts_retries(tmp_path: Path) -> None:
    cfg: Dict[str, Any] = {
        "sharepoint_folder": "/Shared Documents/Reports",
        "ingestion_dir": str(tmp_path),
        "max_retries": 2,
        "retry_delay_seconds": 0,
    }
    sp = FlakySharePoint(fail_times=5)
    db = DBServiceClient(api_url="", session=MagicMock())
    db.get_ingested_files = MagicMock(return_value=[])  # type: ignore

    job = SyncJob(cfg, sp, db)
    out = job.run()
    assert out == []
    # File should not exist after failed attempts
    assert not (tmp_path / "ACQ__2025-08-21_1200.csv").exists()
