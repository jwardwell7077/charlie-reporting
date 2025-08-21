"""Integration: FileConsumer idempotency across multiple runs."""
from pathlib import Path
from unittest.mock import MagicMock

from consumer.file_watcher import FileConsumer


def test_consumer_idempotent_across_runs(tmp_path: Path) -> None:
    ingest_dir = tmp_path / "ingest"
    archive_dir = tmp_path / "archive"
    ingest_dir.mkdir(parents=True, exist_ok=True)
    archive_dir.mkdir(parents=True, exist_ok=True)

    # create a file in ingest
    f = ingest_dir / "dup.csv"
    f.write_text("a,b\n1,2\n")

    db = MagicMock()
    consumer = FileConsumer(ingest_dir, archive_dir, db)

    # First run processes and archives
    consumer.consume_new_files()
    db.send_to_db.assert_called_once()
    assert not f.exists()
    assert (archive_dir / "dup.csv").exists()

    # Move archived file back to ingest to simulate reappearance
    (archive_dir / "dup.csv").replace(f)

    # Second run should skip due to tracker
    consumer.consume_new_files()
    db.send_to_db.assert_called_once()
