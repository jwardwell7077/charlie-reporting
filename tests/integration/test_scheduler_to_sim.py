"""Integration: Scheduler SyncJob downloads only new files via sim REST API."""
from pathlib import Path
from typing import Dict, Any
from unittest.mock import MagicMock

from fastapi.testclient import TestClient
from sharepoint_sim.server import app
from scheduler import SyncJob, SharePointClient, DBServiceClient


def test_scheduler_downloads_new_files(tmp_path: Path) -> None:
    # Arrange: generate two files in simulator via REST
    client = TestClient(app)
    client.post("/sim/reset")
    resp = client.post("/sim/generate", params={"types": "ACQ,Productivity", "rows": 5})
    data = resp.json()
    created = {item["filename"].split("__")[0]: item["filename"] for item in data["files"]}
    acq_name = created["ACQ"]
    prod_name = created["Productivity"]

    # Config scheduler to download into ingestion directory using HTTP SharePointClient
    ingest_dir = tmp_path / "ingest"
    cfg: Dict[str, Any] = {"sharepoint_folder": "/Shared Documents/Reports", "ingestion_dir": str(ingest_dir)}

    sp = SharePointClient(session=client, base_url="")
    db = DBServiceClient()

    # Mock DB to pretend one file already ingested
    db.get_ingested_files = MagicMock(return_value=[acq_name])  # type: ignore

    job = SyncJob(cfg, sp, db)
    downloaded = job.run()

    assert prod_name in downloaded
    assert acq_name not in downloaded
    assert (ingest_dir / prod_name).exists()
