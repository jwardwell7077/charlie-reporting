"""End-to-end: Scheduler downloads via sim REST, Consumer ingests to DB."""
from pathlib import Path
from unittest.mock import MagicMock

from fastapi.testclient import TestClient
from sharepoint_sim.server import app
from scheduler import SyncJob, SharePointClient, DBServiceClient
from consumer.file_watcher import FileConsumer
from db_service import DBClient


def test_e2e_scheduler_to_consumer_to_db(tmp_path: Path) -> None:
    # Generate two simulator files via REST
    client = TestClient(app)
    client.post("/sim/reset")
    resp = client.post("/sim/generate", params={"types": "ACQ,Productivity", "rows": 4})
    created = {item["filename"].split("__")[0]: item["filename"] for item in resp.json()["files"]}
    f1_name = created["ACQ"]
    f2_name = created["Productivity"]

    # Scheduler config and mock DB to allow both files
    ingest_dir = tmp_path / "ingest"
    cfg = {"sharepoint_folder": "/Shared Documents/Reports", "ingestion_dir": str(ingest_dir)}
    sp = SharePointClient(session=client, base_url="")
    db = DBServiceClient()
    db.get_ingested_files = MagicMock(return_value=[])  # type: ignore

    # Run scheduler sync job
    job = SyncJob(cfg, sp, db)
    downloaded = job.run()
    assert set(downloaded) == {f1_name, f2_name}
    assert (ingest_dir / f1_name).exists() and (ingest_dir / f2_name).exists()

    # Consumer ingests into DB
    archive_dir = tmp_path / "archive"
    archive_dir.mkdir(parents=True, exist_ok=True)
    consumer = FileConsumer(ingest_dir, archive_dir, DBClient())
    consumer.consume_new_files()

    # Files archived, not in ingest anymore
    assert not (ingest_dir / f1_name).exists()
    assert not (ingest_dir / f2_name).exists()
    assert (archive_dir / f1_name).exists()
    assert (archive_dir / f2_name).exists()
