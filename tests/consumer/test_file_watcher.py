"""Tests for FileConsumer component (see file_consumer_spec.md).

All tests follow project code style, typing, and docstring standards.
"""
import pytest
from unittest.mock import MagicMock, patch
from pathlib import Path
from consumer.file_watcher import FileConsumer

@pytest.fixture
def tmp_dirs(tmp_path: Path) -> tuple[Path, Path]:
    input_dir = tmp_path / "input"
    archive_dir = tmp_path / "archive"
    input_dir.mkdir()
    archive_dir.mkdir()
    return input_dir, archive_dir

def test_consume_new_files_processes_unseen_files(tmp_dirs: tuple[Path, Path]) -> None:
    """Test that FileConsumer processes new files and archives them after DB send.

    Args:
        tmp_dirs (tuple[Path, Path]): Tuple of input and archive directories as pathlib.Path objects.
    """
    input_dir, archive_dir = tmp_dirs
    # Create dummy file
    f = input_dir / "test.csv"
    f.write_text("col1,col2\n1,2\n")
    db_service = MagicMock()
    consumer = FileConsumer(input_dir, archive_dir, db_service)
    consumer.consume_new_files()
    db_service.send_to_db.assert_called_once()
    assert not f.exists()
    archived = archive_dir / "test.csv"
    assert archived.exists()

def test_consume_new_files_skips_processed(tmp_dirs: tuple[Path, Path]) -> None:
    """Test that FileConsumer does not reprocess already archived files.

    Args:
        tmp_dirs (tuple[Path, Path]): Tuple of input and archive directories as pathlib.Path objects.
    """
    input_dir, archive_dir = tmp_dirs
    f = input_dir / "test.csv"
    f.write_text("col1,col2\n1,2\n")
    db_service = MagicMock()
    consumer = FileConsumer(input_dir, archive_dir, db_service)
    consumer.consume_new_files()
    # Move file back to input to simulate reappearance
    archived = archive_dir / "test.csv"
    archived.replace(f)
    consumer.consume_new_files()
    # Should only call send_to_db once
    db_service.send_to_db.assert_called_once()

def test_process_file_validates_and_sends(tmp_dirs: tuple[Path, Path]) -> None:
    """Test that process_file validates file, sends to DB, and archives on success.

    Args:
        tmp_dirs (tuple[Path, Path]): Tuple of input and archive directories as pathlib.Path objects.
    """
    input_dir, archive_dir = tmp_dirs
    f = input_dir / "good.csv"
    f.write_text("col1,col2\n1,2\n")
    db_service = MagicMock()
    consumer = FileConsumer(input_dir, archive_dir, db_service)
    with patch.object(consumer, 'validate_file', return_value=True) as mock_validate:
        consumer.process_file(f)
        mock_validate.assert_called_once_with(f)
        db_service.send_to_db.assert_called_once()
        assert not f.exists()
        assert (archive_dir / "good.csv").exists()

def test_process_file_invalid_file(tmp_dirs: tuple[Path, Path]) -> None:
    """Test that process_file skips/does not send invalid files.

    Args:
        tmp_dirs (tuple[Path, Path]): Tuple of input and archive directories as pathlib.Path objects.
    """
    input_dir, archive_dir = tmp_dirs
    f = input_dir / "bad.txt"
    f.write_text("not a csv")
    db_service = MagicMock()
    consumer = FileConsumer(input_dir, archive_dir, db_service)
    with patch.object(consumer, 'validate_file', return_value=False):
        consumer.process_file(f)
        db_service.send_to_db.assert_not_called()
        assert f.exists()
        assert not (archive_dir / "bad.txt").exists()

def test_send_to_db_handles_errors(tmp_dirs: tuple[Path, Path]) -> None:
    """Test that send_to_db logs and does not archive on DB error.

    Args:
        tmp_dirs (tuple[Path, Path]): Tuple of input and archive directories as pathlib.Path objects.
    """
    input_dir, archive_dir = tmp_dirs
    f = input_dir / "fail.csv"
    f.write_text("col1,col2\n1,2\n")
    db_service = MagicMock()
    db_service.send_to_db.side_effect = Exception("DB error")
    consumer = FileConsumer(input_dir, archive_dir, db_service)
    with patch.object(consumer, 'validate_file', return_value=True):
        with patch.object(consumer, 'logger') as mock_logger:
            consumer.process_file(f)
            mock_logger.error.assert_called()
            assert f.exists()
            assert not (archive_dir / "fail.csv").exists()

def test_tracker_prevents_duplicate_processing(tmp_dirs: tuple[Path, Path]) -> None:
    """Test that the tracker prevents duplicate processing of files.

    Args:
        tmp_dirs (tuple[Path, Path]): Tuple of input and archive directories as pathlib.Path objects.
    """
    input_dir, archive_dir = tmp_dirs
    f = input_dir / "dupe.csv"
    f.write_text("col1,col2\n1,2\n")
    db_service = MagicMock()
    consumer = FileConsumer(input_dir, archive_dir, db_service)
    consumer.tracker = MagicMock()
    consumer.tracker.is_processed.return_value = True
    consumer.consume_new_files()
    db_service.send_to_db.assert_not_called()

def test_archive_file_moves_file(tmp_dirs: tuple[Path, Path]) -> None:
    """Test that archive_file moves file to archive directory.

    Args:
        tmp_dirs (tuple[Path, Path]): Tuple of input and archive directories as pathlib.Path objects.
    """
    input_dir, archive_dir = tmp_dirs
    f = input_dir / "toarchive.csv"
    f.write_text("col1,col2\n1,2\n")
    db_service = MagicMock()
    consumer = FileConsumer(input_dir, archive_dir, db_service)
    consumer.archive_file(f)
    assert not f.exists()
    assert (archive_dir / "toarchive.csv").exists()
