"""
End-to-end: sharepoint_sim -> scheduler SyncJob -> FileConsumer -> DB stub.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

import pytest

import scheduler_sharepoint_api as sp_api
from scheduler import SyncJob, SharePointClient, DBServiceClient
from consumer.file_watcher import FileConsumer


@pytest.fixture()
def setup_dirs(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Dict[str, Path]:
    sim_root = tmp_path / "sim_root"
    ingest = tmp_path / "ingest"
    archive = tmp_path / "archive"
    sim_root.mkdir(); ingest.mkdir(); archive.mkdir()
    monkeypatch.setenv("SP_SIM_OUTPUT_DIR", str(sim_root))
    sp_api._generator = None  # type: ignore[attr-defined]
    sp_api._storage = None  # type: ignore[attr-defined]
    return {"sim_root": sim_root, "ingest": ingest, "archive": archive}


@pytest.fixture()
def scheduler_config(setup_dirs: Dict[str, Path]) -> Dict[str, Any]:
    return {
        "sharepoint_folder": "/Shared Documents/Reports",
        "ingestion_dir": str(setup_dirs["ingest"]),
        "interval_minutes": 60,
    }


def test_e2e_pipeline(setup_dirs: Dict[str, Path], scheduler_config: Dict[str, Any]) -> None:
    # Pre-generate sim files
    created = sp_api.pregenerate_datasets(["ACQ", "Dials"], rows=4)

    # DB stub: nothing ingested first run
    class DBStub(DBServiceClient):
        def __init__(self) -> None:
            self.sent: list[str] = []
        def get_ingested_files(self, start_time: str, end_time: str) -> list[str]:  # noqa: D401
            return []
        def send_to_db(self, data: str) -> None:  # noqa: D401
            self.sent.append(data)

    sp_client = SharePointClient()
    db_client = DBStub()

    # Run scheduler sync
    job = SyncJob(config=scheduler_config, sharepoint_client=sp_client, db_service_client=db_client)
    downloaded = job.run()
    assert set(downloaded) == set(created)

    # Run consumer to push to DB and archive
    consumer = FileConsumer(Path(scheduler_config["ingestion_dir"]), setup_dirs["archive"], db_client)
    consumer.consume_new_files()

    # Assert DB received data for each file and files archived
    assert len(db_client.sent) == len(created)
    assert not any(Path(scheduler_config["ingestion_dir"]).glob("*.csv"))
    assert len(list(setup_dirs["archive"].glob("*.csv"))) == len(created)
