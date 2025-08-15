"""archiver.py
-----------
Handles archiving of processed files.
Uses pathlib for cross - platform path handling.

Author: Jonathan Wardwell, Copilot, GPT - 4o
License: MIT
"""

import shutil
from pathlib import Path

from logger import LoggerFactory


class Archiver:
    """Archiver encapsulates the logic for moving processed files to an archive directory,
    optionally organizing by date subfolders.
    Uses pathlib for cross - platform path compatibility.
    """
    def __init__(self, archive_dir: str = 'data / archive', log_file: str = 'archiver.log'):
        self.archivedir = Path(archive_dir)  # Convert to Path object
        self.archive_dir.mkdir(parents=True, exist_ok=True)
        self.logger = LoggerFactory.get_logger('archiver', log_file)

    def archive(self, filepath: str):
        """Move the given file to the archive directory.
        """
        filepath = Path(filepath)  # Convert to Path object
        if not file_path.is_file():
            self.logger.warning(f"File not found, cannot archive: {filepath}")
            return

        filename = file_path.name
        destpath = self.archive_dir / filename
        try:
            shutil.move(str(file_path), str(dest_path))
            self.logger.info(f"Archived file: {filename}")
        except Exception as e:
            self.logger.error(f"Failed to archive {filename}: {e}", exc_info=True)