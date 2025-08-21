"""Integration: sim REST-generated files consumed by FileConsumer and inserted into DB via DBClient."""
from pathlib import Path

from fastapi.testclient import TestClient
from sharepoint_sim.server import app
from consumer.file_watcher import FileConsumer
from src.db_service import DBClient


def test_simulator_to_consumer_to_db(tmp_path: Path) -> None:
    # Arrange: generate a simulator file via REST
    client = TestClient(app)
    client.post("/sim/reset")
    resp = client.post("/sim/generate", params={"types": "ACQ", "rows": 3})
    f_name = resp.json()["files"][0]["filename"]

    # Place file into ingestion dir (simulate scheduler having downloaded it)
    ingest_dir = tmp_path / "ingest"
    archive_dir = tmp_path / "archive"
    ingest_dir.mkdir(parents=True, exist_ok=True)
    archive_dir.mkdir(parents=True, exist_ok=True)
    # Download the generated file via REST and place it into ingestion dir (simulating scheduler)
    dest = ingest_dir / f_name
    file_resp = client.get(f"/sim/download/{f_name}")
    dest.write_text(file_resp.text)

    # DB client for in-process ingest
    db_client = DBClient()

    # Consumer configured to use DBClient and archive processed files
    consumer = FileConsumer(ingest_dir, archive_dir, db_client)
    consumer.consume_new_files()

    # Assert file moved to archive and not left in ingest
    assert not dest.exists()
    assert (archive_dir / f_name).exists()
