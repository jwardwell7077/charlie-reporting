"""FileConsumer: Scheduler-driven file watcher and processor for SharePoint CSV drops.

Implements all behaviors and interfaces specified in file_consumer_spec.md.
"""
import logging
import shutil
from pathlib import Path
from typing import Protocol


class DBServiceProtocol(Protocol):
    """Minimal protocol for DB service used by the consumer."""

    def send_to_db(self, data: str) -> None:  # pragma: no cover - simple protocol
        """Send CSV data to the database service."""
        ...


class TrackerProtocol(Protocol):
    """Protocol for tracking processed files."""

    def is_processed(self, filename: str) -> bool:  # pragma: no cover - simple protocol
        """Return True if the filename was processed previously."""
        ...

    def mark_processed(self, filename: str) -> None:  # pragma: no cover - simple protocol
        """Mark the given filename as processed."""
        ...


class FileConsumer:
    """Consumes new files from an input directory, archives them, and sends to DB service.

    Args:
        input_dir (Path): Directory to watch for new files.
        archive_dir (Path): Directory to move processed files.
    db_service (DBServiceProtocol): Service for sending data to the database.
    tracker (TrackerProtocol | None): Tracks processed files. Defaults to in-memory.
        logger (Optional[logging.Logger]): Logger instance. Defaults to standard logger.
    """
    def __init__(
        self,
        input_dir: Path,
        archive_dir: Path,
    db_service: DBServiceProtocol,
    tracker: TrackerProtocol | None = None,
        logger: logging.Logger | None = None,
    ) -> None:
        """Initialize a new FileConsumer.

        Args:
            input_dir: Directory to watch for new files.
            archive_dir: Directory to move processed files.
            db_service: Service for sending data to the database.
            tracker: Optional tracker to record processed files.
            logger: Optional logger instance.
        """
        self.input_dir = Path(input_dir)
        self.archive_dir = Path(archive_dir)
        self.db_service = db_service
        self.tracker = tracker or InMemoryTracker()
        self.logger = logger or logging.getLogger(__name__)

    def consume_new_files(self) -> None:
        """Process all unprocessed files in the input directory."""
        for file_path in self.input_dir.glob("*.csv"):
            if not self.tracker.is_processed(file_path.name):
                self.process_file(file_path)

    def process_file(self, path: Path) -> None:
        """Validate, send to DB, and archive file if successful.

        Args:
            path (Path): Path to the file to process.
        """
        if not self.validate_file(path):
            self.logger.info(f"Skipping invalid file: {path.name}")
            return
        try:
            with path.open("r") as f:
                data = f.read()
            self.send_to_db(data)
            self.archive_file(path)
            self.tracker.mark_processed(path.name)
        except Exception as e:
            self.logger.error(f"Failed to process {path.name}: {e}")

    def archive_file(self, path: Path) -> None:
        """Move file to archive directory.

        Args:
            path (Path): Path to the file to archive.
        """
        # Ensure archive directory exists before moving
        self.archive_dir.mkdir(parents=True, exist_ok=True)
        dest = self.archive_dir / path.name
        shutil.move(str(path), str(dest))

    def send_to_db(self, data: str) -> None:
        """Send file data to the DB service.

        Args:
            data (str): File contents to send.
        """
        self.db_service.send_to_db(data)

    def validate_file(self, path: Path) -> bool:
        """Validate file extension and (optionally) schema.

        Args:
            path (Path): Path to the file to validate.

        Returns:
            bool: True if file is valid, False otherwise.
        """
        return path.suffix == ".csv"

class InMemoryTracker(TrackerProtocol):
    """Tracks processed files in memory."""

    def __init__(self) -> None:
        """Initialize an empty in-memory tracker."""
        self._seen: set[str] = set()

    def is_processed(self, filename: str) -> bool:
        """Return True if the file has been marked as processed."""
        return filename in self._seen

    def mark_processed(self, filename: str) -> None:
        """Mark the file as processed."""
        self._seen.add(filename)
