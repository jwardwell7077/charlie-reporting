"""
Integration: sharepoint_sim storage <-> FileConsumer <-> DB stub.

Flow:
1) Write generated sim file into ingestion_dir
2) FileConsumer consumes, sends to DB stub, and archives
3) Assert DB received data and file moved
"""
from __future__ import annotations

from pathlib import Path

import pytest

from consumer.file_watcher import FileConsumer
from sharepoint_sim.config import load_config
from sharepoint_sim.service import SharePointCSVGenerator


@pytest.fixture()
def dirs(tmp_path: Path) -> tuple[Path, Path]:
    ingest = tmp_path / "ingest"
    archive = tmp_path / "archive"
    ingest.mkdir()
    archive.mkdir()
    return ingest, archive


def test_consumer_processes_sim_file(dirs: tuple[Path, Path]) -> None:
    ingest, archive = dirs

    # Generate one dataset using in-process sim to proper storage
    cfg = load_config()
    gen = SharePointCSVGenerator(root_dir=cfg.output_dir, seed=cfg.seed)
    path = gen.generate("ACQ", rows=3)

    # Copy the generated file into the ingestion directory
    (ingest / path.name).write_text(path.read_text())

    # DB stub records calls
    class DBStub:
        def __init__(self) -> None:
            self.calls: list[str] = []
        def send_to_db(self, data: str) -> None:  # noqa: D401
            self.calls.append(data)

    db = DBStub()
    consumer = FileConsumer(ingest, archive, db)

    consumer.consume_new_files()

    # Assert archived and DB got data
    assert len(db.calls) == 1
    assert not any(ingest.glob("*.csv"))
    assert any(archive.glob("*.csv"))
